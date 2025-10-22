import streamlit as st
import pandas as pd
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Teacher Lesson Plan Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #1f4e79;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .bot-message {
        background-color: #f5f5f5;
    }
    .lesson-plan-card {
        background-color: #ffffff;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'lesson_plans' not in st.session_state:
    st.session_state.lesson_plans = []

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
    "Pre-K", "Kindergarten", "1st Grade", "2nd Grade", "3rd Grade", 
    "4th Grade", "5th Grade", "6th Grade", "7th Grade", "8th Grade", 
    "9th Grade", "10th Grade", "11th Grade", "12th Grade"
]

SUBJECTS = [
    "Mathematics", "English Language Arts", "Science", "Social Studies", 
    "History", "Geography", "Art", "Music", "Physical Education", 
    "Foreign Language", "Computer Science", "Health", "Economics", 
    "Psychology", "Biology", "Chemistry", "Physics", "Literature", 
    "Writing", "Reading Comprehension"
]

# Header
st.markdown('<h1 class="main-header">📚 Teacher Lesson Plan Assistant</h1>', unsafe_allow_html=True)
st.markdown("Create personalized lesson plans with AI assistance")

# Sidebar for filters
with st.sidebar:
    st.header("🔍 Search Filters")
    
    selected_state = st.selectbox("Select State", ["All States"] + STATES)
    selected_grade = st.selectbox("Select Grade Level", ["All Grades"] + GRADE_LEVELS)
    selected_subject = st.selectbox("Select Subject", ["All Subjects"] + SUBJECTS)
    
    st.header("📝 Quick Actions")
    if st.button("Generate Sample Lesson Plan"):
        # Generate a sample lesson plan based on selections
        filters = {
            "state": selected_state if selected_state != "All States" else None,
            "grade": selected_grade if selected_grade != "All Grades" else None,
            "subject": selected_subject if selected_subject != "All Subjects" else None
        }
        
        sample_plan = generate_sample_lesson_plan(filters)
        st.session_state.lesson_plans.append(sample_plan)
        st.success("Sample lesson plan generated!")
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

def generate_sample_lesson_plan(filters):
    """Generate a sample lesson plan based on selected filters"""
    subject = filters.get("subject", "Mathematics")
    grade = filters.get("grade", "5th Grade")
    state = filters.get("state", "California")
    
    return {
        "title": f"{subject} Lesson Plan - {grade}",
        "state": state,
        "grade": grade,
        "subject": subject,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "objectives": [
            f"Students will understand basic concepts in {subject.lower()}",
            f"Students will apply {subject.lower()} skills to solve problems",
            f"Students will demonstrate mastery of {subject.lower()} standards"
        ],
        "materials": [
            "Textbook or digital resources",
            "Worksheets or activity sheets",
            "Writing materials",
            "Interactive whiteboard or projector"
        ],
        "activities": [
            "Introduction and warm-up activity (10 minutes)",
            "Direct instruction with examples (20 minutes)",
            "Guided practice with students (15 minutes)",
            "Independent practice or group work (15 minutes)",
            "Review and assessment (10 minutes)"
        ],
        "assessment": f"Students will complete a worksheet demonstrating their understanding of {subject.lower()} concepts",
        "homework": f"Complete practice problems from textbook related to today's {subject.lower()} lesson"
    }

def display_lesson_plan(plan):
    """Display a formatted lesson plan"""
    st.markdown(f'<div class="lesson-plan-card">', unsafe_allow_html=True)
    st.subheader(f"📋 {plan['title']}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**State:** {plan['state']}")
    with col2:
        st.write(f"**Grade:** {plan['grade']}")
    with col3:
        st.write(f"**Subject:** {plan['subject']}")
    
    st.write(f"**Date Created:** {plan['date']}")
    
    st.subheader("🎯 Learning Objectives")
    for i, objective in enumerate(plan['objectives'], 1):
        st.write(f"{i}. {objective}")
    
    st.subheader("📚 Materials Needed")
    for material in plan['materials']:
        st.write(f"• {material}")
    
    st.subheader("⏰ Lesson Activities")
    for i, activity in enumerate(plan['activities'], 1):
        st.write(f"{i}. {activity}")
    
    st.subheader("📊 Assessment")
    st.write(plan['assessment'])
    
    st.subheader("📝 Homework")
    st.write(plan['homework'])
    
    st.markdown('</div>', unsafe_allow_html=True)

# Main chat interface
st.header("💬 Chat with Your AI Assistant")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me to help create a lesson plan..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate AI response
    with st.chat_message("assistant"):
        response = generate_ai_response(prompt, {
            "state": selected_state if selected_state != "All States" else None,
            "grade": selected_grade if selected_grade != "All Grades" else None,
            "subject": selected_subject if selected_subject != "All Subjects" else None
        })
        st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

def generate_ai_response(user_input, filters):
    """Generate AI response based on user input and filters"""
    # Simple keyword-based responses (in a real app, you'd integrate with an AI service)
    input_lower = user_input.lower()
    
    if "lesson plan" in input_lower or "create" in input_lower:
        subject = filters.get("subject", "Mathematics")
        grade = filters.get("grade", "5th Grade")
        state = filters.get("state", "California")
        
        response = f"""I'll help you create a lesson plan for **{subject}** in **{grade}** for **{state}**!

Here's what I can help you with:
• Learning objectives aligned with state standards
• Engaging activities and materials
• Assessment strategies
• Differentiation for various learning styles

Would you like me to generate a complete lesson plan, or do you have specific aspects you'd like to focus on?"""
        
    elif "objectives" in input_lower or "goals" in input_lower:
        response = """Great question! Learning objectives should be:
• **Specific and measurable**
• **Aligned with state standards**
• **Appropriate for the grade level**
• **Student-centered** (what students will do/achieve)

What subject and grade level are you working with? I can help craft specific objectives for your lesson."""
        
    elif "activities" in input_lower or "engagement" in input_lower:
        response = """I can suggest engaging activities! Here are some effective strategies:
• **Hands-on experiments** for science
• **Group discussions** for literature
• **Problem-solving tasks** for math
• **Creative projects** for art and writing

What type of activities are you looking for? I can provide specific suggestions based on your subject and grade level."""
        
    elif "assessment" in input_lower or "evaluate" in input_lower:
        response = """Assessment strategies should match your learning objectives:
• **Formative assessments** (exit tickets, observations)
• **Summative assessments** (tests, projects)
• **Self-assessment** tools
• **Peer assessment** activities

What type of assessment would work best for your lesson goals?"""
        
    elif "help" in input_lower:
        response = """I'm here to help you create amazing lesson plans! Here's what I can do:

🔍 **Search & Filter**: Use the sidebar to filter by state, grade, and subject
📝 **Generate Plans**: Ask me to create lesson plans for specific topics
🎯 **Objectives**: Help craft learning objectives
📚 **Activities**: Suggest engaging classroom activities
📊 **Assessment**: Design evaluation strategies
💡 **Ideas**: Provide creative teaching ideas

Just ask me anything about lesson planning!"""
        
    else:
        response = """I'm your AI teaching assistant! I can help you:
• Create personalized lesson plans
• Suggest learning objectives
• Design engaging activities
• Plan assessments
• Provide teaching strategies

What would you like help with today? You can also use the filters in the sidebar to specify your state, grade level, and subject."""
    
    return response

# Display saved lesson plans
if st.session_state.lesson_plans:
    st.header("📋 Your Lesson Plans")
    for i, plan in enumerate(st.session_state.lesson_plans):
        display_lesson_plan(plan)
        
        # Add buttons for each lesson plan
        col1, col2, col3 = st.columns([1, 1, 8])
        with col1:
            if st.button(f"Edit", key=f"edit_{i}"):
                st.info("Edit functionality would open a form here")
        with col2:
            if st.button(f"Delete", key=f"delete_{i}"):
                st.session_state.lesson_plans.pop(i)
                st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "🤖 AI-Powered Lesson Plan Assistant | Built with Streamlit"
    "</div>", 
    unsafe_allow_html=True
)


