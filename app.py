from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from models import db, User
from utilis import generate_verification_code, send_verification_email

# Create Flask application instance
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400

    user = User(username=username, email=email)
    user.set_password(password)
    user.verification_code = generate_verification_code()
    
    db.session.add(user)
    db.session.commit()
    
    send_verification_email(user.email, user.verification_code)
    
    return jsonify({'message': 'User registered. Check your email for the verification code.'}), 201

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')

    if not email or not code:
        return jsonify({'error': 'Missing required fields'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or user.verification_code != code:
        return jsonify({'error': 'Invalid verification code'}), 400

    user.is_verified = True
    user.verification_code = None
    db.session.commit()

    return jsonify({'message': 'User verified successfully.'}), 200

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
