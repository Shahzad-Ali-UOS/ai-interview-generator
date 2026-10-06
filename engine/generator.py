import json
import os
import random
from typing import Dict, List, Optional

class InterviewQuestionGenerator:
    """Generates structured role-specific technical and behavioral questions

    Supports Groq (LLaMA), OpenAI (GPT), and a deterministic fallback engine.
    """

    def __init__(self, question_bank_path: str = "data/question_banks.json"):
        self.question_bank: List[Dict] = []
        if os.path.exists(question_bank_path):
            with open(question_bank_path, "r", encoding="utf-8") as f:
                self.question_bank = json.load(f)

    def generate_questions(
        self,
        candidate: Dict,
        job_desc: Dict,
        matcher_analysis: Dict,
        num_technical: int = 3,
        num_behavioral: int = 2,
        llm_provider: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> List[Dict]:
        """Routes generation to an LLM provider or the fallback synthesis engine."""
        if api_key and llm_provider == "Groq":
            try:
                return self._generate_with_groq(candidate, job_desc, matcher_analysis, num_technical, num_behavioral, api_key)
            except Exception as e:
                print(f"[Warning] Groq LLM failed: {e}. Falling back to rule-guided engine.")

        if api_key and llm_provider == "OpenAI":
            try:
                return self._generate_with_openai(candidate, job_desc, matcher_analysis, num_technical, num_behavioral, api_key)
            except Exception as e:
                print(f"[Warning] OpenAI LLM failed: {e}. Falling back to rule-guided engine.")

        return self._generate_fallback(candidate, job_desc, matcher_analysis, num_technical, num_behavioral)

    # ----------------------------------------------------
    # Fallback Deterministic Engine (Offline / Safe Mode)
    # ----------------------------------------------------
    def _generate_fallback(
        self, candidate: Dict, job_desc: Dict, matcher_analysis: Dict,
        num_technical: int, num_behavioral: int
    ) -> List[Dict]:
        target_track = job_desc.get("track", "General")
        missing_skills = matcher_analysis.get("missing_skills", [])
        matched_skills = matcher_analysis.get("matched_skills", [])
        projects = candidate.get("projects", [])

        # 1. Filter bank by track & type
        tech_bank = [q for q in self.question_bank if q.get("track") == target_track and q.get("type") == "Technical"]
        beh_bank = [q for q in self.question_bank if q.get("type") == "Behavioral"]

        questions: List[Dict] = []

        # Pull from vetted bank first
        if tech_bank:
            sample_tech = random.sample(tech_bank, min(len(tech_bank), max(1, num_technical - 1)))
            questions.extend(sample_tech)

        # Dynamically synthesize tailored skill-gap probing question
        if missing_skills:
            gap_skill = missing_skills[0]
            questions.append({
                "id": f"GEN-GAP-{random.randint(100, 999)}",
                "track": target_track,
                "type": "Technical",
                "topic": f"Skill Gap Probing: {gap_skill}",
                "difficulty": "Intermediate",
                "question": f"The job specification emphasizes {gap_skill}, which is an area for progression in your portfolio. How would you apply your existing skills in {', '.join(matched_skills[:2]) or 'programming'} to rapidly ramp up and implement production-ready solutions in {gap_skill}?",
                "ideal_answer": f"The candidate should describe their rapid learning framework: breaking down {gap_skill} documentation, designing an isolated sandbox prototype, transferring algorithmic problem-solving principles, and pairing with mentors.",
                "evaluation_criteria": [
                    f"Articulates a clear learning methodology for {gap_skill}",
                    "Demonstrates foundational agility rather than evasion",
                    "Links prior project discipline to learning unfamiliar technology"
                ]
            })
        elif projects:
            # Dynamically synthesize project-probing question
            featured_project = projects[0]
            questions.append({
                "id": f"GEN-PRJ-{random.randint(100, 999)}",
                "track": target_track,
                "type": "Technical",
                "topic": f"Project Deep Dive: {featured_project}",
                "difficulty": "Advanced",
                "question": f"In your project '{featured_project}', walk me through your architectural choices, the trade-offs you encountered, and how you ensured code maintainability and test reliability.",
                "ideal_answer": "Candidate must articulate end-to-end architecture, bottleneck identification, profiling or metrics used, and unit/integration testing strategies.",
                "evaluation_criteria": [
                    "Depth of technical ownership of the reported project",
                    "Objective reasoning behind architectural and library choices",
                    "Awareness of performance trade-offs"
                ]
            })

        # Fill behavioral questions
        if beh_bank:
            sample_beh = random.sample(beh_bank, min(len(beh_bank), num_behavioral))
            questions.extend(sample_beh)

        return questions[: (num_technical + num_behavioral)]

    # ----------------------------------------------------
    # Cloud LLM: Groq (LLaMA 3.3 / LLaMA 3)
    # ----------------------------------------------------
    def _generate_with_groq(
        self, candidate: Dict, job_desc: Dict, matcher_analysis: Dict,
        num_technical: int, num_behavioral: int, api_key: str
    ) -> List[Dict]:
        from groq import Groq
        client = Groq(api_key=api_key)

        prompt = self._build_llm_prompt(candidate, job_desc, matcher_analysis, num_technical, num_behavioral)
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a Principal Software Engineering Interviewer. Output strict valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        return data.get("questions", [])

    # ----------------------------------------------------
    # Cloud LLM: OpenAI (GPT-4o-mini)
    # ----------------------------------------------------
    def _generate_with_openai(
        self, candidate: Dict, job_desc: Dict, matcher_analysis: Dict,
        num_technical: int, num_behavioral: int, api_key: str
    ) -> List[Dict]:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        prompt = self._build_llm_prompt(candidate, job_desc, matcher_analysis, num_technical, num_behavioral)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Principal Software Engineering Interviewer. Output strict valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        return data.get("questions", [])

    # ----------------------------------------------------
    # Prompt Construction
    # ----------------------------------------------------
    def _build_llm_prompt(self, candidate: Dict, job_desc: Dict, matcher_analysis: Dict, n_tech: int, n_beh: int) -> str:
        return f"""
Generate an interview question set for this candidate applying for the internship role.
Return STRICT JSON containing a root key "questions", with an array of {n_tech + n_beh} objects.

JSON Object Structure:
{{
  "id": "Q-01",
  "track": "{job_desc.get('track', 'General')}",
  "type": "Technical" or "Behavioral",
  "topic": "Specific Topic",
  "difficulty": "Foundational" or "Intermediate" or "Advanced",
  "question": "Clear question text",
  "ideal_answer": "Benchmark answer expectations",
  "evaluation_criteria": ["Criteria 1", "Criteria 2", "Criteria 3"]
}}

Candidate Profile:
- Name: {candidate.get('name')}
- Skills: {', '.join(candidate.get('skills', []))}
- Projects: {', '.join(candidate.get('projects', []))}
- Missing Track Skills to probe: {', '.join(matcher_analysis.get('missing_skills', []))}

Target Job Specification:
- Role: {job_desc.get('title')}
- Track: {job_desc.get('track')}
- Required Skills: {', '.join(job_desc.get('required_skills', []))}
- Context: {job_desc.get('description')}

Required Count: Exactly {n_tech} Technical questions (probing their projects and missing skills) and {n_beh} Behavioral questions using the STAR framework.
"""