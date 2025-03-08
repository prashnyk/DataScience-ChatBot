import sqlite3
import streamlit as st
import openai

# Database setup
def init_db():
    try:
        conn = sqlite3.connect("chatbot_history.db")
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS chat_history (
                     id INTEGER PRIMARY KEY AUTOINCREMENT, 
                     user_query TEXT, 
                     bot_response TEXT, 
                     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def save_to_db(user_query, bot_response):
    try:
        conn = sqlite3.connect("chatbot_history.db")
        c = conn.cursor()
        c.execute("INSERT INTO chat_history (user_query, bot_response) VALUES (?, ?)", (user_query, bot_response))
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Failed to save chat history: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def fetch_history():
    try:
        conn = sqlite3.connect("chatbot_history.db")
        c = conn.cursor()
        c.execute("SELECT * FROM chat_history ORDER BY timestamp DESC LIMIT 10")
        data = c.fetchall()
        return data
    except sqlite3.Error as e:
        st.error(f"Failed to fetch chat history: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()

def generate_response(user_query):
    """Generate a response using OpenAI's GPT model."""
    try:
        openai.api_key = "your_openai_api_key"  # Replace with your actual API key
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a helpful data science chatbot."},
                      {"role": "user", "content": user_query}]
        )
        bot_response = response['choices'][0]['message']['content']
        save_to_db(user_query, bot_response)
        return bot_response
    except openai.error.OpenAIError as e:
        return f"OpenAI API error: {e}"
    except NameError:
        return "OpenAI module is not available. Please install it before using the chatbot."

# Streamlit UI for chatbot
st.title("Customer Query Chatbot - Data Science Support")

init_db()

user_input = st.text_input("Ask a question related to data science:")
if user_input:
    response = generate_response(user_input)
    st.write("### Response:")
    st.write(response)

# Display chat history
st.sidebar.header("Chat History")
history = fetch_history()
for row in history:
    st.sidebar.write(f"**Q:** {row[1]}")
    st.sidebar.write(f"**A:** {row[2]}")
    st.sidebar.write("---")

# Additional End-to-End Features
st.sidebar.header("Additional Features")
if st.sidebar.button("Load Sample Questions"):
    st.write("Examples:")
    st.write("1. What is the difference between supervised and unsupervised learning?")
    st.write("2. How do I handle missing values in Pandas?")
    st.write("3. What is the best approach for feature selection?")
