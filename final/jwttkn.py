import uhashlib
import ubinascii
import json
import time

SECRET_KEY = b"vishnusudeepnaveen"

# Base64 URL encode without padding
def base64url_encode(data):
    encoded = ubinascii.b2a_base64(data).rstrip(b'\n').replace(b'=', b'').replace(b'+', b'-').replace(b'/', b'_')
    return encoded

# Base64 URL decode
def base64url_decode(data):
    padding = b'=' * (4 - (len(data) % 4))  # Add correct padding
    decoded = ubinascii.a2b_base64(data.replace(b'-', b'+').replace(b'_', b'/') + padding)
    return decoded

# HMAC-SHA256 implementation
def hmac_sha256(key, message):
    block_size = 64  # Block size for SHA-256
    if len(key) > block_size:
        key = uhashlib.sha256(key).digest()  # Hash the key if longer than block size
    if len(key) < block_size:
        key = key + b'\x00' * (block_size - len(key))  # Pad key with zeros if shorter than block size

    o_key_pad = bytearray([x ^ 0x5C for x in key])
    i_key_pad = bytearray([x ^ 0x36 for x in key])

    inner_hash = uhashlib.sha256(i_key_pad + message).digest()
    return uhashlib.sha256(o_key_pad + inner_hash).digest()

# Create JWT token with byte string payload
def create_jwt(payload):
    # Create header
    header = {
        "alg": "HS256",
        "typ": "JWT"
    }
    # Convert header to Base64 encoded JSON string
    header_b64 = base64url_encode(json.dumps(header).encode('utf-8'))

    # Payload is already a byte string, so Base64 encode it directly
    payload_b64 = base64url_encode(payload)

    # Create the signature (header + payload)
    signature = hmac_sha256(SECRET_KEY, header_b64 + b'.' + payload_b64)
    signature_b64 = base64url_encode(signature)

    # Return the full JWT token
    return header_b64 + b'.' + payload_b64 + b'.' + signature_b64

# Validate JWT token and return the payload as byte string
def validate_jwt(token):
    try:
        # Split the token into header, payload, and signature
        header_b64, payload_b64, signature_b64 = token.split(b'.')

        # Verify signature
        expected_signature = hmac_sha256(SECRET_KEY, header_b64 + b'.' + payload_b64)
        if signature_b64 != base64url_encode(expected_signature):
            raise ValueError("Invalid signature")

        # Decode payload (which is a byte string)
        payload = base64url_decode(payload_b64)

        # Optional: You can validate fields like expiration time (exp) if present in the payload
        # Convert payload to a dictionary if it's a structured byte string (optional)

        return payload
    except Exception as e:
        #----print("Invalid token:", e)
        return None

# # Example custom payload as byte string
# payload = b'\x01\xa2\x00\x01g\x16\xca\x01\x1c\x00Hello from ESP32 from Sudeep'

# # Create a JWT token
# jwt_token = create_jwt(payload)
# print("JWT Token:", len(jwt_token))

# # Validate the received JWT token
# decoded_payload = validate_jwt(jwt_token)
# if decoded_payload:
#     print("Valid Token. Payload:", decoded_payload)
# else:
#     print("Invalid Token")


