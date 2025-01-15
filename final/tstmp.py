import network
import ntptime
import time
import machine

# Define your timezone offset in hours and minutes
# For example, IST (UTC+5:30)

pin2 = machine.Pin(2, machine.Pin.OUT)

UTC_OFFSET_HOURS = 5
UTC_OFFSET_MINUTES = 30

wlan = network.WLAN(network.STA_IF)


def connect_wifi(ssid, password):
    wlan.active(True)
    try:
        wlan.connect(ssid, password)
    except Exception as e:
        #machine.deepsleep(100)
        print(e)
        
    while not wlan.isconnected():
        #----print("Connecting to Wi-Fi...")
        time.sleep(1)

    #----print("Connected to Wi-Fi")
    #impprint("Network config:", wlan.ifconfig())

def set_time():
    try:
        ntptime.settime()  # Synchronize time with NTP server
        #----print("Time synchronized with NTP server.")
        pin2.value(1)  # Blink LED on receiving message
        time.sleep(0.3)
        pin2.value(0)
        #wlan.disconnect()  # Optionally disconnect from Wi-Fi
        #impprint("Wi-Fi disconnected")
    except Exception as e:
        #----print("Failed to synchronize time:", e)
        return False
        #impprint("Failed to synchronize time:", e)

def get_current_time():
    current_time = time.localtime()
    
    # Adjust time according to the UTC offset
    adjusted_hour = (current_time[3] + UTC_OFFSET_HOURS) % 24
    adjusted_minute = (current_time[4] + UTC_OFFSET_MINUTES) % 60
    
    # Handle overflow for minutes
    if current_time[4] + UTC_OFFSET_MINUTES >= 60:
        adjusted_hour = (adjusted_hour + 1) % 24

    # Format only the time (HH:MM:SS)
    formatted_time = "{:02}:{:02}:{:02}".format(
        adjusted_hour, adjusted_minute, current_time[5]
    )

    # Convert to Unix timestamp
    unix_timestamp = time.mktime(current_time)  # Get Unix timestamp
    #print(formatted_time)

    #return formatted_time, current_time, unix_timestamp  # Return all three
    return unix_timestamp

def get_current_time_from_ntp(ssid, password):
    """Main function to get current time from NTP server."""
    connect_wifi(ssid, password)
    #set_time()
    while(set_time() == False):
        #----print("Improper internet connection trying again")
        #set_time()
        time.sleep(1)
    wlan.disconnect()
    #----print("Wi-Fi disconnected")
    return get_current_time()  # Return formatted time, current time, and Unix timestamp

# Example usage:
# ssid = 'Wokwi-GUEST'
# password = ''

# Call the function and print the current time and Unix timestamp
# formatted_time, current_time, unix_timestamp = get_current_time_from_ntp(ssid, password)
# print("Current Time:", formatted_time)
# print("Current Time Tuple:", current_time)
# print("Unix Timestamp:", unix_timestamp)


