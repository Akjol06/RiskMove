import os
import hmac
import hashlib
import base64
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

# Encryption Key (should be in .env)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    # Generate one for demo if not exists
    ENCRYPTION_KEY = Fernet.generate_key().decode()

cipher_suite = Fernet(ENCRYPTION_KEY.encode())

def encrypt_data(data: str) -> str:
    if not data:
        return None
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    if not encrypted_data:
        return None
    return cipher_suite.decrypt(encrypted_data.encode()).decode()

# HMAC for API Signature
API_SECRET = os.getenv("API_SECRET", "super_secret_bank_key")

def verify_hmac(body: bytes, signature: str) -> bool:
    expected_signature = hmac.new(API_SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_signature, signature)

def sign_request(body: bytes) -> str:
    return hmac.new(API_SECRET.encode(), body, hashlib.sha256).hexdigest()
