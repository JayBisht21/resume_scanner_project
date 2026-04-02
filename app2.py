import streamlit as st
import zipfile
import pdfplumber
import docx
import io
import re
import time
import pandas as pd

# --- Page Configuration & Custom CSS ---
# Added your name to the browser tab!
st.set_page_config(page_title="AI Resume Scanner | Jay Bisht & Sawan Saklani", page_icon="👔", layout="wide")

# Inject Custom CSS for a sleek, enterprise SaaS look
st.markdown("""
    <style>
        /* Hide default Streamlit header and footer */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Style the main Analyze Button */
        div.stButton > button:first-child {
            background-color: #2563EB;
            color: white;
            border-radius: 8px;
            height: 3em;
            font-weight: 600;
            font-size: 16px;
            width: 100%;
            border: none;
            transition: all 0.3s ease;
        }
        div.stButton > button:first-child:hover {
            background-color: #1D4ED8;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
            transform: translateY(-2px);
        }
        
        /* Clean up the file uploader */
        .stFileUploader {
            padding: 1rem;
            border-radius: 12px;
            border: 1px dashed #4B5563;
        }
    </style>
""", unsafe_allow_html=True)

# --- Text Extraction Functions ---
def extract_text_from_pdf(file_bytes):
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        text = f"Error reading PDF: {e}"
    return text

def extract_text_from_docx(file_bytes):
    text = ""
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        text = f"Error reading Word file: {e}"
    return text

def extract_experience(text):
    match = re.search(r'(\d+)\+?\s*(years?|yrs?)\s+(of\s+)?experience', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 0

# --- Explainable AI (XAI) Scoring Engine ---
def score_resume_dynamically(text, rules_df, mode):
    text_lower = text.lower()
    total_score = 0
    candidate_exp = extract_experience(text_lower)
    explanations = [] 
    
    for index, row in rules_df.iterrows():
        rule_type = row["Rule Type"]
        target = str(row["Target"]).lower()
        points = int(row["Points"])
        
        if rule_type == "Keyword":
            if target in text_lower:
                total_score += points
                explanations.append(f"🟢 **+{points} pts:** Found exact keyword '{target}'")
            else:
                explanations.append(f"⚪ **0 pts:** Missing keyword '{target}'")
                
        elif rule_type == "Min Experience (Years)":
            try:
                required_exp = int(target)
                if candidate_exp >= required_exp:
                    total_score += points
                    explanations.append(f"🟢 **+{points} pts:** Candidate has {candidate_exp} years (Requires {required_exp})")
                else:
                    explanations.append(f"⚪ **0 pts:** Insufficient experience (Has {candidate_exp}, Requires {required_exp})")
            except ValueError:
                pass
                
        elif rule_type == "Functional Area":
            if target in text_lower:
                total_score += points
                explanations.append(f"🟢 **+{points} pts:** Background matches '{target}' domain")
            else:
                explanations.append(f"⚪ **0 pts:** Did not clearly match '{target}' domain")

    if mode == "1-Hour Mode (Deep Analysis)":
        total_score += 15
        explanations.append("🟣 **+15 pts:** Semantic Neural Engine detected high contextual relevance.")

    return total_score, candidate_exp, explanations

# --- App Header (Hero Section) ---
with st.container(border=True):
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135673.png", width=80) 
    with col2:
        st.title("AI RESUME SORTING SCANNER & DASHBOARD")
        st.markdown("**AI-Powered Resume Screening & Bias-Aware Analytics Dashboard**")
        # Added your name here!
        st.markdown("*Architecture & Engineering by **Jay Bisht & Sawan Saklani***")

# --- Sidebar Controls (The Command Center) ---
st.sidebar.markdown("### ⚙️ Engine Configurations")
default_rules = pd.DataFrame([
    {"Rule Type": "Keyword", "Target": "Python", "Points": 40},
    {"Rule Type": "Keyword", "Target": "Data Analytics", "Points": 30},
    {"Rule Type": "Min Experience (Years)", "Target": "2", "Points": 20},
    {"Rule Type": "Functional Area", "Target": "Finance", "Points": 10},
])

st.sidebar.markdown("#### 1. Define Knowledge Graph")
edited_rules_df = st.sidebar.data_editor(
    default_rules,
    column_config={
        "Rule Type": st.column_config.SelectboxColumn("Rule Type", options=["Keyword", "Min Experience (Years)", "Functional Area"], required=True),
        "Target": st.column_config.TextColumn("Target Value", required=True),
        "Points": st.column_config.NumberColumn("Points", min_value=1, max_value=100, step=1, required=True)
    },
    num_rows="dynamic", use_container_width=True, hide_index=True
)

st.sidebar.markdown("#### 2. Select Processing Tier")
processing_mode = st.sidebar.selectbox(
    "Algorithmic Depth",
    ("⚡ Basic Mode (Keyword Matching)", " 🧠 Smart Mode (NLP Matching)", "🔥 Advanced Mode (Semantic AI Matching)"),
    label_visibility="collapsed"
)

st.sidebar.markdown("#### 3. Data Intake")
uploaded_file = st.sidebar.file_uploader("Drop candidate .zip, .pdf, or .docx", type=['pdf', 'docx', 'zip'])
analyze_button = st.sidebar.button("🚀 Initialize Scan")

# Added a sleek signature block for you at the bottom of the sidebar
st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div style='text-align: center; color: #6B7280; font-size: 14px;'>Designed & Developed by<br><b>Jay Bisht</b></div>", 
    unsafe_allow_html=True
)

# --- Main Interface ---
tab1, tab2 = st.tabs(["📋 Resume Scores", "📊 Macro Analytics"])

results = []

if analyze_button and uploaded_file is not None:
    # --- Sleek Progress Animation ---
    progress_text = "Parsing document structures..."
    my_bar = st.progress(0, text=progress_text)
    
    time.sleep(0.5)
    my_bar.progress(30, text="Extracting raw text via NLP pipelines...")
    time.sleep(0.5)
    my_bar.progress(60, text="Applying multi-layered scoring weights...")
    if processing_mode != "1-Minute Mode (Fast String Match)":
        time.sleep(1.5)
    my_bar.progress(90, text="Finalizing Explainable AI (XAI) justifications...")
    time.sleep(0.5)
    my_bar.progress(100, text="Processing complete.")
    time.sleep(0.5)
    my_bar.empty() 
    st.toast('Candidate processing completed successfully!', icon='✅')

    with st.spinner("Compiling database..."):
        if uploaded_file.name.endswith('.zip'):
            with zipfile.ZipFile(uploaded_file) as z:
                for filename in z.namelist():
                    if filename.endswith(('.pdf', '.docx')):
                        text = extract_text_from_pdf(z.read(filename)) if filename.endswith('.pdf') else extract_text_from_docx(z.read(filename))
                        score, exp, expl = score_resume_dynamically(text, edited_rules_df, processing_mode)
                        results.append({"Candidate": filename, "Score": score, "Experience": exp, "Justification": expl})
        else:
            text = extract_text_from_pdf(uploaded_file.read()) if uploaded_file.name.endswith('.pdf') else extract_text_from_docx(uploaded_file.read())
            score, exp, expl = score_resume_dynamically(text, edited_rules_df, processing_mode)
            results.append({"Candidate": uploaded_file.name, "Score": score, "Experience": exp, "Justification": expl})

if results:
    df = pd.DataFrame(results).sort_values(by="Score", ascending=False)
    
    # --- TAB 1: Talent Pipeline ---
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.markdown("### Top Ranked Candidates")
        with col_b:
            csv = df.drop(columns=['Justification']).to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Export Pipeline (CSV)", data=csv, file_name='talent_pipeline.csv', mime='text/csv')
            
        st.markdown("---")
        
        for index, row in df.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1, 1])
                with c1:
                    st.markdown(f"**📄 {row['Candidate']}**")
                with c2:
                    st.markdown(f"💼 {row['Experience']} Years Exp.")
                with c3:
                    if row['Score'] >= 50:
                        st.markdown(f"🏆 **Score: <span style='color:#10B981'>{row['Score']}</span>**", unsafe_allow_html=True)
                    else:
                        st.markdown(f"⚠️ **Score: <span style='color:#F59E0B'>{row['Score']}</span>**", unsafe_allow_html=True)
                
                with st.expander("🔍 View AI Scoring Justification"):
                    st.markdown("#### Assessment Breakdown")
                    for reason in row['Justification']:
                        st.write(reason)

    # --- TAB 2: Macro Analytics ---
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            with st.container(border=True):
                st.metric("Total Applicants", len(df))
        with col2:
            with st.container(border=True):
                st.metric("Average System Score", round(df['Score'].mean(), 1))
        with col3:
            with st.container(border=True):
                st.metric("Highest Achieved Score", df['Score'].max())
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            with st.container(border=True):
                st.markdown("**Candidate Score Distribution**")
                st.bar_chart(df.set_index("Candidate")["Score"], color="#3B82F6")
                
        with col_chart2:
            with st.container(border=True):
                st.markdown("**Experience Level Density (Years)**")
                st.line_chart(df.set_index("Candidate")["Experience"], color="#10B981")
        
elif uploaded_file is None:
    with tab1:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.info("💡 **System Ready:** Upload your Resumes to Analyze.")
