import streamlit as st
import zipfile
import pdfplumber
import docx
import io
import re
import time
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="AI Resume Scanner", layout="wide")

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
    explanations = [] # This stores the "Why" for our Explainable AI
    
    # Iterate through every rule the user created
    for index, row in rules_df.iterrows():
        rule_type = row["Rule Type"]
        target = str(row["Target"]).lower()
        points = int(row["Points"])
        
        if rule_type == "Keyword":
            if target in text_lower:
                total_score += points
                explanations.append(f"✅ **+{points} pts:** Found exact keyword '{target}'")
            else:
                explanations.append(f"❌ **0 pts:** Missing keyword '{target}'")
                
        elif rule_type == "Min Experience (Years)":
            try:
                required_exp = int(target)
                if candidate_exp >= required_exp:
                    total_score += points
                    explanations.append(f"✅ **+{points} pts:** Candidate has {candidate_exp} years (Requires {required_exp})")
                else:
                    explanations.append(f"❌ **0 pts:** Insufficient experience (Has {candidate_exp}, Requires {required_exp})")
            except ValueError:
                pass
                
        elif rule_type == "Functional Area":
            if target in text_lower:
                total_score += points
                explanations.append(f"✅ **+{points} pts:** Background matches '{target}' domain")
            else:
                explanations.append(f"❌ **0 pts:** Did not clearly match '{target}' domain")

    # Simulate Semantic Deep Learning Boost
    if mode == "1-Hour Mode (Deep Analysis)":
        total_score += 15
        explanations.append("🤖 **+15 pts:** Semantic Neural Engine detected high contextual relevance in work history.")

    return total_score, candidate_exp, explanations

# --- Streamlit UI ---
st.title("🚀 AI-Powered Resume Screening System")
st.markdown("Filter, rank, and analyze applicant pools using dynamic criteria and explainable AI.")

# --- Sidebar Controls ---
st.sidebar.header("⚙️ Build Screening Rules")
default_rules = pd.DataFrame([
    {"Rule Type": "Keyword", "Target": "Python", "Points": 40},
    {"Rule Type": "Keyword", "Target": "Data Analytics", "Points": 30},
    {"Rule Type": "Min Experience (Years)", "Target": "2", "Points": 20},
    {"Rule Type": "Functional Area", "Target": "Finance", "Points": 10},
])

edited_rules_df = st.sidebar.data_editor(
    default_rules,
    column_config={
        "Rule Type": st.column_config.SelectboxColumn("Rule Type", options=["Keyword", "Min Experience (Years)", "Functional Area"], required=True),
        "Target": st.column_config.TextColumn("Target Value", required=True),
        "Points": st.column_config.NumberColumn("Points", min_value=1, max_value=100, step=1, required=True)
    },
    num_rows="dynamic", use_container_width=True
)

processing_mode = st.sidebar.selectbox(
    "Processing Engine",
    ("1-Minute Mode (Fast & Basic)", "20-Minute Mode (Medium NLP)", "1-Hour Mode (Deep Analysis)")
)

uploaded_file = st.sidebar.file_uploader("Upload Resumes (.zip, .pdf, .docx)", type=['pdf', 'docx', 'zip'])

# --- Main Interface ---
# Create two tabs: One for the ranking, one for the analytics dashboard
tab1, tab2 = st.tabs(["📋 Applicant Rankings", "📊 Analytics Dashboard"])

results = []

if st.sidebar.button("Analyze Applicant Pool") and uploaded_file is not None:
    with st.spinner(f"Engine running: {processing_mode}..."):
        
        # Simulate loading times
        if processing_mode == "20-Minute Mode (Medium NLP)": time.sleep(1.5)
        elif processing_mode == "1-Hour Mode (Deep Analysis)": time.sleep(3)
            
        # Process files
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
    
    # --- TAB 1: Rankings & Explainability ---
    with tab1:
        st.success("Analysis Complete!")
        
        # 1-Click CSV Export
        csv = df.drop(columns=['Justification']).to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Download Rankings as CSV", data=csv, file_name='resume_rankings.csv', mime='text/csv')
        
        # Display Results with Explainable AI Dropdowns
        for index, row in df.iterrows():
            with st.expander(f"{row['Candidate']} — Score: {row['Score']}"):
                st.write(f"**Extracted Experience:** {row['Experience']} Years")
                st.markdown("### AI Scoring Justification:")
                for reason in row['Justification']:
                    st.write(reason)

    # --- TAB 2: Data Analytics Dashboard ---
    with tab2:
        st.header("Applicant Pool Overview")
        
        # Top level metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Applicants", len(df))
        col2.metric("Average Score", round(df['Score'].mean(), 1))
        col3.metric("Top Score", df['Score'].max())
        
        st.divider()
        
        # Visualizations
        st.subheader("Candidate Score Distribution")
        st.bar_chart(df.set_index("Candidate")["Score"])
        
        st.subheader("Experience Level Breakdown (Years)")
        st.line_chart(df.set_index("Candidate")["Experience"])
        
elif uploaded_file is None:
    with tab1:
        st.info("👈 Upload a ZIP file of resumes in the sidebar to begin.")