import requests

import os
VPN_ADDRESS = os.environ.get("N2N_SUPERNODE_URL", "192.168.68.5")

def configure_virtual_ip_sequence(radio_ip: str, virtual_ip_disable: str = "0"):
    """
    Sends a single batch JSON-RPC request to configure the virtual IP and VPN settings.
    """
    url = f"http://{radio_ip}/streamscape_api"

    batch_payload = [
        {"jsonrpc": "2.0", "method": "virtual_ip_disable", "id": 1, "params": [virtual_ip_disable]},
        {"jsonrpc": "2.0", "method": "virtual_ip_gateway", "id": 2, "params": ["172.20.0.1"]},
        {"jsonrpc": "2.0", "method": "vpn_address", "id": 3, "params": [VPN_ADDRESS, "9000"]},
        {"jsonrpc": "2.0", "method": "vpn_disable", "id": 4, "params": ["0"]},
        {"jsonrpc": "2.0", "method": "setenvlinsingle", "id": 5, "params": ["virtual_ip_disable"]},
        {"jsonrpc": "2.0", "method": "setenvlinsingle", "id": 6, "params": ["virtual_ip_gateway"]},
        {"jsonrpc": "2.0", "method": "setenvlinsingle", "id": 7, "params": ["vpn_address"]},
        {"jsonrpc": "2.0", "method": "setenvlinsingle", "id": 8, "params": ["vpn_disable"]}
    ]

    try:
        response = requests.post(url, json=batch_payload, timeout=5)
        response.raise_for_status()
        print(f"[✓] Sent config with virtual_ip_disable={virtual_ip_disable}")
        for item in response.json():
            print(f"ID: {item.get('id')} → {item.get('result', item.get('error'))}")
    except requests.RequestException as e:
        print(f"[✘] HTTP error: {e}")
    except ValueError:
        print("[✘] Failed to parse JSON response.")


def refresh_ptt_settings(radio_ip: str):
    """
    Sends a batch JSON-RPC request to refresh PTT settings on the radio.
    """
    url = f"http://{radio_ip}/streamscape_api"
    
    batch_payload = []
    # ptt_mcast_group settings
    batch_payload.append({"jsonrpc": "2.0", "method": "ptt_mcast_group", "id": 1, "params": ["0", "239.0.0.190"]})
    for i in range(1, 16):
        batch_payload.append({"jsonrpc": "2.0", "method": "ptt_mcast_group", "id": i+1, "params": [str(i), ""]})
    # Remaining PTT settings
    batch_payload += [
        {"jsonrpc": "2.0", "method": "ptt_status", "id": 1, "params": ["1"]},
        {"jsonrpc": "2.0", "method": "setenvlinsingle", "id": 2, "params": ["ptt_status"]}
        # {"jsonrpc": "2.0", "method": "ptt_active_2_mcast_group", "id": 17, "params": ["_"]},
        # {"jsonrpc": "2.0", "method": "ptt_speaker_vol", "id": 18, "params": ["80"]},
        # {"jsonrpc": "2.0", "method": "ptt_mic_bias", "id": 19, "params": ["0"]},
        # {"jsonrpc": "2.0", "method": "ptt_mic_vol", "id": 20, "params": ["80"]},
        # {"jsonrpc": "2.0", "method": "ptt_mic_type", "id": 21, "params": ["1"]},
        # {"jsonrpc": "2.0", "method": "ptt_active_mcast_group", "id": 22, "params": ["0_0"]},
        # {"jsonrpc": "2.0", "method": "ptt_audio_encoder_type", "id": 23, "params": ["2"]},
        # {"jsonrpc": "2.0", "method": "opus_rate", "id": 24, "params": ["30000"]},
        # {"jsonrpc": "2.0", "method": "ptt_beep_volume", "id": 25, "params": ["100"]},
        # {"jsonrpc": "2.0", "method": "ptt_aggr_delay", "id": 26, "params": ["180"]},
        # {"jsonrpc": "2.0", "method": "ptt_hq_link_notifications", "id": 27, "params": ["324743"]},
        # {"jsonrpc": "2.0", "method": "ptt_levels_link_notifications", "id": 28, "params": ["10_20"]},
        # {"jsonrpc": "2.0", "method": "ptt_level_change_link_notifications", "id": 29, "params": ["0"]},
        # {"jsonrpc": "2.0", "method": "ptt_no_link_notifications", "id": 30, "params": ["0"]},
        # {"jsonrpc": "2.0", "method": "ptt_notification_volume", "id": 31, "params": ["100"]},
        # {"jsonrpc": "2.0", "method": "ptt_gpio_pin_mode", "id": 32, "params": ["0"]}
    ]

    try:
        response = requests.post(url, json=batch_payload, timeout=5)
        response.raise_for_status()
        print("[✓] Refreshed PTT settings.")
        for item in response.json():
            print(f"ID: {item.get('id')} → {item.get('result', item.get('error'))}")
    except requests.RequestException as e:
        print(f"[✘] HTTP error: {e}")
    except ValueError:
        print("[✘] Failed to parse JSON response.")
