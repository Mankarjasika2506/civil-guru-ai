import chromadb

client = chromadb.PersistentClient(path="../db")
collection = client.get_collection(name="civil_guru")

query = input("Ask your question: ")

#  Increase retrieval
results = collection.query(
    query_texts=[query],
    n_results=10
)

documents = results["documents"][0]

print("\n🔍 Retrieved Chunks:\n")

for i, doc in enumerate(documents):
    print(f"--- Chunk {i} ---")
    print(doc[:300])   # preview only
    print("\n")

#  Combine context properly
context = "\n\n".join(documents)

# Save context (optional debugging)
with open("last_context.txt", "w", encoding="utf-8") as f:
    f.write(context)

print("\n✅ Context prepared for AI")