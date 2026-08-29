# Tru-Control – Installation Guide

This document provides the **complete, step-by-step installation instructions** for Tru-Control.

It is intentionally separated from the main README to keep conceptual documentation clean while offering a **fully reproducible setup** for users who want to deploy the project.

⚠️ If you don't have time and desire to follow these instructions, here's an easy shortcut for you: ⚠️

the ISO image of the ready-to-use SD-Card to download and install on your Raspberry PI Zero 2W

[Download Raspberry Pi Gateway Image](https://github.com/mk4001/Tru-Control/releases/tag/ISO_Image)

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

```
Python add ons/
├── mqtt_bridge_complete.py
├── truma_ble_server.py
├── mqtt-bridge.service.sh
├── truma-ble.service.sh
├── config.json_EMQX
└── config.json_HiveMQ
```

---

## MQTT Gateway Installation (Remote Access)

This section enables **remote access** to the Truma Combi™ system via MQTT.

### Step 1: Choose Your MQTT Broker

**Option A (Recommended) — Self-Hosted Private Broker, Free & Unlimited**

Run your own Mosquitto broker on a Raspberry Pi at home, secured with TLS and exposed to the internet via port forwarding. No third-party service, no usage caps, no subscription, no data going through anyone else's servers — you own the whole stack end to end.

Full step-by-step guide (Mosquitto install, static IP + router port forwarding, Cloudflare DNS, Let's Encrypt TLS certificate on port 8883, firewall hardening with UFW, and Tru-Control app configuration):

👉 **https://github.com/mk4001/MosquittoPI_TLS**

This is the recommended option for anyone comfortable with basic router/DNS configuration who wants full control over their data and connection, at zero ongoing cost.

**Option B — Cloud MQTT Broker (EMQX / HiveMQ)**

If you'd rather not expose your home network, or want the fastest possible setup, the following free-tier cloud services were tested successfully:

- https://www.emqx.com
- https://www.hivemq.com

Create a free cluster and **save the credentials** provided by the service.

---

### Step 2: Install the MQTT Gateway Script

Install the required Python dependency:

```bash
sudo pip3 install paho-mqtt
```

Copy the gateway script to a system-wide location:

```bash
sudo nano /usr/local/bin/mqtt_bridge_complete.py
```

Paste the contents of `mqtt_bridge_complete.py` into this file.

Make the script executable:

```bash
sudo chmod +x /usr/local/bin/mqtt_bridge_complete.py
```

---

### Step 3: Configure Broker Credentials

Create the configuration directory if it does not exist:

```bash
sudo mkdir -p /etc/mqtt_bridge
```

Copy the example configuration file matching your broker (the repository ships `config.json_EMQX` and `config.json_HiveMQ` under `Python add ons/`):

```bash
sudo cp "Python add ons/config.json_EMQX" /etc/mqtt_bridge/config.json
# or, for HiveMQ:
sudo cp "Python add ons/config.json_HiveMQ" /etc/mqtt_bridge/config.json
```

> If you went with **Option A** (self-hosted private broker), either of these files works fine as a structural template — the JSON keys are broker-agnostic. Just replace `host`, `port` (8883), and the username/password with the ones you configured in the [MosquittoPI_TLS](https://github.com/mk4001/MosquittoPI_TLS) guide.

Then edit the file and **replace only the credential fields**:

```bash
sudo nano /etc/mqtt_bridge/config.json
```

> ⚠️ Do **not** modify topic names or structure.

---

### Step 4: Create and Enable the MQTT Service

Use the provided shell script to install the systemd service:

```bash
sudo sh mqtt-bridge.service.sh
```

Reload systemd and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now mqtt-bridge
```

Verify service status:

```bash
sudo systemctl status mqtt-bridge
```

View live logs:

```bash
sudo journalctl -u mqtt-bridge -f
```

---

## BLE Server Installation (Local Access)

This section enables **local, peer-to-peer access** using Bluetooth Low Energy.

### 1. Install Bluetooth Dependencies

```bash
sudo apt-get install -y bluetooth bluez python3-dbus python3-gi
sudo pip3 install paho-mqtt
```

---

### 2. Configure Bluetooth Device

Edit the Bluetooth configuration file:

```bash
sudo nano /etc/bluetooth/main.conf
```

Apply the following settings:

```
[General]
Name = Truma-BLE
Class = 0x000100
DiscoverableTimeout = 0
Discoverable = yes
AlwaysPairable = yes
```

Reboot the Raspberry Pi:

```bash
sudo reboot
```

---

### 3. Install the BLE Server Script

Copy the BLE server script:

```bash
sudo nano /usr/local/bin/truma_ble_server.py
```

Paste the contents of `truma_ble_server.py` into this file.

Make it executable:

```bash
sudo chmod +x /usr/local/bin/truma_ble_server.py
```

---

### 4. Create and Enable the BLE Service

Install the systemd service using the provided shell script:

```bash
sudo sh truma-ble.service.sh
```

Reload systemd and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now truma_ble_server.service
```

Verify service status:

```bash
sudo systemctl status truma_ble_server.service
```

View live logs:

```bash
sudo journalctl -u truma_ble_server.service -f
```

---

## Final Verification

At this point:

- `inetbox.py` is running and communicating with Truma Combi™
- MQTT gateway is active (if enabled)
- BLE server is active (if enabled)

The Tru-Control iOS app should now be able to connect:

- **Locally** via BLE
- **Remotely** via Internet (MQTT)

---

## Notes

- BLE and MQTT modes can coexist
- No onboard router is required for BLE-only operation
- Remote access depends entirely on the chosen MQTT broker — self-hosted ([MosquittoPI_TLS](https://github.com/mk4001/MosquittoPI_TLS)) or cloud (EMQX/HiveMQ)

---

Happy hacking — and safe travels 🚐
```bash
sudo nano /usr/local/bin/mqtt_bridge_complete.py
```

Paste the contents of `mqtt_bridge_complete.py` into this file.

Make the script executable:

```bash
sudo chmod +x /usr/local/bin/mqtt_bridge_complete.py
```

---

### 3. Configure Broker Credentials

Create the configuration directory if it does not exist:

```bash
sudo mkdir -p /etc/mqtt_bridge
```

Copy the example configuration file matching your broker (the repository ships `config.json_EMQX` and `config.json_HiveMQ` under `Python add ons/`):

```bash
sudo cp "Python add ons/config.json_EMQX" /etc/mqtt_bridge/config.json
# or, for HiveMQ:
sudo cp "Python add ons/config.json_HiveMQ" /etc/mqtt_bridge/config.json
```

Then edit the file and **replace only the credential fields**:

```bash
sudo nano /etc/mqtt_bridge/config.json
```

> ⚠️ Do **not** modify topic names or structure.

---

### 4. Create and Enable the MQTT Service

Use the provided shell script to install the systemd service:

```bash
sudo sh mqtt-bridge.service.sh
```

Reload systemd and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now mqtt-bridge
```

Verify service status:

```bash
sudo systemctl status mqtt-bridge
```

View live logs:

```bash
sudo journalctl -u mqtt-bridge -f
```

---

## BLE Server Installation (Local Access)

This section enables **local, peer-to-peer access** using Bluetooth Low Energy.

### 1. Install Bluetooth Dependencies

```bash
sudo apt-get install -y bluetooth bluez python3-dbus python3-gi
sudo pip3 install paho-mqtt
```

---

### 2. Configure Bluetooth Device

Edit the Bluetooth configuration file:

```bash
sudo nano /etc/bluetooth/main.conf
```

Apply the following settings:

```
[General]
Name = Truma-BLE
Class = 0x000100
DiscoverableTimeout = 0
Discoverable = yes
AlwaysPairable = yes
```

Reboot the Raspberry Pi:

```bash
sudo reboot
```

---

### 3. Install the BLE Server Script

Copy the BLE server script:

```bash
sudo nano /usr/local/bin/truma_ble_server.py
```

Paste the contents of `truma_ble_server.py` into this file.

Make it executable:

```bash
sudo chmod +x /usr/local/bin/truma_ble_server.py
```

---

### 4. Create and Enable the BLE Service

Install the systemd service using the provided shell script:

```bash
sudo sh truma-ble.service.sh
```

Reload systemd and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now truma_ble_server.service
```

Verify service status:

```bash
sudo systemctl status truma_ble_server.service
```

View live logs:

```bash
sudo journalctl -u truma_ble_server.service -f
```

---

## Final Verification

At this point:

- `inetbox.py` is running and communicating with Truma Combi™
- MQTT gateway is active (if enabled)
- BLE server is active (if enabled)

The Tru-Control iOS app should now be able to connect:

- **Locally** via BLE
- **Remotely** via Internet (MQTT)

---

## Notes

- BLE and MQTT modes can coexist
- No onboard router is required for BLE-only operation
- Cloud access depends entirely on the chosen MQTT broker

---

Happy hacking — and safe travels 🚐
