"""Live test of MacBook Reflector scoring"""

import sys
sys.path.insert(0, 'noe/core')

from reflector import build_scoring_request, call_reflector
from scoring import score_response

# Test data
user_prompt = "Explain what Nova is in one paragraph."
generated_output = """Nova is a local-first AI operating system designed to run entirely on your own hardware, 
ensuring your data never leaves your machine. Built as a Phase 12 project, it combines a powerful 
primary node running Nemotron 70B with a validation node running Llama 3.1 8B that acts as a 
quality reflector. Nova emphasizes human agency over AI dependency, providing tools that augment 
your capabilities while maintaining complete privacy and control."""

print("=" * 50)
print("LIVE REFLECTOR TEST")
print("=" * 50)
print()
print(f"User Prompt: {user_prompt}")
print()
print(f"Output to Score:\n{generated_output[:100]}...")
print()
print("Calling MacBook Reflector...")
print()

# Build and send
full_prompt = build_scoring_request(user_prompt, generated_output)
response = call_reflector(full_prompt)

if response:
    print("Raw Reflector Response:")
    print("-" * 30)
    print(response)
    print("-" * 30)
    print()
    
    # Parse scores
    final_score, raw_scores = score_response(response)
    
    if final_score:
        print(f"FINAL WEIGHTED SCORE: {final_score:.3f}")
        print()
        print("Individual Scores:")
        for key, value in raw_scores.items():
            if key != "reasoning":
                print(f"  {key}: {value}")
        print()
        print(f"Reasoning: {raw_scores.get('reasoning', 'N/A')}")
    else:
        print("Failed to parse scores from response")
else:
    print("Failed to get response from Reflector")
