import re
from typing import Dict, List, Set

TECH_SKILL_CORPUS = [
    "python", "pandas", "numpy", "scikit-learn", "xgboost", "pytorch", "tensorflow",
    "opencv", "fastapi", "django", "flask", "postgresql", "mysql", "mongodb", "redis",
    "docker", "kubernetes", "git", "github", "linux", "rest api", "streamlit", "plotly",
    "power bi", "tableau", "aws", "gcp", "azure", "ci/cd", "celery", "sql"
]

class ProfileJDMatcher:
    """Analyzes real-time alignment and extracts technical competencies from raw text."""

    @staticmethod
    def extract_skills_from_raw_text(text: str) -> List[str]:
        """Extracts recognizable technical keywords from raw unstructured resume or JD text."""
        lowered = text.lower()
        extracted = []
        for skill in TECH_SKILL_CORPUS:
            # Match whole words or standard tech phrases
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, lowered):
                extracted.append(skill.title() if len(skill) > 3 else skill.upper())
        return list(dict.fromkeys(extracted))

    @staticmethod
    def extract_projects_from_raw_text(text: str) -> List[str]:
        """Heuristically extracts key project/experience bullets from resume text."""
        lines = [line.strip() for line in text.split("\n") if len(line.strip()) > 20]
        project_lines = []
        keywords = ["project", "built", "developed", "deployed", "implemented", "designed", "created"]
        for line in lines:
            if any(kw in line.lower() for kw in keywords) and len(line) < 140:
                clean_line = re.sub(r'^[•\-\*\d\.\s]+', '', line)
                project_lines.append(clean_line)
                if len(project_lines) >= 3:
                    break
        return project_lines if project_lines else ["Production software development & ML modeling"]

    @staticmethod
    def analyze_alignment(candidate: Dict, job_desc: Dict) -> Dict:
        cand_skills: Set[str] = {s.strip().lower() for s in candidate.get("skills", [])}
        req_skills: Set[str] = {s.strip().lower() for s in job_desc.get("required_skills", [])}

        matched_skills = [s for s in job_desc.get("required_skills", []) if s.lower() in cand_skills]
        missing_skills = [s for s in job_desc.get("required_skills", []) if s.lower() not in cand_skills]

        total_req = len(req_skills) if req_skills else 1
        match_score = round((len(matched_skills) / total_req) * 100, 1)

        return {
            "match_score": match_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "candidate_name": candidate.get("name", "Candidate"),
            "target_role": job_desc.get("title", "Target Role"),
            "total_required": len(req_skills),
            "total_matched": len(matched_skills)
        }