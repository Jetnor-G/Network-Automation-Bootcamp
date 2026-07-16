#!/usr/bin/env python3
"""
Script 01 — NetBox: Query active devices and optionally add a new one.

NetBox is this lab's source of truth (IPAM/DCIM). Its REST API is how
scripts and Ansible read/write inventory data instead of hand-editing it
through the web UI. This script demonstrates the two most common patterns:
  - GET  a filtered, paginated list of objects (get_devices)
  - POST a new object                        (add_device)

Usage: python3 01_netbox_get_devices.py
"""

import sys
import requests

# NetBox in this lab uses a self-signed HTTPS certificate, so requests
# would normally print an "InsecureRequestWarning" for every call unless
# we silence it here (we still skip cert verification below with verify=False).
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

NETBOX_URL   = "https://10.100.100.25"
NETBOX_TOKEN = "aHMRkoDJCWgsfTvodfpaV3GXFcMABlWeTOVrCbeg"          # given at lab start

# NetBox authenticates API calls via a per-user token in the Authorization
# header — "Token <value>" — instead of a username/password on every request.
HEADERS = {
    "Authorization": f"Token {NETBOX_TOKEN}",
    "Content-Type":  "application/json",
    "Accept":        "application/json",
}


def get_devices():
    # status=active and limit=50 are query-string filters supported by the
    # NetBox API — most list endpoints accept filters like this instead of
    # returning (and making you page through) every object.
    url = f"{NETBOX_URL}/api/dcim/devices/?status=active&limit=50"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        resp.raise_for_status()  # raises HTTPError for any 4xx/5xx status
        # NetBox wraps list responses in an envelope: {"count", "next",
        # "previous", "results"} — the actual objects are under "results".
        return resp.json().get("results", [])
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot reach NetBox at {NETBOX_URL}")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] HTTP {resp.status_code}: {e}")
        print(f"        {resp.text}")  # NetBox's JSON error body has the real reason
        sys.exit(1)


def print_device_table(devices):
    print(f"\n{'Name':<20} {'IP Address':<18} {'Role':<20} {'Site':<15} {'Status'}")
    print("-" * 85)
    for d in devices:
        # NetBox represents related objects (role, site, status, primary_ip)
        # as nested dicts — or null if unset. "(d.get(...) or {})" guards
        # against a None value before chaining another .get() on it.
        # Note: this field is called "role" in current NetBox versions —
        # it used to be "device_role" in older releases.
        name    = d.get("name", "N/A")
        ip      = (d.get("primary_ip") or {}).get("address", "N/A")
        role    = (d.get("role") or {}).get("name", "N/A")
        site    = (d.get("site") or {}).get("name", "N/A")
        status  = (d.get("status") or {}).get("label", "N/A")
        print(f"{name:<20} {ip:<18} {role:<20} {site:<15} {status}")
    print()


def add_device(name, role_id, site_id, device_type_id):
    """Exercise extension: add a new device via POST.

    Unlike GET, a POST body is the new object's data as JSON. NetBox
    expects foreign keys (role, site, device_type) as numeric IDs, not
    names — look those IDs up via their own GET endpoints first (e.g.
    /api/dcim/device-roles/) if you don't already know them.
    """
    payload = {
        "name":         name,
        "role":         role_id,
        "site":         site_id,
        "device_type":  device_type_id,
        "status":       "planned",
    }
    resp = requests.post(
        f"{NETBOX_URL}/api/dcim/devices/",
        headers=HEADERS,
        json=payload,   # requests serializes this dict to a JSON body for us
        timeout=10,
        verify=False,
    )
    if resp.status_code == 201:   # 201 Created — the standard success code for POST
        print(f"[+] Device '{name}' created (ID: {resp.json()['id']})")
    else:
        print(f"[!] Could not create device: HTTP {resp.status_code}")
        print(resp.text)


if __name__ == "__main__":
    print(f"[*] Querying devices from NetBox ({NETBOX_URL}) ...")
    devices = get_devices()
    print(f"    Found {len(devices)} active device(s).")
    print_device_table(devices)
