import ollama
import json

MODEL = "llama3.2:3b"

def create_plan(query: str) -> dict:

    prompt = f"""
You are a UPSC Answer Planner.

Return ONLY valid JSON.

Format:

{{
    "intro": "",
    "body_sections": [
        {{
            "heading": "",
            "points": [],
            "keywords": []
        }}
    ],
    "conclusion": ""
}}

Rules:
- intro: 2-3 line context setter
- body_sections: 3-5 sections with clear headings
- conclusion: forward looking balanced statement

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
        return json.loads(output)

    except Exception as e:
        print(f"⚠️ Planner failed: {e}")
        return {
            "intro": "Brief introduction",
            "body_sections": [
                {"heading": "Main features", "points": [], "keywords": []}
            ],
            "conclusion": "Balanced conclusion"
        }