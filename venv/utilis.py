import random
import string
from app import app
from flask_mail import Mail, Message

#Intialize the flask_mail
mail = Mail(app)
def generate_verification_code(length=6):
    """
    Generate a random verification code.
    """
    letters_and_digits = string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

def send_verification_email(email, code):
    """
    Send a verification email with the provided code.
    """
    msg = Message(
        'Your Verification Code',
        sender='your-email@example.com',  # Your email
        recipients=[email]
    )
    msg.body = f'Your verification code is: {code}'
    mail.send(msg)