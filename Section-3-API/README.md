# Section 3 — REST API for Network Automation

## Objective

Query and configure network infrastructure via REST APIs. This section uses **NetBox** as the local source of truth, a **Cisco DevNet Always-On** sandbox for RESTCONF practice, and several **free public APIs** for real-world data exploration — no account or credit card required.

---

## API Sources Used in This Lab

### Local (Lab Network)

| Service | URL | Auth | What You Do |
|---------|-----|------|-------------|
| NetBox | `http://10.100.100.25:8000/api/` | Token (given at start) | Query devices, prefixes, add records |

> Router-1 and Router-2 are virtual Nexus (NX-OS) and Switch-1 is virtual IOS — none of the lab
> devices support the Cisco-IOS-XE-native RESTCONF YANG models used in scripts 02 and 06. Use the
> Cisco DevNet Always-On IOS-XE sandbox below for the RESTCONF exercises instead.

### Free Public APIs (no setup, no account)

| Service | Base URL | Auth Needed | What You Explore |
|---------|----------|------------|-----------------|
| **Cisco DevNet Always-On IOS-XE** | `https://sandbox-iosxe-latest-1.cisco.com` | Basic (devnetuser / Cisco123!) | RESTCONF on a real IOS-XE router |
| **BGPView** | `https://api.bgpview.io` | None | ASN info, BGP prefix lookups, peer data |
| **PeeringDB** | `https://www.peeringdb.com/api/` | None (read) | Internet exchanges, network records |
| **ipinfo.io** | `https://ipinfo.io` | None (50 k/mo free) | IP geolocation, ASN, org name |
| **httpbin.org** | `https://httpbin.org` | None | Practice all HTTP methods safely |

---

## Lab Scripts

| Script | Method | What It Does |
|--------|-------------|
| `01_netbox_get_devices.py` | REST | Query all active devices from local NetBox |
| `02_restconf_push_config.py` | RESTCONF | Push interface config to Router-1 |
| `03_bgpview_lookup.py` | REST (public) | BGPView — ASN / prefix lookups |
| `04_devnet_sandbox.py` | RESTCONF | Cisco DevNet Always-On IOS-XE sandbox |
| `05_push_baseline_ssh.py` | SSH (Netmiko) | Push banner, logging, domain, DNS, NTP via CLI |
| `06_push_baseline_restconf.py` | RESTCONF | Push same baseline via YANG/RESTCONF |

---

## Exercise 5 — SSH: Push Baseline Config with Netmiko

```bash
python3 scripts/05_push_baseline_ssh.py
```

Connects to all three lab devices over SSH using **Netmiko** and pushes:
- `ip domain-name` + `ip name-server` (Domain & DNS)
- `ntp server` (NTP)
- Logging: `logging host` + `logging buffered` + `service timestamps` on Switch-1 (IOS);
  `logging server` + `logging logfile` + `logging timestamp` on Router-1/2 (NX-OS — no
  `service timestamps` or `write memory` on this platform)
- `banner motd` (Banner)

The script prints the full command list, asks for confirmation, then applies and verifies.

**Key concepts:** Netmiko `ConnectHandler`, `send_config_set()`, `save_config()`, error handling.

---

## Exercise 6 — RESTCONF: Push Baseline Config with Python

```bash
python3 scripts/06_push_baseline_restconf.py
```

Pushes the exact same baseline using **RESTCONF PATCH/PUT** requests with IOS-XE YANG models:

| Config Block | YANG Path |
|---|---|
| Domain | `Cisco-IOS-XE-native:native/ip/domain` |
| DNS | `Cisco-IOS-XE-native:native/ip/name-server` |
| NTP | `Cisco-IOS-XE-native:native/ntp` |
| Logging | `Cisco-IOS-XE-native:native/logging` |
| Timestamps | `Cisco-IOS-XE-native:native/service/timestamps` |
| Banner MOTD | `Cisco-IOS-XE-native:native/banner` |

After pushing, the script runs a GET on each path and prints the confirmation.

**Key concepts:** YANG data models, PATCH vs PUT, structured JSON payloads, read-back verification.

---

## SSH vs RESTCONF — Side-by-Side Comparison

| Aspect | SSH / Netmiko (Script 05) | RESTCONF (Script 06) |
|--------|--------------------------|---------------------|
| Protocol | SSH (port 22) | HTTPS (port 443) |
| Data format | CLI text commands | Structured JSON |
| Works on | Any IOS device | IOS-XE ≥ 16.6 only |
| Error detection | Parse text output | HTTP status codes |
| Idempotent | No (re-applies always) | Yes (PUT/PATCH) |
| Best for | Legacy devices | Modern/API-ready devices |

---

## Exercise 1 — NetBox: Query Your Devices

```bash
python3 scripts/01_netbox_get_devices.py
```

Fetches all active devices from NetBox and prints a table. Then extend the script to **add a new device** via POST.

**Key concepts:** API tokens, pagination, filtering with query params.

---

## Exercise 2 — RESTCONF: Push Interface Config

```bash
python3 scripts/02_restconf_push_config.py
```

Uses RESTCONF (RFC 8040) to configure an interface with a description and IP address. `DEVICE_IP`
is a placeholder — point it at the DevNet IOS-XE sandbox (or another IOS-XE device with RESTCONF
enabled), since none of the lab's own devices (NX-OS routers, IOS switch) support it.

**Key concepts:** YANG data models, HTTP PUT, `application/yang-data+json`.

---

## Exercise 3 — BGPView: Real-World Routing Data

```bash
python3 scripts/03_bgpview_lookup.py
```

Looks up BGP routing information for a given ASN or IP prefix. Try it with your ISP's ASN.

**Key concepts:** No-auth public API, JSON parsing, nested data structures.

---

## Exercise 4 — Cisco DevNet Sandbox

```bash
python3 scripts/04_devnet_sandbox.py
```

Connects to Cisco's **always-on, free** IOS-XE sandbox and queries its interfaces via RESTCONF.
Credentials: `devnetuser` / `Cisco123!` (Cisco-provided, public).

**Key concepts:** Public sandboxes, RESTCONF on real hardware, TLS verification.

---

## RESTCONF Quick Reference

**Base URL:** `https://<device>/restconf/data/`

**Required Headers:**
```
Content-Type: application/yang-data+json
Accept:       application/yang-data+json
```

| HTTP Method | Action | When to Use |
|-------------|--------|------------|
| GET | Read config or state | Show interfaces, routes |
| PUT | Replace a resource | Set interface config |
| PATCH | Update part of a resource | Change description only |
| POST | Create a new resource | Add a new VLAN |
| DELETE | Remove a resource | Remove an interface config |

---

## Authentication Patterns

```python
import requests
from requests.auth import HTTPBasicAuth

# Basic auth — IOS-XE RESTCONF
resp = requests.get(url, auth=HTTPBasicAuth("admin", "Lab@1234"), verify=False)

# Token auth — NetBox
headers = {"Authorization": "Token <your-token>"}
resp = requests.get(url, headers=headers)

# No auth — BGPView, PeeringDB, ipinfo.io
resp = requests.get("https://api.bgpview.io/asn/13335")
```

---

## Student Tip — Explore APIs Interactively

Before writing a script, explore endpoints in your browser or with `curl`:

```bash
# BGPView — lookup Cloudflare's ASN
curl https://api.bgpview.io/asn/13335 | python3 -m json.tool

# ipinfo — lookup your public IP
curl https://ipinfo.io

# PeeringDB — find an Internet Exchange
curl "https://www.peeringdb.com/api/ix?name=AMS-IX" | python3 -m json.tool

# httpbin — test a POST request
curl -X POST https://httpbin.org/post -H "Content-Type: application/json" \
     -d '{"device": "router1", "action": "backup"}'
```

---

## Completion Criteria

- [ ] Script 1 queries NetBox and prints at least 3 devices
- [ ] Script 1 extended to POST a new device via API
- [ ] Script 2 applies interface config via RESTCONF PUT
- [ ] Script 3 looks up at least one real ASN and parses the JSON
- [ ] Script 4 queries the DevNet sandbox interfaces
- [ ] Script 5 (SSH) pushes banner, logging, domain, DNS, NTP to all devices
- [ ] Script 6 (RESTCONF) pushes the same baseline to an IOS-XE target (e.g. the DevNet sandbox) and reads back each YANG path to verify
- [ ] Compare script 5 (SSH/CLI, all three lab devices) and script 6 (RESTCONF, IOS-XE only) — same baseline intent, different protocol and platform reach
- [ ] All scripts have try/except for connection and HTTP errors
