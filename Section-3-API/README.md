# Section 3 — REST API for Network Automation

## Objective

Interact with network devices and management platforms programmatically using **REST** and **RESTCONF** APIs. By the end of this section you will query device state, push configuration, and pull inventory from a management platform — all via Python and HTTP.

---

## Why APIs for Network Automation?

| CLI / SSH | REST API |
|-----------|---------|
| Scrape unstructured text | Structured JSON / XML responses |
| Hard to integrate with other tools | Standard HTTP — works with anything |
| No built-in authentication model | Token / OAuth / API keys |
| Vendor-specific commands | Platform-agnostic interfaces |

---

## API Types Covered

| Type | Protocol | Port | Format | Used With |
|------|----------|------|--------|-----------|
| REST | HTTP/HTTPS | 80/443 | JSON | NMS, NetBox, Cisco DNA |
| RESTCONF | HTTPS | 443 | JSON/XML | IOS-XE, NX-OS |
| NETCONF | SSH | 830 | XML | IOS-XE, Junos, NX-OS |

---

## Lab Scripts

### Script 1 — REST GET: Query Interface Status

```bash
python3 scripts/01_rest_get_interfaces.py
```

Queries `http://10.0.0.1/restconf/data/ietf-interfaces:interfaces` and prints a
formatted table of interface names, status, and IP addresses.

---

### Script 2 — RESTCONF PUT: Push Interface Config

```bash
python3 scripts/02_restconf_push_config.py
```

Pushes a JSON payload to configure `GigabitEthernet0/1` description and IP
address via RESTCONF on an IOS-XE device.

---

### Script 3 — NetBox Inventory: Build Dynamic Ansible Inventory

```bash
python3 scripts/03_netbox_inventory.py
```

Pulls all active devices from a NetBox instance and outputs an Ansible-compatible
JSON inventory grouped by device role.

---

## Key Python Libraries

| Library | Install | Purpose |
|---------|---------|---------|
| `requests` | `pip install requests` | HTTP client for REST APIs |
| `netmiko` | `pip install netmiko` | SSH to network devices |
| `napalm` | `pip install napalm` | Multi-vendor device abstraction |
| `ncclient` | `pip install ncclient` | NETCONF client |
| `pynetbox` | `pip install pynetbox` | NetBox API wrapper |

---

## RESTCONF Quick Reference

### Base URL
```
https://<device-ip>/restconf/data/
```

### Headers Required
```http
Content-Type: application/yang-data+json
Accept: application/yang-data+json
```

### Common Operations

| HTTP Method | RESTCONF Action | Example Path |
|-------------|----------------|-------------|
| GET | Read config/state | `/restconf/data/ietf-interfaces:interfaces` |
| PUT | Replace resource | `/restconf/data/ietf-interfaces:interfaces/interface=Gi0%2F1` |
| PATCH | Merge/update resource | same as PUT path |
| POST | Create new resource | `/restconf/data/ietf-interfaces:interfaces` |
| DELETE | Remove resource | `/restconf/data/ietf-interfaces:interfaces/interface=Gi0%2F1` |

---

## Authentication Methods

```python
import requests
from requests.auth import HTTPBasicAuth

# Basic auth (IOS-XE RESTCONF)
resp = requests.get(url, auth=HTTPBasicAuth("admin", "Lab@1234"), verify=False)

# Token auth (NetBox, Cisco DNA Center)
headers = {"Authorization": "Token abc123yourtokenhere"}
resp = requests.get(url, headers=headers)
```

---

## Sample JSON Payloads

### GET Response — Interface List
```json
{
  "ietf-interfaces:interfaces": {
    "interface": [
      {
        "name": "GigabitEthernet0/0",
        "description": "WAN_UPLINK",
        "enabled": true,
        "ietf-ip:ipv4": {
          "address": [{ "ip": "203.0.113.1", "prefix-length": 30 }]
        }
      }
    ]
  }
}
```

### PUT Payload — Configure Interface
```json
{
  "ietf-interfaces:interface": {
    "name": "GigabitEthernet0/1",
    "description": "LAN_SEGMENT_UPDATED",
    "type": "iana-if-type:ethernetCsmacd",
    "enabled": true,
    "ietf-ip:ipv4": {
      "address": [{ "ip": "10.0.0.1", "prefix-length": 24 }]
    }
  }
}
```

---

## Completion Criteria

- [ ] Script 1 successfully queries and prints interface data
- [ ] Script 2 applies a config change via RESTCONF PUT
- [ ] Script 3 generates an Ansible-compatible inventory from NetBox
- [ ] All scripts handle HTTP errors gracefully (try/except)
- [ ] At least one API call uses token-based authentication
