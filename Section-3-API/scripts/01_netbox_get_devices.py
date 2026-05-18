#!/usr/bin/env python3
"""
Script 01 — NetBox: Query active devices and optionally add a new one.
Usage: python3 01_netbox_get_devices.py
"""

import sys
import requests

NETBOX_URL   = "http://10.0.0.100:8000"
NETBOX_TOKEN = "your_netbox_token_here"          # given at lab start

HEADERS = {
    "Authorization": f"Token {NETBOX_TOKEN}",
    "Content-Type":  "application/json",
    "Accept":        "application/json",
}


def get_devices():
    url = f"{NETBOX_URL}/api/dcim/devices/?status=active&limit=50"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return resp.json().get("results", [])
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot reach NetBox at {NETBOX_URL}")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] HTTP {resp.status_code}: {e}")
        sys.exit(1)


def print_device_table(devices):
    print(f"\n{'Name':<20} {'IP Address':<18} {'Role':<20} {'Site':<15} {'Status'}")
    print("-" * 85)
    for d in devices:
        name    = d.get("name", "N/A")
        ip      = (d.get("primary_ip") or {}).get("address", "N/A")
        role    = (d.get("device_role") or {}).get("name", "N/A")
        site    = (d.get("site") or {}).get("name", "N/A")
        status  = (d.get("status") or {}).get("label", "N/A")
        print(f"{name:<20} {ip:<18} {role:<20} {site:<15} {status}")
    print()


def add_device(name, role_id, site_id, device_type_id):
    """Exercise extension: add a new device via POST."""
    payload = {
        "name":         name,
        "device_role":  role_id,
        "site":         site_id,
        "device_type":  device_type_id,
        "status":       "planned",
    }
    resp = requests.post(
        f"{NETBOX_URL}/api/dcim/devices/",
        headers=HEADERS,
        json=payload,
        timeout=10,
    )
    if resp.status_code == 201:
        print(f"[+] Device '{name}' created (ID: {resp.json()['id']})")
    else:
        print(f"[!] Could not create device: HTTP {resp.status_code}")
        print(resp.text)


if __name__ == "__main__":
    print(f"[*] Querying devices from NetBox ({NETBOX_URL}) ...")
    devices = get_devices()
    print(f"    Found {len(devices)} active device(s).")
    print_device_table(devices)
