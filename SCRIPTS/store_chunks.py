import json
import hashlib
import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

class MyEmbeddingFunction:
    def __call__(self, input):
        return model.encode(input).tolist()
    
    def name(self):                        
        return "all-MiniLM-L6-v2"

client = chromadb.PersistentClient(path="../db")

# Fresh start — delete old broken collection
try:
    client.delete_collection("civil_guru")
    print("🗑️ Old collection deleted")
except:
    pass

# Create new clean collection
collection = client.get_or_create_collection(
    name="civil_guru",
    embedding_function=MyEmbeddingFunction()
)

# Load structured chunks
with open("chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

print(f"🚀 Storing {len(chunks)} chunks in batches...")

BATCH_SIZE = 100
stored = 0
skipped = 0

for i in range(0, len(chunks), BATCH_SIZE):
    batch = chunks[i:i+BATCH_SIZE]

    batch_docs = []
    batch_ids = []
    batch_metas = []

    for chunk in batch:
        text = chunk["text"].strip()
        if not text:
            continue

        chunk_id = hashlib.md5(text.encode()).hexdigest()

        batch_docs.append(text)
        batch_ids.append(chunk_id)
        batch_metas.append({
            "subject": chunk.get("subject", "GENERAL"),
            "page": chunk.get("page", "0")
        })

    try:
        collection.add(
            documents=batch_docs,
            ids=batch_ids,
            metadatas=batch_metas
        )
        stored += len(batch_docs)
        print(f"✅ Batch {i//BATCH_SIZE + 1} stored | Total: {stored}")

    except Exception as e:
        skipped += len(batch)
        print(f"⚠️ Batch error: {e}")

print(f"\n🎯 Done! Stored: {stored} | Skipped: {skipped}")