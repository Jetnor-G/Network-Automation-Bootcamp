#!/usr/bin/env python3
"""
Script 02 — NetBox: Parsing API Output.

Script 01 fetched one page of devices and printed a flat table. Real
automation usually needs more than that: paging through everything,
pulling values out of nested objects, filtering, and summarizing. This
script reuses the same NetBox connection as script 01 and walks through
those patterns one at a time against the same /api/dcim/devices/ data.

Usage: python3 02_netbox_parse_output.py
"""

import sys
from collections import Counter
from datetime import date
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


def get_all_devices():
    """Fetch every device, following pagination instead of grabbing one page.

    NetBox list responses look like:
        {"count": 137, "next": "<url or null>", "previous": "<url or null>", "results": [...]}
    "results" is capped at the page size (the "limit" param, 50 here) —
    if "next" isn't null, there's more data waiting on another page.
    Looping until "next" is null is the general pattern for pulling a
    complete dataset out of any paginated REST API, not just NetBox.
    """
    devices = []
    url = f"{NETBOX_URL}/api/dcim/devices/?limit=50"
    try:
        while url:
            resp = requests.get(url, headers=HEADERS, timeout=10, verify=False)
            resp.raise_for_status()
            body = resp.json()
            devices.extend(body.get("results", []))
            url = body.get("next")  # None once we've reached the last page
        return devices
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot reach NetBox at {NETBOX_URL}")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] HTTP {resp.status_code}: {e}")
        print(f"        {resp.text}")
        sys.exit(1)


def group_by_site(devices):
    """Turn a flat list into {site_name: [device_name, ...]} — a plain
    dict comprehension/loop is often all "parsing" really means."""
    groups = {}
    for d in devices:
        site = (d.get("site") or {}).get("name", "Unassigned")
        groups.setdefault(site, []).append(d.get("name", "N/A"))
    return groups


def count_by_status(devices):
    """Tally how many devices are in each status — Counter is a quick way
    to turn a list of labels into a {label: count} summary."""
    labels = [(d.get("status") or {}).get("label", "Unknown") for d in devices]
    return Counter(labels)


def devices_missing_ip(devices):
    """Filter for devices with no primary IP assigned — a common
    "find the problems" pattern: keep only rows where a nested field is
    missing/null instead of the usual "print everything" pass."""
    return [d.get("name", "N/A") for d in devices if not d.get("primary_ip")]


def find_by_role(devices, role_name):
    """Filter to devices matching one role name — a simple example of
    querying client-side once you've already fetched the data, instead of
    re-querying NetBox with a new ?role= filter each time.

    Note: this field is called "role" in current NetBox versions — it
    used to be "device_role" in older releases.
    """
    return [
        d.get("name", "N/A") for d in devices
        if (d.get("role") or {}).get("name", "").lower() == role_name.lower()
    ]


def management_ip_list(devices):
    """Flatten each device down to just "name -> IP" — the shape you'd
    want to feed into an Ansible inventory or a hosts file."""
    return {
        d.get("name", "N/A"): (d.get("primary_ip") or {}).get("address", "N/A")
        for d in devices
    }


def software_lifecycle_report(devices):
    """Flag devices with a software compliance or end-of-support problem —
    a deeper example than the others above, since the data being checked
    isn't a built-in NetBox field but a per-device "custom field" (an
    admin-defined extension), and each finding takes two or three nested
    lookups plus a comparison instead of a single .get().

    NetBox custom fields live under "custom_fields" on every device, e.g.:
        "custom_fields": {
            "software_version": "16.12.10a",
            "vendor_recommended_version": "16.12.10a",
            "end_of_support": "2024-01-31",
            ...
        }
    Every custom field is optional, so most of the work here is deciding
    what "no data" should mean (skip the device) versus what "has data but
    looks bad" should mean (flag it) — that judgment call is the actual
    "parsing" in most real automation scripts, not just reading the JSON.
    """
    today = date.today()
    report = []
    for d in devices:
        name = d.get("name", "N/A")
        cf = d.get("custom_fields") or {}
        current     = cf.get("software_version")
        recommended = cf.get("vendor_recommended_version")
        end_of_support = cf.get("end_of_support")

        if not current:
            continue  # no software version on record — nothing to check

        issues = []
        if recommended and current != recommended:
            issues.append(f"running {current}, vendor recommends {recommended}")
        if end_of_support:
            # NetBox returns dates as "YYYY-MM-DD" strings — comparing them
            # as real date objects (not strings) is what makes "is this in
            # the past?" a correct comparison instead of a lucky one.
            if date.fromisoformat(end_of_support) < today:
                issues.append(f"past end-of-support (was {end_of_support})")

        if issues:
            report.append((name, issues))
    return report


if __name__ == "__main__":
    print(f"[*] Fetching all devices from NetBox ({NETBOX_URL}) — paging through every result ...")
    devices = get_all_devices()
    print(f"    Retrieved {len(devices)} device(s) total.\n")

    print("── Devices per site ──────────────────────────────")
    for site, names in group_by_site(devices).items():
        print(f"  {site:<20} {len(names)} device(s): {', '.join(names)}")

    print("\n── Device count by status ────────────────────────")
    for status, count in count_by_status(devices).items():
        print(f"  {status:<15} {count}")

    print("\n── Devices missing a primary IP ──────────────────")
    missing = devices_missing_ip(devices)
    print(f"  {', '.join(missing) if missing else '(none — every device has a primary IP)'}")

    print("\n── Devices with role 'Network Device' ────────────")
    routers = find_by_role(devices, "Network Device")
    print(f"  {', '.join(routers) if routers else '(no devices with that role — try a role name from your NetBox)'}")

    print("\n── Management IP list (name -> IP) ───────────────")
    for name, ip in management_ip_list(devices).items():
        print(f"  {name:<20} {ip}")

    print("\n── Software lifecycle report (custom_fields) ─────")
    issues = software_lifecycle_report(devices)
    if issues:
        for name, problems in issues:
            print(f"  {name}:")
            for p in problems:
                print(f"    - {p}")
    else:
        print("  (no lifecycle issues found)")

    print("\n[+] Done. Try writing your own group_by/find_by helper against the same 'devices' list.")
