import json
from engine.matcher import ProfileJDMatcher
from engine.generator import InterviewQuestionGenerator

def run_verification():
    print("=" * 65)
    print("      ENGINE VERIFICATION: MATCHER & QUESTION GENERATOR")
    print("=" * 65)

    # 1. Load sample mock data
    with open("data/sample_profiles.json", "r", encoding="utf-8") as f:
        profiles = json.load(f)
    with open("data/job_descriptions.json", "r", encoding="utf-8") as f:
        jobs = json.load(f)

    candidate = profiles[0]  # Ahmed Raza (ML Track)
    job = jobs[0]            # ML Engineering Intern JD

    print(f"\n[1] Candidate: {candidate['name']} ({candidate['target_track']})")
    print(f"[2] Target Role: {job['title']} ({job['track']})")

    # 2. Test Alignment Matcher
    print("\n--- Testing ProfileJDMatcher ---")
    analysis = ProfileJDMatcher.analyze_alignment(candidate, job)
    print(f"Match Readiness Score : {analysis['match_score']}%")
    print(f"Matched Skills ({len(analysis['matched_skills'])})  : {', '.join(analysis['matched_skills'])}")
    print(f"Missing / Gap Skills ({len(analysis['missing_skills'])}): {', '.join(analysis['missing_skills']) if analysis['missing_skills'] else 'None (100% Match)'}")

    # 3. Test Question Generator (Fallback / Offline Mode)
    print("\n--- Testing InterviewQuestionGenerator (Offline / Deterministic) ---")
    generator = InterviewQuestionGenerator(question_bank_path="data/question_banks.json")
    questions = generator.generate_questions(
        candidate=candidate,
        job_desc=job,
        matcher_analysis=analysis,
        num_technical=3,
        num_behavioral=2
    )

    print(f"\nGenerated Total Questions: {len(questions)}\n")
    for idx, q in enumerate(questions, 1):
        print(f"[{idx}] {q['type']} ({q['difficulty']}) - {q['topic']}")
        print(f"    Q: {q['question']}")
        print(f"    Rubric Check: {q['evaluation_criteria'][0]}")
        print("-" * 65)

    print("\n[SUCCESS] Engine pipeline is operational!")

if __name__ == "__main__":
    run_verification()