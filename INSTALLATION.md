# Tru-Control – Installation Guide

This document provides the **complete, step-by-step installation instructions** for Tru-Control.

It is intentionally separated from the main README to keep conceptual documentation clean while offering a **fully reproducible setup** for users who want to deploy the project.

---

## Prerequisites

Before proceeding, ensure the following requirements are met:

- Raspberry Pi (tested with **Raspberry Pi Zero 2W**)
- Truma Combi™ system properly wired and powered
- LIN-UART interface (**FST T151**)
- `inetbox.py` installed, configured, and **fully working**

> ⚠️ **Important**  
> Tru-Control extends `inetbox.py`. Do **not** proceed unless:
> - Hardware wiring is correct
> - `inetbox.py` can read Truma status successfully

Reference project:
https://github.com/danielfett/inetbox.py

---

## Directory Structure

The Tru-Control repository provides additional Python scripts and example configuration files inside the following directory:
Python add ons/
├── mqtt_bridge_complete.py
├── truma_ble_server.py
├── mqtt-bridge.service.sh
├── truma-ble.service.sh
├── config.json_EMQX
└── config.json_HiveMQ

---
## MQTT Gateway Installation (Remote Access)
This section enables **remote access** to the Truma Combi™ system via a cloud MQTT broker.
### 1. Choose a Cloud MQTT Broker
The following free-tier services were tested successfully:
- https://www.emqx.com
- https://www.hivemq.com
Create a free cluster and **save the credentials** provided by the service.
---
### 2. Install the MQTT Gateway Script
Install the required Python dependency:
```bash
sudo pip3 install paho-mqtt
Copy the gateway script to a system-wide location:

sudo nano /usr/local/bin/mqtt_bridge_complete.py
Paste the contents of mqtt_bridge_complete.py into this file.

Make the script executable:

sudo chmod +x /usr/local/bin/mqtt_bridge_complete.py
3. Configure Broker Credentials
Create the configuration directory if it does not exist:

sudo mkdir -p /etc/mqtt_bridge
Copy the example configuration file matching your broker (the repository ships config.json_EMQX and config.json_HiveMQ under Python add ons/):

sudo cp "Python add ons/config.json_EMQX" /etc/mqtt_bridge/config.json
# or, for HiveMQ:
sudo cp "Python add ons/config.json_HiveMQ" /etc/mqtt_bridge/config.json
Then edit the file and replace only the credential fields:

sudo nano /etc/mqtt_bridge/config.json
⚠️ Do not modify topic names or structure.

4. Create and Enable the MQTT Service
Use the provided shell script to install the systemd service:

sudo sh mqtt-bridge.service.sh
Reload systemd and start the service:

sudo systemctl daemon-reload
sudo systemctl enable --now mqtt-bridge
Verify service status:

sudo systemctl status mqtt-bridge
View live logs:

sudo journalctl -u mqtt-bridge -f
BLE Server Installation (Local Access)
This section enables local, peer-to-peer access using Bluetooth Low Energy.

1. Install Bluetooth Dependencies
sudo apt-get install -y bluetooth bluez python3-dbus python3-gi
sudo pip3 install paho-mqtt
2. Configure Bluetooth Device
Edit the Bluetooth configuration file:

sudo nano /etc/bluetooth/main.conf
Apply the following settings:

[General]
Name = Truma-BLE
Class = 0x000100
DiscoverableTimeout = 0
Discoverable = yes
AlwaysPairable = yes
Reboot the Raspberry Pi:

sudo reboot
3. Install the BLE Server Script
Copy the BLE server script:

sudo nano /usr/local/bin/truma_ble_server.py
Paste the contents of truma_ble_server.py into this file.

Make it executable:

sudo chmod +x /usr/local/bin/truma_ble_server.py
4. Create and Enable the BLE Service
Install the systemd service using the provided shell script:

sudo sh truma-ble.service.sh
Reload systemd and start the service:

sudo systemctl daemon-reload
sudo systemctl enable --now truma_ble_server.service
Verify service status:

sudo systemctl status truma_ble_server.service
View live logs:

sudo journalctl -u truma_ble_server.service -f
Final Verification
At this point:

inetbox.py is running and communicating with Truma Combi™
MQTT gateway is active (if enabled)
BLE server is active (if enabled)
The Tru-Control iOS app should now be able to connect:

Locally via BLE
Remotely via Internet (MQTT)
Notes
BLE and MQTT modes can coexist
No onboard router is required for BLE-only operation
Cloud access depends entirely on the chosen MQTT broker
Happy hacking — and safe travels 🚐
