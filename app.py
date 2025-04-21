from flask import Flask, jsonify, render_template
import json # Import json for serializing messages
from handlers import handle_webhook
from db import init_db, get_messages
from config import WEBHOOK_PATH, FLASK_SECRET_KEY
from auth import auth_bp, login_required
from utils import encrypt_data, create_hmac_signature # Import encryption/signing functions

app = Flask(__name__)

# Configure Flask secret key for sessions
app.secret_key = FLASK_SECRET_KEY

# Register authentication blueprint
app.register_blueprint(auth_bp)

# Initialize the database when the app starts
init_db()

@app.route('/')
@login_required
def index():
    """Renders the index page."""
    return render_template('index.html')

@app.route(WEBHOOK_PATH, methods=['GET', 'POST', 'PUT', 'PATCH'])
def webhook_endpoint():
    """Webhook endpoint to receive messages."""
    return handle_webhook()

@app.route('/messages', methods=['GET'])
@login_required
def view_messages():
    """Endpoint to view received messages."""
    messages = get_messages()
    # Serialize messages to JSON string
    messages_json = json.dumps(messages)
    # Encrypt the JSON string
    encrypted_messages = encrypt_data(messages_json)
    # Create HMAC signature for the encrypted data
    signature = create_hmac_signature(encrypted_messages)

    # Return encrypted data and signature
    return jsonify({
        'data': encrypted_messages,
        'signature': signature
    }), 200

if __name__ == '__main__':
    # Run the Flask development server
    # In a production environment, use a production-ready WSGI server like Gunicorn or uWSGI
    app.run(debug=True, host='0.0.0.0', port=5000)
