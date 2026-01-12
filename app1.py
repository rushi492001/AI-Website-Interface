import streamlit as st
import openai
# import cx_Oracle   # ❌ COMMENTED FOR TESTING
from datetime import date

# ----------------------------
# CONFIG
# ----------------------------
openai.api_key = "your-openai-api-key"

# ❌ DATABASE CONFIG (COMMENTED)
# oracle_user = "your-username"
# oracle_password = "your-password"
# oracle_host = "host"
# oracle_port = 1521
# oracle_service = "service"
# oracle_dsn = cx_Oracle.makedsn(
#     oracle_host,
#     oracle_port,
#     service_name=oracle_service
# )

CHECK_ACTIVE_EMPLOYEE = True


# ----------------------------
# DB helpers (DISABLED)
# ----------------------------
# def get_oracle_connection():
#     return cx_Oracle.connect(
#         user=oracle_user,
#         password=oracle_password,
#         dsn=oracle_dsn,
#         encoding="UTF-8"
#     )


def validate_employee(emp_id_text: str, emp_role: str):
    """
    MOCK VALIDATION FOR TESTING
    """
    if not emp_id_text or not emp_role:
        return False, "Employee ID and Role required"

    if not emp_id_text.isdigit():
        return False, "Employee ID must be numeric"

    # ✅ MOCK SUCCESS LOGIN
    return True, "Test User"


# ----------------------------
# Streamlit Page Config
# ----------------------------
st.set_page_config(
    page_title="ICICI Securities Chat",
    page_icon="🤖",
    layout="wide"
)


# ----------------------------
# Session State
# ----------------------------
if "page" not in st.session_state:
    st.session_state.page = "login"

if "employee_name" not in st.session_state:
    st.session_state.employee_name = None

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
    st.session_state.current_chat_id = None


# ----------------------------
# LOGIN PAGE
# ----------------------------
if st.session_state.page == "login":
    st.title("🤖 ICICI Securities Chat (TEST MODE)")
    st.caption("Database disabled – mock login enabled")

    emp_id = st.text_input("Employee ID")
    emp_role = st.text_input("Employee Role")

    if st.button("Login"):
        ok, msg = validate_employee(emp_id, emp_role)

        if ok:
            st.session_state.employee_name = msg
            st.session_state.page = "chat"

            st.session_state.chat_sessions["chat_1"] = []
            st.session_state.current_chat_id = "chat_1"

            st.success(f"Login successful! Welcome {msg}")
            st.rerun()
        else:
            st.error(msg)


# ----------------------------
# CHAT PAGE
# ----------------------------
elif st.session_state.page == "chat":
    st.title("🤖 ICICI Securities AI Assistant")
    st.caption(f"Logged in as {st.session_state.employee_name}")

    messages = st.session_state.chat_sessions[
        st.session_state.current_chat_id
    ]

    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask your question"):
        messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=200
            )

            answer = response.choices[0].message.content
            messages.append({"role": "assistant", "content": answer})

            with st.chat_message("assistant"):
                st.markdown(answer)

        except Exception as e:
            st.error(f"AI Error: {e}")

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
