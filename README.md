# Civil Guru — Agentic AI UPSC Preparation System

Civil Guru is a fully local AI-powered UPSC preparation platform built using multiple AI agents, RAG pipelines, OCR systems, and LLMs.

## Features

- AI Answer Evaluation
- OCR-based Handwritten Answer Analysis
- Dynamic Retrieval System
- Fact Verification Agent
- UPSC Planner Agent
- RAG-based Question Answering

## Tech Stack

- Python
- Streamlit
- Ollama (LLaMA 3.2)
- ChromaDB
- sentence-transformers
- CrossEncoder
- PyMuPDF
- Tesseract OCR
- BeautifulSoup

## AI Agents

- Syllabus Mapper
- Fact Checker
- Answer Evaluator
- Planner Agent

## Status

Under active development.


## Project Structure

```text
CIVIL_GURU/
│
├── DATA/                     # UPSC datasets and PDFs
├── db/                       # ChromaDB vector database
│
├── SCRIPTS/
│   ├── app.py                # Streamlit frontend
│   ├── main.py               # Main execution pipeline
│   │
│   ├── dynamic_retriever.py  # RAG retrieval pipeline
│   ├── reranker.py           # CrossEncoder reranking
│   ├── query_analyzer.py     # Query understanding
│   │
│   ├── syllabus_mapper.py    # UPSC syllabus mapping agent
│   ├── planner_agent.py      # Study planning agent
│   ├── fact_checker.py       # Fact verification agent
│   ├── answer_evaluator.py   # Answer evaluation agent
│   ├── answer_evaluator_ocr.py # OCR handwritten evaluation
│   │
│   ├── chunk_text.py         # Text chunking pipeline
│   ├── store_chunks.py       # Vector DB storage
│   ├── read_pdf.py           # PDF extraction
│   └── clean_text.py         # Data cleaning
│
├── README.md
└── .gitignore
```
