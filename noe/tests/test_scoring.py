"""
NOE Scoring Module Tests
Test-Driven Development verification
"""

import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from scoring import extract_json_defensive, calculate_weighted_score, score_response

def test_clean_json():
    """Test Strategy 1: Clean JSON response"""
    response = '{"quality": 0.8, "clarity": 0.9, "structure": 0.85, "hallucination_risk": 0.7, "identity_alignment": 0.75}'
    result = extract_json_defensive(response)
    assert result is not None, "Failed to parse clean JSON"
    assert result['quality'] == 0.8
    print("✓ Clean JSON parsing works")

def test_code_block_json():
    """Test Strategy 2: JSON in code blocks"""
    response = "Here is my analysis:\n```json\n{\"quality\": 0.8, \"clarity\": 0.9, \"structure\": 0.85, \"hallucination_risk\": 0.7, \"identity_alignment\": 0.75}\n```\nThat is my assessment."
    result = extract_json_defensive(response)
    assert result is not None, "Failed to parse code block JSON"
    assert result['clarity'] == 0.9
    print("✓ Code block JSON parsing works")

def test_embedded_json():
    """Test Strategy 3: JSON embedded in text"""
    response = 'The scores are {"quality": 0.8, "clarity": 0.9, "structure": 0.85, "hallucination_risk": 0.7, "identity_alignment": 0.75} based on my review.'
    result = extract_json_defensive(response)
    assert result is not None, "Failed to parse embedded JSON"
    assert result['structure'] == 0.85
    print("✓ Embedded JSON parsing works")

def test_weighted_score():
    """Test weighted score calculation"""
    scores = {
        'quality': 0.8,
        'clarity': 0.9,
        'structure': 0.85,
        'hallucination_risk': 0.7,
        'identity_alignment': 0.75
    }
    result = calculate_weighted_score(scores)
    assert result is not None, "Failed to calculate score"
    assert 0.0 <= result <= 1.0, "Score out of range"
    print("✓ Weighted score calculation works: " + str(result))

def test_full_pipeline():
    """Test complete scoring pipeline"""
    response = "Based on my analysis:\n```json\n{\"quality\": 0.85, \"clarity\": 0.90, \"structure\": 0.80, \"hallucination_risk\": 0.75, \"identity_alignment\": 0.85}\n```"
    final_score, raw_scores = score_response(response)
    assert final_score is not None, "Pipeline returned no score"
    assert raw_scores is not None, "Pipeline returned no raw scores"
    assert 0.0 <= final_score <= 1.0
    print("✓ Full pipeline works: " + str(final_score))

def run_all_tests():
    """Run all tests"""
    print("NOE Scoring Module Tests")
    print("=" * 40)
    print()
    
    tests = [
        test_clean_json,
        test_code_block_json,
        test_embedded_json,
        test_weighted_score,
        test_full_pipeline,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print("FAIL " + test.__name__ + ": " + str(e))
            failed += 1
        except Exception as e:
            print("FAIL " + test.__name__ + ": Unexpected error - " + str(e))
            failed += 1
    
    print()
    print("=" * 40)
    print("Results: " + str(passed) + " passed, " + str(failed) + " failed")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
