# Network Automation Bootcamp — Lab Topology

## Full Topology Diagram

```
                              INTERNET
                                  │
                 ─────────────────┼──────────────────────
                   FREE PUBLIC APIs (no account needed)
                 ─────────────────┼──────────────────────
                 │                │                      │
        ┌────────┴──────┐ ┌───────┴──────┐  ┌───────────┴────────┐
        │ Cisco DevNet  │ │  BGPView API │  │   PeeringDB API    │
        │ Always-On     │ │ api.bgpview  │  │ peeringdb.com/api/ │
        │ IOS-XE (free) │ │  .io (free)  │  │      (free)        │
        └───────────────┘ └──────────────┘  └────────────────────┘
                 │                │                      │
                 └────────────────┼──────────────────────┘
                                  │ HTTPS / REST
══════════════════════════════════╪═══════════════════════════════════════
                 CLASSROOM MANAGEMENT NETWORK  10.0.0.0/24
══════════════════════════════════╪═══════════════════════════════════════
                                  │
                          ┌───────┴────────┐        ┌────────────────┐
                          │  GIT SERVER    │        │    NETBOX      │
                          │  10.0.0.60     │        │ 10.100.100.25  │
                          │  (Gitea)       │        │ Port: 8000     │
                          │ • Shared repo  │        │ • IPAM / DCIM  │
                          │ • Student repos│        │ • Device reg.  │
                          │ • Webhooks     │        │ • API source   │
                          └───────┬────────┘        │ • Dynamic inv. │
                                  │                  └───────┬────────┘
                                  │                          │
══════════════════════════════════╪══════════════════════════╪══════════
          AUTOMATION & DEVICE NETWORK  10.106.106.0/24
══════════════════════════════════╪══════════════════════════╪══════════
                                  │                          │
                          ┌───────┴────────┐                 │
                          │ CONTROL NODE   │◄─── REST API ────┘
                          │ 10.106.106.60  │
                          │ • Git client   │
                          │ • Ansible      │
                          │ • Python 3     │
                          │ • VS Code      │
                          │ • SSH access   │
                          └───────┬────────┘
                                  │
                                  │   SSH / RESTCONF / Ansible
                                  │
        ┌────────────────────────┼────────────────┐
        │                        │                │
  ┌─────┴──────────┐ ┌───────────┴────┐  ┌────────┴───────┐
  │  ROUTER-1      │ │  ROUTER-2      │  │  SWITCH-1      │
  │ 10.106.106.61  │ │ 10.106.106.62  │  │ 10.106.106.63  │
  │                │ │                │  │                │
  │ IOS-XE         │ │ NX-OS          │  │ IOS            │
  │ OSPF Ar. 0     │ │                │  │ VLAN 10/20     │
  │ RESTCONF       │ │                │  │ Mgmt VLAN      │
  │ SSH            │ │ SSH            │  │ SSH            │
  └────────────────┘ └────────────────┘  └────────────────┘

══════════════════════════════════════════════════════════════════════════
                 STUDENT PODS  10.0.0.101 – 10.0.0.112
══════════════════════════════════════════════════════════════════════════

  ┌──────────┐ ┌──────────┐ ┌──────────┐     ┌──────────┐
  │ Pod-01   │ │ Pod-02   │ │ Pod-03   │ ... │ Pod-12   │
  │10.0.0.101│ │10.0.0.102│ │10.0.0.103│     │10.0.0.112│
  │Laptop/VM │ │Laptop/VM │ │Laptop/VM │     │Laptop/VM │
  └──────────┘ └──────────┘ └──────────┘     └──────────┘

  Each student:
  ├── Own Git branch  (student/pod-XX-name)
  ├── Own Ansible inventory entry in hosts.ini
  └── Shared read/write access to NetBox (separate API token per pod)
```

---

## IP Address Plan

| Device / Host | IP Address | Subnet | Role |
|---------------|-----------|--------|------|
| Control Node | 10.106.106.60 | /24 | Automation engine (shared) |
| NetBox | 10.100.100.25 | /24 | IPAM / DCIM + API |
| Gitea (Git Server) | 10.0.0.60 | /24 | Repository server |
| Router-1 | 10.106.106.61 | /24 | IOS-XE lab router |
| Router-2 | 10.106.106.62 | /24 | NX-OS lab router |
| Switch-1 | 10.106.106.63 | /24 | IOS access switch |
| Student Pod 01–12 | 10.0.0.101–112 | /24 | Student workstations |

---

## Free Public API Reference

| API | Base URL | Auth | Rate Limit | Best For |
|-----|----------|------|-----------|---------|
| Cisco DevNet IOS-XE | `sandbox-iosxe-latest-1.cisco.com` | Basic (devnetuser/Cisco123!) | None | RESTCONF practice |
| NetBox Demo | `https://demo.netbox.dev/api/` | Token (public demo token) | Fair use | IPAM API queries |
| BGPView | `https://api.bgpview.io/` | None | ~45 req/min | BGP / ASN lookups |
| PeeringDB | `https://www.peeringdb.com/api/` | None (read) | Fair use | IX / peering data |
| ipinfo.io | `https://ipinfo.io/` | None (limited) | 50k/mo | IP geolocation & ASN |
| httpbin.org | `https://httpbin.org/` | None | None | HTTP method practice |

---

## Protocol & Port Reference

| Protocol | Port | Used Between |
|----------|------|-------------|
| SSH | 22 | Control Node → Devices |
| RESTCONF | 443 | Control Node → Router-1 |
| HTTP | 8000 | Students → NetBox |
| HTTP | 3000 | Students → Gitea |
| HTTPS | 443 | Students → Public APIs |
| OSPF | — | Router-1 ↔ Router-2 |
