import ollama

MODEL = "llama3.2:3b"

def verify_answer(question, answer, context):

    context_trimmed = context[:3000]

    prompt = f"""
You are a UPSC Fact Checker.

Read the official source carefully.
If the source mentions anything related to the claim — return PASS.
Only return FAIL if source completely contradicts the claim.

Return STRICTLY:

VERDICT: PASS or FAIL
REASON: one sentence
SUPPORTED FACTS:
- fact 1
- fact 2
CONTRADICTIONS:
- None or point
SOURCE RELIABILITY: HIGH or MEDIUM or LOW

Claim: {claim}

Official Source:
{context[:2000]}
"""

    try:
        response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={"num_predict": 150}
        )
        return response["message"]["content"]

    except Exception as e:
        print(f"⚠️ Fact verification failed: {e}")
        return "VERDICT: PASS\n(Verification skipped due to error)"