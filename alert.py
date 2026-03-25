from twilio.rest import Client

def send_whatsapp_alert(message):
    account_sid = "ACda6ebb502b2fb7cbf39ff1150fed18b7"
    auth_token = "a8336b960568f27bdf3459fff5875d21"

    client = Client(account_sid, auth_token)

    msg = client.messages.create(
        from_='whatsapp:+14155238886',  # Twilio sandbox number
        body=message,
        to='whatsapp:+916205025237'  # Your number
    )

    return msg.sid