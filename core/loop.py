# loop.py v1.2.1
import time, requests, json, shutil
from datetime import datetime
from pathlib import Path
from core.ast_shield import shield_gate
from core.sandbox import execute_sandboxed, SANDBOX_DIR

REFLECTOR_TIMEOUT = 75
MAX_ITERATIONS = 5
TARGET_SCORE = 0.85
AUTO_ACCEPT_THRESHOLD = 0.95
AUTO_REJECT_THRESHOLD = 0.50
REFLECTOR_URL = "http://192.168.100.2:11434/api/generate"
REFLECTOR_MODEL = "llama3.1:8b"

def run_sandboxed(code: str, timeout: int = 30) -> dict:
    is_safe, shield_msg = shield_gate(code)
    if not is_safe:
        return {"status": "blocked", "error": shield_msg, "output": "", "artifacts": []}
    return execute_sandboxed(code)

def call_reflector(prompt: str, context: dict = None) -> float:
    reflection_prompt = build_reflection_prompt(prompt, context)
    payload = {"model": REFLECTOR_MODEL, "prompt": reflection_prompt, "stream": False, "options": {"temperature": 0.3, "num_predict": 150}}
    try:
        response = requests.post(REFLECTOR_URL, json=payload, timeout=REFLECTOR_TIMEOUT)
        response.raise_for_status()
        return extract_score(response.json().get("response", ""))
    except requests.exceptions.Timeout:
        print(f"[REFLECTOR] Timeout"); return 0.35
    except requests.exceptions.ConnectionError:
        print("[REFLECTOR] Connection failed"); return 0.0
    except Exception as e:
        print(f"[REFLECTOR] Error: {e}"); return 0.25

def build_reflection_prompt(output: str, context: dict = None) -> str:
    ctx = context or {}
    return f"""Score this output 0.0-1.0. Experiment: {ctx.get('experiment_id', 'unknown')}, Goal: {ctx.get('goal', 'N/A')}
OUTPUT: {output[:2000]}
RESPOND: SCORE: [0.00-1.00] REASON: [explanation]"""

def extract_score(response_text: str) -> float:
    import re
    match = re.search(r'SCORE:\s*([0-9]*\.?[0-9]+)', response_text, re.IGNORECASE)
    if match: return min(max(float(match.group(1)), 0.0), 1.0)
    fallback = re.search(r'\b(0\.\d+|1\.0)\b', response_text)
    if fallback: return float(fallback.group(1))
    return 0.40

def dream_loop(experiment_id: str, initial_hypothesis: str, goal: str) -> dict:
    print(f"[DREAM LOOP] {experiment_id}")
    exp_dir = Path("experiments") / experiment_id
    exp_dir.mkdir(parents=True, exist_ok=True)
    current_hypothesis, current_code, current_score, history = initial_hypothesis, None, 0.0, []
    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"[ITERATION {iteration}]")
        code = crystallize(current_hypothesis, goal)
        if not code: continue
        (exp_dir / f"iter{iteration:03d}_code.py").write_text(code, encoding='utf-8')
        exec_result = run_sandboxed(code, timeout=30)
        print(f"[STATUS] {exec_result['status']}")
        ctx = {"experiment_id": experiment_id, "iteration": iteration, "goal": goal, "exec_status": exec_result['status']}
        score = call_reflector(f"CODE: {code}\nOUTPUT: {exec_result.get('output', '')}", ctx)
        history.append({"iteration": iteration, "score": score, "timestamp": datetime.now().isoformat()})
        current_score, current_code = score, code
        print(f"[SCORE] {score:.2f}")
        if score >= AUTO_ACCEPT_THRESHOLD: break
        if iteration < MAX_ITERATIONS and score < TARGET_SCORE:
            current_hypothesis = refine_hypothesis(code, score, history)
    archive_experiment(experiment_id, current_code, current_score, iteration, history)
    return {"experiment_id": experiment_id, "final_score": current_score, "iterations": iteration, "code": current_code}

def crystallize(hypothesis: str, goal: str) -> str:
    prompt = f"""Generate Python code to test: {hypothesis}. Goal: {goal}. Output ONLY valid Python, use numpy/matplotlib, include prints, save plots as output.png."""
    try:
        response = requests.post("http://localhost:1234/v1/chat/completions", json={"model": "llama-3.1-nemotron-70b-instruct-hf", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": 2000}, timeout=300)
        result = response.json()
        code = result.get('choices', [{}])[0].get('message', {}).get('content', '') or result.get('content', '') or result.get('response', '')
        if '```python' in code: code = code.split('```python')[1].split('```')[0]
        elif '```' in code: code = code.split('```')[1].split('```')[0]
        return code.strip()
    except Exception as e:
        print(f"[ERROR] {e}"); raise

def refine_hypothesis(previous_code: str, score: float, history: list = None) -> str:
    prompt = f"""Code scored {score:.2f}. Suggest one improvement. Code: {previous_code[:1000]}"""
    try:
        response = requests.post("http://localhost:1234/v1/chat/completions", json={"model": "llama-3.1-nemotron-70b-instruct-hf", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": 500}, timeout=300)
        result = response.json()
        return result.get('choices', [{}])[0].get('message', {}).get('content', '').strip() or f"Improve from {score:.2f}"
    except: return f"Improve from {score:.2f}"

def archive_experiment(exp_id: str, code: str, score: float, iterations: int, history: list):
    archive_dir = Path("experiments") / exp_id
    archive_dir.mkdir(parents=True, exist_ok=True)
    (archive_dir / "final_code.py").write_text(code or "# No code", encoding='utf-8')
    (archive_dir / "metadata.json").write_text(json.dumps({"experiment_id": exp_id, "final_score": score, "iterations": iterations}, indent=2), encoding='utf-8')
    print(f"[ARCHIVED] {archive_dir}")

if __name__ == "__main__":
    result = dream_loop("exp_test", "Test hypothesis", "Test goal")
    print(f"[COMPLETE] {result['final_score']:.2f}")
