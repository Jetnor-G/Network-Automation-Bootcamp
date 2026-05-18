# Section 2 — Ansible for Network Automation

## Objective

Use **Ansible** to automate configuration management across multiple network devices simultaneously. This section covers inventory, playbooks, Jinja2 templates, and compliance checking.

---

## Why Ansible for Network Automation?

| Manual CLI | Ansible Playbook |
|------------|-----------------|
| Log into each device one by one | Push to 100 devices in parallel |
| Easy to miss a device or make a typo | Idempotent — same result every run |
| No record of what changed | YAML playbooks are human-readable docs |
| Hard to enforce standards | Compliance checks run automatically |

---

## Lab Architecture

```
Control Node (Linux)
│
├── inventory/
│   ├── hosts.ini          ← Device list + groups
│   └── group_vars/        ← Per-group variables
│
├── playbooks/
│   ├── 01-gather-facts.yml
│   ├── 02-push-config.yml
│   └── 03-compliance-check.yml
│
└── templates/
    └── interface.j2       ← Jinja2 config template
```

---

## Inventory Setup

### `inventory/hosts.ini`

```ini
[routers]
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
ansible_connection=network_cli
ansible_become=yes
ansible_become_method=enable
```

---

## Playbook 1 — Gather Facts from All Devices

```bash
ansible-playbook -i inventory/hosts.ini playbooks/01-gather-facts.yml
```

### What it does:
- Connects to all network devices
- Collects OS version, serial number, interface list
- Saves output to `./facts/` directory

---

## Playbook 2 — Push Interface Configuration

```bash
# Dry run first (check mode)
ansible-playbook -i inventory/hosts.ini playbooks/02-push-config.yml --check --diff

# Apply for real
ansible-playbook -i inventory/hosts.ini playbooks/02-push-config.yml
```

### What it does:
- Renders the `interface.j2` Jinja2 template per device
- Pushes interface descriptions, IP addresses, and shutdown state
- Verifies the config was applied

---

## Playbook 3 — Compliance Check

```bash
ansible-playbook -i inventory/hosts.ini playbooks/03-compliance-check.yml
```

### What it does:
- Verifies SSH v2 is enabled on all devices
- Ensures NTP server is configured
- Checks that `ip routing` is active on routers
- Generates a compliance report in `./reports/`

---

## Key Ansible Modules for Network Automation

| Module | Purpose | Example |
|--------|---------|---------|
| `cisco.ios.ios_command` | Run show commands | `show ip interface brief` |
| `cisco.ios.ios_config` | Push config lines | `interface Gi0/1` |
| `cisco.ios.ios_facts` | Gather device facts | OS, interfaces, neighbours |
| `ansible.netcommon.cli_command` | Vendor-neutral CLI | Multi-OS commands |
| `ansible.netcommon.netconf_config` | NETCONF push | XML config payloads |
| `community.general.napalm_get_facts` | NAPALM integration | Normalised facts |

---

## Jinja2 Template Example

`templates/interface.j2`:
```jinja2
{% for iface in interfaces %}
interface {{ iface.name }}
 description {{ iface.description }}
 {% if iface.ip is defined %}
 ip address {{ iface.ip }} {{ iface.mask }}
 {% endif %}
 {% if iface.shutdown %}
 shutdown
 {% else %}
 no shutdown
 {% endif %}
!
{% endfor %}
```

---

## Variable Files

`inventory/group_vars/routers.yml`:
```yaml
interfaces:
  - name: GigabitEthernet0/0
    description: WAN_UPLINK
    ip: 203.0.113.1
    mask: 255.255.255.252
    shutdown: false
  - name: GigabitEthernet0/1
    description: LAN_SEGMENT
    ip: 10.0.0.1
    mask: 255.255.255.0
    shutdown: false
```

---

## Ansible Cheat Sheet

| Command | Purpose |
|---------|---------|
| `ansible all -i hosts.ini -m ping` | Connectivity test |
| `ansible-playbook pb.yml --check` | Dry run |
| `ansible-playbook pb.yml --diff` | Show config diff |
| `ansible-playbook pb.yml -l router1` | Limit to one host |
| `ansible-playbook pb.yml --tags ntp` | Run tagged tasks only |
| `ansible-vault encrypt vars.yml` | Encrypt secrets |
| `ansible-doc ios_config` | Module documentation |

---

## Completion Criteria

- [ ] Inventory file created with at least 2 device groups
- [ ] `gather-facts` playbook runs successfully
- [ ] `push-config` playbook applies a change via template
- [ ] `compliance-check` playbook generates a report
- [ ] At least one playbook uses `--check` and `--diff` before applying
