import os
from twilio.rest import Client


account_sid = "ACf4b80158623dd36f09d7f95dac4e0724"
auth_token = "fa2c7998f4a9de046dfff6217cec5dc2"
client = Client(account_sid, auth_token)

message = client.messages \
                .create(
                    body="Hello. Testing 123 123 123!~@($)#$()",
                    from_='+18552168577',
                    to='**********'
                )
print("HI")
print(message.sid)
print("hello")
