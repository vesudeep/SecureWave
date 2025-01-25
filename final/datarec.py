import serial
import csv

# Configure the serial port
serial_port = "COM16"  
baud_rate = 115200
csv_file = "received_data.csv"

# Initialize CSV file
with open(csv_file, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Sender ID", "Receiver ID", "Receiver Timestamp", "Range", "Message Size","Signal Strength", "Message ID", "Message", "Status Code"])

# Read from serial and append to CSV
try:
    with serial.Serial(serial_port, baud_rate, timeout=1) as ser:
        print(f"Listening on {serial_port}...")
        while True:
            line = ser.readline().decode().strip()
            if line:
                print(f"Received: {line}")
                # Parse the received data
                data = line.split(",")
                if len(data) == 9:  # Ensure the format is correct
                    with open(csv_file, mode="a", newline="") as file:
                        writer = csv.writer(file)
                        writer.writerow(data)
except KeyboardInterrupt:
    print("Stopped")
except Exception as e:
    print(f"Error: {e}")
