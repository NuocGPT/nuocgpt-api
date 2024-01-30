from twilio.rest import Client
from config.config import Settings


account_sid = Settings().TWILIO_ACCOUNT_SID
auth_token = Settings().TWILIO_AUTH_TOKEN

client = Client(account_sid, auth_token)

def send_otp_sms(to, otp):
    try:
        message = client.messages.create(
            from_='+18882924469',
            to=to,
            body="Ma OTP cua ban la: {0}".format(otp)
        )

        print(f"Message sent successfully to {to} with SID: {message.sid}")
        return True

    except Exception as e:
        print(f"Error sending SMS: {str(e)}")
        return False
