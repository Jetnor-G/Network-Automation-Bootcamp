#!/usr/bin/env python3
"""
Script 03 — NetBox Inventory: Build dynamic Ansible inventory from NetBox API.
Usage: python3 03_netbox_inventory.py
       ansible-playbook pb.yml -i 03_netbox_inventory.py
"""

import json
import sys
import requests

NETBOX_URL   = "http://10.0.0.100:8000"
NETBOX_TOKEN = "your_netbox_api_token_here"

HEADERS = {
    "Authorization": f"Token {NETBOX_TOKEN}",
    "Content-Type":  "application/json",
    "Accept":        "application/json",
}


def get_devices():
    url = f"{NETBOX_URL}/api/dcim/devices/?status=active&limit=1000"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json().get("results", [])
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot reach NetBox at {NETBOX_URL}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as err:
        print(f"[ERROR] {err}", file=sys.stderr)
        sys.exit(1)


def build_inventory(devices):
    inventory = {"_meta": {"hostvars": {}}, "all": {"children": []}}

    for device in devices:
        hostname    = device["name"]
        role        = device.get("device_role", {}).get("slug", "ungrouped")
        primary_ip  = device.get("primary_ip", {})
        ip_address  = primary_ip.get("address", "").split("/")[0] if primary_ip else ""
        platform    = device.get("platform", {}).get("slug", "ios") if device.get("platform") else "ios"

        # Add group
        if role not in inventory:
            inventory[role] = {"hosts": [], "vars": {}}
            inventory["all"]["children"].append(role)

        inventory[role]["hosts"].append(hostname)

        # Per-host vars
        inventory["_meta"]["hostvars"][hostname] = {
            "ansible_host":       ip_address,
            "ansible_network_os": platform,
            "ansible_user":       "admin",
            "netbox_id":          device["id"],
            "netbox_site":        device.get("site", {}).get("name", "") if device.get("site") else "",
        }

    return inventory


if __name__ == "__main__":
    devices   = get_devices()
    inventory = build_inventory(devices)
    print(json.dumps(inventory, indent=2))
