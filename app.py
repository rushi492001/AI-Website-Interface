import streamlit as st
# import cx_Oracle  # Commented out for testing/demo purposes
import openai

# Configure OpenAI API key (replace with your actual key)
openai.api_key = 'your-openai-api-key'

# Oracle database connection details (commented out for testing)
# oracle_user = 'your-username'
# oracle_password = 'your-password'
# oracle_dsn = cx_Oracle.makedsn('host', 'port', service_name='service')

st.set_page_config(
    page_title="ICICI Securities Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# OpenWebUI-inspired Dark Theme CSS
st.markdown("""
<style>
    /* Main background */
    .main {
        background-color: #0a0a0a;
        color: #ffffff;
    }
    .stApp {
        background-color: #0a0a0a;
        color: #ffffff;
    }
    
    /* Header */
    .stTitle, .stHeader, .stMarkdown {
        color: #ffffff;
    }
    
    /* Sidebar */
    .stSidebar {
        background-color: #1a1a1a;
        border-right: 1px solid #333;
    }
    .stSidebar .stMarkdown {
        color: #ffffff;
    }
    .stRadio > div {
        background-color: #2a2a2a;
        border-radius: 8px;
        padding: 10px;
    }
    
    /* Chat messages - OpenWebUI style */
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
    
    /* Input field */
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
    
    /* Buttons */
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
    
    /* Text area */
    .stTextArea > div > div > textarea {
        background-color: #2a2a2a;
        color: #ffffff;
        border: 1px solid #555;
        border-radius: 8px;
        padding: 12px;
    }
    
    /* Success/Error messages */
    .stSuccess, .stError {
        color: #ffffff;
        background-color: #1a1a1a;
        border-radius: 8px;
        padding: 10px;
        border: 1px solid #333;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #1a1a1a;
    }
    ::-webkit-scrollbar-thumb {
        background: #555;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #777;
    }
</style>
""", unsafe_allow_html=True)

if 'page' not in st.session_state:
    st.session_state.page = 'login'

if st.session_state.page == 'login':
    # Minimal header
    st.markdown("# 🤖 ICICI Securities Chat")
    st.markdown("### Welcome to ICICI Securities AI Assistant")
    st.markdown("Please log in to access your account and AI assistant.")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        # Demo login for testing purposes (always succeeds)
        st.session_state.page = 'query'
        st.success("Login successful! Welcome to ICICI Securities AI Assistant.")
        st.rerun()  # Refresh to show new page
    #     try:
    #         # Connect to Oracle database
    #         conn = cx_Oracle.connect(user=oracle_user, password=oracle_password, dsn=oracle_dsn)
    #         cursor = conn.cursor()
            
    #         # Assume a table 'users' with columns 'username' and 'password'
    #         cursor.execute("SELECT COUNT(*) FROM users WHERE username = :1 AND password = :2", (username, password))
    #         count = cursor.fetchone()[0]
            
    #         if count > 0:
    #             st.session_state.page = 'query'
    #             st.success("Login successful! Welcome to ICICI Securities AI Assistant.")
    #             st.rerun()  # Refresh to show new page
    #         else:
    #             st.error("Invalid username or password.")
            
    #         cursor.close()
    #         conn.close()
    #     except cx_Oracle.DatabaseError as e:
    #         st.error(f"Database connection error: {e}")
    #     except Exception as e:
    #         st.error(f"An error occurred: {e}")

elif st.session_state.page == 'query':
    # Minimal header like OpenWebUI
    st.markdown("# 🤖 ICICI Securities Chat")
    st.markdown("Ask me anything about your securities needs!")
    
    # Sidebar menu and chat history
    with st.sidebar:
        st.markdown("## Menu")
        menu_option = st.radio("Choose an option:", ["Chat", "Feedback", "Support"])
        
        if menu_option == "Chat":
            st.markdown("---")
            st.markdown("## Chat History")
            
            # Initialize chat sessions if not exists
            if "chat_sessions" not in st.session_state:
                st.session_state.chat_sessions = {}
                st.session_state.current_chat_id = None
            
            # New Chat button
            if st.button("➕ New Chat", key="new_chat"):
                # Create new chat session
                chat_id = f"chat_{len(st.session_state.chat_sessions) + 1}"
                st.session_state.chat_sessions[chat_id] = []
                st.session_state.current_chat_id = chat_id
                st.session_state.messages = []
                st.rerun()
            
            # Display chat history
            if st.session_state.chat_sessions:
                st.markdown("### Previous Chats")
                for chat_id, messages in st.session_state.chat_sessions.items():
                    # Get first user message as chat title, or use chat ID
                    chat_title = f"Chat {chat_id.split('_')[1]}"
                    if messages and len(messages) > 0:
                        # Find first user message
                        for msg in messages:
                            if msg["role"] == "user":
                                chat_title = msg["content"][:30] + "..." if len(msg["content"]) > 30 else msg["content"]
                                break
                    
                    # Highlight current chat
                    is_current = st.session_state.current_chat_id == chat_id
                    button_label = f"{'🔵 ' if is_current else ''}{chat_title}"
                    
                    if st.button(button_label, key=f"chat_{chat_id}"):
                        st.session_state.current_chat_id = chat_id
                        st.session_state.messages = st.session_state.chat_sessions[chat_id].copy()
                        st.rerun()
    
    if menu_option == "Chat":
        # Initialize chat sessions and current chat
        if "chat_sessions" not in st.session_state:
            st.session_state.chat_sessions = {}
            st.session_state.current_chat_id = None
        
        # Auto-create first chat if none exists
        if not st.session_state.chat_sessions:
            chat_id = "chat_1"
            st.session_state.chat_sessions[chat_id] = []
            st.session_state.current_chat_id = chat_id
        
        # Set current messages from selected chat
        if st.session_state.current_chat_id and st.session_state.current_chat_id in st.session_state.chat_sessions:
            st.session_state.messages = st.session_state.chat_sessions[st.session_state.current_chat_id]
        else:
            # Fallback to first chat
            first_chat = list(st.session_state.chat_sessions.keys())[0]
            st.session_state.current_chat_id = first_chat
            st.session_state.messages = st.session_state.chat_sessions.get(first_chat, [])

        # Display chat messages from current session
        current_messages = st.session_state.chat_sessions.get(st.session_state.current_chat_id, [])
        for message in current_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Accept user input
        if prompt := st.chat_input("How can I help with your securities questions today?"):
            # Add user message to current chat session
            if st.session_state.current_chat_id not in st.session_state.chat_sessions:
                st.session_state.chat_sessions[st.session_state.current_chat_id] = []
            st.session_state.chat_sessions[st.session_state.current_chat_id].append({"role": "user", "content": prompt})
            
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get response from OpenAI
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",  # Or "gpt-4" if available
                    messages=st.session_state.chat_sessions[st.session_state.current_chat_id],
                    max_tokens=200,
                    temperature=0.7
                )
                answer = response.choices[0].message.content
                # Add assistant response to current chat session
                st.session_state.chat_sessions[st.session_state.current_chat_id].append({"role": "assistant", "content": answer})
                # Display assistant response in chat message container
                with st.chat_message("assistant"):
                    st.markdown(answer)
            except Exception as e:
                st.error(f"Error generating answer: {e}")
    
    elif menu_option == "Feedback":
        st.markdown("## Feedback")
        st.markdown("We value your feedback! Please send your thoughts directly to our email.")
        st.markdown("**Email:** feedback@icicisecurities.com")
        st.markdown("You can compose and send your feedback through your preferred email client.")
    
    elif menu_option == "Support":
        st.markdown("## Support")
        st.markdown("Have a different question or need assistance with something else?")
        
        # Similar to AI Assistant but perhaps without OpenAI, or with a different prompt
        if "other_messages" not in st.session_state:
            st.session_state.other_messages = []

        # Display chat messages from history on app rerun
        for message in st.session_state.other_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Accept user input
        if other_prompt := st.chat_input("How can we assist you with support queries?"):
            # Add user message to chat history
            st.session_state.other_messages.append({"role": "user", "content": other_prompt})
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(other_prompt)

            # For now, just echo or provide a static response
            # You can integrate with another AI or handle manually
            answer = "Thank you for your query. Our team will get back to you soon."
            # Add assistant response to chat history
            st.session_state.other_messages.append({"role": "assistant", "content": answer})
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(answer)
    
    # Logout button
    if st.button("Logout"):
        st.session_state.page = 'login'
        st.session_state.messages = []  # Clear chat history on logout
        if "other_messages" in st.session_state:
            st.session_state.other_messages = []
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("*ICICI Securities is committed to your financial security. This AI assistant is for informational purposes only.*")