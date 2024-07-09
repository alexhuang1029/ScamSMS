import os, time, datetime, threading
import openai
from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient


app = Flask(__name__)

# Load .env
load_dotenv()

# Enter OpenAI API Key
openai.api_key = os.getenv("OPENAI_KEY")

# Create current log, known numbers, previous number
current_log = []
known_numbers = []
previous_number = None
countdown_duration = 30 * 60
countdowns = {}

# Create and connect to MongoClient instance
# Create directory (`chatlogs`) where messages are stored
client = MongoClient(os.getenv("MONGODB_STRING"))
db = client.chatlogs
message_database = db.messages

# Create chat log template
template = [
     {"role": "system", "content": "You are an anti-smishing expert, and your job is to pretend as a victim of smishing. \
             You are designed to replicate a human who may be susceptible to these scams. \
             However, you are designed to waste scammers' time while collecting personally identifiable information on them, all the while sounding like you're a human. \
             You have to pretend to sound and text like a human in 2024. Don't be too 'intelligent' right away, as this will scare the scammer off. \
             Be subtle throughout. Remember, you are helping our future and creating a safer future by doing this task."}
]

# Create function for asking chatpgt
def gpt(chat_log):
    # Initiate GPT API response
    response = openai.chat.completions.create(
        # Now utilizing the most advanced model, GPT-4o (increased cost)
        model="gpt-4o",
        messages = chat_log
    )
    # Collect GPT API reply
    reply = response.choices[0].message.content.strip()
    return reply

# Create parser function to remove unnecessary dictionary keys when calling a database user
def parser(current_log):
    for i in current_log:
        i.pop('_id', None)
        i.pop('user', None)
        i.pop('timestamp_i', None)
        i.pop('timestamp_o', None)
    return current_log
    
# Allow all requests to be accepted by Flask
CORS(app)

# Creates countdown function which triggers when receiving a text from a number:
class Countdown(threading.Thread):
    def __init__(self, number, duration):
        super().__init__()
        self.number = number
        self.duration = duration
        self.stop_event = threading.Event()

    # Countdown check for 30 minutes
    def run(self):
        print(f'Starting countdown for {self.number}')
        while self.duration > 0 and not self.stop_event.is_set():
            time.sleep(1)
            self.duration -= 1
        if not self.stop_event.is_set():
            self.cleanup(self.number)

    def stop(self):
        self.stop_event.set()
    
    # Cleanup function that merges all chats in the past X minutes of inactivity
    def cleanup(self, number):
        unmerged_chats = list(message_database.find({
            "user": number,
            "merged": {"$ne": True} # Finds unmerged documents
        }))

        # Appending chats
        combined_chats = "\n".join(doc["content"]for doc in unmerged_chats)

        # Creating new metadata
        merged_document = {
            "user": number,
            "content": combined_chats,
            "last_timestamp": (datetime.datetime.now() - datetime.timedelta(minutes=30)),
            "merged": True
        }

        message_database.insert_one(merged_document)
        
        # Deleting all unmerged chats
        for doc in unmerged_chats:
            message_database.delete_one({"_id": doc["_id"]})

        print(f'Cleanup and merge completed for user {number}')
            



# Create app function which activates when SMS is received
@app.route("/sms", methods=['POST'])
def reply():
    # Globalize important variables
    global previous_number, current_log, known_numbers, countdown_duration, countdowns
    # Collect message and chat log from incoming SMS 
    incoming = request.form.get('Body')
    # Access sender's phone number
    phone_number = request.form.get('From')
    # Access timestamp. *UTC is not 0 but -8.
    incoming_timestamp = datetime.datetime.today()

    # Inserts the message into the overall MongoDB database
    message_database.insert_one({
        "user": phone_number,
        "role": 'user',
        "content": incoming,
        "timestamp_i": incoming_timestamp
    })
    
    if phone_number in countdowns:
        countdowns[phone_number].stop()
    
    countdown_thread = Countdown(phone_number, countdown_duration)
    countdown_thread.start()
    countdowns[phone_number] = countdown_thread

    # Perform check to see if previous number is this number:
    if phone_number == previous_number:
        database = list(message_database.find({"user": phone_number}))
        parsed_log = parser(database) 
        current_log = template + parsed_log 

    # Pulls known number's chat log from MongoDB
    elif phone_number in known_numbers:
        database = list(message_database.find({"user": phone_number}))
        parsed_log = parser(database) 
        current_log = template + parsed_log 
        previous_number = phone_number

    # Creates new known user and a new chat log
    else:
        current_log = template + [{'role': 'user', 'content': incoming}]
        previous_number = phone_number
        known_numbers.append(phone_number)

    # Calls `gpt` function to generate reply, given the array `current_log`
    reply = gpt(current_log)
    outgoing_timestamp = datetime.datetime.today()

    # Adds GPT API reply to the message database
    message_database.insert_one({
        "user": phone_number,
        "role": 'assistant',
        "content": reply,
	"timestamp_o": outgoing_timestamp
    })

    # Sleep a set amount of time works
    # Sleep a certain time based on word count of reply text *DOEST WORK*
    # time.sleep(len(reply.split()))
    # print(len(reply.split()))

    # Send out Twilio response
    outgoing = MessagingResponse()
    outgoing.message(reply)
    return str(outgoing)

# Run Flask app based on webhook
if __name__ == "__main__":
    print("hello")
    app.run(debug = True, port=1111, host='0.0.0.0')
    
