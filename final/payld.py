import struct
import time
from tstmp import *
# Function to get the current timestamp in Unix time format
# def get_current_time():
#     return int(time.time())

# Function to create custom payload
def create_custom_payload(device_id, message_id, data, status_code):
    # Ensure data is in bytes
    if isinstance(data, str):
        data = data.encode('utf-8')  # Convert string to UTF-8 encoded bytes

    if not isinstance(data, bytes):
        raise ValueError("Data must be a bytes object.")

    data_length = len(data)
    #print(f"Data Length: {data_length}")  # Print data length

    # Ensure data length does not exceed 200 bytes
    if data_length > 200:
        raise ValueError("Data too long! Maximum allowed size is 200 bytes.")

    # Get current timestamp using your function
    timestamp = get_current_time()

    # Pack the payload: Device ID (2 bytes), Message ID (2 bytes), Timestamp (4 bytes), Data Length (1 byte), Status Code (1 byte)
    payload = struct.pack('>HHIBB', device_id, message_id, timestamp, data_length, status_code)
    payload += data  # Append the actual data bytes

    return payload

# Function to decode custom payload with timestamp check
def decode_custom_payload(payload):
    # Step 1: Check if the payload has at least the minimum length (10 bytes for fixed fields)
    if len(payload) < 10:
        #----print(f"Payload too short to contain required fields. Expected at least 10 bytes, got {len(payload)}")
        return False
        raise ValueError(f"Payload too short to contain required fields. Expected at least 10 bytes, got {len(payload)}")

    # Step 2: Check if the payload structure matches the expected fields
    expected_header_size = struct.calcsize('>HHIBB')
    if len(payload) < expected_header_size:
        #----print(f"Payload structure is incorrect. Expected at least {expected_header_size} bytes for header, got {len(payload)}")
        return False
        raise ValueError(f"Payload structure is incorrect. Expected at least {expected_header_size} bytes for header, got {len(payload)}")

    # Step 3: Unpack the fixed part of the payload (Device ID, Message ID, Timestamp, Data Length, Status Code)
    device_id, message_id, timestamp, data_length, status_code = struct.unpack('>HHIBB', payload[:10])

    # Step 4: Check if the payload length matches the expected length (fixed part + data length)
    expected_length = 10 + data_length
    if len(payload) != expected_length:
        #----print(f"Payload length does not match data length. Expected {expected_length} bytes, got {len(payload)}")
        return False
        raise ValueError(f"Payload length does not match data length. Expected {expected_length} bytes, got {len(payload)}")

    # Step 5: Check for payload expiration (3 minutes = 180 seconds)
    current_time = get_current_time()
    #print("Current timestamp: ", current_time)
    #print("Receiver time: ", timestamp)
    #print("Difference: ", current_time - timestamp)
    if current_time - timestamp > 180 or current_time - timestamp < -10:  # 180 seconds = 3 minutes
        #----print("Payload has expired. Timestamp is older than 3 minutes.")
        return False
        raise ValueError("Payload has expired. Timestamp is older than 3 minutes.")

    # Step 6: Extract the data part
    data = payload[10:10 + data_length]

    # Step 7: Return the decoded values if all checks pass
    return device_id, message_id, timestamp, data.decode('utf-8'), status_code  # Decode data back to string

# # Example usage
# device_id = 0x01A2  # Example device ID (2 bytes)
# message_id = 0x0001  # Example message ID (2 bytes)
# data = b"Hello from ESP32 from Sudeep"  # Bytes data
# status_code = 0x00  # Example status code (1 byte)

# # Create the payload
# payload = create_custom_payload(device_id, message_id, data, status_code)
# print("Encoded Payload:", payload)

# # Simulate decoding the payload after some time
# try:
#     # Wait 10 seconds (for testing)
#     time.sleep(10)
    
#     # Decode the payload
#     decoded = decode_custom_payload(payload)
#     print(f"Decoded -> Device ID: {decoded[0]}, Message ID: {decoded[1]}, Timestamp: {decoded[2]}, Data: {decoded[3]}, Status Code: {decoded[4]}")
# except ValueError as e:
#     print(f"Error decoding payload: {e}")

