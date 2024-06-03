import os
from twilio.rest import Client


account_sid = "ACf4b80158623dd36f09d7f95dac4e0724"
auth_token = ""
client = Client(account_sid, auth_token)

message = client.messages \
                .create(
                    body="Hello. Testing 123 123 123!~@($)#$()",
                    from_='+18552168577',
                    to='**********'
                )

print(message.sid)
print("hello")
