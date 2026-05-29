import subprocess
import json
import re

# =========================
# USER QUESTION
# =========================

query = input("Enter UPSC question: ")

# =========================
# ANALYZER PROMPT
# =========================

prompt = f"""
You are an intelligent UPSC Query Analyzer.

Your task is to analyze the UPSC question deeply.

Return ONLY valid JSON.

JSON format:

{{
    "subject": "",
    "topic": "",
    "keywords": [],
    "dimensions": []
}}

Rules:
- Subject should be one word like:
  history, polity, economics, geography, sociology, environment, ethics

- Topic should be specific

- Keywords should include important UPSC terms

- Dimensions should include all expected answer areas

Question:
{query}
"""

# =========================
# RUN MODEL
# =========================

response = subprocess.run(
    ["ollama", "run", "llama3:8b"],
    input=prompt,
    text=True,
    capture_output=True,
    encoding="utf-8",
    errors="ignore"
)

output = response.stdout.strip()

# =========================
# CLEAN OUTPUT
# =========================

# Remove markdown if model adds it
# Remove markdown
output = output.replace("```json", "")
output = output.replace("```", "")
output = output.strip()

# 🔥 Extract only JSON part
start = output.find("{")
end = output.rfind("}") + 1

output = output[start:end]

# =========================
# PARSE JSON
# =========================

try:
    data = json.loads(output)

    print("\n🧠 QUERY ANALYSIS\n")

    print("📚 Subject:")
    print(data["subject"])

    print("\n📌 Topic:")
    print(data["topic"])

    print("\n🔑 Keywords:")
    for k in data["keywords"]:
        print("-", k)

    print("\n🧩 Expected Dimensions:")
    for d in data["dimensions"]:
        print("-", d)

except Exception as e:

    print("\n❌ JSON Parsing Failed")
    print("\nRaw Output:\n")
    print(output)

    print("\nError:")
    print(e)