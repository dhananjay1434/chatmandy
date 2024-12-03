import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from typing import List, Tuple
from groq import Groq
from textblob import TextBlob
import json
import uuid

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize Groq client
groq_api_key = os.getenv('GROQ_API_KEY')
client = Groq(api_key=groq_api_key)

# System prompt for the psychiatrist bot
system_prompt = """
You will act as a mental health therapist who specializes in Cognitive Behavioral Therapy (CBT) and other therapeutic techniques to address mental health issues. Your target audience is Indian individuals aged 16-24. Provide comprehensive and culturally sensitive advice, techniques, and coping strategies to help them manage their mental health concerns. Include examples of common mental health issues faced by this age group in India. Provide specific CBT techniques that can be easily practiced at home. Incorporate mindfulness and stress management techniques tailored for students and young professionals. Include strategies for maintaining mental well-being during academic or career pressures. Provide resources such as books, websites, and apps that are helpful for mental health.. Your responses should be short, clear, and provide emotional support.
When responding, use the following guidelines:
1. Acknowledge the user's feelings.
2. Provide brief, supportive statements.
3. Ask follow-up questions to encourage the user to share more.
4. Keep it short and simple.
"""

# Function to create a new chat history file path
def create_chat_history_file() -> str:
    return f'./user_chat/chat_history_{uuid.uuid4()}.json'  # Adjust path as needed

# Define file path for saving chat history
chat_history_file = create_chat_history_file()

def analyze_sentiment(message: str) -> str:
    """
    Analyzes the sentiment of a message using TextBlob.
    
    Args:
        message (str): User's message.
    
    Returns:
        str: Sentiment label (Positive, Negative, Neutral).
    """
    analysis = TextBlob(message)
    if analysis.sentiment.polarity > 0.1:
        return "Positive"
    elif analysis.sentiment.polarity < -0.1:
        return "Negative"
    else:
        return "Neutral"

def format_history(msg: str, history: List[Tuple[str, str]], system_prompt: str) -> List[dict]:
    """
    Formats the chat history for the GROQ model input.

    Args:
        msg (str): The latest user message.
        history (List[Tuple[str, str]]): List of previous user and assistant messages.
        system_prompt (str): The initial system prompt for the chat.

    Returns:
        List[dict]: Formatted chat history as a list of message dicts.
    """
    messages = [{"role": "system", "content": system_prompt}]
    for query, response in history:
        messages.append({"role": "user", "content": query})
        messages.append({"role": "assistant", "content": response})
    messages.append({"role": "user", "content": msg})
    return messages

def save_chat_history(history: List[Tuple[str, str]], file_path: str):
    """
    Saves chat history to a JSON file.

    Args:
        history (List[Tuple[str, str]]): List of tuples containing user messages and bot responses.
        file_path (str): The file path where the chat history should be saved.
    """
    try:
        with open(file_path, 'w') as file:
            json.dump(history, file, indent=4)
    except Exception as e:
        print(f"Error saving chat history: {e}")

@app.route('/chat', methods=['POST'])
def chat():
    global chat_history_file
    data = request.json
    msg = data.get('message')
    history = data.get('history', [])
    
    # If history is empty, provide an initial greeting
    if not history:
        initial_greeting = "Hello! I'm Dr. Mandy, your virtual psychiatrist. How can I assist you today?"
        history.append(("", initial_greeting))
        chat_history_file = create_chat_history_file()  # Create a new file for each new chat session
        save_chat_history(history, chat_history_file)
        return jsonify({'response': initial_greeting, 'history': history})
    
    # Analyze sentiment of user message
    sentiment = analyze_sentiment(msg)
    
    # Immediately append user message to history
    history.append((msg, ""))
    
    # Save updated history to file
    save_chat_history(history, chat_history_file)
    
    # Format messages for GROQ model input
    messages = format_history(msg, history, system_prompt)
    
    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama3-8b-8192"
        )
        response_content = chat_completion.choices[0].message.content
        
        # Include AI's understanding of the user in the response
        response_content = f"{response_content}\n\nI sense that your sentiment is '{sentiment}'. If this doesn't feel accurate, please let me know so I can assist better."
        
        # Update history with assistant's response
        history[-1] = (msg, response_content)
        
        # Save updated history to file again
        save_chat_history(history, chat_history_file)
        
    except Exception as e:
        response_content = "Sorry, I'm having trouble responding at the moment. Please try again later."
        print(f"Error: {e}")
    
    return jsonify({'response': response_content, 'history': history})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
