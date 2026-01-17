import streamlit as st
import re
from src.helper import extract_text_from_pdf, ask_groq

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
if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = False

# Sidebar navigation
st.sidebar.title("🎯 Navigation")
page = st.sidebar.selectbox(
    "Choose a feature:",
    ["📄 Resume Analysis", "🔍 Skill & Domain Extraction", "💬 Career Chat"],
    key="navigation_page"
)

# Demo mode toggle
st.sidebar.markdown("---")
st.sidebar.subheader("🔑 API Configuration")
demo_mode = st.sidebar.checkbox("🎭 Demo Mode", value=st.session_state.demo_mode, help="Use sample responses without API key")

if demo_mode != st.session_state.demo_mode:
    st.session_state.demo_mode = demo_mode
    if demo_mode:
        st.sidebar.success("🎭 Demo Mode Active")
        st.rerun()
    else:
        st.sidebar.info("Demo Mode Deactivated")
        st.rerun()

if st.session_state.demo_mode:
    st.sidebar.success("🎭 Demo Mode Active")
else:
    st.sidebar.warning("⚠️ API Key required for AI features")
    st.sidebar.info("💡 Enable Demo Mode or set GROQ_API_KEY environment variable")

# Main title
st.title("🤖 AI Resume Summarizer & Career Navigator")
st.markdown("*Your intelligent career companion powered by AI*")

# Resume upload section (always visible)
with st.container():
    st.subheader("📤 Upload Your Resume")
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
    
    if uploaded_file and st.session_state.resume_text is None:
        with st.spinner("Processing your resume..."):
            try:
                st.session_state.resume_text = extract_text_from_pdf(uploaded_file)
                if st.session_state.resume_text:
                    st.success("✅ Resume processed successfully!")
                    st.write(f"🔍 Debug: Extracted {len(st.session_state.resume_text)} characters")
                else:
                    st.error("❌ No text could be extracted from the PDF.")
            except Exception as e:
                st.error(f"❌ Error processing resume: {str(e)}")
    
    # Show current status
    if st.session_state.resume_text:
        st.success(f"✅ Resume loaded! ({len(st.session_state.resume_text)} characters)")
        with st.expander("📄 Preview extracted text"):
            st.text(st.session_state.resume_text[:500] + "..." if len(st.session_state.resume_text) > 500 else st.session_state.resume_text)
        
        # Demo mode status
        if st.session_state.get('demo_mode', False):
            st.success("🎭 Demo Mode is Active - All AI features ready!")
        else:
            st.warning("⚠️ Enable Demo Mode to use AI features")

# Page content based on selection
if page == "📄 Resume Analysis":
    st.header("📑 Comprehensive Resume Analysis")
    
    if st.session_state.resume_text:
        col1, col2 = st.columns(2)
        
        with col1:
            with st.spinner("Analyzing your resume..."):
                summary = ask_groq(
                    f"Provide a comprehensive summary of this resume highlighting skills, education, experience, and strengths: \n\n{st.session_state.resume_text}", 
                    max_tokens=600
                )
            
            st.subheader("📋 Resume Summary")
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%'); 
                        padding: 20px; border-radius: 15px; color: white; margin: 10px 0;'>
                {summary}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            with st.spinner("Extracting skills & domains..."):
                skills_analysis = ask_groq(
                    f"""Perform intelligent skill parsing and domain extraction for this resume. Focus on:

** Intelligent Skill Parser:**
- Extract ALL technical skills (programming languages, frameworks, tools, databases)
- Extract ALL soft skills (leadership, communication, teamwork, problem-solving)
- Map each skill to industry-standard categories
- Use modern terminology and classifications

** Industry-Standard Categories:**
**Technical Skills:**
- Programming Languages: Python, JavaScript, Java, C++, etc.
- Web Technologies: React, Angular, Vue.js, HTML/CSS
- Mobile Development: React Native, Flutter, Swift, Kotlin
- Cloud Platforms: AWS, Azure, GCP, Heroku
- Databases: SQL, NoSQL, MongoDB, PostgreSQL
- DevOps Tools: Docker, Kubernetes, Jenkins, Git
- AI/ML: TensorFlow, PyTorch, Scikit-learn, OpenCV

**Soft Skills:**
- Leadership: Team management, project leadership, mentoring
- Communication: Presentations, documentation, client relations
- Problem-Solving: Analytical thinking, debugging, optimization
- Collaboration: Cross-functional teamwork, agile methodology

**Domain Knowledge:**
- Industry sectors: Finance, Healthcare, E-commerce, Education, Gaming
- Business domains: B2B, B2C, SaaS, Enterprise
- Technical domains: Frontend, Backend, Full-stack, DevOps

** Ranking by Relevance:**
- Rank skills by current job market demand (2024 trends)
- Highlight most valuable skills for career growth
- Identify trending vs. declining skills
- Suggest high-impact complementary skills

** Market Insights:**
- Salary impact of each skill category
- Job availability by skill combination
- Growth potential for each domain
- Remote work compatibility

Resume: {st.session_state.resume_text}""", 
                    max_tokens=1000
                )
            
            st.subheader(" Skill & Domain Extraction")
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                        padding: 20px; border-radius: 15px; color: white; margin: 10px 0;'>
                {skills_analysis}
            </div>
            """, unsafe_allow_html=True)
        
        # Skill gap analysis
        with st.spinner("Identifying skill gaps..."):
            gaps = ask_groq(
                f"Based on the skills analysis above and current market demands, identify specific skill gaps, missing certifications, and areas for improvement. Focus on high-demand skills that would complement their existing skillset: \n\n{st.session_state.resume_text}", 
                max_tokens=500
            )
        
        st.subheader("🎯 Skill Gap Analysis")
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%'); 
                    padding: 20px; border-radius: 15px; color: #333; margin: 10px 0;'>
            {gaps}
        </div>
        """, unsafe_allow_html=True)
        
        # Career roadmap
        with st.spinner("Creating personalized roadmap..."):
            roadmap = ask_groq(
                f"Create a detailed 6-month and 1-year career roadmap for this person including specific skills to learn, certifications to pursue, and career moves to consider based on their skill analysis: \n\n{st.session_state.resume_text}", 
                max_tokens=600
            )
        
        st.subheader("🚀 Personalized Career Roadmap")
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%'); 
                    padding: 20px; border-radius: 15px; color: white; margin: 10px 0;'>
            {roadmap}
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.info("👆 Please upload your resume to start analysis")

elif page == "🔍 Skill & Domain Extraction":
    st.header("🔍 Skill & Domain Extraction")
    st.markdown("*Intelligent skill parsing and market relevance analysis*")
    
    if st.session_state.resume_text:
        # Feature description
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🧠 **Intelligent Skill Parser**
            Extracts both technical and soft skills, mapping them to industry-standard categories.
            """)
            
            # Main skill extraction
            with st.spinner("Performing intelligent skill parsing..."):
                skills_analysis = ask_groq(
                    f"""Extract and analyze skills from this resume with comprehensive categorization:

**Technical Skills:**
- Programming Languages: Python, JavaScript, Java, C++, Go, Rust, etc.
- Web Technologies: React, Angular, Vue.js, Next.js, HTML/CSS
- Mobile Development: React Native, Flutter, Swift, Kotlin
- Cloud Platforms: AWS, Azure, GCP, Heroku, DigitalOcean
- Databases: SQL, NoSQL, MongoDB, PostgreSQL, Redis
- DevOps Tools: Docker, Kubernetes, Jenkins, Git, CI/CD
- AI/ML: TensorFlow, PyTorch, Scikit-learn, OpenCV, LangChain

**Soft Skills:**
- Leadership: Team management, project leadership, mentoring, strategy
- Communication: Presentations, documentation, client relations, negotiation
- Problem-Solving: Analytical thinking, debugging, optimization, innovation
- Collaboration: Cross-functional teamwork, agile methodology, pair programming

**Domain Knowledge:**
- Industry sectors: Finance, Healthcare, E-commerce, Education, Gaming
- Business domains: B2B, B2C, SaaS, Enterprise, Startup
- Technical domains: Frontend, Backend, Full-stack, DevOps, Data Science

Resume: {st.session_state.resume_text}""", 
                    max_tokens=1000
                )
            
            st.subheader("🧠 Intelligent Skill Parser")
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%'); 
                        padding: 25px; border-radius: 15px; color: white; margin: 15px 0;'>
                {skills_analysis}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            ### 📊 **Ranking by Relevance**
            Highlights the most important skills based on job market trends.
            """)
            
            # Market relevance ranking
            with st.spinner("Analyzing market relevance..."):
                market_ranking = ask_groq(
                    f"""Based on the skills from this resume, provide market relevance analysis:

**📊 Ranking by Relevance:**
- Top 10 most in-demand skills from their profile
- Current market demand score (1-10)
- Salary range impact for each skill
- Job availability statistics
- Growth potential over next 2 years

**🎯 Key Insights:**
- Which skills are trending upward
- Which skills are declining
- Most valuable skill combinations
- Recommended skills to learn next

**💼 Industry Demand:**
- Top industries seeking their skills
- Remote vs. in-office preferences
- Company size preferences

**📈 Career Projection:**
- Best career paths for their skillset
- Potential salary growth trajectory
- Time to senior/lead positions

Resume: {st.session_state.resume_text}""", 
                    max_tokens=800
                )
            
            st.subheader("📊 Ranking by Relevance")
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%'); 
                        padding: 25px; border-radius: 15px; color: white; margin: 15px 0;'>
                {market_ranking}
            </div>
            """, unsafe_allow_html=True)
    
    else:
        st.info("👆 Please upload your resume to start skill extraction")

elif page == "💬 Career Chat":
    st.header("💬 Chat with Your AI Career Advisor")
    
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
                # Generate AI response immediately
                with st.chat_message("user"):
                    st.write(prompt)
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = ask_groq(
                            f"As a career advisor, based on this resume: {st.session_state.resume_text[:1000]}, please answer: {prompt}",
                            max_tokens=800
                        )
                    st.write(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        with col2:
            if st.button("📈 Career Growth"):
                prompt = "What are the best career growth opportunities for me?"
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                # Generate AI response immediately
                with st.chat_message("user"):
                    st.write(prompt)
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = ask_groq(
                            f"As a career advisor, based on this resume: {st.session_state.resume_text[:1000]}, please answer: {prompt}",
                            max_tokens=800
                        )
                    st.write(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        with col3:
            if st.button("🎓 Skill Development"):
                prompt = "Give me a detailed plan for learning new skills"
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                # Generate AI response immediately
                with st.chat_message("user"):
                    st.write(prompt)
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = ask_groq(
                            f"As a career advisor, based on this resume: {st.session_state.resume_text[:1000]}, please answer: {prompt}",
                            max_tokens=800
                        )
                    st.write(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        with col4:
            if st.button("🎯 Interview Prep"):
                prompt = "How should I prepare for my next technical interview?"
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                # Generate AI response immediately
                with st.chat_message("user"):
                    st.write(prompt)
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = ask_groq(
                            f"As a career advisor, based on this resume: {st.session_state.resume_text[:1000]}, please answer: {prompt}",
                            max_tokens=800
                        )
                    st.write(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Chat input
        if prompt := st.chat_input("Ask me anything about your career..."):
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
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
