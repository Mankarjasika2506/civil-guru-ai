import chromadb
import ollama
import json
from sentence_transformers import SentenceTransformer
from reranker import rerank_chunks
from syllabus_agent import analyze_syllabus
from fact_verifier import verify_answer
from answer_evaluator import evaluate_answer
from dynamic_retriever import retrieve_more_chunks

MODEL = "llama3.2:3b"

# ── Embedding ──
model = SentenceTransformer("all-MiniLM-L6-v2")

# ── Subject Descriptions for Semantic Detection ──
SUBJECT_DESCRIPTIONS = {
    "ART&CULTURE": "Indian art culture painting dance music sculpture cave prehistoric rock paintings festivals architecture",
    "HISTORY": "ancient medieval modern history mughal british empire dynasty revolt civilisation independence",
    "POLITY": "constitution parliament amendment article president governor fundamental rights directive principles judiciary",
    "ECONOMICS": "economy gdp inflation budget fiscal monetary policy rbi banking trade poverty development",
    "GEOGRAPHY": "river mountain climate soil monsoon plateau physical geography environment disaster",
    "ETHICS": "ethics integrity moral attitude aptitude governance values public service honesty",
    "SOCIOLOGY": "society caste tribe social culture religion community women empowerment diversity",
}

def detect_subject_by_embedding(query):
    from sentence_transformers import util
    query_embedding = model.encode(query, convert_to_tensor=True)

    best_subject = "GENERAL"
    best_score = 0.0

    for subject, description in SUBJECT_DESCRIPTIONS.items():
        desc_embedding = model.encode(description, convert_to_tensor=True)
        score = util.cos_sim(query_embedding, desc_embedding).item()
        if score > best_score:
            best_score = score
            best_subject = subject

    print(f"✅ Subject detected: {best_subject} (confidence: {best_score:.2f})")
    return best_subject
class MyEmbeddingFunction:
    def __call__(self, input):
        return model.encode(input).tolist()
    def name(self):
        return "all-MiniLM-L6-v2"
    def embed_documents(self, input):
        return model.encode(input).tolist()
    def embed_query(self, input):
        return model.encode(input).tolist()

# ── ChromaDB ──
client = chromadb.PersistentClient(path="../db")
collection = client.get_collection(
    name="civil_guru",
    embedding_function=MyEmbeddingFunction()
)

# ── User Query ──
query = input("Ask your question: ")

# =====================================
# SYLLABUS AGENT
# =====================================
print("\n🔍 Analyzing syllabus...")
syllabus_data = analyze_syllabus(query)

print("\n📘 SYLLABUS ANALYSIS")
print("Paper:", syllabus_data["paper"])
print("Subject:", syllabus_data["subject"])
print("Topic:", syllabus_data["topic"])

# Always use embedding detection — more reliable than 1b model
subject = detect_subject_by_embedding(query)
print(f"📌 Final subject: {subject}")

# =====================================
# QUERY ANALYSIS
# =====================================
print("\n🧠 Analyzing query...")

analysis_prompt = f"""
You are an intelligent UPSC Query Analyzer.

Return ONLY valid JSON.

JSON format:

{{
    "keywords": [],
    "dimensions": []
}}

Rules:
- keywords: important UPSC terms from the question
- dimensions: all expected answer areas

Question:
{query}
"""

try:
    analysis_response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": analysis_prompt}]
    )
    analysis_output = analysis_response["message"]["content"].strip()
    analysis_output = analysis_output.replace("```json", "").replace("```", "").strip()
    start = analysis_output.find("{")
    end = analysis_output.rfind("}") + 1
    analysis_output = analysis_output[start:end]
    analysis = json.loads(analysis_output)
except Exception as e:
    print(f"⚠️ Query analysis failed: {e}")
    analysis = {"keywords": [], "dimensions": []}

keywords = analysis.get("keywords", [])
dimensions = analysis.get("dimensions", [])

print("Keywords:", keywords)
print("Dimensions:", dimensions)

# =====================================
# MULTI-QUERY RETRIEVAL
# =====================================
print("\n📚 Retrieving chunks...")

all_docs = []

# Main query retrieval
try:
    results = collection.query(
        query_texts=[query],
        n_results=10,
        where={"subject": subject}
    )
    all_docs.extend(results["documents"][0])
except:
    # Fallback without filter
    results = collection.query(
        query_texts=[query],
        n_results=10
    )
    all_docs.extend(results["documents"][0])

# Keyword retrieval
for keyword in keywords[:3]:
    try:
        keyword_results = collection.query(
            query_texts=[keyword],
            n_results=3,
            where={"subject": subject}
        )
        all_docs.extend(keyword_results["documents"][0])
    except Exception as e:
        print(f"⚠️ Keyword retrieval failed for '{keyword}': {e}")

# Remove duplicates and weak chunks
all_docs = list(dict.fromkeys(all_docs))
all_docs = [doc for doc in all_docs if len(doc) > 100]

print(f"✅ Total chunks before rerank: {len(all_docs)}")

# =====================================
# RERANKER
# =====================================
context_docs = rerank_chunks(query, all_docs)
context = "\n\n".join(context_docs[:3])

print(f"✅ Final chunks after rerank: {len(context_docs)}")

# Save debug context
with open("last_context.txt", "w", encoding="utf-8") as f:
    f.write(context)

# =====================================
# ANSWER GENERATION
# =====================================
print("\n✍️ Generating answer...")

prompt = f"""
You are a UPSC Mains topper.

Write a COMPLETE and HIGH-QUALITY answer.

STRICT RULES:
- Use ONLY the given context
- Do NOT hallucinate
- Cover ALL dimensions
- Use proper UPSC structure
- Include keywords wherever relevant
- Do NOT add any references or bibliography
- Do NOT cite any authors or publications

QUESTION:
{query}

Expected Dimensions:
{dimensions}

Syllabus Information:
Paper: {syllabus_data["paper"]}
Topic: {syllabus_data["topic"]}
Subtopic: {syllabus_data["subtopic"]}
Themes: {syllabus_data["themes"]}

Context:
{context}
"""

try:
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    generated_answer = response["message"]["content"]
except Exception as e:
    print(f"⚠️ Answer generation failed: {e}")
    generated_answer = "Answer generation failed."

print("\n🧠 Civil Guru Answer:\n")
print(generated_answer)

# =====================================
# FACT VERIFICATION
# =====================================
print("\n🔍 Verifying facts...")
verification = verify_answer(query, generated_answer, context)
print("\n🔍 FACT VERIFICATION REPORT\n")
print(verification)

# =====================================
# DYNAMIC RETRIEVAL IF FAILED
# =====================================
if "VERDICT: FAIL" in verification:
    print("\n⚠️ Weak answer detected — running dynamic retrieval...")

    extra_docs = retrieve_more_chunks(collection, subject, dimensions)
    extra_docs = list(dict.fromkeys(extra_docs))
    context += "\n\n" + "\n\n".join(extra_docs)

    improved_prompt = f"""
You are a UPSC Mains topper.

Previous answer had weak coverage.
Generate an IMPROVED answer using updated context.

Question:
{query}

Expected Dimensions:
{dimensions}

Updated Context:
{context}
"""

    try:
        improved_response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": improved_prompt}]
        )
        generated_answer = improved_response["message"]["content"]
    except Exception as e:
        print(f"⚠️ Improved answer generation failed: {e}")

    print("\n🧠 IMPROVED ANSWER\n")
    print(generated_answer)

# =====================================
# ANSWER EVALUATION
# =====================================
print("\n📝 Evaluating answer...")
evaluation = evaluate_answer(query, generated_answer)
print("\n📝 ANSWER EVALUATION REPORT\n")
print(evaluation)

def main():
    pass