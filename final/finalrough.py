import network
import espnow
import time
import machine
from tstmp import *
from payld import *
from jwttkn import *

ssid = 'Wokwi-GUEST'
password = ''

get_current_time_from_ntp(ssid, password)
# Setup for pin to indicate reception (you can connect an LED to pin 2)
pin2 = machine.Pin(2, machine.Pin.OUT)

# Setup Wi-Fi interface in station mode
w0 = network.WLAN(network.STA_IF)
w0.active(True)

# ESP-NOW initialization
e = espnow.ESPNow()
e.active(True)

# Broadcast MAC address (used to send to all peers on the same channel)
broadcast_mac = b'\xff\xff\xff\xff\xff\xff'

# Add broadcast peer (all devices listening on the channel will receive the data)
e.add_peer(broadcast_mac)

# Sending data to all 14 channels
def send_message_to_all_channels(message):
    device_id = 0x01A2  # Example device ID (2 bytes)
    message_id = 0x0001  # Example message ID (2 bytes)
    data = message  # Bytes data
    status_code = 0x00  # Example status code (1 byte)

    payload = create_custom_payload(device_id, message_id, data, status_code)
    print("Encoded Payload:", payload)

    jwt_token = create_jwt(payload)
    print("JWT Token:", jwt_token)

    for channel in range(1, 15):  # Loop through channels 1 to 14
        print(f"Switching to channel {channel} to send data")
        w0.config(channel=channel)  # Set the Wi-Fi to the current channel
        # e.send(broadcast_mac, message)  # Send the message to the broadcast address
        e.send(broadcast_mac, jwt_token)
        time.sleep(0.1)  # Small delay to ensure message is sent before switching channels

# Receiving data from all 14 channels
def receive_message_from_all_channels():
    for channel in range(1, 15):  # Loop through channels 1 to 14
        print(f"Switching to channel {channel} to receive data")
        w0.config(channel=channel)  # Set the Wi-Fi to the current channel
        host, msg = e.irecv()  # Non-blocking receive
        if msg:  # If a message is received
            print(f"Received message from {host} on channel {channel}: {msg}")
            jwt_tokenn = msg
            decoded_payload = validate_jwt(jwt_tokenn)
            if decoded_payload:
                print("Valid Token. Payload:", decoded_payload)
                decoded = decode_custom_payload(decoded_payload)
                print(f"Decoded -> Device ID: {decoded[0]}, Message ID: {decoded[1]}, Timestamp: {decoded[2]}, Data: {decoded[3]}, Status Code: {decoded[4]}")
            else:
                print("Invalid Token")
            pin2.value(1)  # Blink LED on receiving message
            time.sleep(0.3)
            pin2.value(0)
            return  # Exit after receiving the first message
        time.sleep(0.1)  # Short delay to allow time for receiving data

# Main loop: alternating between sending data to all channels and receiving messages from all channels
try:
    while True:
        print("Sending message to all channels...")
        print(get_current_time())
        send_message_to_all_channels(b"Hello from ESP32 to all channels")  # Send message to all channels
        time.sleep(1)  # Shorter delay before listening

        print("Listening for incoming messages from all channels...")
        print(get_current_time())
        receive_message_from_all_channels()  # Check if any messages are received
        time.sleep(1)  # Shorter delay before next round
except KeyboardInterrupt:
    print("Process stopped")

# Remove the broadcast peer when done
e.del_peer(broadcast_mac)

