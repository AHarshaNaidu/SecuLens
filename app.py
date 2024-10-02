import streamlit as st
import pandas as pd
from groq import Groq

# Setup API key for Groqcloud
api_key = st.secrets["api_key"]
client = Groq(api_key=api_key)

# Define the prompt templates
preprocess_prompt_template = """
You are an AI assistant specialized in cybersecurity audits.
Analyze the given cybersecurity audit report and provide a detailed summary.
Identify key findings, vulnerabilities, recommendations, and areas of concern.
Ensure the summary includes a clear explanation of each identified item and its importance for security.

### Example Format:
- **Key Findings**:
  - [Description of key findings]
- **Vulnerabilities**:
  - [Description of vulnerabilities]
- **Recommendations**:
  - [Description of recommendations]
- **Other Security Concerns**:
  - [Description of other concerns]
"""

decision_support_prompt_template = """
You are an AI assistant specialized in cybersecurity audit analysis.
Answer the user's question based on the following audit report summary and provide actionable insights.

### Audit Report Summary:
{audit_summary}

### User's Question:
{user_question}
"""

# Function to call the Groq API
def call_llm_api(prompt_template, user_content):
    data = {
        "model": "llama3-groq-70b-8192-tool-use-preview",
        "messages": [
            {"role": "system", "content": prompt_template},
            {"role": "user", "content": user_content}
        ]
    }
    response = client.chat.completions.create(**data)
    return response.choices[0].message.content

# Streamlit interface
st.set_page_config(page_title="SecuLens 🔍", page_icon="🛡️")
st.title("🛡️SecuLens🔍")

# Sidebar title
st.sidebar.title("🛡️SecuLens🔍")

# Initialize session state variables
if 'audit_summary' not in st.session_state:
    st.session_state['audit_summary'] = None
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Step 1: Upload and Analyze Cybersecurity Audit
def analyze_audit():
    st.header('Step 1: Upload and Analyze Cybersecurity Audit Report')

    uploaded_file = st.file_uploader("Upload your audit report (PDF, DOCX, etc.)", type=["pdf", "docx", "txt"])

    if uploaded_file:
        st.write("Uploaded file:", uploaded_file.name)

        if st.button('Analyze Report'):
            with st.spinner("Analyzing..."):
                # For simplicity, we'll use dummy content for the uploaded file
                file_content = "Sample cybersecurity audit content"  # Replace with actual file reading logic

                analysis_prompt = f"Analyze this cybersecurity audit:\n{file_content}"
                audit_summary = call_llm_api(preprocess_prompt_template, analysis_prompt)

                st.session_state['audit_summary'] = audit_summary

            st.write("### Audit Summary:")
            st.write(st.session_state['audit_summary'])

            return st.session_state['audit_summary']

# Step 2: Chat-based Decision Support
def decision_chat():
    st.header('Step 2: Chat-based Decision Support')

    if st.session_state['audit_summary']:
        st.write("### Audit Summary from Step 1:")
        st.write(st.session_state['audit_summary'])

        # Chat interface
        user_question = st.text_input("Ask a decision-related question about the audit:")
        if user_question:
            with st.spinner("Generating answer..."):
                # Combine audit summary and user question for the prompt
                decision_prompt = decision_support_prompt_template.format(
                    audit_summary=st.session_state['audit_summary'],
                    user_question=user_question
                )
                ai_response = call_llm_api(decision_support_prompt_template, decision_prompt)

                # Add user question and AI response to chat history
                st.session_state['chat_history'].append({"question": user_question, "answer": ai_response})

        # Display chat history
        for chat in st.session_state['chat_history']:
            st.write(f"**You:** {chat['question']}")
            st.write(f"**AI:** {chat['answer']}")

# Main function to integrate steps
def main():
    step = st.sidebar.radio("Select Step", ["Step 1: Analyze Audit Report", "Step 2: Chat-based Decision Support"])

    if step == "Step 1: Analyze Audit Report":
        analyze_audit()
    elif step == "Step 2: Chat-based Decision Support":
        if st.session_state['audit_summary'] is None:
            st.warning("Please complete Step 1: Analyze Audit Report first.")
        else:
            decision_chat()

if __name__ == '__main__':
    main()
