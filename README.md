# RV-Control 


The Raspberry Pi acts as a **translation layer** between the vehicle's LIN-BUS network and standard wireless protocols. No modification to the Truma hardware is required.

---

## ✅ Requirements

- A **legally purchased** Truma Combi™ system installed in your vehicle  
- A Raspberry Pi (any model with wireless capability)  
- A LIN-BUS transceiver (e.g. Waveshare, USB-to-LIN)  
- Basic familiarity with Raspberry Pi setup and command line

---

## 📲 Features

- **Native iOS app** with clean, modern interface  
- **Real-time status monitoring** (temperature, flame state, error codes)  
- **Full control** of heating modes and temperature setpoints  
- **Dual connectivity**:
  - Bluetooth Low Energy for direct, offline use inside the vehicle
  - MQTT over Internet for remote monitoring (optional)
- **Leisure battery monitoring** (AGM calibrated)
- **Safety-first logic**: commands are disabled if signal quality is insufficient

---

## 🧪 Compatibility

- ✅ Truma Combi 4 (CP plus)
- ✅ Truma Combi 6 (CP plus)
- ⚠️ Other Truma LIN-BUS devices: not officially tested, but may work

This project is **not affiliated with, endorsed by, or sponsored by Truma Gerätetechnik GmbH & Co. KG**. All product names and trademarks are the property of their respective owners.

---

## 🚦 Quick Start

1. **Prepare your Raspberry Pi**  
   Install Raspberry Pi OS Lite, enable SSH, and connect your LIN-BUS interface.

2. **Install the gateway services**  
   Run the automated setup script included in this repository.  
   This will install and configure:
   - BLE advertisement daemon
   - MQTT bridge (optional)

3. **Install the iOS app**  
   Download Tru-Control from the Apple App Store.

4. **Connect**  
   Open the app. Your gateway will appear automatically via BLE scanning.  
   Tap to connect – no cloud account required.

Detailed step-by-step guides are available in:
- [`INSTALLATION.md`](INSTALLATION.md)
- [`Quick_Start.md`](Quick_Start.md)

---

## 🔧 Development & Contributions

This project is maintained by independent developers and **welcomes contributions** that:

- Improve stability and error handling  
- Add support for additional LIN-BUS devices  
- Enhance the iOS user experience  
- Expand documentation

We are particularly interested in **collaborating with Truma** should they wish to provide official guidance or documentation. We believe in building bridges, not walls.

---

## 📜 License

MIT License – see [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgements

Tru-Control builds upon years of community effort to understand and document **LIN-BUS communication in recreational vehicles**. Special thanks to everyone who has contributed to this knowledge base, and to the early testers who provided invaluable feedback.

---

## ⚠️ Important Disclaimer

**This software is intended for personal, non-commercial use by individuals who own the corresponding Truma hardware.**

- You are responsible for your own installation and use.  
- No warranty or liability is provided – use at your own risk.  
- This project does not grant any rights to Truma's intellectual property.  
- If you are a commercial entity, please contact Truma directly for licensing.



