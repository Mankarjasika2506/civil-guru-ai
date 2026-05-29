import ollama
import json

SUBJECT_MAP = {
    "polity": "POLITY",
    "indian polity": "POLITY",
    "constitution": "POLITY",
    "history": "HISTORY",
    "ancient history": "HISTORY",
    "medieval history": "HISTORY",
    "modern history": "HISTORY",
    "geography": "GEOGRAPHY",
    "indian geography": "GEOGRAPHY",
    "economics": "ECONOMICS",
    "indian economy": "ECONOMICS",
    "economy": "ECONOMICS",
    "ethics": "ETHICS",
    "art": "ART&CULTURE",
    "art and culture": "ART&CULTURE",
    "culture": "ART&CULTURE",
    "sociology": "SOCIOLOGY",
    "society": "SOCIOLOGY",
}

MODEL = "llama3.2:3b"

def analyze_syllabus(query):

    prompt = f"""
You are a UPSC Syllabus Analyzer.

Analyze the UPSC question carefully.

Return ONLY valid JSON.

FORMAT:

{{
    "paper": "",
    "subject": "",
    "topic": "",
    "subtopic": "",
    "themes": [],
    "question_type": "",
    "syllabus_match": ""
}}

Rules:
- subject must be one word only:
  history/polity/economics/geography/sociology/ethics/art

Question:
{query}
"""

    try:
        response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        output = response["message"]["content"].strip()

        output = output.replace("```json", "").replace("```", "").strip()
        start = output.find("{")
        end = output.rfind("}") + 1
        output = output[start:end]

        data = json.loads(output)

        # Normalize subject
        subject_raw = data.get("subject", "").lower()
        data["subject"] = SUBJECT_MAP.get(subject_raw, "GENERAL")

        return data

    except Exception as e:
        print(f"❌ Syllabus analysis failed: {e}")
        return {
            "paper": "UNKNOWN",
            "subject": "GENERAL",
            "topic": "UNKNOWN",
            "subtopic": "UNKNOWN",
            "themes": [],
            "question_type": "UNKNOWN",
            "syllabus_match": "UNKNOWN"
        }