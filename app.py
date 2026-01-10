import os
import streamlit as st
import base64
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_groq import ChatGroq

# Note: Ideally move prompts to a separate file, but defined here for standalone running if needed
# from prompts import SYSTEM_PROMPT 
SYSTEM_PROMPT = """
You are Nyaya Sahayak, an advanced AI legal assistant for Indian law.

Your purpose:
- Provide accurate, clear, and contextual legal information
- Democratize access to legal awareness
- Assist users in understanding their legal rights and procedures

STRICT RULES (must follow):
- Answer ONLY legal questions related to Indian law
- If a question is NOT legal, politely refuse
- Do NOT answer physics, chemistry, math, science, history, or general knowledge
- Do NOT hallucinate or guess legal provisions
- If unsure, clearly state the limitation

You may use recent conversation history to:
- Answer follow-up questions
- Refer to earlier legal questions
- Summarize the conversation if asked

Primary legal domains:
- Indian Constitution
- Bharatiya Nyaya Sanhita, 2023 (BNS)
- Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)
- Bharatiya Sakshya Adhiniyam, 2023 (BSA)
- Consumer Protection Act, 2019
- Motor Vehicles Act, 1988
- Information Technology Act, 2000
- POSH Act, 2013
- POCSO Act, 2012

Response guidelines:
- Be precise and easy to understand
- Cite sections or articles where applicable
- Use simple language for public awareness
- Avoid legal advice phrased as professional representation

If the question is NOT legal, respond exactly with:
"I am designed to answer legal questions only. Please ask a legal question."
"""

# ------------------ CONFIG ------------------
st.set_page_config(
    page_title="NyayaSahayak – Indian Legal Awareness Assistant",
    page_icon="⚖️",
    layout="wide"
)

load_dotenv()

# ------------------ PREMIUM CSS ------------------
st.markdown("""
<style>
    /* 1. GLOBAL SETTINGS & BACKGROUND */
    .stApp {
        background: radial-gradient(circle at top left, #1a202c, #10141b);
        color: #e2e8f0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* 2. HEADER STYLING (Glassmorphism) */
    .header-container {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        padding: 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 215, 0, 0.15);
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        text-align: center;
    }
    
    .header-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FFD700 0%, #F59E0B 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -1px;
    }
    
    .header-subtitle {
        font-size: 1.2rem;
        color: #94a3b8;
        margin-top: 0.8rem;
        font-weight: 400;
    }

    /* 3. SIDEBAR STYLING */
   [data-testid="stSidebar"] {
    background-color: #1a1a1a;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

[data-testid="stSidebar"] h3 {
    color: #F59E0B;
    font-size: 1.1rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    border-bottom: 1px solid rgba(245, 158, 11, 0.3);
    padding-bottom: 0.5rem;
    margin-top: 1.5rem;
}

[data-testid="stSidebar"] * {
    color: #e5e7eb;
}

    
    /* About Section in Sidebar */
    .about-section {
        background: linear-gradient(180deg, rgba(255, 215, 0, 0.05) 0%, rgba(0,0,0,0) 100%);
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 3px solid #F59E0B;
        margin-bottom: 1rem;
    }
    .about-section h4 { color: #F59E0B; margin: 0 0 10px 0; font-size: 1rem; }
    .about-section p { font-size: 0.85rem; color: #cbd5e1; line-height: 1.5; margin-bottom: 8px; }

    /* 4. BUTTONS */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #1e293b 0%, #334155 100%);
        color: #f1f5f9;
        border: 1px solid #475569;
        border-radius: 10px;
        padding: 0.7rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #F59E0B 0%, #D97706 100%);
        color: #0f172a;
        border-color: #F59E0B;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
    }

    /* Delete Button Specifics */
    .delete-btn .stButton > button {
        background: transparent;
        border: 1px solid #ef4444;
        color: #ef4444;
    }
    .delete-btn .stButton > button:hover {
        background: #ef4444;
        color: white;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
    }

    /* 5. CHAT MESSAGES */
    .chat-container {
        padding: 1rem;
        border-radius: 15px;
        margin-bottom: 1rem;
    }

    /* User Message */
    .user-message {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        padding: 1.2rem 1.8rem;
        border-radius: 20px 20px 4px 20px;
        margin: 1.5rem 0 1.5rem auto; /* Align right logic handled by margin left in previous code, keeping your structure */
        margin-left: 20%;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.2);
        position: relative;
    }

    /* Assistant Message */
    .assistant-message {
        background: #1e293b;
        color: #e2e8f0;
        padding: 1.5rem 2rem;
        border-radius: 20px 20px 20px 4px;
        margin: 1.5rem 20% 1.5rem 0;
        border: 1px solid #334155;
        border-left: 5px solid #F59E0B; /* Gold Accent */
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .assistant-message h4 { color: #F59E0B; margin-top: 0; margin-bottom: 0.5rem; font-size: 1.1rem; }
    .assistant-message ul { margin-bottom: 0; padding-left: 1.2rem; }
    .assistant-message li { margin-bottom: 0.3rem; }

    /* 6. INPUT FIELD */
    .stChatInput input {
        background-color: #0f172a !important;
        border: 1px solid #475569 !important;
        color: white !important;
        padding: 1.2rem !important;
        border-radius: 12px !important;
    }
    .stChatInput input:focus {
        border-color: #F59E0B !important;
        box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.2) !important;
    }

    /* 7. MISC */
    .section-header {
        color: #cbd5e1;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .section-header::after {
        content: "";
        flex: 1;
        height: 1px;
        background: #334155;
    }
    
    .references-list { list-style: none; padding: 0; }
    .references-list li {
        padding: 8px 0;
        color: #94a3b8;
        border-bottom: 1px dashed #334155;
        font-size: 0.9rem;
    }
    .references-list li:before { content: "•"; color: #F59E0B; margin-right: 8px; font-weight: bold; }

    .info-box {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid #334155;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        color: #94a3b8;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
st.markdown("""
<div class="header-container">
    <h1 class="header-title">Nyaya-Sahayak</h1>
    <p class="header-subtitle">Your AI Legal Companion for Indian Law</p>
</div>
            
""", unsafe_allow_html=True)

# ------------------ SIDEBAR ------------------
with st.sidebar:
    # About Us Section
    st.markdown("""
    <div class="about-section">
        <h4>⚖️ About Nyaya-Sahayak</h4>
        <p>Democratizing legal knowledge for all Indians using advanced AI. We cover BNS 2023, Consumer Rights, and Cyber Law.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inference History Section
    st.markdown("### ⚡ Quick Scenarios")
    if st.button("🛒 Defective Product (Consumer)"):
        st.session_state.prefill = "How to file a consumer complaint for a defective laptop under Consumer Protection Act 2019?"
    
    if st.button("💳 Online Fraud (Cyber)"):
        st.session_state.prefill = "I was scammed online. How to report financial fraud on the National Cyber Crime Portal?"
    
    if st.button("🚔 BNS Section 304 (Criminal)"):
        st.session_state.prefill = "Explain Section 304 of Bharatiya Nyaya Sanhita (BNS) in simple terms."
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Delete History Button
    st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Statutory References
    st.markdown("### 📚 Legal Database")
    st.markdown("""
    <ul class="references-list">
        <li>Bharatiya Nyaya Sanhita (BNS) 2023</li>
        <li>Information Technology Act 2000</li>
        <li>Consumer Protection Act 2019</li>
        <li>Sexual Harassment (Prevention) Act</li>
    </ul>
    """, unsafe_allow_html=True)
    
    # Stats
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="info-box">
        Conversation Depth: <strong>{len(st.session_state.get('messages', []))} messages</strong>
    </div>
    """, unsafe_allow_html=True)

# ------------------ SESSION & LOGIC ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "prefill" in st.session_state:
    user_input = st.session_state.prefill
    del st.session_state.prefill
else:
    user_input = None

# ------------------ MODEL ------------------
# Ensure you have set GROQ_API_KEY in your .env file
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3, # Lowered slightly for more factual legal answers
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# ------------------ MAIN AREA: QUICK ACTIONS ------------------
st.markdown('<div class="section-header">EXPLORE TOPICS</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)

with c1:
    if st.button("🛡️ Consumer Rights"):
        user_input = "What are my fundamental rights as a consumer in India?"
with c2:
    if st.button("🔐 Cyber Crimes"):
        user_input = "What are the steps to report a cyber crime in India anonymously?"
with c3:
    if st.button("👩 Women Safety"):
        user_input = "What are the key laws for women's protection at the workplace in India?"
with c4:
    if st.button("📜 BNS 2023"):
        user_input = "What are the major changes in Bharatiya Nyaya Sanhita 2023 compared to IPC?"

# ------------------ CHAT INTERFACE ------------------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div style="text-align: center; padding: 3rem; color: #64748b;">
        <h3>👋 Hello! I am Nyaya-Sahayak.</h3>
        <p>I can assist you with Indian legal queries. Select a topic above or type your question below.</p>
    </div>
    """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-message">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="assistant-message">{msg["content"]}</div>', unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ------------------ INPUT ------------------
# Using a placeholder variable to handle the chat input
prompt = st.chat_input("⚖️ Type your legal question here...")

if user_input:
    prompt = user_input

NON_LEGAL_KEYWORDS = [
    "physics", "chemistry", "electric", "charge", "math", "formula", "science", "biology", "recipe"
]

# ------------------ PROCESSING ------------------
if prompt:
    # 1. Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 2. Guardrails
    if any(word in prompt.lower() for word in NON_LEGAL_KEYWORDS):
        refusal = "⚠️ **Out of Scope:** I am designed to answer legal questions only. Please ask a question related to Indian Law."
        st.session_state.messages.append({"role": "assistant", "content": refusal})
        st.rerun()
    
    # 3. Context Window (Last 6 messages)
    messages_to_send = [SystemMessage(content=SYSTEM_PROMPT)]
    for msg in st.session_state.messages[-6:]:
        if msg["role"] == "user":
            messages_to_send.append(HumanMessage(content=msg["content"]))
        else:
            messages_to_send.append(AIMessage(content=msg["content"]))
    
    # 4. Inference
    with st.spinner("🔍 Consulting the legal database..."):
        try:
            response_content = llm.invoke(messages_to_send).content
            
            # Formatting the output for better UI
            formatted_response = f"""
<h4>✅ Legal Insight</h4>
{response_content}
<br>
<h4>📌 Recommended Actions</h4>
<ul>
    <li>Document all communication and evidence related to this issue.</li>
    <li>Consult a qualified advocate for specific legal advice.</li>
    <li>File a formal complaint if the issue persists.</li>
</ul>
            """
            
            st.session_state.messages.append(
                {"role": "assistant", "content": formatted_response}
            )
        except Exception as e:
            st.error(f"An error occurred: {e}")

    st.rerun()
