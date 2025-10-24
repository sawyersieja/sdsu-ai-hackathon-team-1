import streamlit as st
import boto3
from typing import List, Dict, Any
import os
import pypdf
import docx

# Load environment variables

st.set_page_config(
    page_title="AI Chatbot", 
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sample data for dropdowns
STATES = [
    "California", "New York"
]

GRADE_LEVELS = [
    "Kindergarten", "1st Grade", "2nd Grade", "3rd Grade", 
    "4th Grade", "5th Grade", "6th Grade", "7th Grade", "8th Grade", 
    "9th Grade", "10th Grade", "11th Grade", "12th Grade"
]

SUBJECTS = [
    "English", "Social Studies", "U.S. History", "World History", "Other"
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
def get_rag_client() -> Any:
  """Client for RAG (Knowledge Base) operations"""
  return boto3.client(
    'bedrock-agent-runtime',
    region_name=os.getenv('AWS_DEFAULT_REGION', 'us-west-2')
  )

@st.cache_resource
def get_bedrock_client() -> Any:
  """Client for regular Bedrock LLM operations"""
  return boto3.client(
    'bedrock-runtime',
    region_name=os.getenv('AWS_DEFAULT_REGION', 'us-west-2')
  )

def invoke_model(messages: List[Dict[str, str]], context: Dict[str, str] = None) -> str:
  # Get the latest user message
  user_message = messages[-1]["content"] if messages else ""
  
  # Build filter context (for RAG stage)
  filter_context_parts = []
  if context:
    if context.get("states") and len(context["states"]) > 0:
      states_str = ", ".join(context["states"])
      filter_context_parts.append(f"States: {states_str}")
    if context.get("grade") and context["grade"] != "All Grades":
      filter_context_parts.append(f"Grade Level: {context['grade']}")
    if context.get("subject") and context["subject"] != "All Subjects":
      filter_context_parts.append(f"Subject: {context['subject']}")
  
  # STAGE 1: Get RAG response from Knowledge Base
  rag_response = ""
  try:
    rag_client = get_rag_client()
    
    # Build RAG input with filters only
    rag_input = "You are a helpful assistant. Always respond in clear, concise sentences. When you use information from the knowledge base, cite it at the end."
    
    if filter_context_parts:
      rag_input += f"\n\nContext: {', '.join(filter_context_parts)}."
    
    rag_input += f"\n\nUser question: {user_message}"
    
    # Call RAG model
    rag_response_obj = rag_client.retrieve_and_generate(
      input={'text': rag_input},
      retrieveAndGenerateConfiguration={
        'type': 'KNOWLEDGE_BASE',
        'knowledgeBaseConfiguration': {
          'knowledgeBaseId': os.getenv('KNOWLEDGE_BASE_ID'),
          'modelArn': f'arn:aws:bedrock:{os.getenv("AWS_DEFAULT_REGION", "us-west-2")}::foundation-model/{os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")}'
        }
      }
    )
    
    rag_response = rag_response_obj['output']['text']
    
  except Exception as e:
    rag_response = f"RAG model encountered an error: {str(e)}"
  
  # STAGE 2: Use regular Bedrock LLM to synthesize RAG response with uploaded documents
  try:
    bedrock_client = get_bedrock_client()
    
    # Build comprehensive context for regular LLM
    synthesis_prompt = f"""You are a helpful assistant that synthesizes information from multiple sources.

RAG Model Response (from Knowledge Base):
{rag_response}

User's Question: {user_message}

Filter Context: {', '.join(filter_context_parts) if filter_context_parts else 'No specific filters applied'}

Please provide a comprehensive response that:
1. Incorporates the RAG model's response
2. Compares and synthesizes it with any uploaded documents (if provided)
3. Maintains the filter context (states, grade level, subject)
4. Provides a well-structured, helpful answer

If there are uploaded documents, please analyze them in relation to the RAG response and user question."""

    # Add uploaded documents if available
    if context and context.get("documents") and len(context["documents"]) > 0:
      synthesis_prompt += "\n\nUploaded Documents:\n"
      for name, content in context["documents"].items():
        synthesis_prompt += f"\n--- Document: {name} ---\n{content}\n"
    
    # Call regular Bedrock LLM
    bedrock_messages = [
      {
        "role": "user",
        "content": [{"text": synthesis_prompt}]
      }
    ]
    
    response = bedrock_client.converse(
      modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
      messages=bedrock_messages,
      inferenceConfig={
        "maxTokens": 2000,
      }
    )
    
    return response['output']['message']['content'][0]['text']

  except Exception as e:
    return f"Sorry, I encountered an error in the synthesis stage: {str(e)}"

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
