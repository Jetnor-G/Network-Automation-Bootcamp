#!/usr/bin/env python3
"""
Script 03 — BGPView public API: Look up ASN and prefix routing data.
No account or authentication required.
Usage: python3 03_bgpview_lookup.py
"""

import sys
import requests

BASE_URL = "https://api.bgpview.io"


def lookup_asn(asn):
    """Return summary info for a given ASN number (e.g. 13335 = Cloudflare)."""
    url = f"{BASE_URL}/asn/{asn}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", {})
        print(f"\n── ASN {asn} ──────────────────────────────────────")
        print(f"  Name         : {data.get('name', 'N/A')}")
        print(f"  Description  : {data.get('description_short', 'N/A')}")
        print(f"  Country      : {data.get('country_code', 'N/A')}")
        print(f"  RIR          : {data.get('rir_allocation', {}).get('rir_name', 'N/A')}")
        print(f"  Website      : {data.get('website', 'N/A')}")
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot reach api.bgpview.io — check internet access.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] HTTP {resp.status_code}: {e}")


def lookup_prefixes(asn):
    """List IPv4 prefixes announced by an ASN."""
    url = f"{BASE_URL}/asn/{asn}/prefixes"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    prefixes = resp.json().get("data", {}).get("ipv4_prefixes", [])
    print(f"\n── IPv4 Prefixes for AS{asn} ({len(prefixes)} total) ──────────")
    for p in prefixes[:10]:
        print(f"  {p.get('prefix', ''):<20}  {p.get('name', '')}")
    if len(prefixes) > 10:
        print(f"  ... and {len(prefixes) - 10} more.")


def lookup_ip(ip):
    """Get routing info for a specific IP address."""
    url = f"{BASE_URL}/ip/{ip}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data  = resp.json().get("data", {})
    pfxs  = data.get("prefixes", [])
    print(f"\n── IP Lookup: {ip} ─────────────────────────────────")
    for p in pfxs:
        asn  = p.get("asn", {})
        print(f"  Prefix : {p.get('prefix', 'N/A')}")
        print(f"  ASN    : AS{asn.get('asn', 'N/A')} — {asn.get('name', 'N/A')}")
        print(f"  Country: {p.get('country_code', 'N/A')}")


if __name__ == "__main__":
    # ── Exercise A: Look up Cloudflare (AS13335) ──────────────────
    lookup_asn(13335)
    lookup_prefixes(13335)

    # ── Exercise B: Look up a public IP ───────────────────────────
    lookup_ip("1.1.1.1")

    # ── Student challenge: change the ASN to your ISP's ───────────
    # lookup_asn(YOUR_ISP_ASN)
    print("\n[+] Done. Try changing the ASN to your own ISP!")
