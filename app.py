import streamlit as st
import boto3
from typing import List, Dict, Any
import os
import pypdf
import docx

# Load environment variables from .env file
#load_dotenv()

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
    "English", "Social Studies", "U.S. History", "World History"
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
    
    # Pipeline Execution History
    st.subheader("📊 Pipeline History")
    if "pipeline_logs" in st.session_state and st.session_state.pipeline_logs:
        for i, log in enumerate(reversed(st.session_state.pipeline_logs[-3:])):  # Show last 3
            with st.expander(f"Execution #{len(st.session_state.pipeline_logs) - i} - {log['timestamp']}", expanded=(i==0)):
                for stage_info in log["stages"]:
                    if stage_info["type"] == "info":
                        st.info(f"{stage_info['stage']}: {stage_info['status']}")
                    elif stage_info["type"] == "success":
                        st.success(f"{stage_info['stage']}: {stage_info['status']}")
                
                if log["documents_count"] > 0:
                    st.info(f"📄 {log['documents_count']} documents processed")
                
                # Show a preview of the response
                if "response" in log:
                    response_preview = log["response"][:200] + "..." if len(log["response"]) > 200 else log["response"]
                    st.text_area("Response Preview", response_preview, height=100, disabled=True)
    else:
        st.info("No pipeline executions yet")

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

  # Build filter context
  filter_context_parts = []
  if context:
    if context.get("states") and len(context["states"]) > 0:
      states_str = ", ".join(context["states"])
      filter_context_parts.append(f"States: {states_str}")
    if context.get("grade") and context["grade"] != "All Grades":
      filter_context_parts.append(f"Grade Level: {context['grade']}")
    if context.get("subject") and context["subject"] != "All Subjects":
      filter_context_parts.append(f"Subject: {context['subject']}")
  
  st.info("🚀 **STARTING PARALLEL PROCESSING** - Two paths: State Requirements & RAG Knowledge Base")
  
  # PATH 1: State Requirements PDF → LLM
  state_requirements_response = ""
  if context and context.get("documents"):
    st.info("📄 **PATH 1: STATE REQUIREMENTS ANALYSIS** - Processing uploaded PDF...")
    try:
      bedrock_client = get_bedrock_client()
      
      # Process each uploaded document (state requirements)
      for name, content in context["documents"].items():
        state_prompt = f"""Analyze the following state requirements document and provide feedback on how it relates to the user's question.

DOCUMENT: {name}
CONTENT: {content}

USER QUESTION: {user_message}
FILTER CONTEXT: {', '.join(filter_context_parts) if filter_context_parts else 'No specific filters'}

Please provide:
1. Key requirements from the document
2. How these requirements relate to the user's question
3. Specific feedback on alignment or gaps
4. Recommendations based on the state requirements

Focus on being specific and citing exact requirements from the document."""

        state_messages = [{"role": "user", "content": [{"text": state_prompt}]}]
        
        state_response = bedrock_client.converse(
          modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
          messages=state_messages,
          inferenceConfig={"maxTokens": 1500}
        )
        
        state_requirements_response += f"\n\n--- ANALYSIS OF {name} ---\n"
        state_requirements_response += state_response['output']['message']['content'][0]['text']
      
      st.success("✅ **PATH 1 COMPLETE** - State requirements analyzed")
      
    except Exception as e:
      state_requirements_response = f"Error analyzing state requirements: {str(e)}"
      st.error(f"❌ **PATH 1 ERROR** - {str(e)}")
  
  # PATH 2: User Prompt → RAG → Knowledge Base → LLM
  st.info("🔍 **PATH 2: RAG KNOWLEDGE BASE SEARCH** - Searching for matches...")
  
  knowledge_base_matches = {}
  knowledge_base_response = ""
  try:
    rag_client = get_rag_client()
    bedrock_client = get_bedrock_client()
    
    # Use RAG to retrieve relevant documents from knowledge base
    retrieval_response = rag_client.retrieve(
      knowledgeBaseId=os.getenv('KNOWLEDGE_BASE_ID'),
      retrievalQuery={'text': user_message},
      retrievalConfiguration={
        'vectorSearchConfiguration': {
          'numberOfResults': 5
        }
      }
    )
    
    # Extract retrieved documents and create key-value pairs
    retrieved_docs = retrieval_response.get('retrievalResults', [])
    
    for i, doc in enumerate(retrieved_docs):
      # Extract comprehensive source information
      metadata = doc.get('metadata', {})
      source = metadata.get('source', 'Knowledge Base Document')
      location = metadata.get('location', '')
      
      # Try to extract more detailed information from various possible fields
      title = metadata.get('title', '') or metadata.get('name', '') or metadata.get('document_title', '')
      
      # Look for URLs in multiple possible fields (including AWS Bedrock specific fields)
      url = ''
      possible_url_fields = ['x-amz-bedrock-kb-source-uri', 'url', 'source', 'uri', 'link', 'href', 'web_url', 'document_uri', 'file_uri', 'source_uri']
      for field in possible_url_fields:
        if field in metadata and metadata[field] and 'http' in str(metadata[field]):
          url = metadata[field]
          break
      
      page = metadata.get('page', '') or metadata.get('page_number', '')
      section = metadata.get('section', '') or metadata.get('chapter', '')
      
      # Create a more descriptive source name
      if title:
        source_name = title
      elif url:
        source_name = url.split('/')[-1] if '/' in url else url
      elif source and source != 'Knowledge Base Document':
        source_name = source
      else:
        # Try to extract meaningful info from content
        content_preview = doc['content']['text'][:100].replace('\n', ' ')
        if 'Filipino' in content_preview:
          source_name = f"Filipino Immigration Source {i+1}"
        elif 'Asian' in content_preview:
          source_name = f"Asian American History Source {i+1}"
        elif 'immigration' in content_preview.lower():
          source_name = f"Immigration History Source {i+1}"
        else:
          source_name = f"Knowledge Base Document {i+1}"
      
      # Create detailed citation info
      citation_info = {
        'source': source_name,
        'original_source': source,
        'location': location,
        'url': url,
        'page': page,
        'section': section,
        'content': doc['content']['text'],
        'match_number': i + 1,
        'metadata': metadata
      }
      
      key = f"Match {i+1}: {source_name}"
      knowledge_base_matches[key] = citation_info
    
    st.success(f"📚 **PATH 2 RETRIEVAL COMPLETE** - Found {len(retrieved_docs)} matches from knowledge base")
    
    # Debug: Show ALL metadata information
    if retrieved_docs:
      st.info("🔍 **DEBUG: Complete Knowledge Base Metadata**")
      for i, doc in enumerate(retrieved_docs[:3]):  # Show first 3 for debugging
        metadata = doc.get('metadata', {})
        
        # Show ALL metadata fields
        st.markdown(f"**Document {i+1} Complete Metadata:**")
        for key, value in metadata.items():
          st.text(f"  {key}: {value}")
        
        # Check for URLs in various possible fields (including AWS Bedrock specific fields)
        url_found = False
        possible_url_fields = ['x-amz-bedrock-kb-source-uri', 'url', 'source', 'uri', 'link', 'href', 'web_url', 'document_uri', 'file_uri']
        
        for field in possible_url_fields:
          if field in metadata and metadata[field]:
            if 'http' in str(metadata[field]):
              st.success(f"✅ Document {i+1} has URL in '{field}': {metadata[field]}")
              url_found = True
              break
        
        if not url_found:
          st.warning(f"⚠️ Document {i+1} has no URL in any metadata field")
          st.text(f"Available fields: {list(metadata.keys())}")
        
        st.markdown("---")
    
    # Send matches to LLM for feedback
    if knowledge_base_matches:
      st.info("🤖 **PATH 2: LLM FEEDBACK** - Processing knowledge base matches...")
      
      # Format matches with citation information
      matches_text = ""
      citations_list = []
      
      for key, citation_info in knowledge_base_matches.items():
        matches_text += f"{key}:\nSource: {citation_info['source']}\nLocation: {citation_info['location']}\nURL: {citation_info['url']}\nContent: {citation_info['content']}\n\n"
        
        # Create clickable citation with URL if available
        if citation_info['url']:
          citations_list.append(f"[{citation_info['match_number']}] {citation_info['source']} - {citation_info['location']} | URL: {citation_info['url']}")
        else:
          citations_list.append(f"[{citation_info['match_number']}] {citation_info['source']} - {citation_info['location']}")
      
      knowledge_prompt = f"""Based on the following matches from our knowledge base, provide feedback on the user's question.

USER QUESTION: {user_message}
FILTER CONTEXT: {', '.join(filter_context_parts) if filter_context_parts else 'No specific filters'}

KNOWLEDGE BASE MATCHES:
{matches_text}

Please provide:
1. Specific feedback using the knowledge base content
2. Quote relevant sections with proper citations (use format: "Quote text" [Citation #])
3. Explain how the matches relate to the user's question
4. Highlight key insights from the knowledge base

CITATION FORMAT: When quoting, use this format: "Exact quote text" [1] where the number refers to the citation list below.

CITATIONS:
{chr(10).join(citations_list)}

CRITICAL: Always provide proper citations with [number] format when referencing knowledge base content."""

      knowledge_messages = [{"role": "user", "content": [{"text": knowledge_prompt}]}]
      
      knowledge_response = bedrock_client.converse(
        modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        messages=knowledge_messages,
        inferenceConfig={"maxTokens": 1500}
      )
      
      knowledge_base_response = knowledge_response['output']['message']['content'][0]['text']
      st.success("✅ **PATH 2 COMPLETE** - Knowledge base matches processed")

  except Exception as e:
    knowledge_base_response = f"Error processing knowledge base: {str(e)}"
    st.error(f"❌ **PATH 2 ERROR** - {str(e)}")
  
  # COMBINE BOTH RESPONSES
  st.info("🔄 **COMBINING RESPONSES** - Merging both analyses...")
  
  # Create citations section if we have knowledge base matches
  citations_section = ""
  if knowledge_base_matches:
    citations_section = "\n\n## 📚 CITATIONS\n"
    citations_section += "*Sources retrieved from AWS Bedrock Knowledge Base*\n\n"
    
    # Add debug information about metadata
    citations_section += "\n### 🔍 **METADATA DEBUG INFO**\n"
    citations_section += "*This shows what metadata fields are available in your knowledge base*\n\n"
    
    for i, citation_info in enumerate(knowledge_base_matches.values()):
      citations_section += f"**Document {i+1} Metadata Fields:**\n"
      metadata = citation_info.get('metadata', {})
      for key, value in metadata.items():
        citations_section += f"  - {key}: {value}\n"
      citations_section += "\n"
    
    citations_section += "### 📖 **CITATIONS**\n\n"
    
    for citation_info in knowledge_base_matches.values():
      if citation_info['url'] and citation_info['url'].startswith('http'):
        # Create clickable hyperlink
        citations_section += f"[{citation_info['match_number']}] [{citation_info['source']}]({citation_info['url']})\n\n"
      else:
        # Provide more context for knowledge base sources
        content_preview = citation_info['content'][:150].replace('\n', ' ')
        citations_section += f"[{citation_info['match_number']}] {citation_info['source']}\n   📄 Content Preview: {content_preview}...\n   ⚠️ *No URL available in knowledge base metadata*\n\n"
  
  final_response = f"""# ANALYSIS RESULTS

## 📄 STATE REQUIREMENTS ANALYSIS
{state_requirements_response if state_requirements_response else "No state requirements documents provided."}

## 🗄️ KNOWLEDGE BASE ANALYSIS  
{knowledge_base_response if knowledge_base_response else "No knowledge base matches found."}

## 🎯 SUMMARY
Based on both the state requirements and knowledge base analysis, here are the key findings and recommendations for your question: "{user_message}"
{citations_section}
"""
  
  st.success("✅ **FINAL RESPONSE GENERATED** - Both paths completed successfully")
  
  return final_response

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
    # Store pipeline logs in session state for persistence
    if "pipeline_logs" not in st.session_state:
      st.session_state.pipeline_logs = []
    
    # Pass filter context to the AI model
    context = {
      "states": selected_states,
      "grade": selected_grade,
      "subject": selected_subject
    }
    
    # Add document content if available
    if "uploaded_documents" in st.session_state and st.session_state.uploaded_documents:
      context["documents"] = {name: doc_info["content"] for name, doc_info in st.session_state.uploaded_documents.items()}
    
    # Add pipeline logs for this interaction
    pipeline_log = {
      "timestamp": "Just now",
      "stages": [
        {"stage": "🔄 STAGE 1: INPUT PROCESSING", "status": "✅ Input received and context prepared", "type": "info"},
        {"stage": "📄 PATH 1: STATE REQUIREMENTS", "status": "🚀 Processing uploaded PDF with LLM", "type": "info"},
        {"stage": "🔍 PATH 2: RAG KNOWLEDGE BASE", "status": "🚀 Searching knowledge base for matches", "type": "info"},
        {"stage": "🤖 PATH 2: LLM FEEDBACK", "status": "🚀 Processing knowledge base matches", "type": "info"},
        {"stage": "🔄 COMBINING RESPONSES", "status": "🚀 Merging both analyses", "type": "info"},
        {"stage": "📤 FINAL OUTPUT", "status": "✅ Response generated with proper attribution", "type": "success"}
      ],
      "documents_count": len(context.get("documents", {}))
    }
    
    with st.spinner("🔍 Querying knowledge base with filters..."):
      final_response = invoke_model(st.session_state.messages, context)
    
    # Add the response to pipeline log
    pipeline_log["response"] = final_response
    st.session_state.pipeline_logs.append(pipeline_log)
    
    # Display persistent pipeline logs
    st.markdown("### 📊 **PIPELINE EXECUTION LOG**")
    
    # Show the most recent pipeline execution
    if st.session_state.pipeline_logs:
      latest_log = st.session_state.pipeline_logs[-1]
      
      for stage_info in latest_log["stages"]:
        if stage_info["type"] == "info":
          st.info(f"{stage_info['stage']}: {stage_info['status']}")
        elif stage_info["type"] == "success":
          st.success(f"{stage_info['stage']}: {stage_info['status']}")
      
      if latest_log["documents_count"] > 0:
        st.info(f"📄 {latest_log['documents_count']} uploaded documents processed")
    
    # Show the final response
    st.markdown("**📋 PIPELINE RESULTS:**")
    st.write(final_response)

  st.session_state.messages.append({"role": "assistant", "content": final_response})
  st.rerun() # refresh the app to show the new message 
             # updating session state does not automatically refresh the UI
