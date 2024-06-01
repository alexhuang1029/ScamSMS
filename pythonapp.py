import os 
import openai
from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request, jsonify

app = Flask(__name__)


# Enter OpenAI API Key
openai.api_key = ""


# Create app function which activates when SMS is received
@app.route("/sms", methods=['POST'])
def reply():
    # Collect message from incoming SMS
    
    incoming = request.form.get('Body')

    # Insert command from Tuesday SEFCOM meeting
    # Generates ChatGPT response
    # *may need to change code to reflect the previous messages (expand context window)*
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages = [
            {"role": "system", "content": "You are ChatGPT, the most up-to-date and brilliant artificial intelligence system designed to combat against smishing (SMS) scammers. \
             You are designed to replicate a human who may be susceptible to these scams. \
             However, you are designed to waste scammers' time while collecting personally identifiable information on them, all the while sounding like you're a human. \
             You have to pretend to sound and text like a human in 2024. Don't be too 'intelligent' right away, as this will scare the scammer off. \
             Be subtle throughout. Remember, you are helping our future and creating a safer future by doing this task."},
             {"role": "user", "content": incoming}
        ]
    )
    
    # Collect ChatGPT API reply
    reply = response.choices[0].message.content.strip()

    # Send out Twilio response
    outgoing = MessagingResponse()
    outgoing.message(reply)

    return str(outgoing)
    print(str(outgoing))

# Run Flask app based on webhook
if __name__ == "__main__":
    print("hello") 
    app.run(debug = True)
    