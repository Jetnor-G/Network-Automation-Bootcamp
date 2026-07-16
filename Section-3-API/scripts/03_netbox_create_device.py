#!/usr/bin/env python3
"""
Script 03 — NetBox: Create a Network Device via POST.

Script 01's add_device() showed the POST call itself, but skipped the part
that trips most people up: NetBox foreign keys (site, device role, device
type) have to be sent as numeric IDs, not the names you see in the UI. This
script does the full workflow — look up each ID by name first, then POST
the device — and handles the "it already exists" case you'll hit the
second time you run it.

Note this instance of NetBox does NOT enforce unique device names at the
API level — POSTing the same name twice happily creates two devices with
different IDs instead of returning a 400. So "already exists" here is
checked client-side with a GET before the POST, not by reacting to a
server-side validation error (which is what you'd rely on against a
NetBox instance that does enforce uniqueness).

The site, device role, and device type used below must already exist in
NetBox (create them once via the web UI, or adjust the names to match
whatever's already in your lab's NetBox instance) — this script creates
the *device*, not its prerequisites.

Usage: python3 03_netbox_create_device.py
"""

import sys
import requests

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

NETBOX_URL   = "https://10.100.100.25"
NETBOX_TOKEN = "aHMRkoDJCWgsfTvodfpaV3GXFcMABlWeTOVrCbeg"          # given at lab start

HEADERS = {
    "Authorization": f"Token {NETBOX_TOKEN}",
    "Content-Type":  "application/json",
    "Accept":        "application/json",
}

# Edit these to match a device you actually want to create — the role,
# site, and device type must already exist in NetBox. The defaults below
# are real values confirmed against this lab's NetBox instance (there's
# currently only one device role configured, "Network Device" — NetBox
# doesn't ship one named "Access Switch" out of the box).
NEW_DEVICE_NAME    = "Switch-2"
DEVICE_ROLE_NAME   = "Network Device"
SITE_NAME          = "Arena Stadium"
DEVICE_TYPE_MODEL  = "C9200-48P"    # device-types are matched by "model", not "name"


def lookup_id(endpoint, **filters):
    """GET /api/{endpoint}/?<filters> and return the first match's id.

    This is the lookup step NetBox forces on every create/update call: you
    can't POST "site": "Main Lab" — only "site": 4. Every dcim/ipam
    endpoint supports filtering by its own fields as query params, so the
    same pattern (GET filtered by name, read back "results"[0]["id"]) works
    for sites, device-roles, device-types, manufacturers, and more.
    """
    url = f"{NETBOX_URL}/api/{endpoint}/"
    try:
        resp = requests.get(url, headers=HEADERS, params=filters, timeout=10, verify=False)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        if not results:
            print(f"[ERROR] No '{endpoint}' found matching {filters}.")
            print(f"        Create it in NetBox first, or fix the name in this script.")
            sys.exit(1)
        return results[0]["id"]
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot reach NetBox at {NETBOX_URL}")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] HTTP {resp.status_code}: {e}")
        print(f"        {resp.text}")
        sys.exit(1)


def device_exists(name):
    """Check for a device with this name before creating one.

    Some NetBox instances enforce device-name uniqueness server-side and
    reject a duplicate POST with a 400; this one doesn't, so checking with
    a GET first is the only reliable way to avoid creating duplicates.
    """
    resp = requests.get(
        f"{NETBOX_URL}/api/dcim/devices/",
        headers=HEADERS,
        params={"name": name},
        timeout=10,
        verify=False,
    )
    resp.raise_for_status()
    return resp.json().get("count", 0) > 0


def create_device(name, role_id, site_id, device_type_id, status="planned"):
    """POST a new device. NetBox returns 201 on success.

    Note: this field is called "role" in current NetBox versions — it
    used to be "device_role" in older releases (and the older name is
    still what the object is called in the /dcim/device-roles/ endpoint).
    """
    payload = {
        "name":        name,
        "role":        role_id,
        "site":        site_id,
        "device_type": device_type_id,
        "status":      status,
    }
    resp = requests.post(
        f"{NETBOX_URL}/api/dcim/devices/",
        headers=HEADERS,
        json=payload,
        timeout=10,
        verify=False,
    )
    if resp.status_code == 201:
        device = resp.json()
        print(f"[+] Device '{name}' created (ID: {device['id']}, status: {status})")
        return device
    print(f"[!] Could not create device: HTTP {resp.status_code}")
    print(f"    {resp.text}")
    sys.exit(1)


if __name__ == "__main__":
    print(f"[*] Resolving role '{DEVICE_ROLE_NAME}', site '{SITE_NAME}', "
          f"and device type '{DEVICE_TYPE_MODEL}' to their NetBox IDs ...")
    role_id        = lookup_id("dcim/device-roles", name=DEVICE_ROLE_NAME)
    site_id        = lookup_id("dcim/sites", name=SITE_NAME)
    device_type_id = lookup_id("dcim/device-types", model=DEVICE_TYPE_MODEL)
    print(f"    role={role_id}  site={site_id}  device_type={device_type_id}")

    print(f"\n[*] Checking whether '{NEW_DEVICE_NAME}' already exists ...")
    if device_exists(NEW_DEVICE_NAME):
        print(f"[!] '{NEW_DEVICE_NAME}' already exists in NetBox — nothing to create.")
    else:
        print(f"[*] Creating device '{NEW_DEVICE_NAME}' ...")
        create_device(NEW_DEVICE_NAME, role_id, site_id, device_type_id)

    print("\n[+] Done. Re-run this script unchanged to see the duplicate-name handling kick in.")
