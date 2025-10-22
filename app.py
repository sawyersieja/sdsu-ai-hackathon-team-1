import streamlit as st
import boto3
from typing import List, Dict, Any
import pypdf
import docx


st.set_page_config(
    page_title="AI Chatbot", 
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sample data for dropdowns
STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", 
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", 
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", 
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", 
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", 
    "New Hampshire", "New Jersey", "New Mexico", "New York", 
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", 
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", 
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", 
    "West Virginia", "Wisconsin", "Wyoming"
]

GRADE_LEVELS = [
    "Kindergarten", "1st Grade", "2nd Grade", "3rd Grade", 
    "4th Grade", "5th Grade", "6th Grade", "7th Grade", "8th Grade", 
    "9th Grade", "10th Grade", "11th Grade", "12th Grade"
]

SUBJECTS = [
    "Asian American Studies"
]

def extract_text_from_pdf(file) -> str:
    """Extract text from PDF file"""
    try:
        pdf_reader = pypdf.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""

def extract_text_from_docx(file) -> str:
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading DOCX: {str(e)}")
        return ""

def extract_text_from_txt(file) -> str:
    """Extract text from TXT file"""
    try:
        return str(file.read(), "utf-8")
    except Exception as e:
        st.error(f"Error reading TXT: {str(e)}")
        return ""

def process_uploaded_file(uploaded_file) -> str:
    """Process uploaded file and extract text"""
    file_type = uploaded_file.type
    
    if file_type == "application/pdf":
        return extract_text_from_pdf(uploaded_file)
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(uploaded_file)
    elif file_type == "text/plain":
        return extract_text_from_txt(uploaded_file)
    else:
        st.error(f"Unsupported file type: {file_type}")
        return ""

st.title("🤖 Simple AI Chatbot")
st.write("Chat with an AI using AWS Bedrock!")

# Sidebar for filters
with st.sidebar:
    st.header("📄 Document Upload")
    
    uploaded_files = st.file_uploader(
        "Upload documents",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True,
        help="Upload PDF, DOCX, or TXT files to provide context to the AI"
    )
    
    # Process uploaded files
    if uploaded_files:
        if "uploaded_documents" not in st.session_state:
            st.session_state.uploaded_documents = {}
        
        for uploaded_file in uploaded_files:
            if uploaded_file.name not in st.session_state.uploaded_documents:
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    text_content = process_uploaded_file(uploaded_file)
                    if text_content:
                        st.session_state.uploaded_documents[uploaded_file.name] = {
                            "content": text_content,
                            "size": len(text_content)
                        }
                        st.success(f"✅ {uploaded_file.name} processed successfully")
    
    # Display uploaded documents
    if "uploaded_documents" in st.session_state and st.session_state.uploaded_documents:
        st.header("📚 Uploaded Documents")
        for doc_name, doc_info in st.session_state.uploaded_documents.items():
            with st.expander(f"📄 {doc_name} ({doc_info['size']} chars)"):
                st.text_area("Content preview:", doc_info["content"][:500] + "..." if len(doc_info["content"]) > 500 else doc_info["content"], height=100, disabled=True)
                if st.button(f"🗑️ Remove {doc_name}", key=f"remove_{doc_name}"):
                    del st.session_state.uploaded_documents[doc_name]
                    st.rerun()
    
    st.header("🔍 Context Filters")
    
    selected_states = st.multiselect("Select States", STATES, default=[])
    selected_grade = st.selectbox("Select Grade Level", ["All Grades"] + GRADE_LEVELS)
    selected_subject = st.selectbox("Select Subject", ["All Subjects"] + SUBJECTS)
    
    st.header("⚙️ Settings")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("Clear All Documents"):
        if "uploaded_documents" in st.session_state:
            st.session_state.uploaded_documents = {}
        st.rerun()

@st.cache_resource
def get_bedrock_client() -> Any:
  return boto3.client('bedrock-runtime', region_name='us-west-2')

def invoke_model(messages: List[Dict[str, str]], context: Dict[str, str] = None) -> str:
  client = get_bedrock_client()

  # Add context information to the system message
  system_message = "You are a helpful AI assistant."
  if context:
    context_parts = []
    if context.get("states") and len(context["states"]) > 0:
      states_str = ", ".join(context["states"])
      context_parts.append(f"States: {states_str}")
    if context.get("grade") and context["grade"] != "All Grades":
      context_parts.append(f"Grade Level: {context['grade']}")
    if context.get("subject") and context["subject"] != "All Subjects":
      context_parts.append(f"Subject: {context['subject']}")
    
    # Add document content if available
    if context.get("documents") and len(context["documents"]) > 0:
      doc_context = "\n\n".join([f"Document '{name}':\n{content}" for name, content in context["documents"].items()])
      context_parts.append(f"Uploaded Documents:\n{doc_context}")
    
    if context_parts:
      system_message += f" Context: {', '.join(context_parts)}."

  bedrock_messages: List[Dict[str, Any]] = [
    {
      "role": "user",
      "content": [{"text": system_message}]
    }
  ]
  
  for msg in messages:
    bedrock_messages.append({
      "role": msg["role"],
      "content": [{"text": msg["content"]}]
    })

  try:
    response = client.converse(
      modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
      messages=bedrock_messages,
      inferenceConfig={
        "maxTokens": 1000,
      }
    )

    return response['output']['message']['content'][0]['text']

  except Exception as e:
    return f"Sorry, I encountered an error: {str(e)}"

if "messages" not in st.session_state:
  st.session_state.messages = []

for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.write(message["content"])

if prompt := st.chat_input("Type your message here..."):
  st.session_state.messages.append({"role": "user", "content": prompt})
  
  with st.chat_message("user"):
    st.write(prompt)
  
  with st.chat_message("assistant"):
    with st.spinner("Thinking..."):
      # Pass filter context to the AI model
      context = {
        "states": selected_states,
        "grade": selected_grade,
        "subject": selected_subject
      }
      
      # Add document content if available
      if "uploaded_documents" in st.session_state and st.session_state.uploaded_documents:
        context["documents"] = {name: doc_info["content"] for name, doc_info in st.session_state.uploaded_documents.items()}
      response = invoke_model(st.session_state.messages, context)
  
  st.session_state.messages.append({"role": "assistant", "content": response})
  st.rerun() # refresh the app to show the new message 
             # updating session state does not automatically refresh the UI
