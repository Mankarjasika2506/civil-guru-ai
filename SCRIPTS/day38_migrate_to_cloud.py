"""
Day 38 - Civil Guru Production Polish: Migrate to Qdrant Cloud
40-Day Agentic AI Rebuild

Migrates local ChromaDB collection (civil_guru) to Qdrant Cloud,
preserving existing embeddings as-is (no re-embedding).
"""

import os
import chromadb
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

load_dotenv()

BATCH_SIZE = 100
COLLECTIONS_TO_MIGRATE = ["civil_guru", "prs_articles", "pib_articles"]
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 output dimension



def migrate_collection(local_client, qdrant_client, name):
    print(f"\n--- Migrating collection: {name} ---")

    local_collection = local_client.get_collection(name)
    data = local_collection.get(include=["documents", "metadatas", "embeddings"])

    ids = data["ids"]
    documents = data["documents"]
    metadatas = data["metadatas"]
    embeddings = data["embeddings"]

    total = len(ids)
    print(f"  Read {total} chunks from local collection.")

    if not qdrant_client.collection_exists(name):
        qdrant_client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )

    points = [
        PointStruct(id=i, vector=emb, payload={**meta, "text": doc, "original_id": ids[i]})
        for i, (doc, meta, emb) in enumerate(zip(documents, metadatas, embeddings))
    ]

    for start in range(0, total, BATCH_SIZE):
        end = min(start + BATCH_SIZE, total)
        qdrant_client.upsert(collection_name=name, points=points[start:end])
        print(f"  Wrote batch {start}-{end} of {total}")

    count = qdrant_client.count(collection_name=name).count
    print(f"  Local count: {total} | Qdrant count: {count}")
    if count != total:
        print(f"  WARNING: count mismatch for {name}!")
    else:
        print(f"  Verified: {name} migrated successfully.")


if __name__ == "__main__":
    local_client = chromadb.PersistentClient(path="../db")
    qdrant_client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
        timeout=60,
    )

    for name in COLLECTIONS_TO_MIGRATE:
        migrate_collection(local_client, qdrant_client, name)

    print("\nAll collections migrated.")