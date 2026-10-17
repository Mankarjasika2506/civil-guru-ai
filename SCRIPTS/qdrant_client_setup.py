"""
Shared Qdrant client + retrieval used by all Civil Guru agents.
Replaces the old per-agent local ChromaDB clients.
"""

import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer

load_dotenv()

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    timeout=60,
)

model = SentenceTransformer("all-MiniLM-L6-v2")


def retrieve_context(question, collection_name, n_results=10):
    try:
        results = client.query_points(
            collection_name=collection_name,
            query=model.encode(question).tolist(),
            limit=n_results
        )
        docs = [hit.payload.get("text", "") for hit in results.points]
        return "\n\n".join(docs)
    except Exception as e:
        print(f"Error retrieving context: {e}")
        return ""


def query_collection(question, collection_name, n_results=10, subject_filter=None):
    query_filter = None
    if subject_filter:
        query_filter = Filter(
            must=[FieldCondition(key="subject", match=MatchValue(value=subject_filter))]
        )
    results = client.query_points(
        collection_name=collection_name,
        query=model.encode(question).tolist(),
        limit=n_results,
        query_filter=query_filter,
    )
    return results.points

def build_references(points):
    """Build references only from chunks that were actually sent to the LLM."""
    refs, seen_urls, pages = [], set(), {}
    for p in points:
        pl = p.payload
        url = pl.get("url")
        if url:
            if url in seen_urls:
                continue
            seen_urls.add(url)
            label = pl.get("title") or f"{pl.get('source', 'Official')} release"
            refs.append({"label": label, "url": url})
        else:
            subject = pl.get("subject", "General").title()
            pages.setdefault(subject, set()).add(str(pl.get("page", "?")))
    for subject, pg in pages.items():
        nums = sorted(pg, key=lambda x: int(x) if x.isdigit() else 0)
        refs.append({"label": f"Textbook corpus: {subject}, pp. {', '.join(nums)}", "url": None})
    return refs