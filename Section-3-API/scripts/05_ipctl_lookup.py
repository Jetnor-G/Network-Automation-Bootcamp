#!/usr/bin/env python3
"""
Script 05 — ipctl.io public API: Look up ASN and prefix routing data.

This used to target BGPView (api.bgpview.io), a free no-auth REST API —
but BGPView shut down permanently on 2025-11-26 and its domain no longer
resolves at all. ipctl.io is a maintained replacement with the same kind
of data (plus RPKI validation) and, importantly for this exercise, the
/asn and /ip endpoints used below work with no signup and no API key —
only its /as/{asn} route (note: not the one used here) requires a key.

It's real-world routing data either way: ASNs (Autonomous System Numbers)
identify networks on the internet, and each ASN announces the IP prefixes
("blocks of addresses") it owns via BGP.

Usage: python3 05_ipctl_lookup.py
"""

import sys
import requests

BASE_URL = "https://api.ipctl.io/v1"


def lookup_asn(asn):
    """Return summary info for a given ASN number (e.g. 13335 = Cloudflare)."""
    url = f"{BASE_URL}/asn/{asn}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        # Every ipctl.io response wraps its payload in a "data" key —
        # check that envelope shape first when exploring a new endpoint.
        info = resp.json().get("data", {}).get("asn", {})
        print(f"\n── ASN {asn} ──────────────────────────────────────")
        print(f"  Name         : {info.get('name', 'N/A')}")
        print(f"  Country      : {info.get('country_code', 'N/A')}")
        print(f"  RIR          : {info.get('rir', 'N/A')}")
        print(f"  Status       : {info.get('status', 'N/A')}")
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot reach api.ipctl.io — check internet access.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] HTTP {resp.status_code}: {e}")


def lookup_prefixes(asn):
    """List IPv4 prefixes announced by an ASN."""
    url = f"{BASE_URL}/asn/{asn}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    prefixes = resp.json().get("data", {}).get("prefixes", [])
    print(f"\n── Prefixes for AS{asn} ({len(prefixes)} total) ──────────")
    for p in prefixes[:10]:  # large ASNs can announce hundreds of prefixes — show a sample
        rpki = p.get("rpki_status", "unknown")
        print(f"  {p.get('prefix', ''):<20}  rpki={rpki:<10}  {p.get('description', '') or ''}")
    if len(prefixes) > 10:
        print(f"  ... and {len(prefixes) - 10} more.")


def lookup_ip(ip):
    """Get routing info for a specific IP address."""
    url = f"{BASE_URL}/ip/{ip}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data   = resp.json().get("data", {})
    prefix = data.get("prefix") or {}
    asn    = data.get("asn") or {}
    geo    = data.get("geo") or {}
    print(f"\n── IP Lookup: {ip} ─────────────────────────────────")
    print(f"  Reverse DNS : {data.get('reverse_dns', 'N/A')}")
    print(f"  Prefix      : {prefix.get('prefix', 'N/A')}  (rpki={prefix.get('rpki_status', 'N/A')})")
    print(f"  ASN         : AS{asn.get('asn', 'N/A')} — {asn.get('name', 'N/A')}")
    print(f"  Location    : {geo.get('city', 'N/A')}, {geo.get('country_name', 'N/A')}")


if __name__ == "__main__":
    # ── Exercise A: Look up Cloudflare (AS13335) ──────────────────
    lookup_asn(13335)
    lookup_prefixes(13335)

    # ── Exercise B: Look up a public IP ───────────────────────────
    lookup_ip("1.1.1.1")

    # ── Student challenge: change the ASN to your ISP's ───────────
    # lookup_asn(YOUR_ISP_ASN)
    print("\n[+] Done. Try changing the ASN to your own ISP!")
