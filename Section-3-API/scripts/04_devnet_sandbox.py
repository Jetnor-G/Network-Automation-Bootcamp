#!/usr/bin/env python3
"""
Script 04 — Cisco DevNet Always-On IOS-XE Sandbox.
Free, public, no sign-up required.
Credentials: devnetuser / Cisco123!  (Cisco-provided, public)
Usage: python3 04_devnet_sandbox.py
"""

import sys
import requests
from requests.auth import HTTPBasicAuth

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SANDBOX_HOST = "sandbox-iosxe-latest-1.cisco.com"
SANDBOX_USER = "devnetuser"
SANDBOX_PASS = "Cisco123!"
BASE_URL     = f"https://{SANDBOX_HOST}/restconf/data"

HEADERS = {
    "Content-Type": "application/yang-data+json",
    "Accept":       "application/yang-data+json",
}

AUTH = HTTPBasicAuth(SANDBOX_USER, SANDBOX_PASS)


def get_device_info():
    """Query hostname and software version."""
    url = f"{BASE_URL}/Cisco-IOS-XE-native:native/hostname"
    try:
        resp = requests.get(url, auth=AUTH, headers=HEADERS, verify=False, timeout=15)
        resp.raise_for_status()
        hostname = resp.json().get("Cisco-IOS-XE-native:hostname", "N/A")
        print(f"\n── DevNet Sandbox Device ───────────────────────")
        print(f"  Host    : {SANDBOX_HOST}")
        print(f"  Hostname: {hostname}")
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot reach {SANDBOX_HOST} — check internet access.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] HTTP {resp.status_code}: {e}")
        sys.exit(1)


def get_interfaces():
    """List all interfaces and their enabled state."""
    url = f"{BASE_URL}/ietf-interfaces:interfaces"
    resp = requests.get(url, auth=AUTH, headers=HEADERS, verify=False, timeout=15)
    resp.raise_for_status()
    interfaces = (
        resp.json()
        .get("ietf-interfaces:interfaces", {})
        .get("interface", [])
    )
    print(f"\n── Interfaces ({len(interfaces)} total) ─────────────────────")
    print(f"  {'Name':<35} {'Enabled':<10} {'Description'}")
    print("  " + "-" * 65)
    for iface in interfaces:
        name  = iface.get("name", "N/A")
        up    = "yes" if iface.get("enabled", False) else "no"
        desc  = iface.get("description", "")
        print(f"  {name:<35} {up:<10} {desc}")


def get_running_config_snippet():
    """Fetch the hostname block from the native config model."""
    url = f"{BASE_URL}/Cisco-IOS-XE-native:native"
    resp = requests.get(url, auth=AUTH, headers=HEADERS, verify=False, timeout=15)
    resp.raise_for_status()
    native = resp.json().get("Cisco-IOS-XE-native:native", {})
    print(f"\n── Config snippet ──────────────────────────────")
    print(f"  Version   : {native.get('version', 'N/A')}")
    print(f"  Hostname  : {native.get('hostname', 'N/A')}")
    print(f"  IP domain : {native.get('ip', {}).get('domain', {}).get('name', 'N/A')}")


if __name__ == "__main__":
    print(f"[*] Connecting to Cisco DevNet Always-On Sandbox ...")
    print(f"    {SANDBOX_HOST}  (user: {SANDBOX_USER})")
    get_device_info()
    get_interfaces()
    get_running_config_snippet()
    print("\n[+] Done — you just queried a real IOS-XE device via RESTCONF!")
