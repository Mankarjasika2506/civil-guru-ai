import chromadb
import ollama
import re
from sentence_transformers import SentenceTransformer
from reranker import rerank_chunks

MODEL = "llama3.2:3b"

model = SentenceTransformer("all-MiniLM-L6-v2")

class MyEmbeddingFunction:
    def __call__(self, input):
        return model.encode(input).tolist()
    def name(self):
        return "all-MiniLM-L6-v2"
    def embed_documents(self, input):
        return model.encode(input).tolist()
    def embed_query(self, input):
        return model.encode(input).tolist()

client = chromadb.PersistentClient(path="../db")

pib = client.get_collection(
    name="pib_articles",
    embedding_function=MyEmbeddingFunction()
)
prs = client.get_collection(
    name="prs_articles",
    embedding_function=MyEmbeddingFunction()
)

def retrieve_evidence(claim):
    all_docs = []

    try:
        r = pib.query(query_texts=[claim], n_results=5)
        all_docs.extend(r["documents"][0])
    except:
        pass

    try:
        r = prs.query(query_texts=[claim], n_results=3)
        all_docs.extend(r["documents"][0])
    except:
        pass

    if all_docs:
        all_docs = rerank_chunks(claim, all_docs, top_k=3)

    return all_docs

def verify_claim(claim):
    print(f"\n🔍 Verifying: {claim}")

    evidence_docs = retrieve_evidence(claim)

    if not evidence_docs:
        return {
            "verdict": "UNVERIFIABLE",
            "reason": "No relevant official sources found",
            "full_report": "No official sources found in PIB or PRS database.",
            "evidence_count": 0
        }

    context = "\n\n".join(evidence_docs)

    prompt = f"""
You are a UPSC Fact Checker.

Read the official source carefully.
If source mentions anything related to claim — return PASS.
Only return FAIL if source completely contradicts the claim.

Return STRICTLY:

VERDICT: PASS or FAIL or PARTIAL
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
            options={"num_predict": 300}
        )
        output = response["message"]["content"]

        # Smarter verdict
        supported_count = output.lower().count("supported") + output.lower().count("fact")
        contradiction_count = output.lower().count("contradiction") + output.lower().count("inaccurac")

        if "VERDICT: PASS" in output:
            verdict = "PASS"
        elif "VERDICT: PARTIAL" in output:
            if supported_count >= contradiction_count:
                verdict = "PASS"
            else:
                verdict = "PARTIAL"
        elif "VERDICT: FAIL" in output:
            verdict = "FAIL"
        else:
            verdict = "UNVERIFIABLE"

        return {
            "verdict": verdict,
            "full_report": output,
            "evidence_count": len(evidence_docs)
        }

    except Exception as e:
        print(f"⚠️ Verification failed: {e}")
        return {
            "verdict": "ERROR",
            "full_report": str(e),
            "evidence_count": 0
        }

def print_result(claim, result):
    verdict = result.get("verdict", "UNKNOWN")
    emoji = "✅" if verdict == "PASS" else "❌" if verdict == "FAIL" else "⚠️"

    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{emoji} FACT CHECK RESULT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Claim   : {claim}
Verdict : {verdict}
Sources : PIB + PRS ({result.get('evidence_count', 0)} docs)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{result.get('full_report', result.get('reason', ''))}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

if __name__ == "__main__":
    claim = input("Enter claim to verify: ")
    result = verify_claim(claim)
    print_result(claim, result)