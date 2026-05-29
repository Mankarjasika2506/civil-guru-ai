from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

class MyEmbeddingFunction:
    def __call__(self, input):
        return model.encode(input).tolist()
    
    def name(self):
        return "all-MiniLM-L6-v2"

def retrieve_more_chunks(collection, subject, weak_topics, n_results=5):

    extra_docs = []

    for topic in weak_topics:
        try:
            # Try with subject filter first
            results = collection.query(
                query_texts=[topic],
                n_results=n_results,
                where={"subject": subject}
            )

            docs = results["documents"][0]

            # Fallback — no subject filter
            if not docs:
                print(f"⚠️ No results for '{topic}' in {subject}, trying global...")
                results = collection.query(
                    query_texts=[topic],
                    n_results=n_results
                )
                docs = results["documents"][0]

            extra_docs.extend(docs)

        except Exception as e:
            print(f"⚠️ Failed for topic '{topic}': {e}")

    # Remove duplicates
    extra_docs = list(dict.fromkeys(extra_docs))

    # Remove weak chunks
    extra_docs = [doc for doc in extra_docs if len(doc) > 100]

    print(f"✅ Dynamic retrieval found {len(extra_docs)} extra chunks")
    return extra_docs