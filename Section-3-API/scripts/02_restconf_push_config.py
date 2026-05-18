#!/usr/bin/env python3
"""
Script 02 — RESTCONF PUT: Push interface configuration to IOS-XE.
Usage: python3 02_restconf_push_config.py
"""

import json
import sys
import requests
from requests.auth import HTTPBasicAuth

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEVICE_IP  = "10.0.0.1"
USERNAME   = "admin"
PASSWORD   = "Lab@1234"
BASE_URL   = f"https://{DEVICE_IP}/restconf/data"
INTERFACE  = "GigabitEthernet0/1"

HEADERS = {
    "Content-Type": "application/yang-data+json",
    "Accept":       "application/yang-data+json",
}

PAYLOAD = {
    "ietf-interfaces:interface": {
        "name":        INTERFACE,
        "description": "LAN_SEGMENT_AUTOMATED",
        "type":        "iana-if-type:ethernetCsmacd",
        "enabled":     True,
        "ietf-ip:ipv4": {
            "address": [
                {"ip": "10.0.0.1", "prefix-length": 24}
            ]
        }
    }
}

def push_interface_config():
    iface_encoded = INTERFACE.replace("/", "%2F")
    url = f"{BASE_URL}/ietf-interfaces:interfaces/interface={iface_encoded}"

    print(f"[*] Pushing config to {INTERFACE} on {DEVICE_IP} ...")
    print(f"    Payload:\n{json.dumps(PAYLOAD, indent=4)}\n")

    try:
        response = requests.put(
            url,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            headers=HEADERS,
            json=PAYLOAD,
            verify=False,
            timeout=10,
        )

        if response.status_code in (200, 201, 204):
            print(f"[+] Config applied successfully (HTTP {response.status_code})")
        else:
            print(f"[!] Unexpected response: HTTP {response.status_code}")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Could not connect to {DEVICE_IP}.")
        sys.exit(1)
    except requests.exceptions.HTTPError as err:
        print(f"[ERROR] {err}")
        sys.exit(1)


if __name__ == "__main__":
    push_interface_config()
