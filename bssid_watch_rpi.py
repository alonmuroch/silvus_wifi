import subprocess
import time
import re
import threading
from gpiozero import LED

# Define GPIO pin
led = LED(17)

# RSSI thresholds
STRONG_SIGNAL = -60
WEAK_SIGNAL = -70

# Blinking control
blinking = False
blinker_thread = None
stop_blinking = threading.Event()

def start_blinking():
    global blinker_thread
    stop_blinking.clear()
    
    def blink():
        while not stop_blinking.is_set():
            led.on()
            time.sleep(0.3)
            led.off()
            time.sleep(0.3)
    
    if blinker_thread is None or not blinker_thread.is_alive():
        blinker_thread = threading.Thread(target=blink, daemon=True)
        blinker_thread.start()

def stop_blinking_and_clear():
    stop_blinking.set()
    led.off()
    time.sleep(0.1)  # brief pause to allow LED to update

def get_bssid_and_rssi():
    try:
        result = subprocess.run(
            ['iw', 'dev', 'wlan0', 'link'],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )
        lines = result.stdout.splitlines()
        bssid, rssi = None, None

        for line in lines:
            if "Connected to" in line:
                bssid = "BSSID: " + line.split("Connected to")[-1].strip()
            if "signal:" in line:
                rssi_match = re.search(r'-\d+', line)
                if rssi_match:
                    rssi = int(rssi_match.group(0))
            if bssid and rssi is not None:
                break
        return bssid, rssi
    except Exception as e:
        return f"Error: {e}", None

try:
    while True:
        bssid, rssi = get_bssid_and_rssi()
        print("\033c", end="")  # Clear screen
        print(time.strftime("%Y-%m-%d %H:%M:%S"))
        print(bssid if bssid else "BSSID not found")
        print(f"RSSI: {rssi} dBm" if rssi is not None else "RSSI not found")

        if rssi is None or rssi < WEAK_SIGNAL:
            # Weak or no signal: solid ON
            stop_blinking_and_clear()
            led.on()
        elif WEAK_SIGNAL < rssi < STRONG_SIGNAL:
            # Medium signal: blink
            start_blinking()
        else:
            # Strong signal: off
            stop_blinking_and_clear()
            led.off()

        time.sleep(1)

except KeyboardInterrupt:
    print("\nExiting.")
    stop_blinking.set()
    led.off()
