import streamlit as st
import openai
import cx_Oracle
from datetime import date

# ----------------------------
# CONFIG (set your values)
# ----------------------------
openai.api_key = "your-openai-api-key"  # better: store in st.secrets

oracle_user = "your-username"
oracle_password = "your-password"
oracle_host = "host"
oracle_port = 1521
oracle_service = "service"  # service name (recommended)

oracle_dsn = cx_Oracle.makedsn(oracle_host, oracle_port, service_name=oracle_service)  # [web:31]

# If you want: only allow active employees (end_date is null or in future)
CHECK_ACTIVE_EMPLOYEE = True


# ----------------------------
# DB helpers
# ----------------------------
def get_oracle_connection():
    # encoding optional; shown in docs examples
    return cx_Oracle.connect(
        user=oracle_user,
        password=oracle_password,
        dsn=oracle_dsn,
        encoding="UTF-8"
    )  # [web:31]


def validate_employee(emp_id_text: str, emp_role: str) -> tuple[bool, str]:
    """
    Returns: (ok, message)
    """
    if not emp_id_text or not emp_role:
        return False, "Employee ID and Employee Role are required."

    try:
        emp_id = int(emp_id_text)
    except ValueError:
        return False, "Employee ID must be a number."

    sql = """
        SELECT employee_name
        FROM employees
        WHERE employee_id = :emp_id
          AND UPPER(employee_role) = UPPER(:emp_role)
    """  # named bind variables [web:22]

    if CHECK_ACTIVE_EMPLOYEE:
        sql += "
  AND (end_date IS NULL OR end_date >= SYSDATE)"

    try:
        conn = get_oracle_connection()
        cur = conn.cursor()
        cur.execute(sql, emp_id=emp_id, emp_role=emp_role)  # bind-by-name [web:22]
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            return True, row[0]  # employee_name
        return False, "Invalid employee_id / employee_role (or employee inactive)."
    except Exception as e:
        return False, f"Database error: {e}"


# ----------------------------
# Streamlit page config + CSS
# ----------------------------
st.set_page_config(
    page_title="ICICI Securities Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background-color: #0a0a0a; color: #ffffff; }
    .stApp { background-color: #0a0a0a; color: #ffffff; }
    .stTitle, .stHeader, .stMarkdown { color: #ffffff; }
    .stSidebar { background-color: #1a1a1a; border-right: 1px solid #333; }
    .stSidebar .stMarkdown { color: #ffffff; }
    .stRadio > div { background-color: #2a2a2a; border-radius: 8px; padding: 10px; }

    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
        border-radius: 12px !important;
        margin: 8px 0 !important;
        padding: 12px 16px !important;
        max-width: 80% !important;
    }
    .stChatMessage[data-testid="user-message"] {
        background-color: #2a2a2a !important;
        margin-left: auto !important;
        margin-right: 0 !important;
        text-align: left !important;
    }
    .stChatMessage[data-testid="assistant-message"] {
        background-color: #1a1a1a !important;
        margin-left: 0 !important;
        margin-right: auto !important;
        border: 1px solid #333 !important;
    }

    .stTextInput > div > div > input {
        background-color: #2a2a2a;
        color: #ffffff;
        border: 1px solid #555;
        border-radius: 20px;
        padding: 12px 16px;
        font-size: 14px;
    }
    .stTextInput > div > div > input:focus {
        border-color: #007bff;
        box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
    }

    .stButton > button {
        background-color: #007bff;
        color: #ffffff;
        border: none;
        border-radius: 20px;
        padding: 10px 20px;
        font-weight: 500;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background-color: #0056b3;
        transform: translateY(-1px);
    }

    .stTextArea > div > div > textarea {
        background-color: #2a2a2a;
        color: #ffffff;
        border: 1px solid #555;
        border-radius: 8px;
        padding: 12px;
    }

    .stSuccess, .stError {
        color: #ffffff;
        background-color: #1a1a1a;
        border-radius: 8px;
        padding: 10px;
        border: 1px solid #333;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #1a1a1a; }
    ::-webkit-scrollbar-thumb { background: #555; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #777; }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Session state init
# ----------------------------
if "page" not in st.session_state:
    st.session_state.page = "login"

if "employee_name" not in st.session_state:
    st.session_state.employee_name = None

if "employee_id" not in st.session_state:
    st.session_state.employee_id = None

if "employee_role" not in st.session_state:
    st.session_state.employee_role = None

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
    st.session_state.current_chat_id = None


# ----------------------------
# LOGIN PAGE
# ----------------------------
if st.session_state.page == "login":
    st.markdown("# 🤖 ICICI Securities Chat")
    st.markdown("### Welcome to ICICI Securities AI Assistant")
    st.markdown("Please log in to access your account and AI assistant.")

    employee_id = st.text_input("Employee ID")
    employee_role = st.text_input("Employee Role (e.g., ADMIN / ANALYST / TRADER)")

    if st.button("Login"):
        ok, msg = validate_employee(employee_id, employee_role)
        if ok:
            st.session_state.employee_id = employee_id
            st.session_state.employee_role = employee_role
            st.session_state.employee_name = msg  # from DB
            st.session_state.page = "query"

            # Create first chat session on login
            if not st.session_state.chat_sessions:
                st.session_state.chat_sessions["chat_1"] = []
                st.session_state.current_chat_id = "chat_1"

            st.success(f"Login successful! Welcome {st.session_state.employee_name}.")
            st.rerun()
        else:
            st.error(msg)


# ----------------------------
# MAIN APP (after login)
# ----------------------------
elif st.session_state.page == "query":
    st.markdown("# 🤖 ICICI Securities Chat")
    if st.session_state.employee_name:
        st.markdown(f"Logged in as: {st.session_state.employee_name} ({st.session_state.employee_role})")
    st.markdown("Ask me anything about your securities needs!")

    with st.sidebar:
        st.markdown("## Menu")
        menu_option = st.radio("Choose an option:", ["Chat", "Feedback", "Support"])

        if menu_option == "Chat":
            st.markdown("---")
            st.markdown("## Chat History")

            if st.button("➕ New Chat", key="new_chat"):
                chat_id = f"chat_{len(st.session_state.chat_sessions) + 1}"
                st.session_state.chat_sessions[chat_id] = []
                st.session_state.current_chat_id = chat_id
                st.rerun()

            if st.session_state.chat_sessions:
                st.markdown("### Previous Chats")
                for chat_id, messages in st.session_state.chat_sessions.items():
                    chat_title = f"Chat {chat_id.split('_')[1]}"
                    if messages:
                        for m in messages:
                            if m["role"] == "user":
                                chat_title = m["content"][:30] + "..." if len(m["content"]) > 30 else m["content"]
                                break

                    is_current = (st.session_state.current_chat_id == chat_id)
                    label = f"{'🔵 ' if is_current else ''}{chat_title}"

                    if st.button(label, key=f"btn_{chat_id}"):
                        st.session_state.current_chat_id = chat_id
                        st.rerun()

    if menu_option == "Chat":
        # Auto-create first chat if none exists
        if not st.session_state.chat_sessions:
            st.session_state.chat_sessions["chat_1"] = []
            st.session_state.current_chat_id = "chat_1"

        if not st.session_state.current_chat_id:
            st.session_state.current_chat_id = list(st.session_state.chat_sessions.keys())[0]

        current_messages = st.session_state.chat_sessions.get(st.session_state.current_chat_id, [])

        # Display existing messages
        for message in current_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # New user prompt
        if prompt := st.chat_input("How can I help with your securities questions today?"):
            current_messages.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=current_messages,
                    max_tokens=200,
                    temperature=0.7
                )
                answer = response.choices[0].message.content
                current_messages.append({"role": "assistant", "content": answer})

                with st.chat_message("assistant"):
                    st.markdown(answer)
            except Exception as e:
                st.error(f"Error generating answer: {e}")

            # Save back
            st.session_state.chat_sessions[st.session_state.current_chat_id] = current_messages

    elif menu_option == "Feedback":
        st.markdown("## Feedback")
        st.markdown("We value your feedback! Please send your thoughts directly to our email.")
        st.markdown("**Email:** feedback@icicisecurities.com")

    elif menu_option == "Support":
        st.markdown("## Support")
        st.markdown("Have a different question or need assistance with something else?")

        if "other_messages" not in st.session_state:
            st.session_state.other_messages = []

        for message in st.session_state.other_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if other_prompt := st.chat_input("How can we assist you with support queries?"):
            st.session_state.other_messages.append({"role": "user", "content": other_prompt})

            with st.chat_message("user"):
                st.markdown(other_prompt)

            answer = "Thank you for your query. Our team will get back to you soon."
            st.session_state.other_messages.append({"role": "assistant", "content": answer})

            with st.chat_message("assistant"):
                st.markdown(answer)

    # Logout button
    if st.button("Logout"):
        st.session_state.page = "login"
        st.session_state.employee_name = None
        st.session_state.employee_id = None
        st.session_state.employee_role = None
        st.session_state.current_chat_id = None
        st.session_state.chat_sessions = {}
        if "other_messages" in st.session_state:
            st.session_state.other_messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("*ICICI Securities is committed to your financial security. This AI assistant is for informational purposes only.*")
