import os

# SQLite database path
DATABASE_PATH = 'sms_webhook.db'

# Secret key for signature verification
SECRET_KEY = '123456'

# Webhook endpoint path
WEBHOOK_PATH = '/webhook'

# Flask secret key for sessions
# Change this to a random secret key in production
FLASK_SECRET_KEY = '123456'

import hashlib # Import hashlib for SHA256

# Authentication credentials for the web interface
WEB_USERNAME = 'admin'
WEB_PASSWORD = 'password' # Change this to a strong password in production

# Base string for deriving decryption keys
# User will need to enter this string in the frontend
BASE_DECRYPTION_STRING = '123123' # CHANGE THIS IN PRODUCTION

# Derive AES-128 Encryption Key (16 bytes) from the base string using SHA256
# The frontend script uses SHA256 and takes the first 16 bytes (32 hex chars)
AES_KEY = hashlib.sha256(BASE_DECRYPTION_STRING.encode('utf-8')).digest()[:16]

# Derive HMAC Key (32 bytes) from the base string using SHA256
# The frontend script uses the full SHA256 hash
HMAC_KEY = hashlib.sha256(BASE_DECRYPTION_STRING.encode('utf-8')).digest()
