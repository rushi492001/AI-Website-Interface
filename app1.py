import streamlit as st
import openai

# =====================================================
# CONFIG
# =====================================================
openai.api_key = "your-openai-api-key"

# =====================================================
# ORACLE DB CODE (COMMENTED – READY FOR PROD)
# =====================================================
# import cx_Oracle
#
# oracle_user = "your-username"
# oracle_password = "your-password"
# oracle_host = "host"
# oracle_port = 1521
# oracle_service = "service"
#
# oracle_dsn = cx_Oracle.makedsn(
#     oracle_host,
#     oracle_port,
#     service_name=oracle_service
# )
#
# def get_oracle_connection():
#     return cx_Oracle.connect(
#         oracle_user, oracle_password, oracle_dsn
#     )

# =====================================================
# MOCK LOGIN (TEST MODE)
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
st.set_page_config(
    page_title="ICICI Securities Chat",
    page_icon="🤖",
    layout="wide"
)

# =====================================================
# SESSION STATE
# =====================================================
if "page" not in st.session_state:
    st.session_state.page = "login"

if "employee_name" not in st.session_state:
    st.session_state.employee_name = None

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
    st.session_state.current_chat_id = None

if "answer_feedback" not in st.session_state:
    st.session_state.answer_feedback = []


# =====================================================
# LOGIN PAGE
# =====================================================
if st.session_state.page == "login":
    st.title("🤖 ICICI Securities AI Assistant")
    st.caption("Pre-trained model • Human feedback driven • Test Mode")

    emp_id = st.text_input("Employee ID")
    emp_role = st.text_input("Employee Role")

    if st.button("Login"):
        ok, msg = validate_employee(emp_id, emp_role)
        if ok:
            st.session_state.employee_name = msg
            st.session_state.page = "app"
            st.session_state.chat_sessions = {"chat_1": []}
            st.session_state.current_chat_id = "chat_1"
            st.success(f"Welcome {msg}")
            st.rerun()
        else:
            st.error(msg)


# =====================================================
# MAIN APP
# =====================================================
elif st.session_state.page == "app":

    # ---------------- SIDEBAR ----------------
    with st.sidebar:
        st.title("📂 Menu")
        menu = st.radio("Select", ["Chat", "Feedback Log", "Email"])

        if menu == "Chat":
            st.markdown("### 💬 Chat History")

            if st.button("➕ Start New Chat"):
                cid = f"chat_{len(st.session_state.chat_sessions) + 1}"
                st.session_state.chat_sessions[cid] = []
                st.session_state.current_chat_id = cid
                st.rerun()

            for cid in st.session_state.chat_sessions:
                if st.button(f"Chat {cid.split('_')[1]}", key=cid):
                    st.session_state.current_chat_id = cid
                    st.rerun()

        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.rerun()

    st.title("🤖 ICICI Securities AI Assistant")
    st.caption(
        "Using a pre-trained LLM. "
        "Your feedback helps improve future fine-tuning."
    )

    # =================================================
    # CHAT
    # =================================================
    if menu == "Chat":
        messages = st.session_state.chat_sessions[
            st.session_state.current_chat_id
        ]

        for m in messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        if prompt := st.chat_input("Ask your question"):
            messages.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a financial assistant for ICICI Securities. "
                                "Answer clearly, factually, and concisely."
                            )
                        }
                    ] + messages,
                    temperature=0.7,
                    max_tokens=300
                )
                answer = response.choices[0].message.content
            except Exception as e:
                answer = f"⚠️ AI Error: {e}"

            messages.append({"role": "assistant", "content": answer})

            with st.chat_message("assistant"):
                st.markdown(answer)

            # ---------- POST ANSWER OPTIONS ----------
            st.markdown("### 🧠 Was this answer helpful?")
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                if st.button("✅ Complete"):
                    st.session_state.answer_feedback.append(
                        {"question": prompt, "result": "Complete"}
                    )
                    st.success("Marked as Complete")

            with col2:
                if st.button("⚠️ Incomplete"):
                    st.session_state.answer_feedback.append(
                        {"question": prompt, "result": "Incomplete"}
                    )
                    st.warning("Marked as Incomplete")

            with col3:
                if st.button("❌ Incorrect"):
                    st.session_state.answer_feedback.append(
                        {"question": prompt, "result": "Incorrect"}
                    )
                    st.error("Marked as Incorrect")

            with col4:
                if st.button("📧 Email"):
                    st.info("Redirect to Email section from menu")

            with col5:
                if st.button("🆕 New Chat"):
                    cid = f"chat_{len(st.session_state.chat_sessions) + 1}"
                    st.session_state.chat_sessions[cid] = []
                    st.session_state.current_chat_id = cid
                    st.rerun()

    # =================================================
    # FEEDBACK LOG
    # =================================================
    elif menu == "Feedback Log":
        st.subheader("📊 Answer Feedback (Training Signals)")

        if not st.session_state.answer_feedback:
            st.info("No feedback collected yet.")
        else:
            for f in st.session_state.answer_feedback:
                st.write(f"**{f['result']}** — {f['question']}")

    # =================================================
    # EMAIL
    # =================================================
    elif menu == "Email":
        st.subheader("📧 Contact Support")

        to = st.text_input("To", "support@icicisecurities.com")
        subject = st.text_input("Subject")
        body = st.text_area("Message")

        if st.button("Send Email"):
            st.success("Email sent (mock). Stored for audit.")

    st.markdown("---")
    st.caption(
        "⚠️ This system uses a pre-trained model. "
        "Feedback collected here can be used for future fine-tuning."
)
    st.markdown("---")
    st.caption("⚠️ Testing mode active. Oracle DB code is commented.")
