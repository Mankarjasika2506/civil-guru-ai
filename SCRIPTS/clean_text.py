import re
import json

# Read extracted text
with open("cleaned.txt", "r", encoding="utf-8") as f:
    text = f.read()

print("Starting smart cleaning...")

# ------------------------------------------------
# Fix broken hyphen words
# ------------------------------------------------
text = re.sub(r"(\w)-\s+(\w)", r"\1\2", text)

# ------------------------------------------------
# Merge isolated capital letters
# ------------------------------------------------
for _ in range(10):
    text = re.sub(r"\b([A-Z])\s+([A-Z])\b", r"\1\2", text)

# ------------------------------------------------
# OCR fixes
# ------------------------------------------------
ocr_fixes = {
    "PR REHISTORIC": "PREHISTORIC",
    "OCK": "ROCK",
    "P AINTINGS": "PAINTINGS",
    "HS UNTING": "HUNTING",
    "DS ANCING": "DANCING",
    "IV THE NDUS ALLEY": "INDUS VALLEY",
    "A RTS": "ARTS",
    "T HE": "THE",
}

for wrong, correct in ocr_fixes.items():
    text = text.replace(wrong, correct)

# ------------------------------------------------
# Fix lowercase-uppercase joins
# ------------------------------------------------
text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)

# ------------------------------------------------
# Remove repeated spaces
# ------------------------------------------------
text = re.sub(r"[ \t]+", " ", text)

# ------------------------------------------------
# Keep paragraph structure
# ------------------------------------------------
text = re.sub(r"\n\s*\n+", "\n\n", text)

# ------------------------------------------------
# Proper SOURCE formatting
# ------------------------------------------------
text = re.sub(r"\s*\[SOURCE:", r"\n\n[SOURCE:", text)

# ------------------------------------------------
# Remove garbage lines
# ------------------------------------------------
final_lines = []

for line in text.split("\n"):
    line = line.strip()
    if not line:
        continue
    if len(line) <= 1:
        continue
    final_lines.append(line)

text = "\n".join(final_lines)

# ------------------------------------------------
# Save cleaned text
# ------------------------------------------------
with open("cleaned_final.txt", "w", encoding="utf-8") as f:
    f.write(text)

print("✅ cleaned_final.txt generated successfully")