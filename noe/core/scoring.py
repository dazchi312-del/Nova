"""
NOE Scoring Module
Defense in Depth JSON extraction with weighted scoring
"""

import json
import re
from typing import Optional

# Scoring weights from config
WEIGHTS = {
    'quality': 0.20,
    'clarity': 0.25,
    'structure': 0.20,
    'hallucination_risk': 0.20,
    'identity_alignment': 0.15
}

def extract_json_defensive(llm_response: str) -> Optional[dict]:
    """
    Defense in Depth: Six strategies to extract JSON from LLM output.
    LLMs are probabilistic - they don't always format perfectly.
    """
    
    # Strategy 1: Direct parse (clean response)
    try:
        return json.loads(llm_response.strip())
    except json.JSONDecodeError:
        pass
    
    # Strategy 2: Find JSON in code blocks
    code_block = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', llm_response)
    if code_block:
        try:
            return json.loads(code_block.group(1))
        except json.JSONDecodeError:
            pass
    
    # Strategy 3: Find JSON object pattern
    json_match = re.search(r'\{[\s\S]*\}', llm_response)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    
    # Strategy 4: Line-by-line search
    for line in llm_response.split('\n'):
        line = line.strip()
        if line.startswith('{') and line.endswith('}'):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    
    # Strategy 5: Fix common LLM mistakes
    cleaned = llm_response.strip()
    cleaned = re.sub(r',\s*}', '}', cleaned)  # Remove trailing commas
    cleaned = re.sub(r',\s*]', ']', cleaned)
    try:
        json_match = re.search(r'\{[\s\S]*\}', cleaned)
        if json_match:
            return json.loads(json_match.group())
    except json.JSONDecodeError:
        pass
    
    # Strategy 6: Extract key-value pairs manually
    scores = {}
    patterns = [
        r'"?(\w+)"?\s*:\s*(\d*\.?\d+)',
        r'(\w+)\s*=\s*(\d*\.?\d+)',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, llm_response)
        for key, value in matches:
            key_lower = key.lower()
            if key_lower in WEIGHTS:
                scores[key_lower] = float(value)
    
    if scores:
        return scores
    
    return None


def calculate_weighted_score(scores: dict) -> float:
    """
    Calculate final score using configured weights.
    Returns value between 0.0 and 1.0
    """
    if not scores:
        return 0.0
    
    total = 0.0
    weight_sum = 0.0
    
    for dimension, weight in WEIGHTS.items():
        if dimension in scores:
            # Normalize to 0-1 range if needed
            value = scores[dimension]
            if value > 1.0:
                value = value / 10.0  # Handle 0-10 scale
            if value > 1.0:
                value = value / 10.0  # Handle 0-100 scale
            
            total += value * weight
            weight_sum += weight
    
    if weight_sum == 0:
        return 0.0
    
    return round(total / weight_sum * weight_sum, 3)


def score_response(llm_response: str) -> tuple[Optional[float], Optional[dict]]:
    """
    Main entry point: Extract scores and calculate weighted result.
    Returns (final_score, raw_scores) or (None, None) on failure.
    """
    raw_scores = extract_json_defensive(llm_response)
    
    if raw_scores is None:
        return None, None
    
    final_score = calculate_weighted_score(raw_scores)
    return final_score, raw_scores
