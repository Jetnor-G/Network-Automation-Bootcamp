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
              │   demo.netbox.dev  (free)        │
              │   ipctl.io API     (free)        │
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
                     │  (Gitea/GitHub) │        │  HTTPS (443)    │
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
                            │    SSH / Ansible
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
| NetBox Demo | `https://demo.netbox.dev` | IPAM/DCIM REST API |
| ipctl.io | `https://api.ipctl.io/v1` | BGP routing data, prefix lookups, RPKI status |
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
│   │   ├── 03-compliance-check.yml
│   │   └── 04-baseline-config.yml
│   └── templates/
│       ├── interface.j2
│       └── baseline.j2
└── Section-3-API/
    ├── README.md
    ├── Network-Automation-Bootcamp.postman_collection.json
    ├── scripts/
    │   ├── 01_netbox_get_devices.py
    │   ├── 02_netbox_parse_output.py
    │   ├── 03_netbox_create_device.py
    │   ├── 04_push_baseline_ssh.py
    │   └── 05_ipctl_lookup.py
    └── examples/
        └── sample_response.json
```

---

*Lab version 2.0 — May 2026 · 10–12 student capacity*
