#!/usr/bin/env python3
"""Generate the Network Automation Bootcamp Word document."""

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import datetime

doc = Document()

# ── Styles helpers ──────────────────────────────────────────────────────────

def set_heading(doc, text, level=1, color=None):
    h = doc.add_heading(text, level=level)
    if color:
        for run in h.runs:
            run.font.color.rgb = RGBColor(*color)
    return h

def add_code_block(doc, code_text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.5)
    run = p.add_run(code_text)
    run.font.name = "Courier New"
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(0x20, 0x20, 0x20)
    shading = OxmlElement("w:shd")
    shading.set(qn("w:val"), "clear")
    shading.set(qn("w:color"), "auto")
    shading.set(qn("w:fill"), "F0F0F0")
    p._p.get_or_add_pPr().append(shading)
    return p

def add_table(doc, headers, rows, col_widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        for para in hdr_cells[i].paragraphs:
            for run in para.runs:
                run.bold = True
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        tc = hdr_cells[i]._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), "1F4E79")
        tcPr.append(shd)
    for row_data in rows:
        row_cells = table.add_row().cells
        for i, val in enumerate(row_data):
            row_cells[i].text = str(val)
    if col_widths:
        for i, width in enumerate(col_widths):
            for row in table.rows:
                row.cells[i].width = Inches(width)
    doc.add_paragraph()
    return table

# ── Cover page ───────────────────────────────────────────────────────────────

doc.add_paragraph()
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run("Network Automation Bootcamp")
run.bold = True
run.font.size = Pt(28)
run.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
run2 = subtitle.add_run("Lab Guide — Git · Ansible · REST API")
run2.font.size = Pt(16)
run2.font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)

doc.add_paragraph()
meta = doc.add_paragraph()
meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
meta.add_run(f"Version 1.0   |   {datetime.date.today().strftime('%B %Y')}").font.size = Pt(11)

doc.add_page_break()

# ── 1. Introduction ───────────────────────────────────────────────────────────

set_heading(doc, "1. Introduction", 1, (0x1F, 0x4E, 0x79))
doc.add_paragraph(
    "The Network Automation Bootcamp is a hands-on lab environment designed to introduce "
    "network engineers to three core pillars of modern network automation: Git, Ansible, "
    "and REST APIs. Each section builds on the previous one, culminating in a fully "
    "automated change pipeline that can version-control, deploy, and verify network "
    "configurations across a heterogeneous device fleet."
)

set_heading(doc, "1.1 Learning Objectives", 2, (0x2E, 0x74, 0xB5))
objectives = [
    "Use Git to version-control network device configurations and manage change branches.",
    "Write Ansible playbooks that configure routers, switches, and firewalls at scale.",
    "Consume REST and RESTCONF APIs to query device state and push configuration programmatically.",
    "Combine all three tools into a repeatable, auditable end-to-end automation workflow.",
]
for obj in objectives:
    p = doc.add_paragraph(style="List Bullet")
    p.add_run(obj)

set_heading(doc, "1.2 Prerequisites", 2, (0x2E, 0x74, 0xB5))
add_table(doc,
    ["Requirement", "Version", "Purpose"],
    [
        ["Git",        "≥ 2.30",  "Source control for network configs"],
        ["Python",     "≥ 3.9",   "Scripting and API interaction"],
        ["Ansible",    "≥ 2.14",  "Configuration management engine"],
        ["requests",   "latest",  "HTTP client for REST API labs"],
        ["netmiko",    "latest",  "Multi-vendor SSH sessions"],
        ["napalm",     "latest",  "Device abstraction layer"],
    ],
    [2.0, 1.5, 3.5]
)

# ── 2. Lab Topology ───────────────────────────────────────────────────────────

set_heading(doc, "2. Lab Architecture & Topology", 1, (0x1F, 0x4E, 0x79))
doc.add_paragraph(
    "The lab consists of a Control Node running on Linux that communicates with a set of "
    "network devices over the Management Network (10.0.0.0/24). An IPAM platform (NetBox) "
    "and a generic NMS/API endpoint complement the device layer."
)

add_code_block(doc,
"""                        INTERNET
                            │
                     ┌──────┴──────┐
                     │  ISP EDGE   │
                     └──────┬──────┘
                            │ 203.0.113.2
                     ┌──────┴──────────────────┐
                     │        ROUTER-1          │
                     │  Gi0/0: 203.0.113.1/30   │
                     │  Gi0/1: 10.0.0.1/24      │
                     │  IOS-XE / OSPF Area 0    │
                     └──────┬──────────────────┘
                            │
                     ┌──────┴──────────────────┐
                     │        SWITCH-1          │
                     │  VLAN 10/20/99           │
                     │  Mgmt: 10.0.0.10/24      │
                     └──────┬──────┬────────────┘
                  VLAN 10   │      │   VLAN 20
            ┌───────────────┘      └──────────────┐
      ┌─────┴──────┐                     ┌─────────┴──────┐
      │  SERVER-1  │                     │ WORKSTATION-1  │
      │10.0.10.1/24│                     │ 10.0.20.1/24   │
      └────────────┘                     └────────────────┘

  ── MANAGEMENT NETWORK (10.0.0.0/24) ─────────────────────────
        ┌──────────┬──────────┬──────────┬──────────────┐
        │          │          │          │              │
  ┌─────┴───┐ ┌───┴─────┐ ┌──┴──────┐ ┌─┴──────┐ ┌────┴────────┐
  │CONTROL  │ │ROUTER-2 │ │FIREWALL │ │NETBOX  │ │  NMS/API    │
  │  NODE   │ │10.0.0.2 │ │10.0.0.254│ │:8000   │ │   :8080     │
  │10.0.0.50│ │  NX-OS  │ │  ASA    │ │        │ │             │
  │Git/Ans/ │ └─────────┘ └─────────┘ └────────┘ └─────────────┘
  │  API    │
  └─────────┘"""
)

set_heading(doc, "2.1 IP Address Plan", 2, (0x2E, 0x74, 0xB5))
add_table(doc,
    ["Device", "Interface", "IP Address", "Subnet", "Role"],
    [
        ["Router-1",      "Gi0/0",  "203.0.113.1", "/30",  "WAN Uplink"],
        ["Router-1",      "Gi0/1",  "10.0.0.1",   "/24",  "LAN Gateway"],
        ["Router-2",      "Gi0/0",  "10.0.0.2",   "/24",  "Secondary Router"],
        ["Switch-1",      "Vlan99", "10.0.0.10",  "/24",  "Management"],
        ["Firewall-1",    "Mgmt",   "10.0.0.254", "/24",  "Default GW Backup"],
        ["Control Node",  "eth0",   "10.0.0.50",  "/24",  "Automation Engine"],
        ["NetBox",        "eth0",   "10.0.0.100", "/24",  "IPAM / DCIM"],
        ["NMS/API",       "eth0",   "10.0.0.200", "/24",  "REST API Endpoint"],
    ],
    [1.5, 1.2, 1.5, 0.8, 2.0]
)

# ── 3. Section 1 — Git ────────────────────────────────────────────────────────

set_heading(doc, "3. Section 1 — Git for Network Automation", 1, (0x1F, 0x4E, 0x79))
doc.add_paragraph(
    "Git gives network teams a single source of truth for device configurations. "
    "Every change is tracked, attributed, and reversible. This section introduces "
    "core Git concepts through three practical exercises."
)

set_heading(doc, "3.1 Why Git?", 2, (0x2E, 0x74, 0xB5))
add_table(doc,
    ["Traditional Approach", "Git-Based Approach"],
    [
        ["Configs saved on one engineer's laptop", "Shared repository with central backup"],
        ["No change history",                      "Full audit trail: author, date, reason"],
        ["Rollback = manual copy-paste",           "git revert restores instantly"],
        ["No review process",                      "Pull Requests enforce peer review"],
    ],
    [3.2, 3.2]
)

set_heading(doc, "3.2 Exercise 1 — Initialise a Config Repository", 2, (0x2E, 0x74, 0xB5))
doc.add_paragraph("Create a new Git repository and commit a baseline router configuration.")
add_code_block(doc,
"""mkdir net-configs && cd net-configs
git init
git config user.name  "Network Engineer"
git config user.email "neteng@example.com"

cp ../configs/router1_baseline.cfg .
git add router1_baseline.cfg
git commit -m "feat: add Router-1 baseline config"
git log --oneline""")

set_heading(doc, "3.3 Exercise 2 — Branching for Change Management", 2, (0x2E, 0x74, 0xB5))
doc.add_paragraph("Use a feature branch per change request, then merge after peer review.")
add_code_block(doc,
"""git checkout -b change/CR-1042-add-loopback

echo "interface Loopback0
 ip address 10.255.255.1 255.255.255.255
 no shutdown" >> router1_baseline.cfg

git add router1_baseline.cfg
git commit -m "feat(CR-1042): add Loopback0 to Router-1"

git diff main change/CR-1042-add-loopback   # review before merging
git checkout main
git merge --no-ff change/CR-1042-add-loopback""")

set_heading(doc, "3.4 Exercise 3 — Configuration Rollback", 2, (0x2E, 0x74, 0xB5))
doc.add_paragraph("Simulate a bad commit and restore the previous good state.")
add_code_block(doc,
"""echo "no ip routing" >> router1_baseline.cfg
git add router1_baseline.cfg
git commit -m "ERROR: accidentally removed ip routing"

git log --oneline              # identify the good commit hash
git revert HEAD                # safe: creates an undo commit
git push origin main""")

set_heading(doc, "3.5 Key Git Commands", 2, (0x2E, 0x74, 0xB5))
add_table(doc,
    ["Command", "Purpose"],
    [
        ["git init",                    "Initialise a new repository"],
        ["git clone <url>",             "Clone a remote repository"],
        ["git add <file>",              "Stage changes"],
        ["git commit -m 'msg'",         "Commit staged changes"],
        ["git log --oneline",           "Compact commit history"],
        ["git checkout -b <branch>",    "Create and switch to new branch"],
        ["git merge --no-ff <branch>",  "Merge with a merge commit"],
        ["git revert HEAD",             "Undo last commit (safe)"],
        ["git reset --hard <hash>",     "Discard commits (destructive)"],
        ["git tag v1.0",                "Tag a release / golden config"],
    ],
    [3.0, 3.5]
)

# ── 4. Section 2 — Ansible ───────────────────────────────────────────────────

set_heading(doc, "4. Section 2 — Ansible for Network Automation", 1, (0x1F, 0x4E, 0x79))
doc.add_paragraph(
    "Ansible is an agentless automation engine that connects to devices over SSH "
    "or NETCONF and applies declarative YAML playbooks. This section covers inventory "
    "setup, three production-quality playbooks, and Jinja2 templating."
)

set_heading(doc, "4.1 Inventory File", 2, (0x2E, 0x74, 0xB5))
doc.add_paragraph("Group devices by role in inventory/hosts.ini:")
add_code_block(doc,
"""[routers]
router1 ansible_host=10.0.0.1
router2 ansible_host=10.0.0.2

[switches]
switch1 ansible_host=10.0.0.10

[firewalls]
fw1     ansible_host=10.0.0.254

[network:children]
routers
switches
firewalls

[network:vars]
ansible_user=admin
ansible_password=Lab@1234
ansible_network_os=ios
ansible_connection=network_cli""")

set_heading(doc, "4.2 Playbook 1 — Gather Facts", 2, (0x2E, 0x74, 0xB5))
doc.add_paragraph(
    "Connects to all devices, collects OS version, serial number, and interface list, "
    "then saves output to ./facts/ directory."
)
add_code_block(doc,
"ansible-playbook -i inventory/hosts.ini playbooks/01-gather-facts.yml")

set_heading(doc, "4.3 Playbook 2 — Push Interface Configuration", 2, (0x2E, 0x74, 0xB5))
doc.add_paragraph(
    "Renders a Jinja2 template per device and pushes interface descriptions, "
    "IP addresses, and shutdown state."
)
add_code_block(doc,
"""# Dry run first
ansible-playbook -i inventory/hosts.ini playbooks/02-push-config.yml --check --diff

# Apply
ansible-playbook -i inventory/hosts.ini playbooks/02-push-config.yml""")

set_heading(doc, "4.4 Playbook 3 — Compliance Check", 2, (0x2E, 0x74, 0xB5))
doc.add_paragraph(
    "Verifies SSH v2, NTP, and IP routing are configured correctly across all "
    "devices and generates a per-device compliance report."
)
add_code_block(doc,
"ansible-playbook -i inventory/hosts.ini playbooks/03-compliance-check.yml")

set_heading(doc, "4.5 Jinja2 Template Example", 2, (0x2E, 0x74, 0xB5))
add_code_block(doc,
"""{% for iface in interfaces %}
interface {{ iface.name }}
 description {{ iface.description }}
 {% if iface.ip is defined %}
 ip address {{ iface.ip }} {{ iface.mask }}
 {% endif %}
 {% if iface.shutdown %}shutdown{% else %}no shutdown{% endif %}
!
{% endfor %}""")

set_heading(doc, "4.6 Key Ansible Modules", 2, (0x2E, 0x74, 0xB5))
add_table(doc,
    ["Module", "Purpose"],
    [
        ["cisco.ios.ios_command",               "Run show commands on IOS devices"],
        ["cisco.ios.ios_config",                "Push config lines to IOS devices"],
        ["cisco.ios.ios_facts",                 "Gather device facts (OS, interfaces, etc.)"],
        ["ansible.netcommon.cli_command",       "Vendor-neutral CLI commands"],
        ["ansible.netcommon.netconf_config",    "Push NETCONF XML payloads"],
        ["community.general.napalm_get_facts",  "Normalised facts via NAPALM"],
    ],
    [3.0, 3.5]
)

# ── 5. Section 3 — API ────────────────────────────────────────────────────────

set_heading(doc, "5. Section 3 — REST API for Network Automation", 1, (0x1F, 0x4E, 0x79))
doc.add_paragraph(
    "REST and RESTCONF APIs provide structured, programmatic access to network devices "
    "and management platforms. This section covers three Python scripts: querying "
    "interface state, pushing configuration, and building dynamic Ansible inventory "
    "from NetBox."
)

set_heading(doc, "5.1 API Types", 2, (0x2E, 0x74, 0xB5))
add_table(doc,
    ["Type", "Protocol", "Port", "Format", "Used With"],
    [
        ["REST",      "HTTP/S",  "80/443", "JSON",     "NMS, NetBox, Cisco DNA"],
        ["RESTCONF",  "HTTPS",   "443",    "JSON/XML",  "IOS-XE, NX-OS"],
        ["NETCONF",   "SSH",     "830",    "XML",       "IOS-XE, Junos, NX-OS"],
    ],
    [1.2, 1.2, 0.8, 1.2, 2.0]
)

set_heading(doc, "5.2 Script 1 — GET Interface Status", 2, (0x2E, 0x74, 0xB5))
doc.add_paragraph("Queries the RESTCONF interfaces endpoint and prints a formatted table.")
add_code_block(doc,
"""import requests
from requests.auth import HTTPBasicAuth

url = "https://10.0.0.1/restconf/data/ietf-interfaces:interfaces"
resp = requests.get(url,
    auth=HTTPBasicAuth("admin", "Lab@1234"),
    headers={"Accept": "application/yang-data+json"},
    verify=False)
data = resp.json()""")

set_heading(doc, "5.3 Script 2 — PUT Interface Configuration", 2, (0x2E, 0x74, 0xB5))
doc.add_paragraph("Pushes a JSON payload to configure an interface via RESTCONF PUT.")
add_code_block(doc,
"""payload = {
  "ietf-interfaces:interface": {
    "name": "GigabitEthernet0/1",
    "description": "LAN_SEGMENT_AUTOMATED",
    "enabled": True,
    "ietf-ip:ipv4": {
      "address": [{"ip": "10.0.0.1", "prefix-length": 24}]
    }
  }
}
resp = requests.put(url, json=payload, auth=auth, headers=headers, verify=False)""")

set_heading(doc, "5.4 Script 3 — NetBox Dynamic Inventory", 2, (0x2E, 0x74, 0xB5))
doc.add_paragraph(
    "Pulls all active devices from NetBox and outputs Ansible-compatible JSON inventory "
    "grouped by device role. Use as: ansible-playbook pb.yml -i 03_netbox_inventory.py"
)

set_heading(doc, "5.5 RESTCONF Quick Reference", 2, (0x2E, 0x74, 0xB5))
add_table(doc,
    ["HTTP Method", "Action", "Example Path"],
    [
        ["GET",    "Read config/state",    "/restconf/data/ietf-interfaces:interfaces"],
        ["PUT",    "Replace resource",     "/restconf/data/.../interface=Gi0%2F1"],
        ["PATCH",  "Merge/update",         "/restconf/data/.../interface=Gi0%2F1"],
        ["POST",   "Create resource",      "/restconf/data/ietf-interfaces:interfaces"],
        ["DELETE", "Remove resource",      "/restconf/data/.../interface=Gi0%2F1"],
    ],
    [1.5, 1.5, 3.5]
)

# ── 6. End-to-End Pipeline ────────────────────────────────────────────────────

set_heading(doc, "6. End-to-End Automation Pipeline", 1, (0x1F, 0x4E, 0x79))
doc.add_paragraph(
    "Combining all three tools creates a fully auditable, repeatable change pipeline:"
)
add_code_block(doc,
"""CHANGE REQUEST
      │
      ▼
  git checkout -b change/CR-XXXX        ← Branch from main
      │
      ▼
  Edit YAML vars / config template       ← Define desired state
      │
      ▼
  ansible-playbook pb.yml --check --diff ← Preview changes
      │
      ▼
  Pull Request → Peer Review             ← Human gate
      │
      ▼
  git merge --no-ff                      ← Merge to main
      │
      ▼
  ansible-playbook pb.yml                ← Apply to devices
      │
      ▼
  python3 03-compliance-check.py         ← Verify via API
      │
      ▼
  git tag v1.x                           ← Tag golden state""")

# ── 7. Completion Criteria ────────────────────────────────────────────────────

set_heading(doc, "7. Lab Completion Criteria", 1, (0x1F, 0x4E, 0x79))
add_table(doc,
    ["Section", "Criteria", "Done?"],
    [
        ["Git",     "Repository initialised with at least one config file",                 "☐"],
        ["Git",     "At least two commits visible in git log",                              "☐"],
        ["Git",     "Feature branch created and merged",                                    "☐"],
        ["Git",     "Config rollback demonstrated with git revert",                         "☐"],
        ["Ansible", "Inventory file with at least 2 device groups",                        "☐"],
        ["Ansible", "gather-facts playbook runs successfully",                              "☐"],
        ["Ansible", "push-config playbook applies change via Jinja2 template",             "☐"],
        ["Ansible", "compliance-check playbook generates a report",                        "☐"],
        ["API",     "Script 1 queries and prints interface data",                           "☐"],
        ["API",     "Script 2 applies config change via RESTCONF PUT",                     "☐"],
        ["API",     "Script 3 generates Ansible-compatible inventory from NetBox",         "☐"],
        ["API",     "All scripts handle HTTP errors gracefully",                            "☐"],
        ["Pipeline","Full CR-to-deploy pipeline demonstrated end-to-end",                  "☐"],
    ],
    [1.2, 4.0, 0.8]
)

# ── Footer ────────────────────────────────────────────────────────────────────

doc.add_paragraph()
footer_p = doc.add_paragraph()
footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = footer_p.add_run(f"Network Automation Bootcamp v1.0  ·  {datetime.date.today().strftime('%B %Y')}")
run.font.size = Pt(9)
run.font.color.rgb = RGBColor(0x80, 0x80, 0x80)

output_path = "/home/jgo/Documents/Automation/Network-Automation-Bootcamp/Network_Automation_Bootcamp_Lab_Guide.docx"
doc.save(output_path)
print(f"Document saved: {output_path}")
