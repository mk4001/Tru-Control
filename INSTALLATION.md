# Tru-Control 

<img width="150" alt="Tru-Control app icon" src="https://raw.githubusercontent.com/mk4001/Tru-Control/main/images/New-1024.png">

*iOS app currently under App Store review — not yet publicly available.*

## Overview

**Tru-Control** is a project designed to extend and simplify access to Truma Combi™ systems by combining existing community work with a modern, native iOS application.

The project builds upon the excellent reverse‑engineering effort by **DanielFett**, in particular the `inetbox.py` project:

https://github.com/danielfett/inetbox.py

The main goal of Tru-Control is to make this ecosystem more accessible and user-friendly by providing both **local** and **remote** control through widely available hardware and open technologies.

---

## Disclaimer

This project is provided **for educational and recreational purposes only**.

All intellectual property, trademarks, and copyrights related to LIN‑BUS codes and protocols remain the property of **Truma Gerätetechnik GmbH & Co. KG (Putzbrunn, Germany)**.

This project does **not** aim to infringe on Truma's rights, nor to enable unauthorized access, modification, or misuse of proprietary systems. All information shared here is intended solely to support learning and understanding of vehicle communication protocols.

**Use this project at your own risk.**

---

## Motivation

While `inetbox.py` already provides a powerful software interface for interacting with Truma systems via a Raspberry Pi, its usability in real‑world scenarios is limited without a dedicated client.

Tru-Control was created to fill this gap by introducing:

- A **native iOS application** (currently iOS only)
- Simple **local access** directly from the vehicle
- Optional **remote access** without requiring complex onboard infrastructure

The result is a more practical and flexible way to interact with a Truma Combi™ system, both on-site and from anywhere.

---

## System Architecture (High Level)

The project is based on a compact and low-power setup using a Raspberry Pi connected to the Truma Combi™ via a LIN interface.

Thanks to the Raspberry Pi's built-in wireless capabilities, Tru-Control supports two complementary usage modes:

- **Local mode**: direct peer‑to‑peer communication using Bluetooth Low Energy (BLE)
- **Remote mode**: cloud-based communication via an MQTT broker

No additional onboard routers or permanent Internet connections are required for local operation.

---

## Installation Philosophy

Tru-Control does **not** replace `inetbox.py`. Instead, it extends it.

Users are expected to:

1. Successfully install and test `inetbox.py` on their hardware
2. Add the Tru-Control gateway components
3. Choose whether to enable local access, remote access, or both

Detailed installation steps for the base system are intentionally delegated to the original `inetbox.py` documentation to avoid duplication and ensure compatibility.

---

## Gateway Components

### MQTT Gateway (Remote Access)

The MQTT gateway enables secure remote access by bridging a local MQTT broker running on the Raspberry Pi with a cloud-based MQTT broker.

This allows the Tru-Control iOS app to communicate with the system from anywhere, using standard Internet connectivity.

Several free MQTT cloud services are sufficient for typical personal use and were successfully tested during development.

Once configured, the gateway runs as a background service and operates transparently.

---

### BLE Server (Local Access)

For users who prefer a fully local setup, Tru-Control includes a BLE server component.

This enables direct communication between the iOS app and the Raspberry Pi:

- No Internet connection required
- No router or external network hardware needed
- Ideal for on‑site control inside an RV, camper, or van

The BLE service runs continuously in the background and prioritizes reliability and safety.

---

## iOS App: Tru-Control

The **Tru-Control** iOS app acts as the primary user interface for the system.

### Key Characteristics

- Works over **BLE** (local) and **Internet** (remote)
- Real-time display of Truma Combi™ status information
- Safety‑aware command handling
- Designed for everyday, practical use

### Usage Notes

- The app must be connected to the Raspberry Pi (locally or remotely) to send commands
- If BLE signal quality is insufficient, commands are intentionally disabled while status data remains visible
- Due to LIN‑BUS communication characteristics, command execution is not instantaneous and feedback may be delayed by a few seconds
- Errors reported by the Truma system are displayed directly in the app with detailed descriptions

### Additional Features

- Debug logging for both BLE and Internet connections
- Leisure battery monitoring (AGM-calibrated): voltage, charge percentage, and status
- Background operation optimized to minimize iOS battery consumption, especially in BLE mode

---

## Project Goals

- Promote **open knowledge** around vehicle communication systems
- Build on and contribute to existing community projects
- Keep hardware requirements minimal and affordable
- Prioritize safety, transparency, and user control

---

## Documentation

- 📦 Installation: see INSTALLATION.md
- ⚡ Quick Start: see Quick_Start.md
- 🛠 Troubleshooting: see TROUBLESHOOTING.md

---

## Simulator

A Truma Combi™ simulator profile for local testing (local MQTT broker + Node-RED) is planned but not yet published in this repository. This section will be updated once the file is available.

---

## Final Notes

If you enjoy experimenting with open-source projects, vehicle electronics, and practical DIY solutions, Tru-Control aims to provide a solid and extensible foundation.

May it help you enjoy safer, smarter, and more comfortable travels—knowing that your Truma Combi™ is always within reach, whether you are nearby or far away.

Contributions, feedback, and constructive discussion are always welcome.
INSTALLATION.md
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
