import requests

def configure_virtual_ip_sequence(radio_ip: str, virtual_ip_disable: str = "0"):
    """
    Sends a single batch JSON-RPC request to configure the virtual IP and VPN settings.

    :param radio_ip: IP address of the Silvus radio
    :param virtual_ip_disable: "0" to enable, "1" to disable
    """
    url = f"http://{radio_ip}/streamscape_api"

    batch_payload = [
        {"jsonrpc": "2.0", "method": "virtual_ip_disable", "id": 1, "params": [virtual_ip_disable]},
        {"jsonrpc": "2.0", "method": "virtual_ip_gateway", "id": 2, "params": ["172.20.0.1"]},
        {"jsonrpc": "2.0", "method": "vpn_address", "id": 3, "params": ["192.168.68.201", "9000"]},
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
