import json
import re
from sentence_transformers import SentenceTransformer, util
from qdrant_client_setup import query_collection
from groq_client_setup import generate

model = SentenceTransformer("all-MiniLM-L6-v2")

# ── GS Paper descriptions ──
GS_PAPERS = {
    "GS1": "history ancient medieval modern india culture heritage art painting dance music society women urbanisation population world civilisation",
    "GS2": "polity constitution parliament president governor fundamental rights directive principles judiciary federalism international relations foreign policy UN bilateral treaties governance",
    "GS3": "economy gdp inflation rbi monetary fiscal budget agriculture wheat rice crop food security industry infrastructure environment climate change disaster management floods earthquake science technology space isro internal security",
    "GS4": "ethics integrity honesty attitude aptitude emotional intelligence moral thinkers philosophers public service governance accountability transparency"
}

# ── Subject descriptions for embedding detection ──
SUBJECT_DESCRIPTIONS = {
    "POLITY": "constitution parliament fundamental rights directive principles judiciary president governor federalism local government elections",
    "HISTORY": "ancient medieval modern mughal british colonial freedom struggle independence civilisation harappa vedic partition",
    "GEOGRAPHY": "river mountain climate soil monsoon plateau physical geography terrain landforms oceans",
    "ECONOMICS": "economy gdp inflation rbi monetary fiscal budget agriculture wheat crop food security industry trade banking finance poverty",
    "ETHICS": "ethics integrity moral attitude aptitude emotional intelligence governance accountability transparency values",
    "SOCIOLOGY": "society caste tribe social culture religion community women urbanisation population empowerment",
    "SCIENCE": "space isro nuclear biotechnology technology artificial intelligence defence research innovation",
    "ART&CULTURE": "art culture dance music painting temple architecture festivals heritage prehistoric rock sculptures",
}

def detect_gs_paper(topic):
    topic_embedding = model.encode(topic, convert_to_tensor=True)
    best_paper = "GS2"
    best_score = 0.0
    for paper, description in GS_PAPERS.items():
        desc_embedding = model.encode(description, convert_to_tensor=True)
        score = util.cos_sim(topic_embedding, desc_embedding).item()
        if score > best_score:
            best_score = score
            best_paper = paper
    return best_paper, round(best_score, 2)

def detect_subject(topic):
    topic_embedding = model.encode(topic, convert_to_tensor=True)
    best_subject = "GENERAL"
    best_score = 0.0
    for subject, description in SUBJECT_DESCRIPTIONS.items():
        desc_embedding = model.encode(description, convert_to_tensor=True)
        score = util.cos_sim(topic_embedding, desc_embedding).item()
        if score > best_score:
            best_score = score
            best_subject = subject
    return best_subject

def retrieve_context(topic):
    all_docs = []
    sources = []

    try:
        points = query_collection(topic, "civil_guru", n_results=5)
        docs = [p.payload["text"] for p in points]
        all_docs.extend(docs)

        for p in points:
            subject = p.payload.get("subject", "").upper()
            if subject == "POLITY":
                src = "📖 Laxmikanth — Indian Polity"
            elif subject == "HISTORY":
                src = "📖 RS Sharma / Bipin Chandra / Satish Chandra"
            elif subject in ["ART&CULTURE", "ART"]:
                src = "📚 NCERT — Art & Culture"
            elif subject == "ECONOMICS":
                src = "📚 NCERT — Economics"
            elif subject == "GEOGRAPHY":
                src = "📚 NCERT — Geography"
            elif subject == "ETHICS":
                src = "📚 NCERT — Ethics"
            elif subject == "SOCIOLOGY":
                src = "📚 NCERT — Sociology"
            else:
                src = "📚 NCERT Textbooks"
            if src not in sources:
                sources.append(src)
    except Exception as e:
        print(f"civil_guru retrieval error: {e}")

    try:
        points = query_collection(topic, "pib_articles", n_results=3)
        docs = [p.payload["text"] for p in points]
        if docs:
            all_docs.extend(docs)
            sources.append("📰 PIB — Press Information Bureau")
    except Exception as e:
        print(f"pib retrieval error: {e}")

    try:
        points = query_collection(topic, "prs_articles", n_results=2)
        docs = [p.payload["text"] for p in points]
        if docs:
            all_docs.extend(docs)
            sources.append("⚖️ PRS — Legislative Research India")
    except Exception as e:
        print(f"prs retrieval error: {e}")

    return "\n\n".join(all_docs[:5]), sources

def map_to_syllabus(topic):
    print(f"\n🗺️ Mapping: {topic}")

    gs_paper, confidence = detect_gs_paper(topic)
    print(f"📌 Detected: {gs_paper} (confidence: {confidence})")

    context, sources = retrieve_context(topic)

    # Detect subject using embeddings
    subject = detect_subject(topic)
    print(f"📌 Subject: {subject}")

    prompt = f"""
You are a UPSC Syllabus Expert.

Return ONLY valid JSON:

{{
    "topic": "",
    "subtopic": "",
    "relevance": "",
    "question_types": [],
    "related_topics": []
}}

Rules:
- topic: specific UPSC topic name
- subtopic: specific subtopic
- relevance: 2 sentences why UPSC asks this — must NOT be empty
- question_types: 2-3 types of UPSC questions asked from this topic
- related_topics: 3 related UPSC topics

Topic: {topic}

Context:
{context[:2000]}
"""

    try:
        output = generate(prompt, max_tokens=900)
        output = output.replace("```json", "").replace("```", "").strip()
        start = output.find("{")
        end = output.rfind("}") + 1
        output = output[start:end]
        output = re.sub(r',\s*}', '}', output)
        output = re.sub(r',\s*]', ']', output)

        result = json.loads(output)
        result["subject"] = subject
        result["gs_paper"] = gs_paper
        result["confidence"] = confidence
        result["sources"] = sources
        return result

    except Exception as e:
        print(f"⚠️ LLM failed: {e}")
        return {
            "gs_paper": gs_paper,
            "confidence": confidence,
            "subject": subject,
            "topic": topic,
            "subtopic": "",
            "relevance": f"This topic is relevant for UPSC {gs_paper} as it covers key aspects of {subject.lower()} that are frequently examined.",
            "question_types": ["Descriptive", "Analytical"],
            "related_topics": [],
            "sources": sources
        }

def print_result(result):
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 SYLLABUS MAPPING RESULT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GS Paper    : {result.get('gs_paper')} (confidence: {result.get('confidence')})
Subject     : {result.get('subject')}
Topic       : {result.get('topic')}
Subtopic    : {result.get('subtopic')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Relevance   : {result.get('relevance')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Question Types:
{chr(10).join(['- ' + q for q in result.get('question_types', [])])}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Related Topics:
{chr(10).join(['- ' + t for t in result.get('related_topics', [])])}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

if __name__ == "__main__":
    topic = input("Enter news topic or headline: ")
    result = map_to_syllabus(topic)
    print_result(result)