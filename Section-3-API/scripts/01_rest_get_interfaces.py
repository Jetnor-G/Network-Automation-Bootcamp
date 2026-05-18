#!/usr/bin/env python3
"""
Script 01 — REST GET: Query interface status from IOS-XE via RESTCONF.
Usage: python3 01_rest_get_interfaces.py
"""

import json
import sys
import requests
from requests.auth import HTTPBasicAuth

# Suppress SSL warnings for lab environment
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEVICE_IP   = "10.0.0.1"
USERNAME    = "admin"
PASSWORD    = "Lab@1234"
BASE_URL    = f"https://{DEVICE_IP}/restconf/data"

HEADERS = {
    "Content-Type": "application/yang-data+json",
    "Accept":       "application/yang-data+json",
}

def get_interfaces():
    url = f"{BASE_URL}/ietf-interfaces:interfaces"
    try:
        response = requests.get(
            url,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            headers=HEADERS,
            verify=False,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Could not connect to {DEVICE_IP}. Is the device reachable?")
        sys.exit(1)
    except requests.exceptions.HTTPError as err:
        print(f"[ERROR] HTTP {response.status_code}: {err}")
        sys.exit(1)


def print_interface_table(data):
    interfaces = data.get("ietf-interfaces:interfaces", {}).get("interface", [])
    print(f"\n{'Interface':<30} {'Status':<10} {'IP Address':<20} {'Description'}")
    print("-" * 80)
    for iface in interfaces:
        name        = iface.get("name", "N/A")
        enabled     = "UP" if iface.get("enabled", False) else "DOWN"
        description = iface.get("description", "")
        ipv4        = iface.get("ietf-ip:ipv4", {}).get("address", [])
        ip_addr     = f"{ipv4[0]['ip']}/{ipv4[0]['prefix-length']}" if ipv4 else "N/A"
        print(f"{name:<30} {enabled:<10} {ip_addr:<20} {description}")
    print()


if __name__ == "__main__":
    print(f"[*] Querying interfaces on {DEVICE_IP} ...")
    data = get_interfaces()
    print_interface_table(data)
    print("[+] Done.")
