import subprocess
import time
import re
import threading
import logging
import os
from gpiozero import LED, Device
from gpiozero.pins.lgpio import LGPIOFactory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console + Docker logs
        # logging.FileHandler("/app/bssid_watcher.log")  # Optional file log
    ]
)

# Set up GPIO (using lgpio backend)
Device.pin_factory = LGPIOFactory()
led = LED(17)

# RSSI thresholds (in dBm)
STRONG_SIGNAL = int(os.getenv("STRONG_SIGNAL", -60))
WEAK_SIGNAL = int(os.getenv("WEAK_SIGNAL", -70))

# State control
blinking = False
blinker_thread = None
stop_blinking = threading.Event()
last_signal_state = None  # Tracks last LED state to avoid redundant GPIO ops

def turn_led_on():
    if not led.is_lit:
        led.on()

def turn_led_off():
    if led.is_lit:
        led.off()

def start_blinking():
    global blinker_thread, blinking
    if blinking:
        return

    stop_blinking.clear()

    def blink():
        while not stop_blinking.is_set():
            led.on()
            time.sleep(0.3)
            led.off()
            time.sleep(0.3)

    blinker_thread = threading.Thread(target=blink, daemon=True)
    blinker_thread.start()
    blinking = True

def stop_blinking_and_clear():
    global blinking
    stop_blinking.set()
    time.sleep(0.1)
    led.off()
    blinking = False

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

def update_led_based_on_rssi(rssi):
    global last_signal_state

    if rssi is None or rssi < WEAK_SIGNAL:
        if last_signal_state != "weak":
            stop_blinking_and_clear()
            turn_led_on()
            logging.info("Signal weak or missing — LED ON")
            last_signal_state = "weak"
    elif WEAK_SIGNAL < rssi < STRONG_SIGNAL:
        if last_signal_state != "medium":
            start_blinking()
            logging.info("Signal medium — LED BLINKING")
            last_signal_state = "medium"
    else:
        if last_signal_state != "strong":
            stop_blinking_and_clear()
            turn_led_off()
            logging.info("Signal strong — LED OFF")
            last_signal_state = "strong"

def main():
    try:
        while True:
            bssid, rssi = get_bssid_and_rssi()
            logging.info(bssid if bssid else "BSSID not found")
            logging.info(f"RSSI: {rssi} dBm" if rssi is not None else "RSSI not found")

            update_led_based_on_rssi(rssi)
            logging.info("\n")
            time.sleep(1)

    except KeyboardInterrupt:
        logging.info("Exiting gracefully...")
        stop_blinking.set()
        led.off()

if __name__ == "__main__":
    main()
