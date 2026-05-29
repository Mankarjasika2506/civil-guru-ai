import os
import fitz  # PyMuPDF
import re

base_folder = "../DATA"

print("Starting extraction...")

all_text = ""

for root, dirs, files in os.walk(base_folder):

    print(f"\nFolder: {root}")

    for file in files:

        if file.endswith(".pdf"):

            path = os.path.join(root, file)
            print(f"Processing: {file}")

            # Extract subject from folder name
            parts = root.replace("\\", "/").split("/")
            data_index = next((i for i, p in enumerate(parts) if p == "DATA"), None)
            subject = parts[data_index + 1] if data_index is not None else "GENERAL"
            subject = subject.upper()

            try:
                doc = fitz.open(path)
                print(f"Pages: {len(doc)}")

                for page_num, page in enumerate(doc):
                    text = page.get_text()

                    if text:
                        # Remove line breaks
                        text = text.replace("\n", " ")

                        # Remove extra spaces
                        text = " ".join(text.split())

                        # Remove reprint text
                        text = re.sub(r"Reprint\s+\d{4}-\d{2}", "", text)

                        # Remove only standalone page numbers
                        text = re.sub(r"(?<!\d)\b\d{1,3}\b(?!\d)", " ", text)

                        # Clean spaces again
                        text = " ".join(text.split())

                        # Skip small useless text
                        if len(text) > 80:
                            all_text += (
                                f"\n\n[SOURCE:{subject}]"
                                f"[PAGE:{page_num+1}]\n"
                                f"{text}\n"
                            )

            except Exception as e:
                print(f"Error in {file}: {e}")

# Save cleaned text
with open("cleaned.txt", "w", encoding="utf-8") as f:
    f.write(all_text)

print("\nDONE -> cleaned.txt created")