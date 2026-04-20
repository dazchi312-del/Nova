"""
Big Dan Baseball v1.0 — Waiver Wire Scorer
Layer 1: Raw Outlier Score (z-score based)
Layer 2: Contextual Modifier (role, matchup, injury)
Layer 3: Profile + Need Modifier (user risk + category gaps)
Layer 4: Signal Classifier (SIGNAL/WATCH/NOISE)
Layer 5: Final Score + Recommendation
"""

from config import (
    SENSITIVITY,
    STAT_BASELINES,
    MODIFIER_RANGES,
    QUALITY_BASELINES,
    QUALITY_THRESHOLDS,
    PLAYER_CATEGORY_MAP,
    OWNERSHIP_THRESHOLDS,
)

# ─────────────────────────────────────────
# HOLDS HUNTER PROFILE
# ─────────────────────────────────────────

# ─────────────────────────────────────────
# LAYER 1: RAW OUTLIER SCORE
# ─────────────────────────────────────────

def calculate_z_score(value: float, mean: float, std: float) -> float:
    """Calculate standard z-score."""
    if std == 0:
        return 0.0
    return (value - mean) / std


def calculate_raw_score(z_score: float, sensitivity: int = SENSITIVITY) -> float:
    """
    Convert z-score to 0-100 scale.
    Baseline (z=0) = 50, each z-unit moves score by sensitivity points.
    """
    raw = 50 + (z_score * sensitivity)
    return max(0, min(100, raw))


# ─────────────────────────────────────────
# LAYER 2: CONTEXTUAL MODIFIER
# ─────────────────────────────────────────

def calculate_context_modifier(
    role_secure: bool | None,
    starts_next_week: int,
    team_rank: int,
    opp_rank: int,
    injury_risk: bool,
    platoon_risk: bool,
) -> float:
    """
    Adjust score based on playing time and matchup context.
    Returns modifier between 0.5 and 1.5.
    """
    modifier = 1.0

    # Role security (handle None as slight penalty)
    if role_secure is None:
        modifier *= 0.9
    elif role_secure:
        modifier *= 1.1
    else:
        modifier *= 0.8

    # Starts next week (SP specific)
    if starts_next_week >= 2:
        modifier *= 1.15
    elif starts_next_week == 1:
        modifier *= 1.0
    else:
        modifier *= 0.85

    # Team strength (1 = best, 30 = worst)
    if team_rank <= 10:
        modifier *= 1.1
    elif team_rank >= 20:
        modifier *= 0.9

    # Opponent weakness (higher rank = weaker opponent = good)
    if opp_rank >= 20:
        modifier *= 1.1
    elif opp_rank <= 10:
        modifier *= 0.9

    # Risk factors
    if injury_risk:
        modifier *= 0.85
    if platoon_risk:
        modifier *= 0.9

    # Clamp to range
    return max(
        MODIFIER_RANGES["context"]["min"],
        min(MODIFIER_RANGES["context"]["max"], modifier),
    )


# ─────────────────────────────────────────
# LAYER 3: PROFILE + NEED MODIFIER
# ─────────────────────────────────────────

def calculate_need_modifier(
    player_type: str,
    category_need: list[str],
) -> float:
    """
    Boost score if player contributes to categories you're chasing.
    """
    if not category_need:
        return 1.0

    player_categories = PLAYER_CATEGORY_MAP.get(player_type, [])
    overlap = set(player_categories) & set(category_need)

    if len(overlap) >= 3:
        return 1.5  # Strong multi-category fit
    elif len(overlap) == 2:
        return 1.3  # Good fit
    elif len(overlap) == 1:
        return 1.15  # Marginal fit
    else:
        return 0.85  # Doesn't address your gaps


def calculate_profile_modifier(
    profile: str,
    need_modifier: float,
) -> float:
    """
    Combine user risk profile with category need.
    """
    profile_base = {
        "aggressive": 1.2,
        "neutral": 1.0,
        "conservative": 0.85,
    }

    base = profile_base.get(profile, 1.0)
    combined = base * need_modifier

    # Clamp to range
    return max(
        MODIFIER_RANGES["profile"]["min"],
        min(MODIFIER_RANGES["profile"]["max"], combined),
    )


# ─────────────────────────────────────────
# LAYER 4: SIGNAL CLASSIFIER
# ─────────────────────────────────────────

def classify_signal(
    hot_streak_days: int,
    confirming_stats: int,
    quality_score: float,
) -> str:
    """
    Classify player data quality.
    
    Args:
        hot_streak_days: Length of current performance spike
        confirming_stats: Number of underlying metrics supporting breakout
        quality_score: xwOBA or equivalent quality metric
    
    Returns:
        SIGNAL, WATCH, or NOISE
    """
    # Quality threshold check
    if quality_score >= QUALITY_THRESHOLDS["auto_add"]:
        quality_tier = "elite"
    elif quality_score >= QUALITY_THRESHOLDS["watch"]:
        quality_tier = "good"
    else:
        quality_tier = "poor"

    # Classification logic
    if quality_tier == "elite" and confirming_stats >= 2:
        return "SIGNAL"
    elif quality_tier == "elite" and confirming_stats < 2:
        return "WATCH"  # Great underlying, need more confirmation
    elif quality_tier == "good" and hot_streak_days >= 10 and confirming_stats >= 2:
        return "SIGNAL"
    elif quality_tier == "good":
        return "WATCH"
    else:
        return "NOISE"


# ─────────────────────────────────────────
# LAYER 5: FINAL SCORE + RECOMMENDATION
# ─────────────────────────────────────────

def calculate_quality_score(
    x_woba: float | None,
    hard_hit_rate: float | None,
    exit_velo: float | None,
    k_per_9: float | None = None,
    whip: float | None = None,
    player_type: str = "balanced_hitter",
) -> float:
    """
    Calculate composite quality score from Statcast metrics.
    Returns 0.0 to 0.500 scale (like xwOBA).
    """
    # Pitcher logic
    if player_type in ["ace", "closer", "holds_hunter", "streamer"]:
        scores = []
        if k_per_9 is not None:
            scores.append(min(0.5, k_per_9 / 25))
        if whip is not None:
            scores.append(max(0.2, 0.5 - (whip - 0.8) * 0.4))
        return sum(scores) / len(scores) if scores else 0.32

    # Hitter logic
    scores = []
    weights = []

    if x_woba is not None:
        scores.append(x_woba)
        weights.append(3)

    if hard_hit_rate is not None:
        scores.append(hard_hit_rate * 0.8 + 0.05)
        weights.append(2)

    if exit_velo is not None:
        scores.append((exit_velo - 80) / 35)
        weights.append(1)

    if not scores:
        return 0.32

    return sum(s * w for s, w in zip(scores, weights)) / sum(weights)


    # Hitter logic
    scores = []
    weights = []

    if x_woba is not None:
        scores.append(x_woba)
        weights.append(3)  # Primary metric

    if hard_hit_rate is not None:
        # Convert HH% to xwOBA-like scale
        scores.append(hard_hit_rate * 0.8 + 0.05)
        weights.append(2)

    if exit_velo is not None:
        # Convert EV to xwOBA-like scale (88 EV = 0.32, 94 EV = 0.40)
        scores.append((exit_velo - 80) / 35)
        weights.append(1)

    if not scores:
        return 0.32  # League average default

    return sum(s * w for s, w in zip(scores, weights)) / sum(weights)


def final_score(
    z_score: float,
    role_secure: bool | None,
    starts_next_week: int,
    team_rank: int,
    opp_rank: int,
    injury_risk: bool,
    platoon_risk: bool,
    profile: str,
    player_type: str,
    category_need: list[str],
    hot_streak_days: int,
    confirming_stats: int,
    x_woba: float | None = None,
    hard_hit_rate: float | None = None,
    exit_velo: float | None = None,
    k_per_9: float | None = None,
    whip: float | None = None,
    ownership_pct: float = 0.0,
) -> dict:
    """
    Master scoring function combining all layers.
    
    Returns:
        {
            "score": 0-100,
            "recommendation": "ADD" | "WATCH" | "IGNORE",
            "signal": "SIGNAL" | "WATCH" | "NOISE",
            "category_fit": ["HR", "RBI", ...],
            "flags": ["quality_elite", "role_uncertain", ...]
        }
    """
    flags = []

    # Layer 1: Raw score
    raw = calculate_raw_score(z_score)

    # Layer 2: Context modifier
    context_mod = calculate_context_modifier(
        role_secure=role_secure,
        starts_next_week=starts_next_week,
        team_rank=team_rank,
        opp_rank=opp_rank,
        injury_risk=injury_risk,
        platoon_risk=platoon_risk,
    )

    if role_secure is None:
        flags.append("role_uncertain")
    if injury_risk:
        flags.append("injury_risk")
    if platoon_risk:
        flags.append("platoon_risk")

    # Layer 3: Profile + Need modifier
    need_mod = calculate_need_modifier(player_type, category_need)
    profile_mod = calculate_profile_modifier(profile, need_mod)

    # Category fit for output
    player_categories = PLAYER_CATEGORY_MAP.get(player_type, [])
    category_fit = list(set(player_categories) & set(category_need))

    # Layer 4: Quality + Signal classification
    quality = calculate_quality_score(
        x_woba=x_woba,
        hard_hit_rate=hard_hit_rate,
        exit_velo=exit_velo,
        k_per_9=k_per_9,
        whip=whip,
        player_type=player_type,
    )

    signal = classify_signal(
        hot_streak_days=hot_streak_days,
        confirming_stats=confirming_stats,
        quality_score=quality,
    )

    if quality >= QUALITY_THRESHOLDS["auto_add"]:
        flags.append("quality_elite")
    elif quality >= QUALITY_THRESHOLDS["watch"]:
        flags.append("quality_good")

    # Ownership filter (type-specific thresholds)
    if player_type == "holds_hunter":
        threshold = OWNERSHIP_THRESHOLDS["holds_hunter"]
    else:
        threshold = OWNERSHIP_THRESHOLDS["default"]

    if ownership_pct > threshold["max_ownership"]:
        flags.append("ownership_high")
        profile_mod *= threshold["penalty"]


    # Layer 5: Combine
    final = raw * context_mod * profile_mod

    # Quality bonus (up to +15 for elite quality)
    if quality >= QUALITY_THRESHOLDS["auto_add"]:
        final += 15
    elif quality >= QUALITY_THRESHOLDS["watch"]:
        final += 7

    # Signal bonus
    if signal == "SIGNAL":
        final += 10

    # Clamp
    final = max(0, min(100, final))

    # Recommendation
    if final >= 75 and signal in ["SIGNAL", "WATCH"]:
        recommendation = "ADD"
    elif final >= 50 or signal == "WATCH":
        recommendation = "WATCH"
    else:
        recommendation = "IGNORE"

    return {
        "score": round(final, 1),
        "recommendation": recommendation,
        "signal": signal,
        "category_fit": category_fit,
        "flags": flags,
        "breakdown": {
            "raw": round(raw, 1),
            "context_mod": round(context_mod, 2),
            "profile_mod": round(profile_mod, 2),
            "quality": round(quality, 3),
        },
    }
