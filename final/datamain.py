import network
import espnow
import time
import machine
import _thread  # Import the multithreading module
from tstmp import *
from payld import *
from jwttkn import *
from aes import *
import random

ssid = 'Wokwi-GUEST'
password = ''

# ssid = 'Sudeep’s iPhone'
# password = 'sude1234'

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

def unix_to_timestamp(unix_time):
    # Convert Unix time to a localtime tuple
    local_time = time.localtime(unix_time)
    
    # Format the time as a string (YYYY-MM-DD HH:MM:SS)
    formatted_time = "{:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(
        local_time[0], local_time[1], local_time[2],  # Year, Month, Day
        local_time[3], local_time[4], local_time[5]   # Hour, Minute, Second
    )
    return formatted_time

message_id = [0x0001, 0x0005, 0x0032, 0x0240]
#device_id = [0x02CC, 0x0400, 0x1945, 0x14D5]
device_id = [0x0011, 0x0406, 0x1964, 0x157C]
status_code = [0x01, 0x00, 0x02, 0x10]
message = [b"Welcome aboard Device is now connected.", b"Welcome Device is now online.", b"Welcome Device is powered up and ready.", b"hello from device."]
num = [0,1,2,3]

#message_id = 0x0001
#device_id = 0x01A2
#status_code = 0x00
#data = b"Hello from Sudeep 1 to all channels"
#message = b"Hello from Sudeep 1 to all channels"

# Function to send messages to all channels
def send_message_to_all_channels():
    #message = data
    

    while True:
        #print("Inside send")
        rnum = random.choice(num)
        payload = create_custom_payload(random.choice(device_id), message_id[rnum], message[rnum], status_code[rnum])
        jwt_token = create_jwt(payload)
        encrypted_payload = encrypt_payload(jwt_token, key)
        for channel in range(1, 15):  # Loop through channels 1 to 14
            #print(f"{message} : Inside channel {channel}")
            w0.config(channel=channel)  # Set the Wi-Fi to the current channel
            e.send(broadcast_mac, encrypted_payload)  # Send the message to the broadcast address
            time.sleep(0.1)  # Small delay to ensure message is sent before switching channels
        time.sleep(1)  # Pause before the next round of sending

# Function to estimate RSSI-based distance
def rssi_to_distance(rssi, tx_power=-40, path_loss_exponent=3.0, num_samples=5):
    global last_distance

    rssi_samples = [rssi for _ in range(num_samples)]  # Replace with actual RSSI readings
    avg_rssi = sum(rssi_samples) / len(rssi_samples)

    distance = 10 ** ((tx_power - avg_rssi) / (10 * path_loss_exponent))

    if 'last_distance' in globals():
        distance = 0.8 * last_distance + 0.2 * distance  # Smooth factor
    last_distance = distance

    return distance

# Function to receive messages from all channels
def receive_message_from_all_channels():
    while True:
        for channel in range(1, 15):  # Loop through channels 1 to 14
            w0.config(channel=channel)  # Set the Wi-Fi to the current channel
            host, msg = e.irecv()  # Non-blocking receive
            if msg:  # If a message is received
                decrypted_payloadtkn = decrypt_payload(msg, key)
                jwt_tokenn = decrypted_payloadtkn
                decoded_payload = validate_jwt(jwt_tokenn)
                if decoded_payload:
                    decoded = decode_custom_payload(decoded_payload)
                    if decoded:
                        rdevice_id, rmessage_id, rtimestamp, rdata, rstatus_code = decoded
                        rnum = random.choice(num)
                        print(f"{device_id[rnum]},{rdevice_id},{unix_to_timestamp(rtimestamp)},{rssi_to_distance(e.peers_table[host][0])},{len(rdata)},{e.peers_table[host][0]},{rmessage_id},{rdata},{rstatus_code}")
                        pin2.value(1)  # Blink LED on receiving message
                        time.sleep(0.3)
                        pin2.value(0)
            time.sleep(0.1)  # Short delay before trying the next channel

# Start threads for sending and receiving messages
try:
    _thread.start_new_thread(send_message_to_all_channels, ())
    _thread.start_new_thread(receive_message_from_all_channels, ())
    # Keep the main thread running
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("Process stopped")

# Remove the broadcast peer when done
e.del_peer(broadcast_mac)

