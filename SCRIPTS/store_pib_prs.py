import json
import hashlib
import chromadb
from sentence_transformers import SentenceTransformer

print("🚀 Storing PIB + PRS into ChromaDB...")

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

# ── Delete old if exists ──
for col in ["pib_articles", "prs_articles"]:
    try:
        client.delete_collection(col)
        print(f"🗑️ Deleted old {col}")
    except:
        pass

# ── Create collections ──
pib_collection = client.get_or_create_collection(
    name="pib_articles",
    embedding_function=MyEmbeddingFunction()
)

prs_collection = client.get_or_create_collection(
    name="prs_articles",
    embedding_function=MyEmbeddingFunction()
)

BATCH_SIZE = 50

# ══════════════════════════════
# STORE PIB ARTICLES
# ══════════════════════════════
print("\n📰 Storing PIB articles...")

with open("pib_articles.json", "r", encoding="utf-8") as f:
    pib_data = json.load(f)

print(f"Total PIB articles: {len(pib_data)}")

stored_pib = 0
for i in range(0, len(pib_data), BATCH_SIZE):
    batch = pib_data[i:i+BATCH_SIZE]

    docs, ids, metas = [], [], []
    for article in batch:
        text = article["text"].strip()
        if not text:
            continue
        chunk_id = "pib_" + hashlib.md5(text.encode()).hexdigest()
        docs.append(text)
        ids.append(chunk_id)
        metas.append({
            "ministry": article.get("ministry", "General"),
            "url": article.get("url", ""),
            "source": "PIB"
        })

    try:
        pib_collection.add(
            documents=docs,
            ids=ids,
            metadatas=metas
        )
        stored_pib += len(docs)
        print(f"✅ PIB batch {i//BATCH_SIZE+1} | Total: {stored_pib}")
    except Exception as e:
        print(f"⚠️ PIB batch error: {e}")

# ══════════════════════════════
# STORE PRS BILLS
# ══════════════════════════════
print("\n⚖️ Storing PRS bills...")

with open("prs_articles.json", "r", encoding="utf-8") as f:
    prs_data = json.load(f)

print(f"Total PRS bills: {len(prs_data)}")

stored_prs = 0
for i in range(0, len(prs_data), BATCH_SIZE):
    batch = prs_data[i:i+BATCH_SIZE]

    docs, ids, metas = [], [], []
    for bill in batch:
        text = bill["text"].strip()
        if not text:
            continue
        chunk_id = "prs_" + hashlib.md5(text.encode()).hexdigest()
        docs.append(text)
        ids.append(chunk_id)
        metas.append({
            "title": bill.get("title", "")[:100],
            "category": bill.get("category", "General"),
            "url": bill.get("url", ""),
            "source": "PRS"
        })

    try:
        prs_collection.add(
            documents=docs,
            ids=ids,
            metadatas=metas
        )
        stored_prs += len(docs)
        print(f"✅ PRS batch {i//BATCH_SIZE+1} | Total: {stored_prs}")
    except Exception as e:
        print(f"⚠️ PRS batch error: {e}")

print(f"\n🎯 Done!")
print(f"✅ PIB stored : {stored_pib}")
print(f"✅ PRS stored : {stored_prs}")
print(f"✅ Total      : {stored_pib + stored_prs}")