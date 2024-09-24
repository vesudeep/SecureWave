import network
import espnow
import time

# Setup Wi-Fi interface in station mode (Wi-Fi must be on for espnow)
w0 = network.WLAN(network.STA_IF)
w0.active(True)

# ESP-NOW initialization (no need to call init())
e = espnow.ESPNow()
e.active(True)  # Activate ESP-NOW

# Add peer devices (replace with actual MAC addresses of other ESP32s)
# You need to know the MAC addresses of the other ESP32s beforehand
peer1_mac = b'\x24\x6f\x28\x12\x34\x56'  # ESP32 peer1 MAC address
peer2_mac = b'\xcc{\\%jL'  # ESP32 peer2 MAC address

# Add peers to ESP-NOW
e.add_peer(peer1_mac)
e.add_peer(peer2_mac)

# Sending data to peers
def send_message(message):
    e.send(peer1_mac, message, True)  # Send message to peer1
    e.send(peer2_mac, message, True)  # Send message to peer2

# Receiving data from peers
def receive_message():
    while True:
        print("inside recieve")
        host, msg = e.irecv()  # Non-blocking receive
        if msg:  # If message received
            print(f"Received message from {host}: {msg}")
            break

# Example loop: alternating between sending and receiving
try:
    while True:
        send_message(b"Hello from ESP32 from sudeep")
        time.sleep(2)  # Wait before next send
        receive_message()
        time.sleep(2)
except KeyboardInterrupt:
    print("Process stopped")

# Remove peers when done
e.del_peer(peer1_mac)
e.del_peer(peer2_mac)

