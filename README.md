# SMS-forward Webhook Server

A simple Python Flask webhook server designed to receive SMS messages forwarded from applications like SmsForwarder, store them in an SQLite database, and provide a web interface to view the received messages with authentication and frontend decryption.

`"I'm grateful for Gemini-2.5-pro's help, which allowed me to develop this demo project with unbelievable speed.`

## Features

*   Receives webhook requests (POST, GET, PUT, PATCH) containing SMS or notification data.
*   Stores received messages in a local SQLite database (`sms_webhook.db`).
*   Provides a web interface (`/`) to view historical messages.
*   Web interface is protected by username/password session authentication.
*   Messages displayed on the web interface are encrypted at rest and decrypted in the browser using a user-provided key.
*   Supports signature verification for incoming webhook requests using a configurable secret key.

## Requirements

*   Python 3.8+ (Tested with 3.13.2)
*   Flask
*   Flask-Session (although basic session is used, Flask's built-in session requires a secret key)
*   `cryptography` library for AES and HMAC
*   `requests` (if you plan to add outbound forwarding features, currently not implemented)

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/a2102107/sms-forward-webhook-server.git
    cd sms-webhook
    ```
2.  Install dependencies using pip:
    ```bash
    pip install Flask cryptography
    ```
    *(Note: Flask's built-in session is used, which requires a secret key. `Flask-Session` is not strictly needed for the current implementation but might be useful for more advanced session management.)*

## Configuration

Edit the `config.py` file to set up your server:

*   `DATABASE_PATH`: Path to the SQLite database file (default: `sms_webhook.db`).
*   `SECRET_KEY`: Secret key for verifying incoming webhook signatures (matches the `secret` setting in SmsForwarder). Set to `None` to disable signature verification.
*   `WEBHOOK_PATH`: The URL path where the server listens for incoming webhooks (default: `/webhook`).
*   `FLASK_SECRET_KEY`: A secret key for Flask sessions. **Change this to a random, strong key.**
*   `WEB_USERNAME`: Username for web interface login (default: `admin`). **Change this in production.**
*   `WEB_PASSWORD`: Password for web interface login (default: `password`). **Change this to a strong password in production.**
*   `BASE_DECRYPTION_STRING`: A base string used to derive the AES and HMAC keys for message encryption/decryption. **Change this to a secure, unique string.** This string will be the "Decryption Key" you enter in the web interface.

## Running the Server

Run the `app.py` file:

```bash
py app.py
```

The server will start and listen on `http://0.0.0.0:5000/` by default.

## Usage

### Webhook Endpoint

Configure your SMS forwarding application (like SmsForwarder) to send POST, GET, PUT, or PATCH requests to `http://your_server_ip:5000/webhook` (or the path you configured in `WEBHOOK_PATH`). Refer to the SmsForwarder wiki for details on the request format and signature verification.

### Web Interface

1.  Open your web browser and navigate to `http://your_server_ip:5000/`.
2.  You will be redirected to a login page. Enter the `WEB_USERNAME` and `WEB_PASSWORD` configured in `config.py`.
3.  After logging in, you will see the messages page. Messages will initially appear encrypted.
4.  Enter the `BASE_DECRYPTION_STRING` you configured in `config.py` into the "Decryption Key" input field and click "Decrypt Messages".
5.  If the key is correct, the messages will be decrypted and displayed. The key will be stored in your browser's `sessionStorage` for automatic decryption on subsequent page loads within the same session.

## Security Notes

*   **Frontend Decryption (Compromise for HTTP):** Decrypting messages in the browser is implemented as a compromise when using the server over HTTP (instead of the recommended HTTPS). This means the decryption logic and key derivation method are exposed in the frontend JavaScript code. While the `BASE_DECRYPTION_STRING` itself is not directly in the JS, the method to derive the AES/HMAC keys from it is. This approach is **not recommended for sensitive data in untrusted environments**.
*   **Change Default Credentials and Keys:** Always change the default `FLASK_SECRET_KEY`, `WEB_USERNAME`, `WEB_PASSWORD`, and `BASE_DECRYPTION_STRING` in `config.py` before deploying to a production environment.
*   **HTTPS:** For production use, it is highly recommended to deploy this server behind a reverse proxy (like Nginx or Caddy) and use HTTPS to encrypt communication between the client and the server. HTTPS provides encryption in transit, protecting both the login credentials and the encrypted message data from eavesdropping.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
