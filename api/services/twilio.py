from twilio.rest import Client
from config.config import Settings


account_sid = Settings().TWILIO_ACCOUNT_SID
auth_token = Settings().TWILIO_AUTH_TOKEN
otp_service = Settings().TWILIO_OTP_SERVICE

client = Client(account_sid, auth_token)

def send_otp_sms(to):
    try:
        verification = client.verify.v2.services(otp_service).verifications.create(to=to, channel='sms')

        print(f"Message sent successfully to {to} with SID: {verification.sid}")
        return True

    except Exception as e:
        print(f"Error sending SMS: {str(e)}")
        return False

def verify_otp_sms(to, code):
    try:
        verification = client.verify.v2.services(otp_service).verification_checks.create(to=to, code=code)

        if verification.status == "approved":
            print(f"Verify successfully for {to} with SID: {verification.sid}")
            return True

        return False

    except Exception as e:
        print(f"Error verify SMS: {str(e)}")
        return False
