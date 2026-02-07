# Tru-Control – Troubleshooting Guide

This document collects common issues encountered during installation or operation of Tru-Control and provides practical steps to diagnose and resolve them.

---

## BLE Issues

### BLE Device Not Visible on iPhone

**Symptoms**
- The Tru-Control app cannot find the Raspberry Pi
- The BLE device does not appear during scanning

**Checks**
- Ensure Bluetooth is enabled on the Raspberry Pi
- Verify that the BLE service is running
- Confirm the Raspberry Pi has been rebooted after Bluetooth configuration

**Diagnostic Commands**
```bash
systemctl status truma_ble_server.service
bluetoothctl show
```

**Common Causes**
- Bluetooth service not running
- Incorrect Bluetooth configuration
- Raspberry Pi not discoverable

---

### BLE Connects but Commands Are Disabled

**Symptoms**
- Status data is visible
- Commands are not accepted

**Explanation**
This is expected behavior when BLE signal quality is insufficient. For safety reasons, commands are disabled while still allowing read-only access.

**Resolution**
- Reduce distance between iPhone and Raspberry Pi
- Remove physical obstructions

---

## MQTT Issues

### App Does Not Connect via Internet

**Symptoms**
- App shows "Disconnected" in Internet mode
- No status updates from Truma Combi™

**Checks**
- Verify Internet connectivity on the Raspberry Pi
- Confirm MQTT credentials are correct
- Ensure the MQTT service is running

**Diagnostic Commands**
```bash
systemctl status mqtt-bridge
journalctl -u mqtt-bridge -n 50
```

**Common Causes**
- Incorrect broker hostname or port
- Invalid credentials
- Free-tier broker limits reached

---

### MQTT Service Running but No Data

**Symptoms**
- MQTT service is active
- No messages received by the app

**Checks**
- Ensure topic structure has not been modified
- Confirm `inetbox.py` is publishing locally
- Check cloud broker dashboard for incoming messages

---

## inetbox.py Issues

### No Data from Truma Combi™

**Symptoms**
- App connects but shows no status

**Checks**
- Verify `inetbox.py` is running correctly
- Confirm LIN-UART wiring
- Test communication directly via `inetbox.py`

**Important**
If `inetbox.py` does not work standalone, Tru-Control will not work.

---

## General Diagnostics

### Check Running Services

```bash
systemctl list-units --type=service | grep truma
systemctl list-units --type=service | grep mqtt
```

### View Live Logs

```bash
journalctl -f
```

---

## Still Stuck?

If the issue persists:

- Re-read INSTALLATION.md step-by-step
- Restart the Raspberry Pi
- Open an issue with logs and a clear description of the problem

Community feedback and reports help improve the project for everyone.

---

Happy debugging 🚐

