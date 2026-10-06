import json
import os
import pypdf
import streamlit as st
import plotly.graph_objects as go

from engine.matcher import ProfileJDMatcher
from engine.generator import InterviewQuestionGenerator

st.set_page_config(
    page_title="AI Interview Assessment Cockpit | internee.pk",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Custom Modern UI Styling
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .hero-banner {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.15), rgba(99, 102, 241, 0.12));
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        backdrop-filter: blur(10px);
    }
    
    .metric-card {
        background: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.2);
        transition: transform 0.25s ease, border-color 0.25s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #38BDF8;
    }
    .metric-val {
        font-size: 2rem;
        font-weight: 700;
        color: #F8FAFC;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }

    .question-card {
        background: #0F172A;
        border-left: 4px solid #38BDF8;
        border-top: 1px solid #1E293B;
        border-right: 1px solid #1E293B;
        border-bottom: 1px solid #1E293B;
        border-radius: 12px;
        padding: 20px 22px;
        margin-bottom: 16px;
    }
    
    .tag-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-right: 6px;
    }
    .tag-tech { background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.3); }
    .tag-beh { background: rgba(168, 85, 247, 0.15); color: #C084FC; border: 1px solid rgba(168, 85, 247, 0.3); }
    .tag-foundational { background: rgba(34, 197, 94, 0.15); color: #4ADE80; border: 1px solid rgba(34, 197, 94, 0.3); }
    .tag-intermediate { background: rgba(251, 191, 36, 0.15); color: #FBBF24; border: 1px solid rgba(251, 191, 36, 0.3); }
    .tag-advanced { background: rgba(239, 68, 68, 0.15); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.3); }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------
def extract_text_from_pdf(uploaded_file) -> str:
    reader = pypdf.PdfReader(uploaded_file)
    extracted = []
    for page in reader.pages:
        txt = page.extract_text()
        if txt:
            extracted.append(txt)
    return "\n".join(extracted).strip()

@st.cache_data
def load_demo_data():
    with open("data/sample_profiles.json", "r", encoding="utf-8") as f:
        profiles = json.load(f)
    with open("data/job_descriptions.json", "r", encoding="utf-8") as f:
        jobs = json.load(f)
    return profiles, jobs

demo_profiles, demo_jobs = load_demo_data()
generator = InterviewQuestionGenerator(question_bank_path="data/question_banks.json")

# ---------------------------------------------------------
# Sidebar: Real-Time Ingestion Cockpit
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/microphone--v1.png", width=64)
    st.title("Interview Studio")
    st.caption("Real-Time AI Candidate Question & Rubric Synthesizer")
    st.markdown("---")

    input_mode = st.radio("Ingestion Mode:", ["📄 Upload Live Resume (PDF)", "👥 Use Demo Profiles"])
    
    candidate = {}
    job_desc = {}

    if input_mode == "📄 Upload Live Resume (PDF)":
        uploaded_file = st.file_uploader("Upload Candidate Resume (.pdf):", type=["pdf"])
        jd_title_input = st.text_input("Target Role Title:", value="AI & Machine Learning Intern")
        jd_text_input = st.text_area(
            "Paste Target Job Description (JD):",
            value="Looking for an intern proficient in Python, Scikit-Learn, XGBoost, PyTorch, Pandas, and Git to deploy production models with Streamlit.",
            height=120
        )

        if uploaded_file is not None:
            raw_resume = extract_text_from_pdf(uploaded_file)
            extracted_cand_skills = ProfileJDMatcher.extract_skills_from_raw_text(raw_resume)
            extracted_projects = ProfileJDMatcher.extract_projects_from_raw_text(raw_resume)
            extracted_jd_skills = ProfileJDMatcher.extract_skills_from_raw_text(jd_text_input)

            candidate = {
                "name": uploaded_file.name.replace(".pdf", "").replace("_", " ").title(),
                "target_track": "Machine Learning" if any(s.lower() in ["pytorch", "xgboost", "scikit-learn"] for s in extracted_cand_skills) else "Backend Development",
                "skills": extracted_cand_skills,
                "projects": extracted_projects,
                "bio": raw_resume[:300] + "..."
            }
            job_desc = {
                "title": jd_title_input,
                "track": candidate["target_track"],
                "required_skills": extracted_jd_skills if extracted_jd_skills else ["Python", "Git", "Scikit-Learn", "FastAPI"],
                "description": jd_text_input
            }
        else:
            st.info("👆 Upload an intern's resume PDF above to run live analysis.")
            st.stop()
    else:
        profile_names = [f"{p['name']} ({p['target_track']})" for p in demo_profiles]
        sel_cand_idx = st.selectbox("Select Candidate:", range(len(profile_names)), format_func=lambda x: profile_names[x])
        candidate = demo_profiles[sel_cand_idx]

        job_titles = [j['title'] for j in demo_jobs]
        sel_job_idx = st.selectbox("Select Job Description:", range(len(job_titles)), format_func=lambda x: job_titles[x])
        job_desc = demo_jobs[sel_job_idx]

    st.markdown("---")
    st.subheader("Question Composition")
    n_tech = st.slider("Technical Questions:", 1, 5, 3)
    n_beh = st.slider("Behavioral Questions (STAR):", 1, 4, 2)

    st.markdown("---")
    st.subheader("Model Engine")
    llm_choice = st.selectbox("Engine:", ["Zero-Cost Deterministic (Offline)", "Groq (LLaMA 3.3)", "OpenAI (GPT-4o-mini)"])
    api_key = ""
    provider_name = None
    if "Groq" in llm_choice:
        api_key = st.text_input("Groq API Key:", type="password")
        provider_name = "Groq"
    elif "OpenAI" in llm_choice:
        api_key = st.text_input("OpenAI API Key:", type="password")
        provider_name = "OpenAI"

    generate_btn = st.button("⚡ Generate Live Interview Set", type="primary", use_container_width=True)

# ---------------------------------------------------------
# Dynamic Alignment Analysis
# ---------------------------------------------------------
matcher_analysis = ProfileJDMatcher.analyze_alignment(candidate, job_desc)
match_score = matcher_analysis["match_score"]
matched_skills = matcher_analysis["matched_skills"]
missing_skills = matcher_analysis["missing_skills"]

# ---------------------------------------------------------
# Hero Banner & KPI Ribbon
# ---------------------------------------------------------
st.markdown(f"""
<div class="hero-banner">
    <h2 style="margin: 0; color: #F8FAFC;">🎙️ Real-Time Interview Question Generator & Assessment</h2>
    <p style="margin: 6px 0 0 0; color: #94A3B8; font-size: 0.95rem;">
        Dynamic candidate analysis for <b>{candidate['name']}</b> targeting <b>{job_desc['title']}</b>
    </p>
</div>
""", unsafe_allow_html=True)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-sub">Role Alignment Match</div>
        <div class="metric-val" style="color: {'#10B981' if match_score >= 70 else '#F59E0B'};">{match_score}%</div>
    </div>
    """, unsafe_allow_html=True)
with kpi2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-sub">Matched Skills</div>
        <div class="metric-val" style="color: #38BDF8;">{len(matched_skills)} <span style="font-size: 1rem; color: #64748B;">/ {matcher_analysis['total_required']}</span></div>
    </div>
    """, unsafe_allow_html=True)
with kpi3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-sub">Target Skill Gaps</div>
        <div class="metric-val" style="color: #F87171;">{len(missing_skills)}</div>
    </div>
    """, unsafe_allow_html=True)
with kpi4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-sub">Interview Questions</div>
        <div class="metric-val" style="color: #A855F7;">{n_tech + n_beh} <span style="font-size: 1rem; color: #64748B;">Qs</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Dynamic Competency Radar & Inventory
# ---------------------------------------------------------
col_radar, col_skills = st.columns([1.2, 1.3])

with col_radar:
    st.subheader("📊 Competency Alignment Radar")
    radar_labels = job_desc.get("required_skills", [])
    cand_skills_lower = [s.lower() for s in candidate.get("skills", [])]
    
    if radar_labels:
        cand_scores = [1.0 if s.lower() in cand_skills_lower else 0.2 for s in radar_labels]
        req_scores = [1.0 for _ in radar_labels]

        r_labels = radar_labels + [radar_labels[0]]
        r_cand = cand_scores + [cand_scores[0]]
        r_req = req_scores + [req_scores[0]]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=r_req,
            theta=r_labels,
            fill='toself',
            name='Target Role',
            line=dict(color='#64748B', dash='dash'),
            fillcolor='rgba(100, 116, 139, 0.15)'
        ))
        fig.add_trace(go.Scatterpolar(
            r=r_cand,
            theta=r_labels,
            fill='toself',
            name='Candidate Resume',
            line=dict(color='#0EA5E9', width=2),
            fillcolor='rgba(14, 165, 233, 0.35)'
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=False, range=[0, 1.1]),
                angularaxis=dict(tickfont=dict(size=10, color="#CBD5E1"))
            ),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            height=300,
            margin=dict(l=30, r=30, t=10, b=30),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No specific skills identified in the Job Description to plot.")

with col_skills:
    st.subheader("🎯 Parsed Resume Inventory")
    st.markdown("**✅ Verified Skills from Resume:**")
    if matched_skills:
        st.write(" ".join([f"`{s}`" for s in matched_skills]))
    else:
        st.caption("No direct overlaps detected.")

    st.markdown("**⚠️ Unverified Skills (Target for Interview Probing):**")
    if missing_skills:
        st.write(" ".join([f"`{s}`" for s in missing_skills]))
    else:
        st.success("Candidate covers 100% of required job skills!")

    st.markdown("**📂 Detected Project Highlights:**")
    for prj in candidate.get("projects", []):
        st.markdown(f"- 🛠️ *{prj}*")

st.markdown("---")

# ---------------------------------------------------------
# Dynamic Question Generation Execution
# ---------------------------------------------------------
session_key = f"{candidate['name']}_{job_desc['title']}_{n_tech}_{n_beh}"

if "last_session_key" not in st.session_state or st.session_state.last_session_key != session_key or generate_btn:
    with st.spinner("Analyzing resume bullets and synthesizing targeted interview questions..."):
        st.session_state.generated_questions = generator.generate_questions(
            candidate=candidate,
            job_desc=job_desc,
            matcher_analysis=matcher_analysis,
            num_technical=n_tech,
            num_behavioral=n_beh,
            llm_provider=provider_name,
            api_key=api_key
        )
        st.session_state.last_session_key = session_key

questions = st.session_state.get("generated_questions", [])

st.subheader(f"📋 Tailored Interview Question Set ({len(questions)} Questions)")
st.caption("Generated with evaluation benchmarks and scorecards:")

for idx, q in enumerate(questions, 1):
    q_type = q.get("type", "Technical")
    type_badge_class = "tag-tech" if q_type == "Technical" else "tag-beh"
    diff = q.get("difficulty", "Intermediate")
    diff_class = f"tag-{diff.lower()}"

    st.markdown(f"""
    <div class="question-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <div>
                <span class="tag-badge {type_badge_class}">{q_type}</span>
                <span class="tag-badge {diff_class}">{diff}</span>
                <span style="color: #94A3B8; font-size: 0.85rem; font-weight: 600;">{q.get('topic', 'General')}</span>
            </div>
            <span style="color: #64748B; font-weight: 700; font-size: 0.85rem;">Q{idx}</span>
        </div>
        <div style="font-size: 1.05rem; font-weight: 600; color: #F8FAFC; line-height: 1.5;">
            {q.get('question')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander(f"🔍 View Evaluation Rubric & Ideal Benchmark (Q{idx})"):
        st.markdown("**💡 Ideal Candidate Response:**")
        st.write(q.get("ideal_answer", "N/A"))
        st.markdown("**📋 Key Evaluation Criteria:**")
        for crit in q.get("evaluation_criteria", []):
            st.markdown(f"- [ ] {crit}")

# ---------------------------------------------------------
# Export Interview Guide
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📥 Export Interview Guide")

markdown_export = f"""# Candidate Interview Evaluation Guide - internee.pk
**Candidate:** {candidate['name']}  
**Target Role:** {job_desc['title']}  
**Readiness Match Score:** {match_score}%  

---
## Skills & Gap Breakdown
- **Verified Skills:** {', '.join(matched_skills)}
- **Skill Gaps Probed:** {', '.join(missing_skills) if missing_skills else 'None'}

---
## Question Set & Evaluation Rubric
"""

for i, q in enumerate(questions, 1):
    markdown_export += f"\n### Q{i}: [{q.get('type')} - {q.get('difficulty')}] {q.get('topic')}\n"
    markdown_export += f"**Question:** {q.get('question')}\n\n"
    markdown_export += f"**Ideal Benchmark:** {q.get('ideal_answer')}\n\n"
    markdown_export += "**Evaluation Criteria:**\n"
    for c in q.get("evaluation_criteria", []):
        markdown_export += f"- [ ] {c}\n"

st.download_button(
    label="📄 Download Interview Guide (.md)",
    data=markdown_export,
    file_name=f"Interview_Guide_{candidate['name'].replace(' ', '_')}.md",
    mime="text/markdown"
)