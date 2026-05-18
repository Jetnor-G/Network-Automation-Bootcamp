# Network Automation Bootcamp — Lab Topology

## Full Topology Diagram

```
                        INTERNET
                            │
                     ┌──────┴──────┐
                     │  ISP EDGE   │
                     │203.0.113.0/30│
                     └──────┬──────┘
                            │ 203.0.113.2
                     ┌──────┴──────────────────────┐
                     │        ROUTER-1              │
                     │  Gi0/0: 203.0.113.1/30       │
                     │  Gi0/1: 10.0.0.1/24          │
                     │  OS   : IOS-XE               │
                     │  OSPF : Area 0               │
                     └──────┬──────────────────────┘
                            │ 10.0.0.1
                     ┌──────┴──────────────────────┐
                     │        SWITCH-1              │
                     │  VLAN 10: SERVERS            │
                     │  VLAN 20: WORKSTATIONS       │
                     │  VLAN 99: MANAGEMENT         │
                     │  Mgmt  : 10.0.0.10/24        │
                     └──────┬──────┬───────────────┘
                    VLAN 10 │      │ VLAN 20
              ┌─────────────┘      └──────────────┐
      ┌───────┴────────┐              ┌───────────┴──────┐
      │   SERVER-1     │              │  WORKSTATION-1   │
      │  10.0.10.1/24  │              │  10.0.20.1/24    │
      └────────────────┘              └──────────────────┘

  ── MANAGEMENT NETWORK (10.0.0.0/24) ──────────────────────────────────
                            │ 10.0.0.0/24
        ┌─────────┬─────────┼──────────┬──────────┐
        │         │         │          │          │
  ┌─────┴───┐ ┌───┴─────┐ ┌─┴───────┐ ┌┴─────────┐ ┌──────────────┐
  │CONTROL  │ │ROUTER-2 │ │FIREWALL │ │ NETBOX   │ │   NMS/API    │
  │  NODE   │ │10.0.0.2 │ │10.0.0.254│ │10.0.0.100│ │  10.0.0.200  │
  │10.0.0.50│ │NX-OS    │ │  ASA    │ │:8000     │ │    :8080     │
  │         │ │         │ │         │ │          │ │              │
  │ • Git   │ │         │ │         │ │          │ │              │
  │ • Ansible│ └─────────┘ └─────────┘ └──────────┘ └──────────────┘
  │ • Python│
  └─────────┘
```

## IP Address Plan

| Device | Interface | IP Address | Subnet | Role |
|--------|-----------|-----------|--------|------|
| Router-1 | Gi0/0 | 203.0.113.1 | /30 | WAN Uplink |
| Router-1 | Gi0/1 | 10.0.0.1 | /24 | LAN Gateway |
| Router-2 | Gi0/0 | 10.0.0.2 | /24 | Secondary Router |
| Switch-1 | Vlan99 | 10.0.0.10 | /24 | Mgmt |
| Firewall-1 | Mgmt | 10.0.0.254 | /24 | Default GW Backup |
| Control Node | eth0 | 10.0.0.50 | /24 | Automation Engine |
| NetBox | eth0 | 10.0.0.100 | /24 | IPAM / DCIM |
| NMS/API | eth0 | 10.0.0.200 | /24 | REST API Endpoint |
| Server-1 | eth0 | 10.0.10.1 | /24 | VLAN 10 Server |
| Workstation-1 | eth0 | 10.0.20.1 | /24 | VLAN 20 Client |

## Protocol & Port Reference

| Protocol | Port | Used By | Direction |
|----------|------|---------|-----------|
| SSH | 22 | Ansible, Netmiko | Control → Devices |
| RESTCONF | 443 | Python REST scripts | Control → Devices |
| NETCONF | 830 | ncclient | Control → Devices |
| HTTP | 8000 | NetBox API | Control → NetBox |
| HTTP | 8080 | NMS API | Control → NMS |
| OSPF | N/A | Router-1, Router-2 | Between Routers |

## Connection Legend

```
───────  Physical / logical link
═══════  Management-plane connection (SSH / API)
- - - -  Out-of-band management
```
