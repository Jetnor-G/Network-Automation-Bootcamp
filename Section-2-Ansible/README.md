# Section 2 — Ansible for Network Automation

## Objective

Use **Ansible** to configure routers and switches at scale using playbooks and Jinja2 templates. This section uses the shared lab devices (Router-1, Router-2, Switch-1) and NetBox as the source of truth for inventory.

---

## Lab Devices

| Host | IP | OS | Role |
|------|----|----|------|
| router1 | 10.106.106.61 | NX-OS (virtual Nexus) | Core router / OSPF |
| router2 | 10.106.106.62 | NX-OS (virtual Nexus) | Secondary router |
| switch1 | 10.106.106.63 | IOS (virtual) | Access switch / VLANs |

Routers use `cisco.nxos.*` modules and log in straight to full EXEC (no `enable`/become needed).
Switch-1 uses `cisco.ios.*` modules and does need `enable` — see the per-group vars in
`inventory/hosts.ini`.

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
| `cisco.ios.ios_facts` / `cisco.nxos.nxos_facts` | Gather device facts (IOS / NX-OS) |
| `cisco.ios.ios_config` / `cisco.nxos.nxos_config` | Push configuration lines |
| `cisco.ios.ios_command` / `cisco.nxos.nxos_command` | Run show commands |
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

## Playbook 4 — Baseline Config (Banner, Logging, Domain, DNS, NTP)

```bash
# Dry run first
ansible-playbook -i inventory/hosts.ini playbooks/04-baseline-config.yml --check --diff

# Apply to all devices
ansible-playbook -i inventory/hosts.ini playbooks/04-baseline-config.yml
```

Variables are centralised in `inventory/group_vars/all.yml` — edit once, applies everywhere:

```yaml
domain_name:     lab.example.com
dns_servers:     [8.8.8.8, 8.8.4.4]
ntp_servers:     [216.239.35.0, 216.239.35.4]
syslog_server:   10.106.106.60
logging_buffer_size: 16384
logging_severity: informational
banner_motd: |
  *** AUTHORIZED ACCESS ONLY ***
```

The `templates/baseline.j2` Jinja2 template renders the full config block from those variables.

### Modules Used in Playbook 4

Playbook 4 runs a separate task per platform for each config block, since the routers (NX-OS)
and switch (IOS) use different resource modules — and NX-OS has no `service timestamps` or
`write memory` equivalent.

| Config Block | IOS (Switch-1) | NX-OS (Router-1/2) |
|--------------|-----------------|---------------------|
| Domain / DNS | `cisco.ios.ios_system` | `cisco.nxos.nxos_system` |
| NTP | `cisco.ios.ios_ntp_global` | `cisco.nxos.nxos_ntp_global` |
| Logging | `cisco.ios.ios_logging_global` | `cisco.nxos.nxos_logging_global` |
| Timestamps | `cisco.ios.ios_config` (`service timestamps`) | n/a — set via `timestamp:` key on `nxos_logging_global` |
| Banner | `cisco.ios.ios_banner` | `cisco.nxos.nxos_banner` |
| Save config | `cisco.ios.ios_command` (`write memory`) | `cisco.nxos.nxos_command` (`copy running-config startup-config`) |

---

## Completion Criteria

- [ ] Inventory created with routers and switches groups
- [ ] `gather-facts` playbook runs successfully on all devices
- [ ] `push-config` playbook applies a change via Jinja2 template
- [ ] `compliance-check` playbook generates a report
- [ ] `--check --diff` used before every real push
- [ ] `baseline-config` playbook pushes banner, logging, domain, DNS, NTP to all devices
- [ ] Verify with `show ntp associations` and `show logging` after apply
