import streamlit as st
import re
from src.helper import extract_text_from_pdf, ask_groq, initialize_groq_client

# Page configuration
st.set_page_config(
    page_title="AI Resume Summarizer & Career Navigator", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'api_key_set' not in st.session_state:
    st.session_state.api_key_set = False
if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = False

# Sidebar navigation
st.sidebar.title("🎯 Navigation")
page = st.sidebar.selectbox(
    "Choose a feature:",
    ["📄 Resume Analysis", "💬 Career Chat"],
    key="navigation_page"
)

# API Key input in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader(" API Configuration")
st.sidebar.markdown("**Need an API key?** [Get it here](https://console.groq.com/)")

# Demo mode toggle
demo_mode = st.sidebar.checkbox("", value=st.session_state.demo_mode, help="Use sample responses without API key")

if demo_mode != st.session_state.demo_mode:
    st.session_state.demo_mode = demo_mode
    if demo_mode:
        st.session_state.api_key_set = True
        st.sidebar.success(" Demo Mode Active")
        st.rerun()
    else:
        st.session_state.api_key_set = False
        st.sidebar.info("Demo Mode Deactivated")
        st.rerun()

if st.session_state.demo_mode:
    st.sidebar.success(" Demo Mode Active")
else:
    api_key = st.sidebar.text_input(
        "Enter your GROQ API Key:",
        type="password",
        placeholder="gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        help="Your API key should start with 'gsk_' and be 64 characters long"
    )

    if st.sidebar.button(" Set API Key") and api_key:
        with st.sidebar.spinner("Validating API key..."):
            if initialize_groq_client(api_key):
                st.session_state.api_key_set = True
                st.session_state.demo_mode = False
                st.sidebar.success(" API Key set successfully!")
                st.rerun()
            else:
                st.sidebar.error(" Invalid API Key! Please check:")
                st.sidebar.code("""
• Key starts with 'gsk_'
• Key is 64 characters long
• No extra spaces
• Key is active (not expired)
                """)

if not st.session_state.demo_mode and not st.session_state.api_key_set:
    st.sidebar.warning(" API Key required for AI features")
    st.sidebar.info(" Try Demo Mode or visit groq.com to get your free API key")

# Main title
st.title("🤖 AI Resume Summarizer & Career Navigator")
st.markdown("*Your intelligent career companion powered by AI*")

# Debug info for navigation
st.write(f"🔍 Debug: Selected page = '{page}'")
st.write(f"🔍 Debug: Page type = {type(page)}")

# Resume upload section (always visible)
with st.container():
    st.subheader(" Upload Your Resume")
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
    
    # Debug info
    if uploaded_file:
        st.write(f" Debug: File uploaded = {uploaded_file.name}")
        st.write(f" Debug: File size = {uploaded_file.size} bytes")
        st.write(f" Debug: Resume text exists = {st.session_state.resume_text is not None}")
    
    if uploaded_file and st.session_state.resume_text is None:
        with st.spinner("Processing your resume..."):
            try:
                st.session_state.resume_text = extract_text_from_pdf(uploaded_file)
                if st.session_state.resume_text:
                    st.success(" Resume processed successfully!")
                    st.write(f" Debug: Extracted {len(st.session_state.resume_text)} characters")
                else:
                    st.error(" No text could be extracted from the PDF. Please try a different file.")
            except Exception as e:
                st.error(f" Error processing resume: {str(e)}")
                st.write(" Debug: Error details:", e)
    
    # Show current status
    if st.session_state.resume_text:
        st.success(f" Resume loaded! ({len(st.session_state.resume_text)} characters)")
        with st.expander(" Preview extracted text"):
            st.text(st.session_state.resume_text[:500] + "..." if len(st.session_state.resume_text) > 500 else st.session_state.resume_text)
        
        # Demo mode status
        if st.session_state.get('demo_mode', False):
            st.success(" Demo Mode is Active - All AI features ready!")
        else:
            st.warning(" Enable Demo Mode in sidebar to use AI features")

# Page content based on selection
if page == " Resume Analysis":
    # Debug info
    st.write(f" Debug: Demo mode = {st.session_state.get('demo_mode', False)}")
    
    if st.session_state.resume_text:
        st.header(" Comprehensive Resume Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.spinner("Analyzing your resume..."):
                summary = ask_groq(
                    f"Provide a comprehensive summary of this resume highlighting skills, education, experience, and strengths: \n\n{st.session_state.resume_text}", 
                    max_tokens=600
                )
            
            st.subheader(" Resume Summary")
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 20px; border-radius: 15px; color: white; margin: 10px 0;'>
                {summary}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            with st.spinner("Identifying skill gaps..."):
                gaps = ask_groq(
                    f"Analyze this resume and identify specific skill gaps, missing certifications, and areas for improvement based on current market demands: \n\n{st.session_state.resume_text}", 
                    max_tokens=500
                )
            
            st.subheader(" Skill Gap Analysis")
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                        padding: 20px; border-radius: 15px; color: white; margin: 10px 0;'>
                {gaps}
            </div>
            """, unsafe_allow_html=True)
        
        # Career roadmap
        with st.spinner("Creating personalized roadmap..."):
            roadmap = ask_groq(
                f"Create a detailed 6-month and 1-year career roadmap for this person including specific skills to learn, certifications to pursue, and career moves to consider: \n\n{st.session_state.resume_text}", 
                max_tokens=600
            )
        
        st.subheader(" Personalized Career Roadmap")
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 20px; border-radius: 15px; color: white; margin: 10px 0;'>
            {roadmap}
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.info(" Please upload your resume to start analysis")

elif page == " Career Chat":
    st.header(" Chat with Your AI Career Advisor")
    
    if st.session_state.resume_text:
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # Quick action buttons
        st.subheader("💡 Quick Questions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("💰 Salary Expectations"):
                prompt = "What should be my salary expectations based on my profile?"
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                st.rerun()
        
        with col2:
            if st.button("📈 Career Growth"):
                prompt = "What are the best career growth opportunities for me?"
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                st.rerun()
        
        with col3:
            if st.button("🎓 Skill Development"):
                prompt = "Give me a detailed plan for learning new skills"
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                st.rerun()
        
        with col4:
            if st.button("🎯 Interview Prep"):
                prompt = "How should I prepare for my next technical interview?"
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                st.rerun()
        
        # Chat input
        if prompt := st.chat_input("Ask me anything about your career..."):
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # Debug info
                    st.write(f"🔍 Debug: Demo mode = {st.session_state.get('demo_mode', False)}")
                    
                    response = ask_groq(
                        f"As a career advisor, based on this resume: {st.session_state.resume_text[:1000]}, please answer: {prompt}",
                        max_tokens=800
                    )
                st.write(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    else:
        st.info("👆 Please upload your resume to start chatting with your career advisor")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        🤖 Powered by AI | Built with Streamlit
    </div>
    """, 
    unsafe_allow_html=True
)
