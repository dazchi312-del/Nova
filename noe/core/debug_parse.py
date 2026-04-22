"""Debug the exact response that failed"""

import json
import re

# This is the exact response from the Reflector
response = '''{
  "quality": 0.0,
  "clarity": 0.0,
  "structure": 0.0,
  "hallucination_risk": 0.0,
  "identity_alignment": 0.0,
  "reasoning": "The output contains significant inaccuracies."
}'''

print("Testing parse strategies...")
print()

# Strategy 1: Direct
try:
    result = json.loads(response.strip())
    print("Strategy 1 (direct): SUCCESS")
    print(f"  Result: {result}")
except Exception as e:
    print(f"Strategy 1 (direct): FAILED - {e}")

# Strategy 3: Regex extract
json_match = re.search(r'\{[\s\S]*\}', response)
if json_match:
    try:
        result = json.loads(json_match.group())
        print("Strategy 3 (regex): SUCCESS")
        print(f"  Result: {result}")
    except Exception as e:
        print(f"Strategy 3 (regex): FAILED - {e}")

# Now test with the actual module
print()
print("Testing scoring module...")

import sys
sys.path.insert(0, 'noe/core')
from scoring import score_response

final, raw = score_response(response)
print(f"Final score: {final}")
print(f"Raw scores: {raw}")
