# Network Automation Bootcamp

A hands-on lab environment for learning network automation using **Git**, **Ansible**, and **REST APIs**.

---

## Lab Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     NETWORK AUTOMATION BOOTCAMP                         │
│                                                                         │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │                    AUTOMATION CONTROL NODE                       │  │
│   │                                                                  │  │
│   │   ┌─────────────┐   ┌──────────────┐   ┌──────────────────┐    │  │
│   │   │    G I T    │   │   ANSIBLE    │   │   REST API       │    │  │
│   │   │  Repository │   │  Engine      │   │   Client         │    │  │
│   │   │             │   │              │   │                  │    │  │
│   │   │ • Track     │   │ • Playbooks  │   │ • HTTP Requests  │    │  │
│   │   │   configs   │   │ • Roles      │   │ • JSON Parsing   │    │  │
│   │   │ • Branches  │   │ • Inventory  │   │ • Auth Tokens    │    │  │
│   │   │ • Rollback  │   │ • Templates  │   │ • Automation     │    │  │
│   │   └──────┬──────┘   └──────┬───────┘   └────────┬─────────┘    │  │
│   │          │                 │                     │              │  │
│   └──────────┼─────────────────┼─────────────────────┼──────────────┘  │
│              │                 │                     │                  │
│              └─────────────────┼─────────────────────┘                  │
│                                │  SSH / NETCONF / REST                  │
│                   ─────────────┼─────────────                           │
│                                │                                        │
│   ┌─────────────────────────────────────────────────────────────┐       │
│   │                     NETWORK DEVICES                         │       │
│   │                                                             │       │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │       │
│   │  │ Router-1 │  │ Router-2 │  │Switch-1  │  │Firewall-1│   │       │
│   │  │10.0.0.1  │  │10.0.0.2  │  │10.0.0.10 │  │10.0.0.254│   │       │
│   │  │          │  │          │  │          │  │          │   │       │
│   │  │ IOS-XE   │  │ NX-OS    │  │ IOS      │  │ ASA      │   │       │
│   │  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │       │
│   │                                                             │       │
│   └─────────────────────────────────────────────────────────────┘       │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────┐       │
│   │                    NETWORK SERVICES                         │       │
│   │                                                             │       │
│   │  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐    │       │
│   │  │   NMS / API  │   │   NETBOX     │   │   NAPALM     │    │       │
│   │  │   Endpoint   │   │   (IPAM/DCIM)│   │   (Multi-OS) │    │       │
│   │  │  :8080       │   │   :8000      │   │   Library    │    │       │
│   │  └──────────────┘   └──────────────┘   └──────────────┘    │       │
│   │                                                             │       │
│   └─────────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Lab Sections Overview

| # | Section | Tools | Objective |
|---|---------|-------|-----------|
| 1 | [Git for Network Automation](Section-1-GIT/README.md) | Git, GitHub | Version-control network configurations |
| 2 | [Ansible for Network Automation](Section-2-Ansible/README.md) | Ansible, Jinja2 | Automate device configuration at scale |
| 3 | [API for Network Automation](Section-3-API/README.md) | Python, REST, RESTCONF | Programmatic network control |

---

## Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Git | ≥ 2.30 | Source control |
| Python | ≥ 3.9 | Scripting & API calls |
| Ansible | ≥ 2.14 | Configuration management |
| `requests` (pip) | latest | HTTP client for API labs |
| `netmiko` (pip) | latest | Multi-vendor SSH sessions |
| `napalm` (pip) | latest | Network device abstraction |

```bash
# Install Python dependencies
pip install ansible requests netmiko napalm
```

---

## Quick Start

```bash
git clone https://github.com/<your-org>/Network-Automation-Bootcamp.git
cd Network-Automation-Bootcamp

# Section 1 — Git
cd Section-1-GIT && cat README.md

# Section 2 — Ansible
cd ../Section-2-Ansible && ansible-playbook -i inventory/hosts.ini playbooks/01-gather-facts.yml

# Section 3 — API
cd ../Section-3-API && python3 scripts/01_rest_get_interfaces.py
```

---

## Repository Structure

```
Network-Automation-Bootcamp/
├── README.md                         ← You are here
├── diagrams/
│   └── lab-topology.md               ← Detailed topology diagram
├── Section-1-GIT/
│   ├── README.md
│   ├── exercises/
│   │   ├── 01-init-and-commit.md
│   │   ├── 02-branching-strategy.md
│   │   └── 03-config-rollback.md
│   └── configs/
│       ├── router1_baseline.cfg
│       └── switch1_baseline.cfg
├── Section-2-Ansible/
│   ├── README.md
│   ├── inventory/
│   │   ├── hosts.ini
│   │   └── group_vars/
│   ├── playbooks/
│   │   ├── 01-gather-facts.yml
│   │   ├── 02-push-config.yml
│   │   └── 03-compliance-check.yml
│   └── templates/
│       └── interface.j2
└── Section-3-API/
    ├── README.md
    ├── scripts/
    │   ├── 01_rest_get_interfaces.py
    │   ├── 02_restconf_push_config.py
    │   └── 03_netbox_inventory.py
    └── examples/
        ├── sample_response.json
        └── postman_collection.json
```

---

## Learning Outcomes

After completing this bootcamp you will be able to:

- Track and roll back network configurations using **Git workflows**
- Write **Ansible playbooks** to configure routers, switches, and firewalls at scale
- Consume **REST / RESTCONF APIs** to query and push configuration programmatically
- Combine all three tools into an end-to-end **automated change pipeline**

---

*Lab version 1.0 — May 2026*
