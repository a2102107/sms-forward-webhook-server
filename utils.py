import time
import hmac
import hashlib
import base64
import urllib.parse
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.backends import default_backend
from config import SECRET_KEY, AES_KEY, HMAC_KEY

backend = default_backend()

def verify_signature(timestamp, sign, secret=SECRET_KEY):
    """Verifies the signature of the incoming request."""
    if not secret:
        return True  # No secret set, no verification needed

    try:
        secret_enc = secret.encode('utf-8')
        string_to_sign = f'{timestamp}\n{secret}'
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.HMAC(secret_enc, hashes.SHA256(), backend=backend)
        hmac_code.update(string_to_sign_enc)
        expected_sign = urllib.parse.quote_plus(base64.b64encode(hmac_code.finalize()).decode('utf-8'))
        return expected_sign == sign
    except Exception as e:
        print(f"Signature verification failed: {e}")
        return False

def replace_tags(content, data):
    """Replaces tags in the content with actual data."""
    # Basic tag replacement based on wiki
    content = content.replace('[from]', data.get('from', ''))
    content = content.replace('[content]', data.get('content', ''))
    content = content.replace('[msg]', data.get('content', '')) # [msg] is alias for [content]
    content = content.replace('[timestamp]', data.get('timestamp', ''))
    content = content.replace('[sign]', data.get('sign', ''))
    content = content.replace('[device_mark]', data.get('device_mark', ''))
    content = content.replace('[app_version]', data.get('app_version', ''))
    content = content.replace('[card_slot]', data.get('card_slot', ''))
    content = content.replace('[title]', data.get('card_slot', '')) # [title] is alias for [card_slot]
    content = content.replace('[receive_time]', data.get('receive_time', '')) # This might be generated on server side

    # Note: The wiki mentions using variables from Appendix 3 directly in message templates
    # This basic implementation only covers the tags listed in Appendix 1.
    # A more advanced implementation might parse the template more thoroughly.

    return content

def pad(data):
    """Pads data to be a multiple of 16 bytes (AES block size)."""
    block_size = algorithms.AES.block_size // 8
    padding_length = block_size - (len(data) % block_size)
    padding = bytes([padding_length] * padding_length)
    return data + padding

def unpad(data):
    """Removes padding from data."""
    padding_length = data[-1]
    return data[:-padding_length]

def encrypt_data(data, key=AES_KEY):
    """Encrypts data using AES-128 in CBC mode."""
    iv = os.urandom(16) # 16 bytes for AES block size
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    padded_data = pad(data.encode('utf-8'))
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(iv + ciphertext).decode('utf-8')

def decrypt_data(encrypted_data, key=AES_KEY):
    """Decrypts data using AES-128 in CBC mode."""
    decoded_data = base64.b64decode(encrypted_data)
    iv = decoded_data[:16]
    ciphertext = decoded_data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    decrypted_padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    return unpad(decrypted_padded_data).decode('utf-8')

def create_hmac_signature(data, key=HMAC_KEY):
    """Creates an HMAC-SHA256 signature for the data."""
    h = hmac.HMAC(key, hashes.SHA256(), backend=backend)
    h.update(data.encode('utf-8'))
    return base64.b64encode(h.finalize()).decode('utf-8')

def verify_hmac_signature(data, signature, key=HMAC_KEY):
    """Verifies the HMAC-SHA256 signature of the data."""
    try:
        key_hmac = hmac.HMAC(key, hashes.SHA256(), backend=backend)
        key_hmac.update(data.encode('utf-8'))
        key_hmac.verify(base64.b64decode(signature))
        return True
    except Exception as e:
        print(f"HMAC verification failed: {e}")
        return False
