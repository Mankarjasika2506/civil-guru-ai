"""
Syllabus Mapper - maps a current-affairs topic to a UPSC GS paper and subject.

Design:
  1. Retrieve chunks (textbooks + PIB + PRS) with per-collection relevance cutoffs.
  2. Subject  = majority subject of retrieved textbook chunks (if >= 2 agree),
                otherwise nearest example phrases (fallback).
  3. GS paper = derived from the subject, so the two never contradict.
  4. "Also relevant" = a second GS paper when the topic clearly spans two papers.
  5. References are built ONLY from chunks whose text was sent to the LLM.

Known limits (document in README):
  - Subject / GS paper are heuristics, not ground truth.
  - "confidence" is the share of retrieved-chunk votes (or phrase similarity),
    NOT a probability of being correct.
"""

import json
import re
from collections import defaultdict

from sentence_transformers import SentenceTransformer, util

from qdrant_client_setup import query_collection, build_references
from groq_client_setup import generate

model = SentenceTransformer("all-MiniLM-L6-v2")


RETRIEVAL_PLAN = [
    ("civil_guru", 3, 0.45),
    ("pib_articles", 1, 0.50),
    ("prs_articles", 1, 0.50),
]


SECONDARY_MIN_SCORE = 0.50

SUBJECT_TO_GS = {
    "POLITY": "GS2",
    "HISTORY": "GS1",
    "GEOGRAPHY": "GS1",
    "ART&CULTURE": "GS1",
    "SOCIOLOGY": "GS1",
    "ECONOMICS": "GS3",
    "ENVIRONMENT": "GS3",
    "SCIENCE": "GS3",
    "ETHICS": "GS4",
}


SUBJECT_EXAMPLES = {
    "POLITY": [
        "Parliament bill and constitutional amendment",
        "fundamental rights and Supreme Court judgments",
        "federalism and Centre-State relations",
        "elections and the Election Commission",
        "privacy and data protection law",
    ],
    "HISTORY": [
        "Mauryan and Gupta empires",
        "Mughal administration and land revenue",
        "British colonial policy in India",
        "freedom struggle and Gandhian movements",
        "Harappan civilisation",
    ],
    "GEOGRAPHY": [
        "monsoon and rainfall patterns",
        "rivers and drainage systems",
        "soil types and agriculture regions",
        "plate tectonics and earthquakes",
        "climate zones and vegetation",
    ],
    "ECONOMICS": [
        "inflation and RBI monetary policy",
        "GDP growth and fiscal deficit",
        "banking, finance and insurance",
        "ports, shipping and logistics policy",
        "agriculture prices and food security",
    ],
    "ENVIRONMENT": [
        "climate change and global warming",
        "biodiversity and wildlife conservation",
        "pollution and environmental laws",
        "disaster management and climate adaptation",
    ],
    "ETHICS": [
        "ethics and integrity in public service",
        "emotional intelligence and attitude",
        "moral thinkers and philosophers",
        "probity and accountability in governance",
    ],
    "SOCIOLOGY": [
        "caste and social stratification",
        "women empowerment and gender issues",
        "tribal communities and welfare",
        "urbanisation and migration",
    ],
    "SCIENCE": [
        "space missions and ISRO",
        "biotechnology and genetic engineering",
        "artificial intelligence and emerging technology",
        "defence technology and nuclear energy",
    ],
    "ART&CULTURE": [
        "classical dance and music forms",
        "temple architecture and sculpture",
        "painting traditions and folk art",
        "festivals, heritage sites and UNESCO",
    ],
}


_EXAMPLE_VECS = {
    subject: model.encode(phrases, convert_to_tensor=True)
    for subject, phrases in SUBJECT_EXAMPLES.items()
}


def _norm_subject(raw):
    s = (raw or "").upper().strip()
    return "ART&CULTURE" if s == "ART" else s


def classify_by_examples(topic):
    """Best single-phrase match across all subjects -> (subject, similarity)."""
    topic_vec = model.encode(topic, convert_to_tensor=True)
    best_subject, best_score = "POLITY", -1.0
    for subject, vecs in _EXAMPLE_VECS.items():
        score = util.cos_sim(topic_vec, vecs).max().item()
        if score > best_score:
            best_subject, best_score = subject, score
    return best_subject, round(best_score, 2)


def classify(topic, used):
    """Return (subject, gs_paper, confidence, method)."""
    votes = defaultdict(float)
    counts = defaultdict(int)
    for p in used:
        subject = _norm_subject(p.payload.get("subject"))
        if subject in SUBJECT_TO_GS:  # only textbook chunks carry a subject tag
            votes[subject] += p.score
            counts[subject] += 1

    if votes:
        subject = max(votes, key=votes.get)
        if counts[subject] >= 2:
            confidence = round(votes[subject] / sum(votes.values()), 2)
            return subject, SUBJECT_TO_GS[subject], confidence, "retrieved chunks"

    subject, score = classify_by_examples(topic)
    return subject, SUBJECT_TO_GS[subject], score, "topic similarity"


def secondary_gs(topic, gs_paper):
    """A second GS paper if the topic clearly spans two, else None."""
    subject, score = classify_by_examples(topic)
    other = SUBJECT_TO_GS[subject]
    if other != gs_paper and score >= SECONDARY_MIN_SCORE:
        return f"{other} ({subject.title()})"
    return None


def retrieve_context(topic):
    """Return (context_text, used_points). Only used points become references."""
    used = []
    for name, take, min_score in RETRIEVAL_PLAN:
        try:
            points = query_collection(topic, name, n_results=take)
            used += [p for p in points if p.score >= min_score]
        except Exception as e:
            print(f"{name} retrieval error: {e}")
    context = "\n\n".join(p.payload["text"] for p in used)
    return context, used


def _parse_json(raw):
    raw = raw.replace("```json", "").replace("```", "").strip()
    start, end = raw.find("{"), raw.rfind("}") + 1
    raw = raw[start:end]
    raw = re.sub(r",\s*}", "}", raw)
    raw = re.sub(r",\s*]", "]", raw)
    return json.loads(raw)


def map_to_syllabus(topic):
    topic = topic.strip().strip("\"'“”‘’") 
    print(f"\n🗺️ Mapping: {topic}")

    context, used = retrieve_context(topic)
    references = build_references(used)
    sources = [r["label"] for r in references]  

    subject, gs_paper, confidence, method = classify(topic, used)
    also = secondary_gs(topic, gs_paper)
    print(f"📌 {gs_paper} / {subject} (via {method}, score {confidence})")

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
- relevance: exactly 2 sentences on why UPSC asks this; must NOT be empty
- question_types: 2-3 short labels (e.g. "Analytical essay", "Statement-based MCQ")
- related_topics: 3 real UPSC syllabus topics, historically consistent
  (never list something that came later as a predecessor, or the reverse)
- Use only facts supported by the Context or well-established general knowledge.
  Do not invent names, numbers or dates.

Topic: {topic}
This topic belongs to {gs_paper} ({subject}).

Context:
{context[:2000] if context else "(no relevant passages found)"}
"""

    base = {
        "gs_paper": gs_paper,
        "also_relevant": also,
        "confidence": confidence,
        "subject": subject,
        "sources": sources,
        "references": references,
    }

    for attempt in (1, 2):  # one retry if the model returns broken JSON
        try:
            result = _parse_json(generate(prompt, max_tokens=900))
            result.update(base)
            return result
        except Exception as e:
            print(f"⚠️ LLM attempt {attempt} failed: {e}")

    return {
        **base,
        "topic": topic,
        "subtopic": "",
        "relevance": (
            f"This topic is relevant for UPSC {gs_paper} as it covers key "
            f"aspects of {subject.lower()} that are frequently examined."
        ),
        "question_types": ["Descriptive", "Analytical"],
        "related_topics": [],
    }


def print_result(result):
    refs = result.get("references", [])
    ref_lines = "\n".join(
        f"- {r['label']}" + (f" ({r['url']})" if r.get("url") else "")
        for r in refs
    ) or "- (none)"
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 SYLLABUS MAPPING RESULT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GS Paper    : {result.get('gs_paper')} (score: {result.get('confidence')})
Also in     : {result.get('also_relevant') or '-'}
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
References (chunks actually used):
{ref_lines}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


if __name__ == "__main__":
    topic = input("Enter news topic or headline: ")
    print_result(map_to_syllabus(topic))