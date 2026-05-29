import pytesseract
from PIL import Image
import ollama
import re
import chromadb
from sentence_transformers import SentenceTransformer
from reranker import rerank_chunks

# ── Tesseract path ──
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

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
civil_guru = client.get_collection(
    name="civil_guru",
    embedding_function=MyEmbeddingFunction()
)

def extract_text_from_image(image_path):
    print(f"📸 Reading image: {image_path}")
    try:
        img = Image.open(image_path)

        # Enhance image for better OCR
        img = img.convert("L")  # grayscale

        text = pytesseract.image_to_string(img, lang="eng")
        text = text.strip()

        if len(text) < 20:
            return None, "Could not extract enough text from image"

        print(f"✅ Extracted {len(text)} characters")
        return text, None

    except Exception as e:
        return None, str(e)

def retrieve_context(question):
    try:
        results = civil_guru.query(
            query_texts=[question],
            n_results=10
        )
        docs = results["documents"][0]
        docs = rerank_chunks(question, docs, top_k=3)
        return "\n\n".join(docs)
    except:
        return ""

def evaluate_handwritten_answer(image_path, question):
    print(f"\n📝 Evaluating handwritten answer...")
    print(f"❓ Question: {question}")

    # Step 1 — Extract text from image
    extracted_text, error = extract_text_from_image(image_path)

    if error:
        print(f"❌ OCR Error: {error}")
        return None

    print(f"\n📄 Extracted Text:\n{extracted_text}\n")

    # Step 2 — Retrieve context
    context = retrieve_context(question)

    # Step 3 — Evaluate
    prompt = f"""
You are a UPSC Mains Examiner.

Evaluate the handwritten answer strictly.

Question: {question}

Student's Answer (extracted from handwriting):
{extracted_text}

Reference Context:
{context[:2000]}

Score strictly out of 15:

INTRODUCTION: X/2
STRUCTURE: X/2
DIMENSIONS: X/3
FACTS: X/3
ANALYSIS: X/3
CONCLUSION: X/2
TOTAL: X/15

STRENGTHS: one sentence
WEAKNESSES: one sentence
IMPROVEMENTS: one sentence
HANDWRITING NOTE: comment on clarity of handwriting
"""

    try:
        response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={"num_predict": 350}
        )
        raw = response["message"]["content"]

        # Parse scores
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

        strengths = re.search(r"STRENGTHS:(.*?)(?:WEAKNESSES:|$)", raw, re.DOTALL)
        weaknesses = re.search(r"WEAKNESSES:(.*?)(?:IMPROVEMENTS:|$)", raw, re.DOTALL)
        improvements = re.search(r"IMPROVEMENTS:(.*?)(?:HANDWRITING|$)", raw, re.DOTALL)
        handwriting = re.search(r"HANDWRITING NOTE:(.*?)$", raw, re.DOTALL)

        result = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 ANSWER EVALUATION REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Question : {question}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 EXTRACTED TEXT:
{extracted_text[:300]}...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 SCORES:
INTRODUCTION : {scores.get('INTRODUCTION', 1)}/2
STRUCTURE    : {scores.get('STRUCTURE', 1)}/2
DIMENSIONS   : {scores.get('DIMENSIONS', 2)}/3
FACTS        : {scores.get('FACTS', 2)}/3
ANALYSIS     : {scores.get('ANALYSIS', 2)}/3
CONCLUSION   : {scores.get('CONCLUSION', 1)}/2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL        : {total}/15
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ STRENGTHS   : {strengths.group(1).strip() if strengths else 'Good attempt'}
⚠️ WEAKNESSES  : {weaknesses.group(1).strip() if weaknesses else 'Needs improvement'}
💡 IMPROVEMENTS: {improvements.group(1).strip() if improvements else 'Add more facts'}
✍️ HANDWRITING : {handwriting.group(1).strip() if handwriting else 'Legible'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return result

    except Exception as e:
        print(f"⚠️ Evaluation failed: {e}")
        return None

if __name__ == "__main__":
    print("📸 UPSC Handwritten Answer Evaluator")
    print("─────────────────────────────────────")
    image_path = input("Enter image path: ")
    question = input("Enter the question: ")

    result = evaluate_handwritten_answer(image_path, question)

    if result:
        print(result)
    else:
        print("❌ Evaluation failed")