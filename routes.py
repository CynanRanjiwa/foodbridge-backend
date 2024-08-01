from flask import Flask, request, jsonify, current_app
from utils import generate_verification_code
import smtplib
from email.mime.text import MIMEText
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'  # Replace with your database URI
app.config['MAIL_USERNAME'] = 'your-email@example.com'  # Replace with your email username
app.config['MAIL_PASSWORD'] = 'your-email-password'  # Replace with your email password
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    verification_code = db.Column(db.String(6), nullable=True)
    verified = db.Column(db.Boolean, default=False)

@app.route('/verify-email', methods=['POST'])
def verify_email():
    data = request.get_json()
    email = data.get('email')

    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({"msg": "User not found"}), 404

    verification_code = generate_verification_code()
    user.verification_code = verification_code
    db.session.commit()

    msg = MIMEText(f'Your verification code is: {verification_code}')
    msg['Subject'] = 'Email Verification'  # Subject line of the email
    msg['From'] = current_app.config['MAIL_USERNAME']  # Sender's email address
    msg['To'] = email  # Recipient's email address

    with smtplib.SMTP('smtp.mailtrap.io', 587) as server:
        server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
        server.sendmail(msg['From'], [msg['To']], msg.as_string())

    return jsonify({"msg": "Verification code sent"}), 200

@app.route('/verify-code', methods=['POST'])
def verify_code():
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')

    user = User.query.filter_by(email=email).first()

    if not user or user.verification_code != code:
        return jsonify({"msg": "Invalid code"}), 401

    user.verified = True
    db.session.commit()

    return jsonify({"msg": "Email verified successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
