# Tru-Control — Hardware Installation (Truma ↔ Raspberry Pi gateway)

> Guide reorganized from the hardware documentation of the open-source project [danielfett/inetbox.py](https://github.com/danielfett/inetbox.py) (README + `docs/` folder), which this gateway uses as the reference implementation for the Truma Combi's LIN bus. For the original photographic diagrams and the physical RJ12 pinout, see [`connections.png`](https://github.com/danielfett/inetbox.py/blob/master/docs/connections.png), [`pinout.jpg`](https://github.com/danielfett/inetbox.py/blob/master/docs/pinout.jpg) and [`cpplus.jpg`](https://github.com/danielfett/inetbox.py/blob/master/docs/cpplus.jpg) in the original repository.

## What this installation achieves

Tru-Control never talks to the heater directly: it relies on a **self-hosted gateway** (a Raspberry Pi) that physically taps into the LIN bus between the Truma Combi and the CP Plus control panel, translates that traffic into MQTT/BLE, and it's that gateway the app actually connects to. This guide covers only the electrical side of that gateway — not the gateway's own software, nor the app.

## Required hardware

| Component | Notes |
|---|---|
| Truma Combi (4/6 or E) | Verified by the original author on the Combi 4; Combi 6/E should work on the same bus |
| CP Plus control panel | Must be labeled **"inet ready"** — older CP Plus panels don't expose the required bus |
| Raspberry Pi | Any recent model with GPIO and UART available |
| LIN-to-UART transceiver module | Adapts the Truma LIN bus's electrical levels to the Raspberry Pi's 3.3V serial pins |
| RJ12 cable (6P6C, 6-pin) | Standard telephony cable, used by the Truma bus |
| RJ12 splitter (optional) | Only needed to tap the signal without disconnecting the existing cable between Combi and CP Plus |
| 12V power supply | Shared with the one already powering the Combi and CP Plus |

## Wiring: transceiver ↔ Raspberry Pi

| Transceiver pin | Connects to |
|---|---|
| 12V | External 12V supply (same one powering Combi/CP Plus) |
| TX | Raspberry Pi GPIO 15 (Pi's RX) |
| RX | Raspberry Pi GPIO 14 (Pi's TX) |
| GND (second GND pin) | A Raspberry Pi ground pin |
| INH, SLP | Not connected |

**Easy mistake to make**: the transceiver's TX goes to the Pi's RX and vice versa — it's a crossed connection (as on any serial bus), not a 1:1 wiring.

## Wiring: transceiver ↔ Truma bus (RJ12)

| Transceiver pin | RJ12 connector pin |
|---|---|
| LIN | Pin 3 |
| GND | Pin 5 |

The RJ12 connector plugs into **any free port on the Truma Combi**, or — if none is free — is inserted with a splitter directly into the existing cable between the Combi and the CP Plus panel, with no need to cut or modify it.

## Raspberry Pi software prerequisites (before the actual gateway software)

1. Enable the Raspberry Pi's hardware UART (disabling the default serial console) — the exact steps vary slightly by Raspberry Pi model/OS version; follow the official guide for your model.
2. Grant the user that will run the gateway access to the serial port:
   ```bash
   sudo adduser pi dialout
   ```
3. Log out and back in (or reboot) for the permission to take effect.

## Safety notes

- The transceiver's 12V supply must share the **same ground/reference** as the Combi and CP Plus. A floating ground or an unreferenced separate supply can cause unstable bus readings or damage the transceiver.
- Confirm the panel is actually "inet ready" **before** opening any connector: on an incompatible panel the exposed bus may not be the same one, risking short circuits between pins not meant for this use.
- As with any work on the camper/RV's electrical system: disconnect the Truma's power before inserting or removing RJ12 connectors.

## Compatibility notes

- Verified by the original author on a **Truma Combi 4**; Combi 6 and E are expected to share the same bus protocol but haven't been directly confirmed by him.
- The CP Plus panel must expose the **"inet ready"** feature — that's the prerequisite that physically exposes the LIN bus this guide relies on.
