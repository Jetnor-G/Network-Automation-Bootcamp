# Section 3 — REST API for Network Automation

## Objective

Query and configure network infrastructure via REST APIs. This section uses **NetBox** as the local source of truth, a **Cisco DevNet Always-On** sandbox for RESTCONF practice, and several **free public APIs** for real-world data exploration — no account or credit card required.

---

## API Sources Used in This Lab

### Local (Lab Network)

| Service | URL | Auth | What You Do |
|---------|-----|------|-------------|
| NetBox | `http://10.0.0.100:8000/api/` | Token (given at start) | Query devices, prefixes, add records |
| Router-1 (RESTCONF) | `https://10.0.1.1/restconf/` | Basic auth | Push/pull interface config |

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

| Script | What It Does |
|--------|-------------|
| `01_netbox_get_devices.py` | Query all active devices from local NetBox |
| `02_restconf_push_config.py` | Push interface config to Router-1 via RESTCONF |
| `03_bgpview_lookup.py` | Look up ASN / prefix info using BGPView public API |
| `04_devnet_sandbox.py` | Query interfaces on Cisco DevNet Always-On IOS-XE |

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

Uses RESTCONF (RFC 8040) to configure `GigabitEthernet0/1` on Router-1 with a description and IP address.

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
- [ ] All scripts have try/except for connection and HTTP errors
