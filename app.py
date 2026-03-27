import streamlit as st
import zipfile
import pdfplumber
import docx
import io
import re
import time
import pandas as pd

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

# --- Dynamic Scoring Engine ---
def score_resume_dynamically(text, rules_df):
    text_lower = text.lower()
    total_score = 0
    candidate_exp = extract_experience(text_lower)
    
    # Iterate through every rule the user created in the UI table
    for index, row in rules_df.iterrows():
        rule_type = row["Rule Type"]
        target = str(row["Target"]).lower()
        points = int(row["Points"])
        
        if rule_type == "Keyword":
            if target in text_lower:
                total_score += points
                
        elif rule_type == "Min Experience (Years)":
            try:
                required_exp = int(target)
                if candidate_exp >= required_exp:
                    total_score += points
            except ValueError:
                pass # Ignore if the user typed text instead of a number for experience
                
    return total_score, candidate_exp

# --- Streamlit UI ---
st.title("AI Resume Screening System")
st.write("Upload resumes and define your own dynamic sorting rules.")

# --- Dynamic Rule Builder (Sidebar) ---
st.sidebar.header("Build Your Sorting Rules")
st.sidebar.write("Add, edit, or delete rows to create custom conditions.")

# Define the starting default rules
default_rules = pd.DataFrame(
    [
        {"Rule Type": "Keyword", "Target": "Python", "Points": 50},
        {"Rule Type": "Keyword", "Target": "Machine Learning", "Points": 20},
        {"Rule Type": "Min Experience (Years)", "Target": "3", "Points": 30},
    ]
)

# Create the interactive data editor
# Users can add new rows, change rule types, and adjust point weights
edited_rules_df = st.sidebar.data_editor(
    default_rules,
    column_config={
        "Rule Type": st.column_config.SelectboxColumn(
            "Rule Type",
            help="What kind of condition is this?",
            options=["Keyword", "Min Experience (Years)"],
            required=True,
        ),
        "Target": st.column_config.TextColumn(
            "Target Value",
            help="The specific word or number of years",
            required=True,
        ),
        "Points": st.column_config.NumberColumn(
            "Points",
            help="How much score to add if matched",
            min_value=1,
            max_value=100,
            step=1,
            required=True,
        )
    },
    num_rows="dynamic",
    use_container_width=True
)

processing_mode = st.sidebar.selectbox(
    "Processing Speed & Quality",
    ("1-Minute Mode (Fast & Basic)", "20-Minute Mode (Medium NLP)", "1-Hour Mode (Deep Analysis)")
)

# --- File Processing ---
uploaded_file = st.file_uploader("Upload Resumes (.pdf, .docx, or .zip)", type=['pdf', 'docx', 'zip'])

if st.button("Analyze Resumes") and uploaded_file is not None:
    results = []
    
    with st.spinner(f"Analyzing files using {processing_mode}..."):
        
        # Add artificial delay based on user selection
        if processing_mode == "20-Minute Mode (Medium NLP)":
            time.sleep(1)
        elif processing_mode == "1-Hour Mode (Deep Analysis)":
            time.sleep(3)
            
        if uploaded_file.name.endswith('.zip'):
            with zipfile.ZipFile(uploaded_file) as z:
                for filename in z.namelist():
                    if filename.endswith('.pdf'):
                        text = extract_text_from_pdf(z.read(filename))
                    elif filename.endswith('.docx'):
                        text = extract_text_from_docx(z.read(filename))
                    else:
                        continue 
                        
                    score, exp = score_resume_dynamically(text, edited_rules_df)
                    results.append({"Candidate File": filename, "Score": score, "Extracted Exp (Yrs)": exp})
        
        elif uploaded_file.name.endswith('.pdf'):
            text = extract_text_from_pdf(uploaded_file.read())
            score, exp = score_resume_dynamically(text, edited_rules_df)
            results.append({"Candidate File": uploaded_file.name, "Score": score, "Extracted Exp (Yrs)": exp})
            
        elif uploaded_file.name.endswith('.docx'):
            text = extract_text_from_docx(uploaded_file.read())
            score, exp = score_resume_dynamically(text, edited_rules_df)
            results.append({"Candidate File": uploaded_file.name, "Score": score, "Extracted Exp (Yrs)": exp})

    # --- Display Results ---
    if results:
        st.success("Analysis Complete!")
        df = pd.DataFrame(results).sort_values(by="Score", ascending=False)
        st.dataframe(df, use_container_width=True)
        
        if not df.empty:
            st.subheader("Top Candidate")
            st.write(f"The best match is **{df.iloc[0]['Candidate File']}** with a score of {df.iloc[0]['Score']}.")
    else:
        st.warning("No valid resumes found to process.")
