import subprocess
import re
import os

network_range = "10.0.0.0/24"
known_file = "known_devices.txt"
names_file = "device_names.txt"


def run_scan(network):
    result = subprocess.run(
        ["nmap", "-sn", network],
        capture_output=True,
        text=True
    )
    return result.stdout


def parse_nmap_output(output):
    devices = []
    current_device = {}

    for line in output.splitlines():
        line = line.strip()

        ip_match = re.match(r"Nmap scan report for (\d+\.\d+\.\d+\.\d+)", line)
        mac_match = re.match(r"MAC Address: ([0-9A-Fa-f:]{17})(?: \((.*?)\))?", line)

        if ip_match:
            if current_device:
                devices.append(current_device)
            current_device = {
                "ip": ip_match.group(1),
                "mac": None,
                "vendor": None
            }

        elif mac_match and current_device:
            current_device["mac"] = mac_match.group(1).upper()
            current_device["vendor"] = mac_match.group(2) if mac_match.group(2) else None

    if current_device:
        devices.append(current_device)

    return devices


def load_known_devices(filename):
    known = {}
    if os.path.exists(filename):
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("|")
                if len(parts) >= 2:
                    mac = parts[0].strip().upper()
                    ip = parts[1].strip()
                    known[mac] = ip
    return known


def save_known_devices(filename, devices):
    with open(filename, "w") as f:
        for device in sorted(devices, key=lambda d: (d["mac"] or "", d["ip"])):
            if device["mac"]:
                f.write(f'{device["mac"]}|{device["ip"]}\n')


def load_device_names(filename):
    names = {}
    if os.path.exists(filename):
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if "=" in line:
                    mac, name = line.split("=", 1)
                    names[mac.strip().upper()] = name.strip()
    return names


def save_device_names(filename, names):
    with open(filename, "w") as f:
        for mac in sorted(names):
            f.write(f"{mac}={names[mac]}\n")


def display_devices(devices, names):
    print("\nCurrent devices:")
    for device in sorted(devices, key=lambda d: d["ip"]):
        ip = device["ip"]
        mac = device["mac"] or "No MAC Seen"
        vendor = device["vendor"] or "Unknown Vendor"
        label = names.get(device["mac"], "Unknown Device") if device["mac"] else "Unknown Device"
        print(f"- IP: {ip}")
        print(f"  MAC: {mac}")
        print(f"  Name: {label}")
        print(f"  Vendor: {vendor}\n")
    print(f"Total devices: {len(devices)}")


def prompt_to_name_unknowns(devices, names):
    updated = False
    for device in devices:
        mac = device["mac"]
        if mac and mac not in names:
            answer = input(f'Name device {device["ip"]} [{mac}]? Press Enter to skip: ').strip()
            if answer:
                names[mac] = answer
                updated = True
    return updated


def main():
    print(f"Scanning {network_range}...\n")

    output = run_scan(network_range)
    current_devices = parse_nmap_output(output)

    known_devices = load_known_devices(known_file)
    device_names = load_device_names(names_file)

    current_macs = {d["mac"]: d["ip"] for d in current_devices if d["mac"]}
    known_macs = set(known_devices.keys())
    current_mac_set = set(current_macs.keys())

    new_macs = current_mac_set - known_macs
    missing_macs = known_macs - current_mac_set

    display_devices(current_devices, device_names)

    if new_macs:
        print("\nNew device(s) detected:")
        for mac in sorted(new_macs):
            name = device_names.get(mac, "Unknown Device")
            print(f"+ {name} [{mac}] at {current_macs[mac]}")

    if missing_macs:
        print("\nDevice(s) disconnected:")
        for mac in sorted(missing_macs):
            name = device_names.get(mac, "Unknown Device")
            old_ip = known_devices.get(mac, "unknown IP")
            print(f"- {name} [{mac}] last seen at {old_ip}")

    ip_changes = []
    for mac in current_mac_set & known_macs:
        old_ip = known_devices.get(mac)
        new_ip = current_macs.get(mac)
        if old_ip != new_ip:
            ip_changes.append((mac, old_ip, new_ip))

    if ip_changes:
        print("\nIP change(s) detected:")
        for mac, old_ip, new_ip in ip_changes:
            name = device_names.get(mac, "Unknown Device")
            print(f"* {name} [{mac}] moved from {old_ip} to {new_ip}")

    print("\nName any unknown devices you recognize.")
    updated_names = prompt_to_name_unknowns(current_devices, device_names)

    if updated_names:
        save_device_names(names_file, device_names)
        print("\nDevice names saved.")

    save_known_devices(known_file, current_devices)
    print("\nScan complete.")


if __name__ == "__main__":
    main()
import subprocess
import re
import os

network_range = "10.0.0.0/24"
known_file = "known_devices.txt"
names_file = "device_names.txt"


def run_scan(network):
    result = subprocess.run(
        ["nmap", "-sn", network],
        capture_output=True,
        text=True
    )
    return result.stdout


def parse_nmap_output(output):
    devices = []
    current_device = {}

    for line in output.splitlines():
        line = line.strip()

        ip_match = re.match(r"Nmap scan report for (\d+\.\d+\.\d+\.\d+)", line)
        mac_match = re.match(r"MAC Address: ([0-9A-Fa-f:]{17})(?: \((.*?)\))?", line)

        if ip_match:
            if current_device:
                devices.append(current_device)
            current_device = {
                "ip": ip_match.group(1),
                "mac": None,
                "vendor": None
            }

        elif mac_match and current_device:
            current_device["mac"] = mac_match.group(1).upper()
            current_device["vendor"] = mac_match.group(2) if mac_match.group(2) else None

    if current_device:
        devices.append(current_device)

    return devices


def load_known_devices(filename):
    known = {}
    if os.path.exists(filename):
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("|")
                if len(parts) >= 2:
                    mac = parts[0].strip().upper()
                    ip = parts[1].strip()
                    known[mac] = ip
    return known


def save_known_devices(filename, devices):
    with open(filename, "w") as f:
        for device in sorted(devices, key=lambda d: (d["mac"] or "", d["ip"])):
            if device["mac"]:
                f.write(f'{device["mac"]}|{device["ip"]}\n')


def load_device_names(filename):
    names = {}
    if os.path.exists(filename):
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if "=" in line:
                    mac, name = line.split("=", 1)
                    names[mac.strip().upper()] = name.strip()
    return names


def save_device_names(filename, names):
    with open(filename, "w") as f:
        for mac in sorted(names):
            f.write(f"{mac}={names[mac]}\n")


def display_devices(devices, names):
    print("\nCurrent devices:")
    for device in sorted(devices, key=lambda d: d["ip"]):
        ip = device["ip"]
        mac = device["mac"] or "No MAC Seen"
        vendor = device["vendor"] or "Unknown Vendor"
        label = names.get(device["mac"], "Unknown Device") if device["mac"] else "Unknown Device"
        print(f"- IP: {ip}")
        print(f"  MAC: {mac}")
        print(f"  Name: {label}")
        print(f"  Vendor: {vendor}\n")
    print(f"Total devices: {len(devices)}")


def prompt_to_name_unknowns(devices, names):
    updated = False
    for device in devices:
        mac = device["mac"]
        if mac and mac not in names:
            answer = input(f'Name device {device["ip"]} [{mac}]? Press Enter to skip: ').strip()
            if answer:
                names[mac] = answer
                updated = True
    return updated


def main():
    print(f"Scanning {network_range}...\n")

    output = run_scan(network_range)
    current_devices = parse_nmap_output(output)

    known_devices = load_known_devices(known_file)
    device_names = load_device_names(names_file)

    current_macs = {d["mac"]: d["ip"] for d in current_devices if d["mac"]}
    known_macs = set(known_devices.keys())
    current_mac_set = set(current_macs.keys())

    new_macs = current_mac_set - known_macs
    missing_macs = known_macs - current_mac_set

    display_devices(current_devices, device_names)

    if new_macs:
        print("\nNew device(s) detected:")
        for mac in sorted(new_macs):
            name = device_names.get(mac, "Unknown Device")
            print(f"+ {name} [{mac}] at {current_macs[mac]}")

    if missing_macs:
        print("\nDevice(s) disconnected:")
        for mac in sorted(missing_macs):
            name = device_names.get(mac, "Unknown Device")
            old_ip = known_devices.get(mac, "unknown IP")
            print(f"- {name} [{mac}] last seen at {old_ip}")

    ip_changes = []
    for mac in current_mac_set & known_macs:
        old_ip = known_devices.get(mac)
        new_ip = current_macs.get(mac)
        if old_ip != new_ip:
            ip_changes.append((mac, old_ip, new_ip))

    if ip_changes:
        print("\nIP change(s) detected:")
        for mac, old_ip, new_ip in ip_changes:
            name = device_names.get(mac, "Unknown Device")
            print(f"* {name} [{mac}] moved from {old_ip} to {new_ip}")

    print("\nName any unknown devices you recognize.")
    updated_names = prompt_to_name_unknowns(current_devices, device_names)

    if updated_names:
        save_device_names(names_file, device_names)
        print("\nDevice names saved.")

    save_known_devices(known_file, current_devices)
    print("\nScan complete.")


if __name__ == "__main__":
    main()

