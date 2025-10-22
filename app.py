import streamlit as st
import boto3
from typing import List, Dict, Any

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

st.title("🤖 Simple AI Chatbot")
st.write("Chat with an AI using AWS Bedrock!")

# Sidebar for filters
with st.sidebar:
    st.header("🔍 Context Filters")
    
    selected_states = st.multiselect("Select States", STATES, default=[])
    selected_grade = st.selectbox("Select Grade Level", ["All Grades"] + GRADE_LEVELS)
    selected_subject = st.selectbox("Select Subject", ["All Subjects"] + SUBJECTS)
    
    st.header("⚙️ Settings")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
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
      response = invoke_model(st.session_state.messages, context)
  
  st.session_state.messages.append({"role": "assistant", "content": response})
  st.rerun() # refresh the app to show the new message 
             # updating session state does not automatically refresh the UI
