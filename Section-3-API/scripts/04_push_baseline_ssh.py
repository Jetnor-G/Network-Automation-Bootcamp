#!/usr/bin/env python3
"""
Script 04 — Push baseline config via SSH using Netmiko.
Configures: Banner MOTD, Logging, Domain, DNS, NTP
on all devices defined in DEVICES.

Router-1 / Router-2 are virtual Nexus (NX-OS, no enable needed).
Switch-1 is virtual IOS (needs enable). Command syntax differs per
platform, so commands are built separately for each device_type.

Usage: python3 04_push_baseline_ssh.py
Requires: pip install netmiko
"""

# Netmiko wraps a raw SSH session (via Paramiko) with per-vendor CLI
# handling — it knows how to detect prompts, enter config mode, and send
# commands correctly for each "device_type" without you writing any of
# that logic by hand.
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException

# ── Baseline values ────────────────────────────────────────────────────────
DOMAIN_NAME      = "lab.example.com"
DNS_SERVERS      = ["8.8.8.8", "8.8.4.4"]
NTP_SERVERS      = ["216.239.35.0", "216.239.35.4"]
SYSLOG_SERVER    = "10.106.106.60"
LOG_BUFFER_SIZE  = 16384
LOG_SEVERITY     = "informational"
LOG_SEVERITY_NUM = 6  # NX-OS logging commands take a numeric severity (0-7)
BANNER_TEXT      = (
    "******************************************************************\n"
    "*   AUTHORIZED ACCESS ONLY — Network Automation Bootcamp Lab     *\n"
    "*   Unauthorized access is strictly prohibited and monitored.    *\n"
    "*   All activities are logged.                                   *\n"
    "******************************************************************"
)

# ── Devices ───────────────────────────────────────────────────────────────────
# Each dict is passed straight into Netmiko's ConnectHandler(**device) —
# "device_type" selects the driver Netmiko uses to talk to that platform.
# Only the IOS switch needs "secret" (the enable password); NX-OS logs
# straight into full EXEC mode, so there's nothing to escalate to.
DEVICES = [
    {"device_type": "cisco_nxos", "host": "10.106.106.61", "username": "admin", "password": "Lab@1234"},
    {"device_type": "cisco_nxos", "host": "10.106.106.62", "username": "admin", "password": "Lab@1234"},
    {"device_type": "cisco_ios",  "host": "10.106.106.63", "username": "admin", "password": "Lab@1234", "secret": "Lab@1234"},
]


def build_ios_commands():
    """Return a flat list of classic IOS config commands for the baseline."""
    commands = []

    commands += [f"ip domain-name {DOMAIN_NAME}"]
    commands += [f"ip name-server {ns}" for ns in DNS_SERVERS]

    commands += [f"ntp server {NTP_SERVERS[0]} prefer"]
    commands += [f"ntp server {s}" for s in NTP_SERVERS[1:]]
    commands += ["ntp update-calendar"]

    commands += [
        "no logging console",
        f"logging buffered {LOG_BUFFER_SIZE} {LOG_SEVERITY}",
        f"logging host {SYSLOG_SERVER}",
        f"logging trap {LOG_SEVERITY}",
        "service timestamps log datetime msec localtime show-timezone year",
        "service timestamps debug datetime msec localtime show-timezone year",
    ]

    commands += [f"banner motd ^\n{BANNER_TEXT}\n^"]

    return commands


def build_nxos_commands():
    """Return a flat list of NX-OS config commands for the baseline.

    NX-OS has no "write memory", no "service timestamps", and uses
    "logging server" / "logging logfile" instead of IOS's
    "logging host" / "logging buffered".
    """
    commands = []

    commands += [f"ip domain-name {DOMAIN_NAME}"]
    commands += [f"ip name-server {ns}" for ns in DNS_SERVERS]

    commands += [f"ntp server {NTP_SERVERS[0]} prefer"]
    commands += [f"ntp server {s}" for s in NTP_SERVERS[1:]]

    commands += [
        "no logging console",
        "logging timestamp milliseconds",
        f"logging logfile messages {LOG_SEVERITY_NUM} size {LOG_BUFFER_SIZE}",
        f"logging server {SYSLOG_SERVER} {LOG_SEVERITY_NUM}",
    ]

    commands += [f"banner motd ^\n{BANNER_TEXT}\n^"]

    return commands


def build_config_commands(device_type):
    return build_ios_commands() if device_type == "cisco_ios" else build_nxos_commands()


def push_to_device(device):
    host        = device["host"]
    device_type = device["device_type"]
    print(f"\n[*] Connecting to {host} ({device_type}) ...")
    try:
        conn = ConnectHandler(**device)  # opens the SSH session and logs in
        if device_type == "cisco_ios":
            conn.enable()   # escalate to privileged EXEC — only IOS needs this

        commands = build_config_commands(device_type)
        # send_config_set() enters config mode, sends each command in
        # order, then exits config mode — cmd_verify=False skips Netmiko's
        # per-command echo check, which speeds things up for long lists.
        output   = conn.send_config_set(commands, cmd_verify=False)
        # save_config() runs the correct "save to startup" command for
        # this device_type automatically (Netmiko knows IOS uses
        # "write memory" and NX-OS uses "copy running-config startup-config").
        conn.save_config()

        print(f"[+] {host} — config applied and saved.")

        # Verify key items — send_command() runs a single show command
        # and returns its plain-text output for us to parse/print.
        ntp_cmd = "show ntp associations" if device_type == "cisco_ios" else "show ntp peer-status"
        ntp_out = conn.send_command(ntp_cmd)
        log_out = conn.send_command("show logging")
        print(f"    NTP  : {ntp_out.splitlines()[0] if ntp_out.strip() else 'no associations yet'}")
        print(f"    Log  : {log_out.splitlines()[0] if log_out.strip() else 'no log output'}")

        conn.disconnect()

    # Catching these individually — instead of one bare "except Exception" —
    # means one bad device (timeout, wrong password) can't crash the loop
    # in main() and stop the script from reaching the rest of DEVICES.
    except NetmikoTimeoutException:
        print(f"[ERROR] {host} — connection timed out.")
    except NetmikoAuthenticationException:
        print(f"[ERROR] {host} — authentication failed.")


def main():
    print("=" * 60)
    print("Baseline config commands to be pushed:")
    print("=" * 60)
    for device in DEVICES:
        print(f"\n{device['host']} ({device['device_type']}):")
        for cmd in build_config_commands(device["device_type"]):
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
