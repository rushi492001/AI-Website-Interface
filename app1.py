import streamlit as st
import openai
import time
from streamlit_lottie import st_lottie
import json

# =====================================================
# CONFIG
# =====================================================
openai.api_key = "your-openai-api-key"

# =====================================================
# ORACLE DB (COMMENTED)
# =====================================================
# import cx_Oracle
# oracle_user = "your-username"
# oracle_password = "your-password"
# oracle_host = "host"
# oracle_port = 1521
# oracle_service = "service"
# oracle_dsn = cx_Oracle.makedsn(oracle_host, oracle_port, service_name=oracle_service)
# def get_oracle_connection():
#     return cx_Oracle.connect(oracle_user, oracle_password, oracle_dsn)

# =====================================================
# MOCK LOGIN (FOR TEST)
# =====================================================
def validate_employee(emp_id, emp_role):
    if not emp_id or not emp_role:
        return False, "Employee ID & Role required"
    if not emp_id.isdigit():
        return False, "Employee ID must be numeric"
    return True, "Test User"

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="ICICI Securities Chat", page_icon="🤖", layout="wide")

# =====================================================
# CUSTOM STYLING
# =====================================================
st.markdown(
    """
    <style>
    /* General body */
    body {
        background-color: #f5f7fa;
        font-family: 'Poppins', sans-serif;
    }

    /* Title */
    h1 {
        color: #003366 !important;
        text-shadow: 2px 2px 5px #dbe9f6;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #001f3f, #003366);
        color: white;
    }

    /* Sidebar radio and buttons */
    [data-testid="stSidebar"] button, [data-testid="stSidebar"] label {
        color: white !important;
    }
    [data-testid="stSidebar"] button:hover {
        background-color: #004c8c !important;
        transition: 0.3s;
    }

    /* Chat Messages Animation */
    .stChatMessage {
        animation: fadeIn 0.6s ease-in-out;
    }

    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(5px);}
        to {opacity: 1; transform: translateY(0);}
    }

    /* Animated Gradient Buttons */
    .animated-btn {
        background: linear-gradient(90deg, #ff9966, #ff5e62);
        border: none;
        color: white;
        padding: 8px 20px;
        border-radius: 30px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease-in-out;
    }
    .animated-btn:hover {
        background: linear-gradient(90deg, #36d1dc, #5b86e5);
        transform: scale(1.05);
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================
# LOTTIE ANIMATION LOADER
# =====================================================
def load_lottie(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

try:
    loading_lottie = load_lottie("Loading.json")  # your animation file
except:
    loading_lottie = None

# =====================================================
# SESSION STATE
# =====================================================
if "page" not in st.session_state:
    st.session_state.page = "login"
if "employee_name" not in st.session_state:
    st.session_state.employee_name = None
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {"chat_1": []}
    st.session_state.current_chat_id = "chat_1"
if "answer_feedback" not in st.session_state:
    st.session_state.answer_feedback = []

# =====================================================
# LOGIN PAGE
# =====================================================
if st.session_state.page == "login":
    st.title("🤖 ICICI Securities AI Assistant")
    st.caption("Pre-trained LLM • Human feedback guided • Test Mode")

    emp_id = st.text_input("Employee ID")
    emp_role = st.text_input("Employee Role")

    if st.button("Login", key="login_btn"):
        ok, msg = validate_employee(emp_id, emp_role)
        if ok:
            st.session_state.employee_name = msg
            st.session_state.page = "app"
            st.success(f"Welcome {msg}")
            time.sleep(0.6)
            st.rerun()
        else:
            st.error(msg)

# =====================================================
# MAIN APP
# =====================================================
elif st.session_state.page == "app":
    with st.sidebar:
        st.title("📂 Menu")
        menu = st.radio("Select", ["Chat", "Feedback Log", "Email"])

        st.markdown("---")
        if st.button("🚪 Logout", key="logout_btn"):
            st.session_state.clear()
            st.rerun()

    st.title("💼 ICICI Securities AI Assistant")
    st.caption("Interactive, Intelligent & Beautiful ✨")

    # -------------- CHAT --------------
    if menu == "Chat":
        messages = st.session_state.chat_sessions[st.session_state.current_chat_id]

        for m in messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        if prompt := st.chat_input("Ask your question 💬"):
            messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # show animation while thinking
            with st.spinner("Assistant is thinking..."):
                if loading_lottie:
                    st_lottie(loading_lottie, height=100, key="thinking")
                time.sleep(1)

                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You are a financial assistant for ICICI Securities. "
                                    "Answer with clear, concise, and factual tone."
                                )
                            }
                        ] + messages,
                        temperature=0.7,
                        max_tokens=250
                    )
                    answer = response.choices[0].message.content
                except Exception as e:
                    answer = f"⚠️ AI Error: {e}"

            messages.append({"role": "assistant", "content": answer})
            with st.chat_message("assistant"):
                st.markdown(answer)

            # Animated feedback buttons
            st.markdown("### 🧠 Was this answer helpful?")
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                if st.button("✅ Complete", key="complete", help="Answer is correct and complete"):
                    st.session_state.answer_feedback.append({"question": prompt, "result": "Complete"})
                    st.success("Marked as Complete ✅")

            with col2:
                if st.button("⚠️ Incomplete", key="incomplete"):
                    st.session_state.answer_feedback.append({"question": prompt, "result": "Incomplete"})
                    st.warning("Marked as Incomplete ⚠️")

            with col3:
                if st.button("❌ Incorrect", key="incorrect"):
                    st.session_state.answer_feedback.append({"question": prompt, "result": "Incorrect"})
                    st.error("Marked as Incorrect ❌")

            with col4:
                if st.button("📧 Email", key="email_btn"):
                    st.info("Redirecting to Email tab…")
                    st.session_state.page = "app"
                    menu = "Email"
                    st.rerun()

            with col5:
                if st.button("🆕 New Chat", key="new_chat_btn"):
                    cid = f"chat_{len(st.session_state.chat_sessions) + 1}"
                    st.session_state.chat_sessions[cid] = []
                    st.session_state.current_chat_id = cid
                    st.success("New Chat Started 💬")
                    st.rerun()

    # -------------- FEEDBACK LOG --------------
    elif menu == "Feedback Log":
        st.subheader("📊 Model Feedback History")

        if not st.session_state.answer_feedback:
            st.info("No feedback yet.")
        else:
            for f in st.session_state.answer_feedback:
                st.markdown(f"**{f['result']}** — {f['question']}")

    # -------------- EMAIL --------------
    elif menu == "Email":
        st.subheader("📧 Contact Support")
        to = st.text_input("To", "support@icicisecurities.com")
        subject = st.text_input("Subject")
        body = st.text_area("Message")

        if st.button("Send", key="send_btn"):
            st.success("✅ Email sent (mock mode).")

    st.markdown("---")
    st.caption("⚠️ Using pre-trained model with user feedback collection.")
