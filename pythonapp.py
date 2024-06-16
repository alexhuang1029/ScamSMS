import os 
import openai
from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
from redis import Redis

app = Flask(__name__)

# Set up Flask Session
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = Redis(host='localhost',port=6379)
app.config.from_object(__name__)
Session(app)

# Enter OpenAI API Key
openai.api_key = "sk-proj-Z6wBmhirL8XkArbSF6hIT3BlbkFJzoisYJVWci5tAlkeNLQ2"

# Set threshold for messages in a session
max_messages = 40

# Allow all requests to be accepted by Flask
CORS(app)

# Create app function which activates when SMS is received
@app.route("/sms", methods=['POST'])
def reply():
    # Collect message from incoming SMS
    incoming = request.form.get('Body')

    # Get context from session, if exists
    if 'conversation' not in session:
            session['conversation'] = []

    # Add incoming message to context history
    session['conversation'].append({"role": "user", "content": incoming})

    # Check for if exceeded message threshold and delete oldest message
    if len(session['conversation']) > max_messages:
         session['conversation'] = session['conversation'][-max_messages:]

    # Generates ChatGPT response
    # *may need to change code to reflect the previous messages (expand context window)*
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages = [
            {"role": "system", "content": "You are an anti-smishing expert, and your job is to pretend as a victim of smishing. \
             You are designed to replicate a human who may be susceptible to these scams. \
             However, you are designed to waste scammers' time while collecting personally identifiable information on them, all the while sounding like you're a human. \
             You have to pretend to sound and text like a human in 2024. Don't be too 'intelligent' right away, as this will scare the scammer off. \
             Be subtle throughout. Remember, you are helping our future and creating a safer future by doing this task."},
             {"role": "user", "content": incoming}
        ]
    )
    
    # Collect ChatGPT API reply
    reply = response.choices[0].message.content.strip()

    # Add ChatGPT response to context history
    session['conversation'].append({"role": "assistant", "content": reply})

    # Send out Twilio response
    outgoing = MessagingResponse()
    outgoing.message(reply)

    return str(outgoing)
    print(str(outgoing))

# Run Flask app based on webhook
if __name__ == "__main__":
    print("hello") 
    app.run(debug = True, port=1111)
    