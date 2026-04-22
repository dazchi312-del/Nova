"""
NOE Reflector Client
Communicates with the MacBook Reflector node for output scoring
"""

import requests
import json
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

# Load prompt template
PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "reflector_scoring.txt"


def load_scoring_prompt() -> str:
    """Load the reflector scoring prompt template"""
    if PROMPT_PATH.exists():
        return PROMPT_PATH.read_text(encoding='utf-8')
    else:
        raise FileNotFoundError(f"Scoring prompt not found at {PROMPT_PATH}")


def build_scoring_request(user_prompt: str, generated_output: str) -> str:
    """Build the complete prompt for the Reflector"""
    template = load_scoring_prompt()
    return template.format(
        user_prompt=user_prompt,
        generated_output=generated_output
    )


def call_reflector(
    prompt: str,
    reflector_url: str = "http://10.0.0.167:11434",
    model: str = "llama3.1:8b",
    timeout: int = 120
) -> Optional[str]:
    """
    Send prompt to MacBook Reflector via Ollama API
    
    Args:
        prompt: The complete scoring prompt
        reflector_url: Ollama server URL on MacBook
        model: Model to use for reflection
        timeout: Request timeout in seconds
    
    Returns:
        Response text or None if failed
    """
    endpoint = f"{reflector_url}/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 500
        }
    }
    
    try:
        response = requests.post(
            endpoint,
            json=payload,
            timeout=timeout
        )
        response.raise_for_status()
        
        result = response.json()
        return result.get("response", None)
        
    except requests.exceptions.ConnectionError:
        print("[Reflector] Connection failed - is MacBook Ollama running?")
        return None
    except requests.exceptions.Timeout:
        print("[Reflector] Request timed out")
        return None
    except Exception as e:
        print(f"[Reflector] Error: {e}")
        return None


def get_reflection_score(
    user_prompt: str,
    generated_output: str,
    reflector_url: str = "http://10.0.0.167:11434"
) -> Tuple[Optional[float], Optional[Dict[str, Any]]]:
    """
    Complete reflection pipeline: build prompt, call reflector, parse scores
    
    Args:
        user_prompt: Original user request
        generated_output: Nemotron's output to evaluate
        reflector_url: MacBook Ollama URL
    
    Returns:
        Tuple of (final_score, raw_scores_dict) or (None, None) on failure
    """
    from scoring import score_response
    
    # Build the scoring prompt
    full_prompt = build_scoring_request(user_prompt, generated_output)
    
    # Call the Reflector
    reflector_response = call_reflector(full_prompt, reflector_url)
    
    if reflector_response is None:
        return None, None
    
    # Parse and score the response
    return score_response(reflector_response)


# === Local testing without MacBook ===

def mock_reflector_response() -> str:
    """Generate a mock Reflector response for testing"""
    return json.dumps({
        "quality": 0.85,
        "clarity": 0.90,
        "structure": 0.80,
        "hallucination_risk": 0.75,
        "identity_alignment": 0.85,
        "reasoning": "Mock response for local testing"
    })


def test_local():
    """Test the module without MacBook connection"""
    print("Testing Reflector Module (Local Mode)")
    print("=" * 40)
    
    # Test prompt loading
    try:
        template = load_scoring_prompt()
        print(f"✓ Prompt template loaded ({len(template)} chars)")
    except FileNotFoundError as e:
        print(f"✗ Prompt loading failed: {e}")
        return False
    
    # Test prompt building
    test_prompt = "Explain what Nova is"
    test_output = "Nova is a local-first AI operating system..."
    
    full_prompt = build_scoring_request(test_prompt, test_output)
    assert "{user_prompt}" not in full_prompt, "Template not filled"
    assert "{generated_output}" not in full_prompt, "Template not filled"
    print("✓ Prompt building works")
    
    # Test mock scoring
    from scoring import score_response
    mock_response = mock_reflector_response()
    score, raw = score_response(mock_response)
    assert score is not None, "Mock scoring failed"
    print(f"✓ Mock scoring works: {score:.3f}")
    
    print()
    print("=" * 40)
    print("Local tests passed. MacBook connection required for live tests.")
    return True


if __name__ == "__main__":
    test_local()
