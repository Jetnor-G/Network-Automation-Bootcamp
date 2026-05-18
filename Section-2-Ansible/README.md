# Section 2 — Ansible for Network Automation

## Objective

Use **Ansible** to configure routers and switches at scale using playbooks and Jinja2 templates. This section uses the shared lab devices (Router-1, Router-2, Switch-1) and NetBox as the source of truth for inventory.

---

## Lab Devices

| Host | IP | OS | Role |
|------|----|----|------|
| router1 | 10.0.1.1 | IOS-XE | Core router / OSPF |
| router2 | 10.0.1.2 | NX-OS | Secondary router |
| switch1 | 10.0.1.10 | IOS | Access switch / VLANs |

---

## Playbook 1 — Gather Facts

```bash
ansible-playbook -i inventory/hosts.ini playbooks/01-gather-facts.yml
```

Collects OS version, serial number, and interface list from all devices. Saves per-device YAML files to `./facts/`.

---

## Playbook 2 — Push Interface Configuration

```bash
# Preview changes first (mandatory step in the bootcamp)
ansible-playbook -i inventory/hosts.ini playbooks/02-push-config.yml --check --diff

# Apply after review
ansible-playbook -i inventory/hosts.ini playbooks/02-push-config.yml
```

Renders `templates/interface.j2` per device using variables from `group_vars/`, then pushes and verifies.

---

## Playbook 3 — Compliance Check

```bash
ansible-playbook -i inventory/hosts.ini playbooks/03-compliance-check.yml
```

Verifies SSH v2, NTP, and IP routing are correctly configured. Generates a report in `./reports/`.

---

## Jinja2 Template

`templates/interface.j2` renders per-device interface config from YAML variables:

```jinja2
{% for iface in interfaces %}
interface {{ iface.name }}
 description {{ iface.description }}
 {% if iface.ip is defined %}
 ip address {{ iface.ip }} {{ iface.mask }}
 {% endif %}
 {% if iface.shutdown %}shutdown{% else %}no shutdown{% endif %}
!
{% endfor %}
```

---

## Key Ansible Modules

| Module | Purpose |
|--------|---------|
| `cisco.ios.ios_facts` | Gather device facts |
| `cisco.ios.ios_config` | Push configuration lines |
| `cisco.ios.ios_command` | Run show commands |
| `ansible.netcommon.cli_command` | Vendor-neutral CLI |

---

## Cheat Sheet

| Command | Purpose |
|---------|---------|
| `ansible all -i hosts.ini -m ping` | Connectivity test |
| `ansible-playbook pb.yml --check` | Dry run |
| `ansible-playbook pb.yml --diff` | Show config diff |
| `ansible-playbook pb.yml -l router1` | Limit to one host |
| `ansible-vault encrypt vars.yml` | Encrypt secrets |

---

## Completion Criteria

- [ ] Inventory created with routers and switches groups
- [ ] `gather-facts` playbook runs successfully on all devices
- [ ] `push-config` playbook applies a change via Jinja2 template
- [ ] `compliance-check` playbook generates a report
- [ ] `--check --diff` used before every real push
