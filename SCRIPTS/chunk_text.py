import re
import json

with open("cleaned_final.txt", "r", encoding="utf-8") as f:
    text = f.read()

print("🚀 Chunking started")

sections = text.split("[SOURCE:")

chunks = []

CHUNK_SIZE = 600
OVERLAP = 100

for section in sections:
    section = section.strip()
    if not section:
        continue

    section = "[SOURCE:" + section

    # Extract metadata
    source_match = re.search(r"\[SOURCE:([\w&]+)\]\[PAGE:(\d+)\]", section)
    subject = source_match.group(1) if source_match else "GENERAL"
    page = source_match.group(2) if source_match else "0"

    # Split by sentences
    sentences = re.split(r'(?<=[.!?])\s+', section)

    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= CHUNK_SIZE:
            current_chunk += " " + sentence
        else:
            if current_chunk.strip():
                chunks.append({
                    "text": current_chunk.strip(),
                    "subject": subject,
                    "page": page
                })
            # Overlap
            current_chunk = current_chunk[-OVERLAP:] + " " + sentence

    # Last chunk
    if current_chunk.strip():
        chunks.append({
            "text": current_chunk.strip(),
            "subject": subject,
            "page": page
        })

with open("chunks.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2, ensure_ascii=False)

print(f"✅ {len(chunks)} structured chunks created -> chunks.json")