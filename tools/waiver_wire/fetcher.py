# tools/waiver_wire/fetcher.py
# Yahoo Fantasy API connection layer
# OAuth2 + token caching + waiver wire data

import json
import os
import webbrowser
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
from requests_oauthlib import OAuth2Session
from models import PlayerProfile

# ── Credentials ──────────────────────────────────────────────────────────────
# Loaded from yahoo_credentials.py (excluded from git)
try:
    from yahoo_credentials import CLIENT_ID, CLIENT_SECRET
except ImportError:
    raise RuntimeError(
        "yahoo_credentials.py not found.\n"
        "Create it in tools/waiver_wire/ with:\n"
        "  CLIENT_ID = 'your_client_id'\n"
        "  CLIENT_SECRET = 'your_client_secret'"
    )

# ── Constants ─────────────────────────────────────────────────────────────────
REDIRECT_URI = "https://wrench-paparazzi-buffer.ngrok-free.dev/callback"
AUTH_URL         = "https://api.login.yahoo.com/oauth2/request_auth"
TOKEN_URL        = "https://api.login.yahoo.com/oauth2/get_token"
BASE_URL         = "https://fantasysports.yahooapis.com/fantasy/v2"
LEAGUE_ID        = "46348"
GAME_CODE        = "mlb"
TOKEN_CACHE_FILE = ".yahoo_token_cache.json"
SCOPE            = "fspt-r"


# ── Token Cache ───────────────────────────────────────────────────────────────
def _save_token(token: dict):
    with open(TOKEN_CACHE_FILE, "w") as f:
        json.dump(token, f, indent=2)


def _load_token() -> dict | None:
    if not os.path.exists(TOKEN_CACHE_FILE):
        return None
    with open(TOKEN_CACHE_FILE, "r") as f:
        return json.load(f)


def _token_is_valid(token: dict) -> bool:
    expires_at = token.get("expires_at", 0)
    return datetime.now(datetime.UTC).timestamp() < expires_at - 60



# ── OAuth2 Flow ───────────────────────────────────────────────────────────────
class _CallbackHandler(BaseHTTPRequestHandler):
    """Captures the OAuth2 callback code from Yahoo."""
    auth_code = None

    def do_GET(self):
        params = parse_qs(urlparse(self.path).query)
        if "code" in params:
            _CallbackHandler.auth_code = params["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Auth complete. Return to terminal.")
        else:
            self.send_response(400)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress server logs


def _run_oauth_flow() -> dict:
    """Full OAuth2 browser flow. Returns token dict."""
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPE)
    auth_url, _ = oauth.authorization_url(AUTH_URL)

    print("\n── Yahoo OAuth2 ─────────────────────────────")
    print("Opening browser for authorization...")
    print(f"If browser doesn't open, visit:\n  {auth_url}\n")
    webbrowser.open(auth_url)

    # Start local server to catch callback
    server = HTTPServer(("localhost", 8080), _CallbackHandler)
    print("Waiting for callback on localhost:8080...")
    server.handle_request()

    if not _CallbackHandler.auth_code:
        raise RuntimeError("No auth code received from Yahoo.")

    # Exchange code for token
    token = oauth.fetch_token(
        TOKEN_URL,
        code=_CallbackHandler.auth_code,
        client_secret=CLIENT_SECRET
    )

    _save_token(token)
    print("Token saved to cache.\n")
    return token


# ── Session Manager ───────────────────────────────────────────────────────────
def _get_session() -> OAuth2Session:
    """Returns authenticated OAuth2Session, refreshing token if needed."""
    token = _load_token()

    if token and _token_is_valid(token):
        return OAuth2Session(CLIENT_ID, token=token)

    if token:
        # Attempt refresh
        print("Token expired. Refreshing...")
        try:
            oauth = OAuth2Session(CLIENT_ID, token=token)
            new_token = oauth.refresh_token(
                TOKEN_URL,
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET
            )
            _save_token(new_token)
            return OAuth2Session(CLIENT_ID, token=new_token)
        except Exception as e:
            print(f"Refresh failed: {e}. Re-authenticating...")

    # Full auth flow
    token = _run_oauth_flow()
    return OAuth2Session(CLIENT_ID, token=token)


# ── API Helpers ───────────────────────────────────────────────────────────────
def _get(endpoint: str, params: dict = None) -> dict:
    """Authenticated GET. Returns parsed JSON."""
    session = _get_session()
    url = f"{BASE_URL}{endpoint}"
    if params is None:
        params = {}
    params["format"] = "json"

    response = session.get(url, params=params)
    response.raise_for_status()
    return response.json()


# ── League Info ───────────────────────────────────────────────────────────────
def get_league_key() -> str:
    """Returns the full Yahoo league key for the current season."""
    data = _get(f"/game/{GAME_CODE}/leagues;league_keys={GAME_CODE}.l.{LEAGUE_ID}")
    return data["fantasy_content"]["game"][1]["leagues"]["0"]["league"][0]["league_key"]


# ── Waiver Wire Players ───────────────────────────────────────────────────────
def get_waiver_players(league_key: str, count: int = 25) -> list[PlayerProfile]:
    """
    Fetches top available (waiver) players from Yahoo.
    Returns list of validated PlayerProfile objects.
    """
    endpoint = f"/league/{league_key}/players"
    params = {
        "status": "A",        # Available players only
        "sort": "AR",         # Sort by adds + ranking
        "count": count,
        "start": 0
    }

    data = _get(endpoint, params)
    players_raw = data["fantasy_content"]["league"][1]["players"]

    profiles = []
    for key, val in players_raw.items():
        if key == "count":
            continue
        try:
            p = val["player"][0]
            name_data = next(x for x in p if isinstance(x, dict) and "full" in str(x))
            full_name = name_data.get("full_name", "Unknown")
            team = next(
                (x["editorial_team_abbr"] for x in p if isinstance(x, dict)
                 and "editorial_team_abbr" in x), "UNK"
            )
            positions_raw = next(
                (x["display_position"] for x in p if isinstance(x, dict)
                 and "display_position" in x), ""
            )
            positions = [pos.strip() for pos in positions_raw.split(",") if pos.strip()]
            status = next(
                (x["status"] for x in p if isinstance(x, dict) and "status" in x), None
            )
            ownership_raw = val["player"][1]
            ownership_pct = float(
                ownership_raw.get("ownership", {}).get("ownership_percent", 0.0)
            )

            profile = PlayerProfile(
                name=full_name,
                team=team,
                positions=positions,
                is_available=True,
                injury_status=status,
                ownership_pct=ownership_pct
            )
            profiles.append(profile)

        except Exception as e:
            print(f"  Skipped player (parse error): {e}")
            continue

    return profiles


# ── Quick Test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import json as _json
    print("Testing Yahoo connection...")
    league_key = get_league_key()
    print(f"League key: {league_key}")

    # Raw dump to see actual structure
    endpoint = f"/league/{league_key}/players"
    params = {"status": "A", "sort": "AR", "count": 3, "start": 0}
    data = _get(endpoint, params)
    print("\n── Raw API Response ──")
    print(_json.dumps(data, indent=2))
