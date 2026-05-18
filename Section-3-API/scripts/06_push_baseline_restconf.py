#!/usr/bin/env python3
"""
Script 06 — Push baseline config via RESTCONF (IOS-XE YANG models).
Configures: Banner MOTD, Logging, Domain, DNS, NTP
Target: Router-1 (IOS-XE with RESTCONF enabled)

Usage: python3 06_push_baseline_restconf.py
Requires: pip install requests
"""

import json
import sys
import requests
from requests.auth import HTTPBasicAuth

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ── Target device ─────────────────────────────────────────────────────────────
DEVICE_IP  = "10.0.1.1"
USERNAME   = "admin"
PASSWORD   = "Lab@1234"
BASE_URL   = f"https://{DEVICE_IP}/restconf/data"

AUTH    = HTTPBasicAuth(USERNAME, PASSWORD)
HEADERS = {
    "Content-Type": "application/yang-data+json",
    "Accept":       "application/yang-data+json",
}

# ── Baseline values ────────────────────────────────────────────────────────────
DOMAIN_NAME      = "lab.example.com"
DNS_SERVERS      = ["8.8.8.8", "8.8.4.4"]
NTP_SERVERS      = ["216.239.35.0", "216.239.35.4"]
SYSLOG_SERVER    = "10.0.0.50"
LOG_BUFFER_SIZE  = 16384
BANNER_TEXT      = (
    "******************************************************************\n"
    "*   AUTHORIZED ACCESS ONLY — Network Automation Bootcamp Lab     *\n"
    "*   Unauthorized access is strictly prohibited and monitored.    *\n"
    "*   All activities are logged.                                   *\n"
    "******************************************************************"
)


# ── Helper ────────────────────────────────────────────────────────────────────

def restconf_patch(path, payload, label):
    url  = f"{BASE_URL}/{path}"
    resp = requests.patch(url, auth=AUTH, headers=HEADERS, json=payload, verify=False, timeout=10)
    if resp.status_code in (200, 201, 204):
        print(f"  [+] {label} — OK (HTTP {resp.status_code})")
    else:
        print(f"  [!] {label} — HTTP {resp.status_code}")
        print(f"      {resp.text[:200]}")


def restconf_put(path, payload, label):
    url  = f"{BASE_URL}/{path}"
    resp = requests.put(url, auth=AUTH, headers=HEADERS, json=payload, verify=False, timeout=10)
    if resp.status_code in (200, 201, 204):
        print(f"  [+] {label} — OK (HTTP {resp.status_code})")
    else:
        print(f"  [!] {label} — HTTP {resp.status_code}")
        print(f"      {resp.text[:200]}")


# ── Config sections ───────────────────────────────────────────────────────────

def push_domain():
    """Set IP domain name via native IOS-XE YANG model."""
    payload = {
        "Cisco-IOS-XE-native:domain": {
            "name": DOMAIN_NAME
        }
    }
    restconf_patch("Cisco-IOS-XE-native:native/ip/domain", payload, "Domain")


def push_dns():
    """Set DNS name servers via native YANG model."""
    payload = {
        "Cisco-IOS-XE-native:name-server": {
            "no-vrf": DNS_SERVERS
        }
    }
    restconf_put("Cisco-IOS-XE-native:native/ip/name-server", payload, "DNS servers")


def push_ntp():
    """Set NTP servers via Cisco-IOS-XE-ntp YANG model."""
    server_list = []
    for i, addr in enumerate(NTP_SERVERS):
        entry = {"ip-address": addr}
        if i == 0:
            entry["prefer"] = [None]        # prefer the first server
        server_list.append(entry)

    payload = {
        "Cisco-IOS-XE-ntp:ntp": {
            "Cisco-IOS-XE-ntp:server": {
                "server-list": server_list
            },
            "Cisco-IOS-XE-ntp:update-calendar": [None]
        }
    }
    restconf_patch("Cisco-IOS-XE-native:native/ntp", payload, "NTP servers")


def push_logging():
    """Set syslog host, buffer size, and timestamps via native YANG model."""
    payload = {
        "Cisco-IOS-XE-native:logging": {
            "host": {
                "ipv4-host-list": [
                    {"ipv4-host": SYSLOG_SERVER}
                ]
            },
            "buffered": {
                "size-value": LOG_BUFFER_SIZE,
                "severity":   "informational"
            },
            "trap":    "informational",
            "console": {"severity": "critical"}
        }
    }
    restconf_patch("Cisco-IOS-XE-native:native/logging", payload, "Logging")

    # Timestamps are under the service subtree
    ts_payload = {
        "Cisco-IOS-XE-native:timestamps": {
            "log": {
                "datetime": {
                    "msec":       [None],
                    "localtime":  [None],
                    "show-timezone": [None],
                    "year":       [None]
                }
            },
            "debug": {
                "datetime": {
                    "msec":       [None],
                    "localtime":  [None],
                    "show-timezone": [None],
                    "year":       [None]
                }
            }
        }
    }
    restconf_patch("Cisco-IOS-XE-native:native/service/timestamps", ts_payload, "Log timestamps")


def push_banner():
    """Set Banner MOTD via native YANG model."""
    payload = {
        "Cisco-IOS-XE-native:banner": {
            "motd": {
                "banner": BANNER_TEXT
            }
        }
    }
    restconf_patch("Cisco-IOS-XE-native:native/banner", payload, "Banner MOTD")


def verify_config():
    """Read back key fields to confirm what was applied."""
    print("\n── Verification ────────────────────────────────────────────────")
    checks = {
        "Domain":  "Cisco-IOS-XE-native:native/ip/domain",
        "DNS":     "Cisco-IOS-XE-native:native/ip/name-server",
        "NTP":     "Cisco-IOS-XE-native:native/ntp",
        "Logging": "Cisco-IOS-XE-native:native/logging",
        "Banner":  "Cisco-IOS-XE-native:native/banner",
    }
    for label, path in checks.items():
        url  = f"{BASE_URL}/{path}"
        resp = requests.get(url, auth=AUTH, headers=HEADERS, verify=False, timeout=10)
        if resp.status_code == 200:
            print(f"  [✓] {label:10} : {json.dumps(resp.json(), indent=None)[:80]}")
        else:
            print(f"  [✗] {label:10} : HTTP {resp.status_code}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print(f"[*] Pushing baseline config to {DEVICE_IP} via RESTCONF ...\n")
    try:
        push_domain()
        push_dns()
        push_ntp()
        push_logging()
        push_banner()
        verify_config()
        print("\n[+] Baseline config applied via RESTCONF.")
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot reach {DEVICE_IP}. Is RESTCONF enabled?")
        print("        Enable with:  ip http secure-server  /  restconf")
        sys.exit(1)


if __name__ == "__main__":
    main()
