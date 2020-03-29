print('hello')

from twilio.twiml.voice_response import Dial, VoiceResponse, Say, Number
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Start, Stream


# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure


response = VoiceResponse()
# dial = Dial()
# response.pause(length=10)
# dial.number('646-518-9805', send_digits= meetingid)
# response.append(dial)
response.say('Hello, this is a bit of a longer message. This is a continued test.')
start = Start()
start.stream(
    name='Stream', url='wss://hoohacks2020-272521.appspot.com/'
)
response.append(start)
response.pause(length=60)
print(response)

call = client.calls.create(
                        twiml=response,
                        send_digits='190812663##',
                        to=meetingnumber,
                        from_='+12027513283',

                    )

print(call)