# 🎙️ AI Interview Question Generator & Evaluation Rubric Engine

An intelligent recruitment assessment platform designed for tech internships. The system ingests candidate resumes (live PDF parsing or curated profiles), analyzes alignment against target Job Descriptions, plots skill gaps, and synthesizes role-specific technical and behavioral (STAR) questions equipped with evaluation rubrics and benchmark answers.

---

## 📌 Features

- **Live PDF Resume Parser:** Real-time text extraction using `pypdf`, extracting technical competencies and project highlights automatically.
- **Dynamic Skill Matcher & Gap Radar:** Interactive Plotly radar chart displaying verified candidate coverage vs. target job requirements.
- **Dual-Engine Question Generator:**
  - **Cloud LLM Support:** Direct integration with **Groq (LLaMA 3.3)** or **OpenAI (GPT-4o-mini)**.
  - **Deterministic Zero-Cost Fallback:** Built-in template and heuristic synthesis engine running completely offline without API keys or costs.
- **STAR Behavioral & Technical Rubrics:** Generates benchmark ideal answers and checkbox-style evaluation criteria for each question.
- **One-Click Export:** Download a complete, formatted Markdown interview guide for hiring panels.

---

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **Parsing & NLP:** `pypdf`, Regex, Scikit-Learn
- **LLM Integrations:** `groq`, `openai`
- **Dashboard & Visualizations:** `streamlit`, `plotly`
- **Data Serialization:** JSON, Pandas

---

## 📂 Project Structure

```text
ai_interview_generator/
├── data/
│   ├── question_banks.json      # Structured questions with rubrics and benchmarks
│   ├── sample_profiles.json     # Demo profiles for instant evaluation
│   └── job_descriptions.json    # Standard role requirements
├── engine/
│   ├── __init__.py              # Package initializer
│   ├── matcher.py               # Resume parsing & skill alignment engine
│   └── generator.py             # Dual-engine LLM / rule-guided question synthesizer
├── app.py                       # Streamlit interactive evaluation cockpit
├── test_engine.py               # Headless verification script
├── requirements.txt             # Project dependencies
└── README.md                    # Documentation