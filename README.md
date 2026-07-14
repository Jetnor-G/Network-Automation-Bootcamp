# Network Automation Bootcamp

A hands-on lab for **10–12 students** learning network automation with **Git**, **Ansible**, and **REST APIs**.

---

## Lab Architecture Diagram

```
                        INTERNET
                            │
              ──────────────┼──────────────
              Free Online APIs (Section 3)
              ──────────────┼──────────────
                            │
              ┌─────────────┴──────────────────┐
              │   Cisco DevNet Always-On (free) │
              │   demo.netbox.dev  (free)        │
              │   bgpview API      (free)        │
              │   peeringdb API    (free)        │
              └─────────────┬──────────────────┘
                            │ HTTPS / REST
════════════════════════════╪══════════════════════════════════════
              CLASSROOM MANAGEMENT NETWORK  10.0.0.0/24
════════════════════════════╪══════════════════════════════════════
                            │
                     ┌──────┴──────────┐        ┌─────────────────┐
                     │  GIT SERVER     │        │     NETBOX      │
                     │  10.0.0.60      │        │  10.100.100.25  │
                     │  (Gitea/GitHub) │        │  :8000          │
                     │  • Shared repo  │        │  • IPAM/DCIM    │
                     │  • Student repos│        │  • Inventory    │
                     └──────┬──────────┘        │  • API source   │
                            │                    └────────┬────────┘
                            │                             │
════════════════════════════╪═════════════════════════════╪══════════
              AUTOMATION & LAB DEVICE NETWORK  10.106.106.0/24
════════════════════════════╪═════════════════════════════╪══════════
                            │                             │
                     ┌──────┴──────────┐                  │
                     │  CONTROL NODE   │◄──── REST API ────┘
                     │  10.106.106.60  │
                     │  • Git          │
                     │  • Ansible      │
                     │  • Python       │
                     │  • VS Code      │
                     └──────┬──────────┘
                            │
                            │    SSH / RESTCONF / Ansible
                            │
        ┌───────────────────┼──────────────────┐
        │                   │                  │
┌───────┴────────┐  ┌───────┴────────┐  ┌──────┴──────────┐
│  ROUTER-1      │  │  ROUTER-2      │  │  SWITCH-1       │
│  10.106.106.61 │  │  10.106.106.62 │  │  10.106.106.63  │
│  NX-OS         │  │  NX-OS         │  │  IOS            │
│  OSPF Area0    │  │                │  │  VLAN 10/20     │
└────────────────┘  └────────────────┘  └─────────────────┘

  ┌──────────────────────────────────────────────────────────┐
  │              STUDENT PODS  (×10–12 students)             │
  │                                                          │
  │  Pod-01..12   10.0.0.101–112   Laptop / VM               │
  │  Each student: own Git branch + Ansible inventory entry  │
  └──────────────────────────────────────────────────────────┘
```

---

## Lab Sections

| # | Section | Tools | Objective |
|---|---------|-------|-----------|
| 1 | [Git for Network Automation](Section-1-GIT/README.md) | Git, Gitea | Version-control device configs; branch-per-CR workflow |
| 2 | [Ansible for Network Automation](Section-2-Ansible/README.md) | Ansible, Jinja2 | Push config to routers & switch; compliance checks |
| 3 | [API for Network Automation](Section-3-API/README.md) | Python, REST, RESTCONF, NetBox | Query devices & public APIs; build dynamic inventory |

---

## Free Online APIs Used in Section 3

| Service | URL | What Students Explore |
|---------|-----|-----------------------|
| Cisco DevNet Always-On IOS-XE | `sandbox-iosxe-latest-1.cisco.com` | RESTCONF on a real IOS-XE device |
| NetBox Demo | `https://demo.netbox.dev` | IPAM/DCIM REST API |
| BGPView | `https://api.bgpview.io` | BGP routing data, prefix lookups |
| PeeringDB | `https://www.peeringdb.com/api/` | Internet exchange and peering data |
| ipinfo.io | `https://ipinfo.io` | IP geolocation & ASN info |
| httpbin.org | `https://httpbin.org` | HTTP method practice (GET/POST/PUT) |

---

## Student Lab Setup

```bash
# Each student clones the shared repo and creates their own branch
git clone http://10.0.0.60/bootcamp/Network-Automation-Bootcamp.git
cd Network-Automation-Bootcamp
git checkout -b student/pod-XX-yourname

# Install Python dependencies
pip install ansible requests netmiko napalm pynetbox
```

---

## Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Git | ≥ 2.30 | Source control |
| Python | ≥ 3.9 | Scripting & API calls |
| Ansible | ≥ 2.14 | Configuration management |
| `requests` | latest | HTTP client |
| `netmiko` | latest | Multi-vendor SSH |
| `napalm` | latest | Device abstraction |
| `pynetbox` | latest | NetBox API client |

---

## Repository Structure

```
Network-Automation-Bootcamp/
├── README.md
├── diagrams/lab-topology.md
├── Section-1-GIT/
│   ├── README.md
│   ├── configs/
│   │   ├── router1_baseline.cfg
│   │   └── switch1_baseline.cfg
│   └── exercises/
├── Section-2-Ansible/
│   ├── README.md
│   ├── inventory/
│   │   ├── hosts.ini
│   │   └── group_vars/
│   ├── playbooks/
│   │   ├── 01-gather-facts.yml
│   │   ├── 02-push-config.yml
│   │   └── 03-compliance-check.yml
│   └── templates/interface.j2
└── Section-3-API/
    ├── README.md
    ├── scripts/
    │   ├── 01_netbox_get_devices.py
    │   ├── 02_restconf_push_config.py
    │   ├── 03_bgpview_lookup.py
    │   └── 04_devnet_sandbox.py
    └── examples/
        └── sample_response.json
```

---

*Lab version 2.0 — May 2026 · 10–12 student capacity*
