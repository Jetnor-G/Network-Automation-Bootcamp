# Section 3 — REST API for Network Automation

## Objective

Query and configure network infrastructure via REST APIs. This section uses **NetBox** as the local source of truth, several **free public APIs** for real-world data exploration, and **SSH/Netmiko** to push baseline config to this lab's own devices — no account or credit card required. RESTCONF/YANG concepts are covered as reference material (see below), but there is currently no live RESTCONF target anywhere in this lab to practice against — see the note below for why.

---

## API Sources Used in This Lab

### Local (Lab Network)

| Service | URL | Auth | What You Do |
|---------|-----|------|-------------|
| NetBox | `https://10.100.100.25/api/` | Token (given at start) | Query devices, prefixes, add records |

> **Why there's no RESTCONF/NETCONF exercise in this lab:** this was tested directly, not assumed.
> Router-1/2 (virtual NX-OS) will enable `feature restconf` and start the nginx front-end, but every
> authenticated request under `/restconf/data/*` returns an empty `204` — even for a nonexistent
> YANG module — meaning the backend datastore handler isn't actually implemented on this virtual
> platform; NETCONF (port 830) is refused outright. Switch-1 (IOSv/classic IOS) has neither: port
> 443 (RESTCONF) is refused, and the NETCONF SSH subsystem on port 22 doesn't respond. This section
> previously used Cisco's free DevNet Always-On IOS-XE sandbox as a working RESTCONF example
> instead — but as of this lab, that entire sandbox platform is offline for a full rebuild, with
> Cisco targeting early 2027 for it to return. The only thing that reliably works against all three
> lab devices is CLI over SSH — see Exercise 4.

### Free Public APIs (no setup, no account)

| Service | Base URL | Auth Needed | What You Explore |
|---------|----------|------------|-----------------|
| **ipctl.io** | `https://api.ipctl.io/v1` | None (for `/asn`, `/ip`, `/prefix`) | ASN info, BGP prefix lookups, RPKI status |
| **PeeringDB** | `https://www.peeringdb.com/api/` | None (read) | Internet exchanges, network records |
| **ipinfo.io** | `https://ipinfo.io` | None (50 k/mo free) | IP geolocation, ASN, org name |
| **httpbin.org** | `https://httpbin.org` | None | Practice all HTTP methods safely |

> **Why ipctl.io and not BGPView:** BGPView (`api.bgpview.io`) shut down permanently on
> 2025-11-26 — the domain no longer resolves at all, for anyone. ipctl.io is a maintained
> replacement covering the same kind of data (plus RPKI validation); its `/asn`, `/ip`, and
> `/prefix` endpoints work with no signup, though its separate `/as/{asn}` route does require
> an API key — script 05 uses `/asn`, not `/as`, specifically to stay key-free.

---

## Lab Scripts

| Script | Method | What It Does |
|--------|--------|---------------|
| `01_netbox_get_devices.py` | REST | Query all active devices from local NetBox |
| `02_netbox_parse_output.py` | REST | Parsing patterns: pagination, grouping, filtering, summarizing |
| `03_netbox_create_device.py` | REST | Resolve site/role/device-type names to IDs, then create a device via POST |
| `04_push_baseline_ssh.py` | SSH (Netmiko) | Push banner, logging, domain, DNS, NTP via CLI |
| `05_ipctl_lookup.py` | REST (public) | ipctl.io — ASN / prefix lookups |

---

## Postman Collection

[`Network-Automation-Bootcamp.postman_collection.json`](Network-Automation-Bootcamp.postman_collection.json)
mirrors every HTTP request scripts 01–03 and 05 make, so you can explore or tweak them in Postman
instead of (or before) writing Python. Script 04 isn't included — it's SSH/Netmiko, not HTTP.

**To use it:**
1. Postman → Import → select the file.
2. Settings → General → turn **off** "SSL certificate verification" — NetBox uses a self-signed
   cert, and every NetBox request will fail with a certificate error otherwise.
3. The `NetBox (Scripts 01–03)` folder has collection-level auth already wired up (`Authorization:
   Token {{netbox_token}}`) — no per-request setup needed.
4. Run the `03 - NetBox: Create Device` requests **top to bottom**: steps 1–3 look up numeric IDs
   and save them as collection variables (`role_id`, `site_id`, `device_type_id`); step 5's create
   request depends on those already being set. Use the folder's "Run" button, or click each request
   in order.
5. `ipctl.io (Script 05)` needs no auth or setup — those requests work immediately.

All default variable values (`device_role_name`, `site_name`, `device_type_model`, `asn`, `ip`,
`prefix`, etc.) are real values confirmed against this lab's NetBox and ipctl.io — change them in
the collection's Variables tab to point at different data.

**Troubleshooting — `"JSON parse error - Expecting value"` on Step 5:** this means `role_id`,
`site_id`, or `device_type_id` is still blank, because Steps 1–3 haven't been run yet in this
Postman session (collection variables reset when you reopen Postman, or if you never ran them at
all). Step 5 now checks for this itself and will refuse to send with a clear error naming which
variable is missing — run Steps 1–3 first, or use the folder's "Run" button to execute the whole
sequence automatically.

---

## Exercise 1 — NetBox: Query Your Devices

```bash
python3 scripts/01_netbox_get_devices.py
```

Fetches all active devices from NetBox and prints a table. Then extend the script to **add a new device** via POST.

**Key concepts:** API tokens, pagination, filtering with query params.

---

## Exercise 2 — NetBox: Parsing API Output

```bash
python3 scripts/02_netbox_parse_output.py
```

Fetches **every** device (paging through `next` until it's `null`, instead of one page like Exercise
1), then runs the same list through several parsing patterns: grouping by site, counting by status,
filtering to devices missing a primary IP, filtering by role, and flattening to a name→IP map.

The last pattern goes deeper: a **software lifecycle report** that reaches into each device's
`custom_fields` (an admin-defined extension, not a built-in NetBox field) to compare
`software_version` against `vendor_recommended_version` and check `end_of_support` against today's
date — real compliance-style logic, not just reading a flat field.

**Key concepts:** Pagination loops, dict/list comprehensions, `collections.Counter`, defensive
`.get()` chains on nested JSON, parsing custom fields, comparing ISO date strings as real `date`
objects.

---

## Exercise 3 — NetBox: Create a Network Device

```bash
python3 scripts/03_netbox_create_device.py
```

POSTs a new device to NetBox — but first resolves the site, device role, and device type **names**
to the numeric **IDs** NetBox actually requires, via three separate filtered GET calls. Also checks
whether the device already exists (with its own GET) before creating it, since this NetBox instance
doesn't enforce unique device names server-side — a duplicate POST would otherwise silently create
a second device with the same name instead of erroring. Edit `NEW_DEVICE_NAME` / `DEVICE_ROLE_NAME`
/ `SITE_NAME` / `DEVICE_TYPE_MODEL` at the top of the script to match data that already exists in
your NetBox instance — the defaults (`Network Device` / `Arena Stadium` / `C9200-48P`) are real
values confirmed against this lab's NetBox.

**Key concepts:** Resolving foreign keys before a POST, checking for an existing resource before
creating one, `requests.post(json=...)`. Also note: this NetBox version calls the field `role`, not
`device_role` (the older name, still used for the `/dcim/device-roles/` endpoint itself).

---

## Exercise 4 — SSH: Push Baseline Config with Netmiko

```bash
python3 scripts/04_push_baseline_ssh.py
```

Connects to all three lab devices over SSH using **Netmiko** and pushes:
- `ip domain-name` + `ip name-server` (Domain & DNS)
- `ntp server` (NTP)
- Logging: `logging host` + `logging buffered` + `service timestamps` on Switch-1 (IOS);
  `logging server` + `logging logfile` + `logging timestamp` on Router-1/2 (NX-OS — no
  `service timestamps` or `write memory` on this platform)
- `banner motd` (Banner)

The script prints the full command list, asks for confirmation, then applies and verifies.

This is also the only exercise in this section that touches the lab's own devices, since none of
them expose a working REST/RESTCONF API (see the note above) — everything else in this section
(Exercises 1–3, 5) talks to NetBox or a public internet API instead.

**Key concepts:** Netmiko `ConnectHandler`, `send_config_set()`, `save_config()`, error handling.

---

## Exercise 5 — ipctl.io: Real-World Routing Data

```bash
python3 scripts/05_ipctl_lookup.py
```

Looks up BGP routing information for a given ASN or IP prefix. Try it with your ISP's ASN.

**Key concepts:** No-auth public API, JSON parsing, nested data structures.

---

## RESTCONF & YANG — Reference Material (No Live Target Right Now)

There's currently nothing in this lab you can point these at — Router-1/2 and Switch-1 don't
support a working RESTCONF API (see the note above), and Cisco's DevNet Always-On IOS-XE sandbox,
which previously filled that gap, is offline for a full platform rebuild (Cisco is targeting early
2027 for it to return). This section is kept as reference for when a live IOS-XE target becomes
available again — your own device, a VM, or the sandbox once it's back.

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

# Basic auth — IOS-XE RESTCONF (reference only — see note above)
resp = requests.get(url, auth=HTTPBasicAuth("admin", "Lab@1234"), verify=False)

# Token auth — NetBox
headers = {"Authorization": "Token <your-token>"}
resp = requests.get(url, headers=headers)

# No auth — ipctl.io, PeeringDB, ipinfo.io
resp = requests.get("https://api.ipctl.io/v1/asn/13335")
```

---

## Student Tip — Explore APIs Interactively

Before writing a script, explore endpoints in your browser, in Postman (see the collection above),
or with `curl`:

```bash
# ipctl.io — lookup Cloudflare's ASN
curl https://api.ipctl.io/v1/asn/13335 | python3 -m json.tool

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

- [ ] Script 1 (NetBox) queries active devices and prints at least 3
- [ ] Script 1 extended to POST a new device via API
- [ ] Script 2 (NetBox parsing) pages through all devices and prints each summary (by site, by status, missing IP, by role, IP map, software lifecycle report)
- [ ] Script 3 (NetBox create) resolves site/role/device-type to IDs and creates a device
- [ ] Script 4 (SSH/Netmiko) pushes banner, logging, domain, DNS, NTP to all three lab devices
- [ ] Script 5 (ipctl.io) looks up at least one real ASN and parses the JSON
- [ ] Explain why there's no working RESTCONF/NETCONF target anywhere in this lab right now
- [ ] Imported the Postman collection and successfully run the NetBox and ipctl.io folders
- [ ] All scripts have try/except for connection and HTTP errors
