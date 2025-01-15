import network
import espnow
import time
import machine
from tstmp import *
from payld import *
from jwttkn import *
from aes import *

#ssid = 'Wokwi-GUEST'
#password = ''

ssid = 'Sudeep’s iPhone'
password = 'sude1234'

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

message_id = 0x0001
device_id = 0x01A2
status_code = 0x00
data = ""
# Sending data to all 14 channels
def send_message_to_all_channels(message):
      # Example device ID (2 bytes)
      # Example message ID (2 bytes)
    data = message  # Bytes data
      # Example status code (1 byte)

    payload = create_custom_payload(device_id, message_id, data, status_code)
    #----print("Encoded Payload:", payload)

    jwt_token = create_jwt(payload)
    #----print("JWT Token:", jwt_token)

    encrypted_payload = encrypt_payload(jwt_token, key)
    #----print("Encrypted Payload:", encrypted_payload)

    for channel in range(1, 15):  # Loop through channels 1 to 14
        #----print(f"Switching to channel {channel} to send data")
        w0.config(channel=channel)  # Set the Wi-Fi to the current channel
        # e.send(broadcast_mac, message)  # Send the message to the broadcast address
        e.send(broadcast_mac, encrypted_payload)
        time.sleep(0.1)  # Small delay to ensure message is sent before switching channels
        
def rssi_to_distance(rssi, tx_power=-40, path_loss_exponent=3.0, num_samples=5):
    """
    Estimate distance based on RSSI with calibration and averaging.

    Parameters:
    - rssi: Received signal strength in dBm.
    - tx_power: Calibrated transmitter power in dBm.
    - path_loss_exponent: Environmental factor (calibrate this value).
    - num_samples: Number of samples for averaging RSSI.

    Returns:
    - Estimated distance in meters.
    """
    global last_distance
    
    # Average RSSI samples
    rssi_samples = [rssi for _ in range(num_samples)]  # Replace with actual RSSI readings
    avg_rssi = sum(rssi_samples) / len(rssi_samples)
    
    # Calculate distance
    distance = 10 ** ((tx_power - avg_rssi) / (10 * path_loss_exponent))
    
    # Smooth the output (optional)
    if 'last_distance' in globals():
        distance = 0.8 * last_distance + 0.2 * distance  # Smooth factor
    last_distance = distance
    
    return distance



# Receiving data from all 14 channels
def receive_message_from_all_channels():
    for channel in range(1, 15):  # Loop through channels 1 to 14
        #----print(f"Switching to channel {channel} to receive data")
        w0.config(channel=channel)  # Set the Wi-Fi to the current channel
        host, msg = e.irecv()  # Non-blocking receive
        if msg:  # If a message is received
            #----print(f"Received message from {host} on channel {channel}: {msg}")
            #print(e.peers_table[host])
            #----print(f"{rssi_to_distance(e.peers_table[host][0])} meters")
            msgg = msg
            decrypted_payloadtkn = decrypt_payload(msg, key)
            #----print("Decrypted Payload:", decrypted_payloadtkn)
            jwt_tokenn = decrypted_payloadtkn
            decoded_payload = validate_jwt(jwt_tokenn)
            if decoded_payload:
                #----print("Valid Token. Payload:", decoded_payload)
                decoded = decode_custom_payload(decoded_payload)
                if decoded:
                    rdevice_id, rmessage_id, rtimestamp, rdata, rstatus_code = decoded
                    #print(f"Decoded -> Device ID: {decoded[0]}, Message ID: {decoded[1]}, Timestamp: {decoded[2]}, Data: {decoded[3]}, Status Code: {decoded[4]}")
                    print(f"{device_id},{rdevice_id},{rtimestamp},{rssi_to_distance(e.peers_table[host][0])},{len(rdata)},{e.peers_table[host][0]},{rmessage_id},{rdata},{rstatus_code}")
                    pin2.value(1)  # Blink LED on receiving message
                    time.sleep(0.3)
                    pin2.value(0)
            else:
                #----print("Invalid Token")
            return  # Exit after receiving the first message
        time.sleep(0.1)  # Short delay to allow time for receiving data

# Main loop: alternating between sending data to all channels and receiving messages from all channels
try:
    while True:
        #----print("Sending message to all channels...")
        #print(get_current_time())
        send_message_to_all_channels(b"Hello from Sudeep 1 to all channels")  # Send message to all channels
        time.sleep(1)  # Shorter delay before listening

        #----print("Listening for incoming messages from all channels...")
        #print(get_current_time())
        receive_message_from_all_channels()  # Check if any messages are received
        time.sleep(1)  # Shorter delay before next round
except KeyboardInterrupt:
    print("Process stopped")

# Remove the broadcast peer when done
e.del_peer(broadcast_mac)







