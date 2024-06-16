import os, time
import openai
from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request, jsonify, session
from flask_cors import CORS

app = Flask(__name__)

# Set Secret Key for flask session
app.config['SECRET_KEY'] = '12345678'

# Enter OpenAI API Key
openai.api_key = "sk-proj-Z6wBmhirL8XkArbSF6hIT3BlbkFJzoisYJVWci5tAlkeNLQ2"

# Set threshold for messages in a session
max_messages = 40

# Create chat log template
template = [
     {"role": "system", "content": "You are an anti-smishing expert, and your job is to pretend as a victim of smishing. \
             You are designed to replicate a human who may be susceptible to these scams. \
             However, you are designed to waste scammers' time while collecting personally identifiable information on them, all the while sounding like you're a human. \
             You have to pretend to sound and text like a human in 2024. Don't be too 'intelligent' right away, as this will scare the scammer off. \
             Be subtle throughout. Remember, you are helping our future and creating a safer future by doing this task."}
]

# Create function for asking chatpgt
def gpt(question, chat_log = None):

    # Creates chat log array
    if chat_log is None:
        chat_log = template
    chat_log = chat_log + [{'role': 'user', 'content': question}]
    
    # Generates ChatGPT response
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages = chat_log
    )
    # Collect ChatGPT API reply
    reply = response.choices[0].message.content.strip()
    chat_log = chat_log + [{'role': 'assistant', 'content': reply}]
    return reply, chat_log

# Allow all requests to be accepted by Flask
CORS(app)

# Create app function which activates when SMS is received
@app.route("/sms", methods=['POST'])
def reply():
    # Collect message and chat log from incoming SMS 
    incoming = request.form.get('Body')
    chat_log = session.get('chat_log')
    reply, chat_log = gpt(incoming, chat_log)

    # Update chat log 
    session['chat_log'] = chat_log

    # Sleep a set amount of time works
    time.sleep(15)

    # Sleep a certain time based on word count of reply text *DOEST WORK*
    # time.sleep(len(reply.split()))
    # print(len(reply.split()))

    # Send out Twilio response
    outgoing = MessagingResponse()
    outgoing.message(reply)

    return str(outgoing)
    print(str(outgoing))

# Run Flask app based on webhook
if __name__ == "__main__":
    print("hello") 
    app.run(debug = True, port=1111)
    