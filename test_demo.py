import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.helper import get_demo_response

# Test the demo response function
test_prompts = [
    "What should be my salary expectations based on my profile?",
    "Give me a detailed plan for learning new skills",
    "How should I prepare for my next technical interview?",
    "What are the best career growth opportunities for me?"
]

print("Testing Demo Responses:")
print("=" * 50)

for i, prompt in enumerate(test_prompts, 1):
    print(f"\nTest {i}: {prompt}")
    print("-" * 30)
    response = get_demo_response(prompt)
    print(response[:200] + "..." if len(response) > 200 else response)
    print("\n" + "=" * 50)
