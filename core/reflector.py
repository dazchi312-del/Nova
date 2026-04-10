"""
Nova Reflector - Layer 5
Observes Nova's own outputs and judges quality.
First step toward self-awareness.
"""

from core.logger import log


class ReflectionResult:
    """The result of reflecting on a response."""

    def __init__(self, passed: bool, reason: str, response: str):
        self.passed = passed
        self.reason = reason
        self.response = response

    def __str__(self):
        status = "[PASS]" if self.passed else "[FAIL]"
        return f"{status} {self.reason}"


class Reflector:
    """
    Nova's self-inspection engine.
    Checks responses for quality before they reach the user.
    """

    FAILURE_PHRASES = [
        "i cannot",
        "i can't",
        "i don't know",
        "i am unable",
        "as an ai",
        "i'm not able",
        "i do not have the ability",
        "an error occurred",
        "i encountered an error",
        "something went wrong",
        "i failed to",
        "i was unable to",
    ]

    MIN_LENGTH = 10
    REPETITION_THRESHOLD = 3

    def reflect(self, response: str) -> ReflectionResult:
        """Inspect a response and return a ReflectionResult."""
        log("REFLECT", f"Inspecting response ({len(response)} chars)")

        # Check 1: Empty
        if not response or not response.strip():
            log("REFLECT", "FAIL - empty response")
            return ReflectionResult(
                passed=False,
                reason="Response is empty",
                response=response
            )

        # Check 2: Too short
        if len(response.strip()) < self.MIN_LENGTH:
            log("REFLECT", "FAIL - response too short")
            return ReflectionResult(
                passed=False,
                reason=f"Response too short ({len(response.strip())} chars)",
                response=response
            )

        # Check 3: Failure phrases
        lower = response.lower()
        for phrase in self.FAILURE_PHRASES:
            if phrase in lower:
                log("REFLECT", f"FAIL - failure phrase detected: '{phrase}'")
                return ReflectionResult(
                    passed=False,
                    reason=f"Failure phrase detected: '{phrase}'",
                    response=response
                )

        # Check 4: Repetition
        words = response.split()
        if len(words) > self.REPETITION_THRESHOLD:
            chunks = [" ".join(words[i:i+4]) for i in range(0, len(words)-3, 4)]
            if len(chunks) != len(set(chunks)):
                log("REFLECT", "FAIL - repetition detected")
                return ReflectionResult(
                    passed=False,
                    reason="Repetitive output detected",
                    response=response
                )

        log("REFLECT", "PASS")
        return ReflectionResult(
            passed=True,
            reason="Response passed all checks",
            response=response
        )
