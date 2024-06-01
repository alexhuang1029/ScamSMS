import os
from twilio.rest import Client


account_sid = "ACf4b80158623dd36f09d7f95dac4e0724"
auth_token = "6972f9c7d1f2dfc091a1e50325be8b2d"
client = Client(account_sid, auth_token)

message = client.messages \
                .create(
                    body="Hello. Testing 123 123 123!~@($)#$()",
                    from_='+18552168577',
                    to='+14807498123'
                )

print(message.sid)
print("hello")