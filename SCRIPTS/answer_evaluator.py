import ollama
import re

MODEL = "llama3.2:3b"

def evaluate_answer(question, answer):

    prompt = f"""
You are a UPSC examiner. Evaluate this answer.

Use ONLY these exact lines, fill in X with a number:

INTRODUCTION: X/2
STRUCTURE: X/2
DIMENSIONS: X/3
FACTS: X/3
ANALYSIS: X/3
CONCLUSION: X/2
TOTAL: X/15
STRENGTHS: write one sentence only
WEAKNESSES: write one sentence only
IMPROVEMENTS: write one sentence only

Question: {question}

Answer: {answer[:1500]}
"""

    try:
        response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={"num_predict": 350}
        )
        raw = response["message"]["content"]

        # Cut off after IMPROVEMENTS line
        if "IMPROVEMENTS:" in raw:
            cut = raw.find("IMPROVEMENTS:")
            end = raw.find("\n", cut + 50)
            if end != -1:
                raw = raw[:end]

        # ── Parse scores manually ──
        scores = {}
        maxes = {
            "INTRODUCTION": 2,
            "STRUCTURE": 2,
            "DIMENSIONS": 3,
            "FACTS": 3,
            "ANALYSIS": 3,
            "CONCLUSION": 2
        }

        for key, max_val in maxes.items():
            match = re.search(rf"{key}:\s*(\d+)", raw)
            if match:
                score = min(int(match.group(1)), max_val)
                scores[key] = score
            else:
                scores[key] = max_val // 2

        total = sum(scores.values())

        # ── Extract feedback ──
        strengths = re.search(r"STRENGTHS:(.*?)(?:WEAKNESSES:|$)", raw, re.DOTALL)
        weaknesses = re.search(r"WEAKNESSES:(.*?)(?:IMPROVEMENTS:|$)", raw, re.DOTALL)
        improvements = re.search(r"IMPROVEMENTS:(.*?)$", raw, re.DOTALL)

        result = f"""
━━━━━━━━━━━━━━━━━━━━━━━━
📝 ANSWER EVALUATION
━━━━━━━━━━━━━━━━━━━━━━━━
INTRODUCTION : {scores.get('INTRODUCTION', 1)}/2
STRUCTURE    : {scores.get('STRUCTURE', 1)}/2
DIMENSIONS   : {scores.get('DIMENSIONS', 2)}/3
FACTS        : {scores.get('FACTS', 2)}/3
ANALYSIS     : {scores.get('ANALYSIS', 2)}/3
CONCLUSION   : {scores.get('CONCLUSION', 1)}/2
━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL        : {total}/15
━━━━━━━━━━━━━━━━━━━━━━━━
✅ STRENGTHS   : {strengths.group(1).strip() if strengths else 'Good coverage'}
⚠️ WEAKNESSES  : {weaknesses.group(1).strip() if weaknesses else 'Needs more facts'}
💡 IMPROVEMENTS: {improvements.group(1).strip() if improvements else 'Add more examples'}
━━━━━━━━━━━━━━━━━━━━━━━━"""

        return result

    except Exception as e:
        print(f"⚠️ Evaluation failed: {e}")
        return "Evaluation unavailable"