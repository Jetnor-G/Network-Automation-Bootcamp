#!/usr/bin/env python3
"""
Script 05 — Push baseline config via SSH using Netmiko.
Configures: Banner MOTD, Logging, Domain, DNS, NTP
on all devices defined in DEVICES.

Usage: python3 05_push_baseline_ssh.py
Requires: pip install netmiko
"""

from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException

# ── Baseline values ────────────────────────────────────────────────────────
DOMAIN_NAME      = "lab.example.com"
DNS_SERVERS      = ["8.8.8.8", "8.8.4.4"]
NTP_SERVERS      = ["216.239.35.0", "216.239.35.4"]
SYSLOG_SERVER    = "10.0.0.50"
LOG_BUFFER_SIZE  = 16384
LOG_SEVERITY     = "informational"
BANNER_TEXT      = (
    "******************************************************************\n"
    "*   AUTHORIZED ACCESS ONLY — Network Automation Bootcamp Lab     *\n"
    "*   Unauthorized access is strictly prohibited and monitored.    *\n"
    "*   All activities are logged.                                   *\n"
    "******************************************************************"
)

# ── Devices ───────────────────────────────────────────────────────────────────
DEVICES = [
    {"device_type": "cisco_ios",  "host": "10.0.1.1",  "username": "admin", "password": "Lab@1234", "secret": "Lab@1234"},
    {"device_type": "cisco_ios",  "host": "10.0.1.2",  "username": "admin", "password": "Lab@1234", "secret": "Lab@1234"},
    {"device_type": "cisco_ios",  "host": "10.0.1.10", "username": "admin", "password": "Lab@1234", "secret": "Lab@1234"},
]


def build_config_commands():
    """Return a flat list of IOS config commands for the baseline."""
    commands = []

    # Domain
    commands += [f"ip domain-name {DOMAIN_NAME}"]

    # DNS
    commands += [f"ip name-server {ns}" for ns in DNS_SERVERS]

    # NTP (first server is preferred)
    commands += [f"ntp server {NTP_SERVERS[0]} prefer"]
    commands += [f"ntp server {s}" for s in NTP_SERVERS[1:]]
    commands += ["ntp update-calendar"]

    # Logging
    commands += [
        "no logging console",
        f"logging buffered {LOG_BUFFER_SIZE} {LOG_SEVERITY}",
        f"logging host {SYSLOG_SERVER}",
        f"logging trap {LOG_SEVERITY}",
        "service timestamps log datetime msec localtime show-timezone year",
        "service timestamps debug datetime msec localtime show-timezone year",
    ]

    # Banner MOTD  (^ as delimiter — cannot appear in banner text)
    commands += [f"banner motd ^\n{BANNER_TEXT}\n^"]

    return commands


def push_to_device(device):
    host = device["host"]
    print(f"\n[*] Connecting to {host} ...")
    try:
        conn = ConnectHandler(**device)
        conn.enable()

        commands = build_config_commands()
        output   = conn.send_config_set(commands, cmd_verify=False)
        conn.save_config()

        print(f"[+] {host} — config applied and saved.")

        # Verify key items
        ntp_out = conn.send_command("show ntp associations")
        log_out = conn.send_command("show logging | include Syslog|Trap|Buffer")
        print(f"    NTP  : {ntp_out.splitlines()[0] if ntp_out.strip() else 'no associations yet'}")
        print(f"    Log  : {log_out.splitlines()[0] if log_out.strip() else 'no log output'}")

        conn.disconnect()

    except NetmikoTimeoutException:
        print(f"[ERROR] {host} — connection timed out.")
    except NetmikoAuthenticationException:
        print(f"[ERROR] {host} — authentication failed.")


def main():
    commands = build_config_commands()
    print("=" * 60)
    print("Baseline config commands to be pushed:")
    print("=" * 60)
    for cmd in commands:
        print(f"  {cmd}")
    print("=" * 60)

    confirm = input("\nApply to all devices? [y/N]: ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        return

    for device in DEVICES:
        push_to_device(device)

    print("\n[+] All done.")


if __name__ == "__main__":
    main()
