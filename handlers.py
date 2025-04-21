from flask import request, jsonify
import json
import urllib.parse
import time
import logging

from db import insert_message
from utils import verify_signature, replace_tags
from config import SECRET_KEY

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def handle_webhook():
    """Handles incoming webhook requests."""
    method = request.method
    path = request.path
    headers = dict(request.headers)
    body = request.get_data(as_text=True)

    logging.info(f"Received {method} request to {path}")
    logging.info(f"Headers: {headers}")
    logging.info(f"Body: {body}")

    data = {}
    if method == 'GET':
        data = request.args.to_dict()
    elif method in ['POST', 'PUT', 'PATCH']:
        if request.content_type == 'application/json':
            try:
                data = request.get_json()
                if data is None:
                     logging.error("Received POST/PUT/PATCH with application/json but body is empty or invalid JSON")
                     return jsonify({"status": "error", "message": "Invalid or empty JSON body"}), 400
            except Exception as e:
                logging.error(f"Failed to parse JSON body: {e}")
                return jsonify({"status": "error", "message": "Invalid JSON"}), 400
        elif request.content_type == 'application/x-www-form-urlencoded':
            data = request.form.to_dict()
        else:
            # Attempt to parse body as form data if content-type is not specified or is text
            try:
                data = dict(urllib.parse.parse_qsl(body))
            except Exception as e:
                 logging.warning(f"Failed to parse body as form data: {e}")
                 # If parsing fails, data remains empty and we proceed

    # Extract relevant data based on wiki
    from_number = data.get('from')
    content = data.get('content')
    timestamp = data.get('timestamp')
    sign = data.get('sign')

    # --- Validation Checks ---

    # Check for required fields (basic check, can be expanded)
    if not timestamp:
         logging.error("Missing timestamp in request data")
         return jsonify({"status": "error", "message": "Missing timestamp"}), 400

    # Timestamp validation (within 1 hour)
    try:
        client_timestamp = int(timestamp)
        server_timestamp = int(time.time() * 1000)
        # Check if the timestamp is within 1 hour (3600 * 1000 milliseconds)
        if abs(server_timestamp - client_timestamp) > 3600000:
            logging.error(f"Timestamp out of range: client={client_timestamp}, server={server_timestamp}")
            return jsonify({"status": "error", "message": "Timestamp out of acceptable range"}), 400
    except ValueError:
        logging.error(f"Invalid timestamp format: {timestamp}")
        return jsonify({"status": "error", "message": "Invalid timestamp format"}), 400


    # Verify signature if secret key is set
    if SECRET_KEY:
        if not sign:
            logging.error("Secret key is set but signature is missing")
            return jsonify({"status": "error", "message": "Signature required"}), 401
        if not verify_signature(timestamp, sign):
            logging.error(f"Invalid signature: provided={sign}, timestamp={timestamp}")
            return jsonify({"status": "error", "message": "Invalid signature"}), 401

    # --- End Validation Checks ---

    # Handle webParams logic if present (basic implementation)
    # The wiki describes complex webParams logic, this is a simplified approach
    # A full implementation would need to parse webParams and apply tag replacements
    # based on the request method and content type.
    # For now, we prioritize direct 'from', 'content', 'timestamp', 'sign' from request data.

    # Insert message into database
    try:
        insert_message(
            from_number=from_number,
            content=content,
            timestamp=timestamp,
            method=method,
            path=path,
            headers=json.dumps(headers),
            body=body
        )
        logging.info("Message successfully inserted into DB")
        return jsonify({"status": "success", "message": "Message received"}), 200
    except Exception as e:
        logging.error(f"Failed to insert message into DB: {e}")
        return jsonify({"status": "error", "message": "Failed to store message"}), 500
