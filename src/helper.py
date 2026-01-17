import os
import fitz  # PyMuPDF
from groq import Groq


# -----------------------------
# 1. Load environment variables
# -----------------------------
# Temporarily disable dotenv loading due to encoding issues
# try:
#     from dotenv import load_dotenv
#     load_dotenv()
# except ImportError:
#     pass

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("⚠️  Please set your GROQ_API_KEY environment variable")
    print("   You can get a free API key from https://console.groq.com/")
    print("   Run: set GROQ_API_KEY=your_actual_api_key_here")
    GROQ_API_KEY = None

# Initialize Groq client
client = None

def initialize_groq_client(api_key=None):
    """Initialize Groq client with provided API key"""
    global client
    try:
        if api_key:
            # Validate API key format
            if not api_key.startswith('gsk_') or len(api_key) < 50:
                return False
            client = Groq(api_key=api_key)
        elif GROQ_API_KEY:
            client = Groq(api_key=GROQ_API_KEY)
        else:
            client = None
            return False
        
        # Test the API key with a simple request
        test_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1
        )
        return client is not None
    except Exception as e:
        print(f"Error initializing Groq client: {e}")
        client = None
        return False

# Try to initialize with environment variable
if GROQ_API_KEY:
    initialize_groq_client()


# -----------------------------
# 2. Extract text from PDF
# -----------------------------
def extract_text_from_pdf(uploaded_file):
    """
    Extracts text from a PDF file.
    
    Args:
        uploaded_file (file-like): A file object (e.g. Streamlit upload).
        
    Returns:
        str: The extracted text.
    """
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text


# -----------------------------
# 3. Ask Groq
# -----------------------------
def ask_groq(prompt, model_name="llama-3.1-8b-instant", max_tokens=500, temperature=0.5):
    """
    Sends a prompt to the Groq API and returns the response.
    
    Args:
        prompt (str): The input text prompt.
        model_name (str): Groq model to use (e.g. 'llama3-8b-8192', 'mixtral-8x7b-32768').
        max_tokens (int): Maximum number of tokens in the response.
        temperature (float): Controls randomness.
        
    Returns:
        str: The response text.
    """
    # Check if demo mode is active
    try:
        import streamlit as st
        if hasattr(st.session_state, 'demo_mode') and st.session_state.demo_mode:
            return get_demo_response(prompt)
    except Exception as e:
        print(f"Demo mode check error: {e}")
        pass
    
    if not client:
        return """
        ⚠️ **API Key Required**
        
        Please enter your GROQ API key in sidebar to use AI features.
        
        📝 **Steps:**
        1. Visit [https://console.groq.com/](https://console.groq.com/)
        2. Sign up for a free account
        3. Copy your API key (starts with 'gsk_')
        4. Enter it in sidebar and click 'Set API Key'
        """
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "invalid_api_key" in error_msg:
            return """
            ❌ **Invalid API Key**
            
            The API key you entered is not valid.
            
            🔧 **Solutions:**
            • Check if you copied the full key (64 characters)
            • Ensure it starts with 'gsk_'
            • Remove any extra spaces
            • Generate a new key from [groq.com](https://console.groq.com/)
            """
        else:
            return f"❌ **API Error**: {error_msg}"

def get_demo_response(prompt):
    """Generate demo responses for testing without API key"""
    prompt_lower = prompt.lower()
    
    if "summary" in prompt_lower or "highlighting skills" in prompt_lower:
        return """
        **📋 Resume Summary**
        
        **Professional Profile:**
        Experienced software developer with 3+ years in full-stack development, specializing in Python, JavaScript, and cloud technologies. Demonstrated expertise in building scalable web applications and leading cross-functional teams.
        
        **Key Skills:**
        • Programming: Python, JavaScript, Java, SQL
        • Frameworks: React, Node.js, Django, Flask
        • Cloud: AWS, Azure, Google Cloud
        • Tools: Git, Docker, Kubernetes
        
        **Education:**
        Bachelor of Computer Science - GPA: 3.8/4.0
        
        **Experience Highlights:**
        • Led development of 5+ production applications
        • Improved system performance by 40%
        • Managed team of 4 developers
        """
    
    elif "skill gap" in prompt_lower or "missing certifications" in prompt_lower:
        return """
        **🎯 Skill Gap Analysis**
        
        **Current Strengths:**
        ✅ Strong programming foundation
        ✅ Full-stack development experience
        ✅ Team leadership capabilities
        
        **Identified Gaps:**
        🔸 **Advanced Cloud Architecture:** Consider AWS Solutions Architect certification
        🔸 **DevOps Practices:** Learn CI/CD pipelines with Jenkins/GitLab CI
        🔸 **Machine Learning:** Basic ML/AI knowledge is becoming essential
        🔸 **Security:** OWASP and security best practices
        
        **Recommended Certifications:**
        • AWS Certified Developer - Associate
        • Google Cloud Professional Developer
        • Certified Kubernetes Administrator (CKA)
        
        **Timeline:** 3-6 months to close critical gaps
        """
    
    elif "roadmap" in prompt_lower or "6-month" in prompt_lower or "1-year" in prompt_lower:
        return """
        **🚀 Personalized Career Roadmap**
        
        **🎯 6-Month Plan:**
        **Months 1-2: Skill Enhancement**
        • Complete AWS Developer certification
        • Master advanced React patterns
        • Learn Docker and Kubernetes basics
        
        **Months 3-4: Project Leadership**
        • Lead a medium-scale project
        • Implement CI/CD pipeline
        • Mentor junior developers
        
        **Months 5-6: Networking & Growth**
        • Attend tech conferences/meetups
        • Contribute to open source
        • Build professional portfolio
        
        **🎯 1-Year Vision:**
        **Technical Growth:**
        • Senior Developer position
        • Cloud architecture expertise
        • Team leadership role
        
        **Career Moves:**
        • Target FAANG/tech unicorn companies
        • Consider technical product management
        • Explore startup opportunities
        
        **Salary Expectation:** 40-60% increase
        """
    
    elif "plan" in prompt_lower and "learn" in prompt_lower:
        return """
        **📚 Personalized Skill Learning Plan**
        
        **🎯 Phase 1: Foundation Strengthening (Months 1-2)**
        
        **Technical Skills:**
        • **Cloud Computing:** Start with AWS Cloud Practitioner (2 weeks)
        • **Containerization:** Docker fundamentals (1 week)
        • **Version Control:** Advanced Git workflows (1 week)
        
        **Resources:**
        - AWS Free Tier tutorials
        - Docker official documentation
        - GitHub Learning Lab
        
        **🎯 Phase 2: Advanced Technologies (Months 3-4)**
        
        **Cloud Architecture:**
        • AWS Solutions Architect Associate (6 weeks)
        • Microservices with Kubernetes (4 weeks)
        
        **Development Practices:**
        • CI/CD with Jenkins/GitLab CI (2 weeks)
        • Test-driven development (2 weeks)
        
        **Resources:**
        - AWS Certified Solutions Architect course
        - Kubernetes documentation
        - Jenkins tutorials
        
        **🎯 Phase 3: Specialization (Months 5-6)**
        
        **Choose Your Track:**
        
        **🔹 Backend Focus:**
        - Advanced system design
        - Database optimization
        - API security
        
        **🔹 Frontend Focus:**
        - React/Next.js advanced patterns
        - Performance optimization
        - Progressive Web Apps
        
        **🔹 DevOps Focus:**
        - Infrastructure as Code (Terraform)
        - Monitoring and observability
        - Site reliability engineering
        
        **📅 Weekly Schedule:**
        - **Monday/Wednesday/Friday:** 2 hours technical learning
        - **Tuesday/Thursday:** 1 hour hands-on practice
        - **Saturday:** 3 hours project work
        - **Sunday:** Review and planning
        
        **📊 Progress Tracking:**
        - Create GitHub repository for learning projects
        - Document progress in technical blog
        - Join study groups or communities
        - Schedule monthly skill assessments
        
        **🎯 Success Metrics:**
        - Complete 2 certifications within 6 months
        - Build 3 portfolio projects
        - Contribute to 2 open-source projects
        - Network with 10+ industry professionals
        """
    
    elif "salary" in prompt_lower or "expectation" in prompt_lower:
        return """
        **💰 Salary Expectations & Negotiation Guide**
        
        **📊 Current Market Analysis:**
        
        **Your Experience Level:** 3+ years
        **Your Skills:** Full-stack, Cloud, Leadership
        
        **Salary Ranges (2024):**
        • **Mid-level Developer:** $80,000 - $120,000
        • **Senior Developer:** $120,000 - $160,000  
        • **Tech Lead:** $140,000 - $200,000
        • **Staff Engineer:** $160,000 - $250,000
        
        **🎯 Your Target Range:** $130,000 - $180,000
        
        **💡 Negotiation Strategy:**
        
        **Preparation:**
        - Research company salary bands
        - Document your achievements and impact
        - Prepare market data from multiple sources
        
        **Key Talking Points:**
        - Led 5+ production applications
        - Improved performance by 40%
        - Managed team of 4 developers
        - Cloud certifications and expertise
        
        **Benefits to Negotiate:**
        - Sign-on bonus ($10,000 - $20,000)
        - Stock options/RSUs
        - Professional development budget
        - Flexible work arrangements
        - Performance bonus structure
        
        **📈 Timeline:**
        - 6 months: Target 15-20% increase
        - 1 year: Aim for senior position
        - 2 years: Target tech lead role
        """
    
    elif "interview" in prompt_lower or "prepare" in prompt_lower:
        return """
        **🎯 Interview Preparation Plan**
        
        **📚 Technical Preparation (2 weeks):**
        
        **Week 1: Core Concepts**
        - Data Structures & Algorithms (2 hours/day)
        - System Design fundamentals (1 hour/day)
        - Database concepts (1 hour/day)
        
        **Week 2: Advanced Topics**
        - Cloud architecture patterns (2 hours/day)
        - Security best practices (1 hour/day)
        - Scalability concepts (1 hour/day)
        
        **🗣️ Behavioral Questions (1 week):**
        
        **Key Areas to Prepare:**
        - Leadership experiences
        - Conflict resolution
        - Project failures and learnings
        - Team collaboration challenges
        
        **STAR Method Examples:**
        - **Situation:** Describe the context
        - **Task:** Explain your responsibility
        - **Action:** Detail what you did
        - **Result:** Quantify the outcome
        
        **💻 Mock Interviews:**
        - Schedule 3-5 mock interviews
        - Practice with peers or online platforms
        - Record and review your performance
        - Focus on communication clarity
        
        **📱 Day Before Interview:**
        - Review your resume and projects
        - Prepare questions for the interviewer
        - Get good sleep and relax
        - Test your technical setup (if remote)
        """
    
    else:
        return """
        **💬 Personalized Career Advice**
        
        **🎯 Immediate Action Items (Next 30 Days):**
        
        **1. Skill Enhancement:**
        - Start AWS Cloud Practitioner certification
        - Build 2 new portfolio projects
        - Contribute to an open-source project
        
        **2. Networking Strategy:**
        - Join 3 tech communities (Discord/Slack)
        - Attend 2 virtual tech meetups
        - Connect with 5 industry professionals on LinkedIn
        
        **3. Personal Branding:**
        - Update LinkedIn profile with achievements
        - Start a technical blog (1 post/week)
        - Create GitHub portfolio with 5+ projects
        
        **📈 3-Month Goals:**
        - Complete AWS certification
        - Apply to 20+ target companies
        - Secure 3-5 interviews
        - Negotiate 20%+ salary increase
        
        **🚀 Long-term Vision (6-12 months):**
        - Target Senior Developer role
        - Build technical leadership skills
        - Explore tech entrepreneurship
        - Consider graduate education if relevant
        
        **📊 Success Metrics:**
        - Technical: 2 certifications, 5 portfolio projects
        - Career: 50%+ salary growth, senior position
        - Network: 100+ professional connections
        - Brand: 1000+ LinkedIn followers, 50+ blog readers
        
        **🔄 Monthly Review:**
        - Track skill progress
        - Update resume with new achievements
        - Adjust strategy based on market feedback
        - Celebrate small wins and learn from setbacks
        """
