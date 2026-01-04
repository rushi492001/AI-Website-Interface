# SecureBank AI Assistant

This is a Streamlit web application themed as a bank website, featuring:
- A secure login page with bank branding
- An AI-powered chat assistant for banking queries
- Professional UI with blue theme and sidebar

## Setup

1. Ensure you have Python installed.
2. Install dependencies: `pip install -r requirements.txt`
3. For Oracle database connection:
   - Install Oracle Instant Client (required for cx-Oracle on Windows).
   - Uncomment the cx_Oracle import and Oracle connection code in `app.py`.
   - Update `oracle_dsn`, `oracle_user`, `oracle_password` with your Oracle database details.
   - Ensure your Oracle database has a `users` table with `username` and `password` columns.
4. Set up OpenAI API key in `app.py`:
   - Replace `'your-openai-api-key'` with your actual OpenAI API key.
5. For testing without Oracle, use the mock login with username: 'admin', password: 'password'.

## Running the App

Run the app with: `streamlit run app.py`

The app will start on `http://localhost:8501`

## Notes

- Currently using mock login for testing. Replace with actual Oracle connection once set up.
- The AI model used is OpenAI's GPT (assuming 'mcp model' refers to an AI model). If you meant a different model, please clarify.
- Database connection details are placeholders; update them accordingly.
- For production, consider security best practices like hashing passwords and using environment variables for secrets.
- The UI is styled to resemble a professional bank website.