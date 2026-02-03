# Tru-Control 

<img width="150" alt="Apple Store" src="https://github.com/mk4001/Tru-Control/blob/main/images/New-1024.png">
Available on Apple Store 

## Overview

**Tru-Control** is an open-source project designed to extend and simplify access to Truma Combi™ systems by combining existing community work with a modern, native iOS application.

The project builds upon the excellent reverse‑engineering effort by **DanielFett**, in particular the `inetbox.py` project:

https://github.com/danielfett/inetbox.py

The main goal of Tru-Control is to make this ecosystem more accessible and user-friendly by providing both **local** and **remote** control through widely available hardware and open technologies.

---

## Disclaimer

This project is provided **for educational and recreational purposes only**.

All intellectual property, trademarks, and copyrights related to LIN‑BUS codes and protocols remain the property of **Truma Gerätetechnik GmbH & Co. KG (Putzbrunn, Germany)**.

This project does **not** aim to infringe on Truma’s rights, nor to enable unauthorized access, modification, or misuse of proprietary systems. All information shared here is intended solely to support learning and understanding of vehicle communication protocols.

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

Thanks to the Raspberry Pi’s built-in wireless capabilities, Tru-Control supports two complementary usage modes:

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

## Final Notes

If you enjoy experimenting with open-source projects, vehicle electronics, and practical DIY solutions, Tru-Control aims to provide a solid and extensible foundation.

May it help you enjoy safer, smarter, and more comfortable travels—knowing that your Truma Combi™ is always within reach, whether you are nearby or far away.

Contributions, feedback, and constructive discussion are always welcome.


