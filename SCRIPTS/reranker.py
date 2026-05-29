from sentence_transformers import CrossEncoder

# Load once
reranker_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank_chunks(query, chunks, top_k=5):

    if not chunks:
        return []

    # Max 15 candidates
    candidates = chunks[:15]

    # Score all at once — very fast!
    pairs = [[query, chunk] for chunk in candidates]
    scores = reranker_model.predict(pairs)

    # Sort by score
    ranked = sorted(
        zip(scores, candidates),
        key=lambda x: x[0],
        reverse=True
    )

    best_chunks = [chunk for score, chunk in ranked[:top_k]]

    print(f"✅ Reranked {len(candidates)} chunks → top {top_k} selected")

    return best_chunks