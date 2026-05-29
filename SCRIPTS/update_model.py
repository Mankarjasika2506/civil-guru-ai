import os

files = [
    "ask_ai.py",
    "syllabus_agent.py",
    "fact_verifier.py",
    "answer_evaluator.py",
    "planner_agent.py",
    "syllabus_mapper.py",
    "fact_checker.py",
    "answer_evaluator_ocr.py"
]

for filename in files:
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        
        updated = content.replace("llama3.2:1b", "llama3.2:3b")
        updated = updated.replace("llama3:8b", "llama3.2:3b")
        updated = updated.replace("llama3.2\"", "llama3.2:3b\"")
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(updated)
        
        print(f"✅ Updated: {filename}")
    else:
        print(f"⚠️ Not found: {filename}")

print("\n🎯 All files updated to llama3.2:3b!")