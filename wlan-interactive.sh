#!/bin/bash

# Interactive WLAN Password Viewer
# Asks user for Wi-Fi network name and shows its password

echo "Interactive WLAN Password Viewer"
echo "==============================="
echo ""

# Get current Wi-Fi network (only SSID, not MAC address)
current_ssid=$(powershell -ExecutionPolicy Bypass -File get-current-ssid.ps1)

# Get Wi-Fi network name from user
echo -n "Enter Wi-Fi network name (or press Enter for current: $current_ssid): "
read ssid

# If input is empty, use current network
if [ -z "$ssid" ]; then
    if [ -n "$current_ssid" ]; then
        ssid="$current_ssid"
        echo "Using current network: $ssid"
    else
        echo "ERROR: No current Wi-Fi connection found and no network name provided"
        read -s -p "Press any key to exit ..."
        exit 1
    fi
fi

echo ""
echo "Searching for network: $ssid"
echo ""

# Get profile details with password
netsh wlan show profile name="$ssid" key=clear

# Check if command was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "Profile found!"
else
    echo ""
    echo "ERROR: Network '$ssid' not found"
    echo "Available networks:"
    netsh wlan show profiles | grep -o ":\s*.*" | sed 's/:\s*//'
fi

echo ""
read -s -p "Press any key to exit ..."
