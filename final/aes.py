import cryptolib
import os

# Define the AES key (must be 16, 24, or 32 bytes long)
key = b'\x9f\xeb\x24\x63\x4b\xcd\x52\x31\x15\x1c\xa3\x0b\xd6\x4f\x84\x8d'

# Function to pad the payload to a multiple of the AES block size (16 bytes)
def pad(data):
    pad_len = 16 - len(data) % 16
    return data + bytes([pad_len] * pad_len)

# Function to unpad the payload after decryption
def unpad(data):
    return data[:-data[-1]]

# Function to encrypt the payload (with size check)
def encrypt_payload(payload, key):
    # Check if payload is less than or equal to 250 bytes
    if len(payload) > 250:
        raise ValueError("Payload exceeds 250 bytes. Please reduce the size.")
    
    payload = pad(payload)  # Pad the payload
    iv = os.urandom(16)  # Generate a random 16-byte IV
    cipher = cryptolib.aes(key, 2, iv)  # AES.MODE_CBC with the IV
    encrypted = cipher.encrypt(payload)  # Encrypt the data
    return iv + encrypted  # Prepend IV to the encrypted payload

# Function to decrypt the payload
def decrypt_payload(encrypted_payload, key):
    iv = encrypted_payload[:16]  # Extract the IV (first 16 bytes)
    encrypted = encrypted_payload[16:]  # Extract the ciphertext
    cipher = cryptolib.aes(key, 2, iv)  # AES.MODE_CBC with the extracted IV
    decrypted = cipher.decrypt(encrypted)  # Decrypt the data
    return unpad(decrypted)  # Unpad the decrypted data

# Example usage
# original_payload = b"Your data here that you want to encrypt and send"  # Example payload

# try:
#     encrypted_payload = encrypt_payload(original_payload, key)
#     print("Encrypted Payload:", encrypted_payload)

#     decrypted_payload = decrypt_payload(encrypted_payload, key)
#     print("Decrypted Payload:", decrypted_payload)
# except ValueError as e:
#     print(e)

