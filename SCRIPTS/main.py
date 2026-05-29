import os
import sys

print("""
╔═══════════════════════════════════════╗
║         CIVIL GURU AI AGENT           ║
║   Your Personal UPSC AI Assistant     ║
╚═══════════════════════════════════════╝
""")

def show_menu():
    print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Choose an option:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 🗺️  Map news to UPSC Syllabus
2. ✅  Verify a fact/claim
3. 📝  Evaluate handwritten answer
4. 🧠  Generate UPSC answer
5. ❌  Exit
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

def run_syllabus_mapper():
    from syllabus_mapper import map_to_syllabus, print_result
    print("\n🗺️  SYLLABUS MAPPER")
    print("Enter a news headline or current affairs topic:")
    topic = input("→ ")
    result = map_to_syllabus(topic)
    print_result(result)

def run_fact_checker():
    from fact_checker import verify_claim, print_result
    print("\n✅  FACT CHECKER")
    print("Enter a claim or statement to verify:")
    claim = input("→ ")
    result = verify_claim(claim)
    print_result(claim, result)

def run_answer_evaluator():
    from answer_evaluator_ocr import evaluate_handwritten_answer
    print("\n📝  HANDWRITTEN ANSWER EVALUATOR")
    print("Enter image path of your handwritten answer:")
    image_path = input("→ ").strip('"')
    print("Enter the question:")
    question = input("→ ")
    result = evaluate_handwritten_answer(image_path, question)
    if result:
        print(result)
    else:
        print("❌ Evaluation failed — check image path")

def run_answer_generator():
    from ask_ai import main as run_ask_ai
    print("\n🧠  ANSWER GENERATOR")
    run_ask_ai()

def main():
    while True:
        show_menu()
        choice = input("Enter choice (1-5): ").strip()

        if choice == "1":
            run_syllabus_mapper()
        elif choice == "2":
            run_fact_checker()
        elif choice == "3":
            run_answer_evaluator()
        elif choice == "4":
            run_answer_generator()
        elif choice == "5":
            print("\n👋 Goodbye! Keep studying for UPSC! 🎯\n")
            sys.exit(0)
        else:
            print("⚠️ Invalid choice! Enter 1-5")

        input("\n\nPress Enter to continue...")

if __name__ == "__main__":
    main()