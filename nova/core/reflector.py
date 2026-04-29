"""
core/reflector.py - L5 Response Evaluator
Chat-mode: scores prose responses (legacy).
Experiment-mode: goal-grounded grading with sandbox evidence and hard bounds.
"""

import json
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI


PASS_RE = re.compile(r"\bPASS\b")
FAIL_RE = re.compile(r"\bFAIL\b")
VERIFY_HINT_RE = re.compile(r"\b(verify|test|check|validate|assert|confirm)\b", re.I)


class Reflector:
    def __init__(self, config: dict):
        self.client = OpenAI(
            base_url=config.get("base_url", "http://10.0.0.167:11434/v1"),
            api_key=config.get("api_key", "lm-studio"),
        )
        self.model = config.get("reflection_model", "phi4:latest")
        self.threshold = config.get("reflection_threshold", 0.75)
        self.chat_dimensions = ["accuracy", "coherence", "identity_alignment", "utility"]
        self.exp_dimensions  = ["goal_satisfaction", "verdict_evidence", "accuracy", "coherence"]

    # ------------------------------------------------------------------
    def evaluate(
        self,
        prompt: str,
        response: str,
        *,
        goal: str | None = None,
        sandbox_status: str | None = None,
        sandbox_stdout: str | None = None,
    ) -> dict:
        sandbox_status = (sandbox_status or "").lower() or None
        experiment_mode = sandbox_status is not None

        if experiment_mode:
            messages = self._build_experiment_prompt(
                goal or prompt, response, sandbox_status, sandbox_stdout or ""
            )
            dimensions = self.exp_dimensions
        else:
            messages = self._build_chat_prompt(prompt, response)
            dimensions = self.chat_dimensions
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=512,
                response_format={"type": "json_object"},  # TD-002: force JSON mode
            )

            raw = completion.choices[0].message.content or ""
            result = self._parse_evaluation(raw, dimensions)
        except Exception as e:
            print(f"[Reflector] Evaluation error: {e}")
            result = self._fallback(dimensions)

        # --- Hard score bounds (experiment mode) ---
        bounds_applied: list[dict] = []
        score = result.get("score", 0.0)

        if experiment_mode:
            # Sandbox failure cap: 0.3
            if sandbox_status and sandbox_status != "success":
                cap = 0.3
                bounds_applied.append({
                    "cap": cap,
                    "reason": "sandbox_failure",
                    "active": score > cap,
                    "pre_cap_score": score,
                })
                score = min(score, cap)

            # Verdict failure cap: 0.4 (explicit FAIL detected)
            if FAIL_RE.search(response or ""):
                cap = 0.4
                bounds_applied.append({
                    "cap": cap,
                    "reason": "verdict_failure",
                    "active": score > cap,
                    "pre_cap_score": score,
                })
                score = min(score, cap)

            # Missing verdict cap: 0.6 (no PASS/FAIL token at all)
            elif not PASS_RE.search(response or ""):
                cap = 0.6
                bounds_applied.append({
                    "cap": cap,
                    "reason": "verdict_missing",
                    "active": score > cap,
                    "pre_cap_score": score,
                })
                score = min(score, cap)

        result["bounds_applied"] = bounds_applied
        result["score"] = round(score, 3)
        return result

    # ------------------------------------------------------------------
    def _build_chat_prompt(self, prompt: str, response: str) -> list:
        """Legacy chat-mode evaluation prompt."""
        dim_keys = self.chat_dimensions
        dim_template = ", ".join(f'"{d}": 0.0' for d in dim_keys)
        system = (
            "You are a strict evaluator. You output only valid JSON. "
            "No markdown. No prose."
        )
        user = (
            f"PROMPT:\n{prompt}\n\nRESPONSE:\n{response}\n\n"
            f"Score 0.0-1.0 on each dimension: {', '.join(dim_keys)}.\n"
            "score = unweighted mean of the dimensions.\n\n"
            "Output ONLY JSON:\n"
            f'{{"dimensions": {{{dim_template}}}, '
            '"score": 0.0, "reasoning": "short note", "flags": []}}'
        )
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]


    # ------------------------------------------------------------------
    def _build_experiment_prompt(
        self, goal: str, code: str, status: str, stdout: str
    ) -> list:

        # Truncate stdout to last 2KB to fit context
        stdout_trunc = stdout[-2048:] if len(stdout) > 2048 else stdout
        if len(stdout) > 2048:
            stdout_trunc = "...[truncated]...\n" + stdout_trunc

        return [
            {
                "role": "system",
                "content": (
                    "You are a strict experiment evaluator. You grade whether code "
                    "actually achieved its stated GOAL based on its STDOUT evidence. "
                    "Aesthetics and code style are secondary. "
                    "You output only valid JSON. No markdown. No prose."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"GOAL:\n{goal}\n\n"
                    f"SANDBOX_STATUS: {status}\n\n"
                    f"STDOUT:\n{stdout_trunc or '(empty)'}\n\n"
                    f"CODE:\n{code}\n\n"
                    "Score 0.0-1.0 on each dimension:\n"
                    "- goal_satisfaction: Did the stdout demonstrate the goal was met? "
                    "You MUST quote the specific stdout line(s) as evidence in your "
                    "reasoning. If you cannot quote evidence, score <= 0.3.\n"
                    "- verdict_evidence: Did stdout contain a clear PASS/FAIL or "
                    "numerical verification? 1.0 if explicit PASS with numbers, "
                    "0.5 if implicit, 0.0 if absent.\n"
                    "- accuracy: Is the code logically correct for the goal?\n"
                    "- coherence: Is the code well-structured?\n\n"
                    "Flags from [SANDBOX_FAILURE, VERDICT_FAIL, VERDICT_MISSING, "
                    "GOAL_MISMATCH, HALLUCINATION_RISK] if applicable.\n\n"
                    "score = 0.5*goal_satisfaction + 0.25*verdict_evidence + "
                    "0.15*accuracy + 0.10*coherence\n\n"
                    "Output ONLY JSON:\n"
                    '{"dimensions": {"goal_satisfaction": 0.0, "verdict_evidence": 0.0, '
                    '"accuracy": 0.0, "coherence": 0.0}, '
                    '"score": 0.0, "reasoning": "quoted evidence here", "flags": []}'
                ),
            },
        ]

    # ------------------------------------------------------------------
    def _parse_evaluation(self, raw: str, expected_dims: list) -> dict:
        text = raw.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            text = "\n".join(l for l in lines if not l.startswith("```")).strip()

        start = text.find("{")
        end   = text.rfind("}") + 1
        if start != -1 and end > start:
            text = text[start:end]

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            print(f"[Reflector] JSON parse error: {e}")
            return self._fallback(expected_dims)

        raw_dims   = data.get("dimensions", {}) or {}
        score      = data.get("score", 0.0)
        flags      = data.get("flags", []) or []
        reasoning  = data.get("reasoning", "")

        # TD-002: normalize keys (Phi-4 drifts on case/separators)
        dimensions = {
            self._normalize_key(k): v
            for k, v in raw_dims.items()
            if isinstance(v, (int, float))
        }

        # TD-002: ensure all expected dimensions present (default 0.0 if missing)
        for d in expected_dims:
            dimensions.setdefault(d, 0.0)

        if score == 0.0 and dimensions:
            values = list(dimensions.values())
            if values:
                score = sum(values) / len(values)

        return {
            "score":      round(float(score), 4),
            "flags":      [str(f) for f in flags],
            "dimensions": {k: round(float(v), 4) for k, v in dimensions.items()},
            "reasoning":  str(reasoning),
        }

    # ------------------------------------------------------------------
    @staticmethod
    def _normalize_key(k: str) -> str:
        """TD-002: Phi-4 sometimes returns 'Goal_Satisfaction' or 'goal-satisfaction'."""
        return k.strip().lower().replace("-", "_").replace(" ", "_")

    # ------------------------------------------------------------------
    def _fallback(self, dimensions: list) -> dict:
        return {
            "score":      0.0,
            "flags":      ["INCOMPLETE"],
            "dimensions": {d: 0.0 for d in dimensions},
            "reasoning":  "",
        }


# ----------------------------------------------------------------------
if __name__ == "__main__":
    config = {
        "base_url":             "http://10.0.0.167:11434/v1",
        "reflection_model": "phi4:latest",
        "reflection_threshold": 0.75,
    }
    r = Reflector(config)

    print("=== Chat mode (legacy) ===")
    result = r.evaluate(
        prompt="What is the capital of France?",
        response="The capital of France is Paris.",
    )
    print(json.dumps(result, indent=2))

    print("\n=== Experiment mode: sandbox failure ===")
    result = r.evaluate(
        prompt="ignored",
        response="import numpy as np\nprint(np.mean([1,2,3]))",
        goal="Verify the central limit theorem with 1000 samples",
        sandbox_status="ERROR",
        sandbox_stdout="Traceback: ImportError",
    )
    print(json.dumps(result, indent=2))

    print("\n=== Experiment mode: missing verdict ===")
    result = r.evaluate(
        prompt="ignored",
        response="print('done')",
        goal="Verify CLT holds",
        sandbox_status="SUCCESS",
        sandbox_stdout="done\n",
    )
    print(json.dumps(result, indent=2))
