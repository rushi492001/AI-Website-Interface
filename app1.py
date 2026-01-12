import streamlit as st
import openai
# import cx_Oracle   # 🔒 COMMENTED FOR TESTING

# =====================================================
# CONFIG
# =====================================================
openai.api_key = "your-openai-api-key"

# ---------------- ORACLE CONFIG (COMMENTED) ----------------
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
# CHECK_ACTIVE_EMPLOYEE = True
# -----------------------------------------------------------


# =====================================================
# ORACLE DB HELPERS (COMMENTED)
# =====================================================
# def get_oracle_connection():
#     return cx_Oracle.connect(
#         user=oracle_user,
#         password=oracle_password,
#         dsn=oracle_dsn,
#         encoding="UTF-8"
#     )


# def validate_employee(emp_id_text: str, emp_role: str):
#     if not emp_id_text or not emp_role:
#         return False, "Employee ID and Role required"
#
#     try:
#         emp_id = int(emp_id_text)
#     except ValueError:
#         return False, "Employee ID must be numeric"
#
#     sql = """
#         SELECT employee_name
#         FROM employees
#         WHERE employee_id = :emp_id
#           AND UPPER(employee_role) = UPPER(:emp_role)
#     """
#
#     if CHECK_ACTIVE_EMPLOYEE:
#         sql += " AND (end_date IS NULL OR end_date >= SYSDATE)"
#
#     try:
#         conn = get_oracle_connection()
#         cur = conn.cursor()
#         cur.execute(sql, emp_id=emp_id, emp_role=emp_role)
#         row = cur.fetchone()
#         cur.close()
#         conn.close()
#
#         if row:
#             return True, row[0]
#         return False, "Invalid or inactive employee"
#
#     except Exception as e:
#         return False, f"DB Error: {e}"


# =====================================================
# MOCK LOGIN (ACTIVE FOR TESTING)
# =====================================================
def validate_employee(emp_id, emp_role):
    if not emp_id or not emp_role:
        return False, "Employee ID and Role required"
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

if "feedback" not in st.session_state:
    st.session_state.feedback = []

if "emails" not in st.session_state:
    st.session_state.emails = []


# =====================================================
# LOGIN PAGE
# =====================================================
if st.session_state.page == "login":
    st.title("🤖 ICICI Securities AI Assistant")
    st.caption("TEST MODE – Oracle DB Disabled")

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

    with st.sidebar:
        st.title("📂 Menu")
        menu = st.radio("Select Option", ["Chat", "Feedback", "Email"])

        if menu == "Chat":
            st.markdown("### 💬 Chat History")

            if st.button("➕ New Chat"):
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
    st.caption(f"Logged in as {st.session_state.employee_name}")

    # ---------------- CHAT ----------------
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
                    messages=messages,
                    temperature=0.7,
                    max_tokens=200
                )
                answer = response.choices[0].message.content
            except Exception as e:
                answer = f"⚠️ AI Error: {e}"

            messages.append({"role": "assistant", "content": answer})

            with st.chat_message("assistant"):
                st.markdown(answer)

    # ---------------- FEEDBACK ----------------
    elif menu == "Feedback":
        st.subheader("📝 Feedback")

        text = st.text_area("Your Feedback")
        rating = st.selectbox("Rating", ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"])

        if st.button("Submit"):
            st.session_state.feedback.append({
                "text": text,
                "rating": rating
            })
            st.success("Feedback submitted")

        for f in st.session_state.feedback:
            st.write(f"{f['rating']} — {f['text']}")

    # ---------------- EMAIL ----------------
    elif menu == "Email":
        st.subheader("📧 Email Support")

        to = st.text_input("To", "support@icicisecurities.com")
        subject = st.text_input("Subject")
        body = st.text_area("Message")

        if st.button("Send"):
            st.session_state.emails.append({
                "to": to,
                "subject": subject,
                "body": body
            })
            st.success("Email sent (mock)")

        for e in st.session_state.emails:
            st.write(f"**To:** {e['to']}")
            st.write(f"**Subject:** {e['subject']}")
            st.write(e['body'])
            st.markdown("---")

    st.markdown("---")
    st.caption("⚠️ Testing mode active. Oracle DB code is commented.")
