import subprocess
import re

def scanForHosts(networkRange):
    try:
        result = subprocess.run(
            ['nmap', '-sn', networkRange],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running nmap: {e}")
        return []

    onlineDevices = []
    lines = result.stdout.splitlines()

    ipPattern = re.compile(r'Nmap scan report for (\d+\.\d+\.\d+\.\d+)')
    macPattern = re.compile(r'MAC Address: ([\da-fA-F:]+)')

    currentIp = None

    for line in lines:
        ipMatch = ipPattern.search(line)
        macMatch = macPattern.search(line)

        if ipMatch:
            currentIp = ipMatch.group(1)
        elif macMatch and currentIp:
            onlineDevices.append({'ip': currentIp, 'mac': macMatch.group(1)})
            currentIp = None

    return onlineDevices
