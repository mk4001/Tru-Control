sudo tee /etc/systemd/system/truma_ble_server.service << 'EOF'
[Unit]
Description=Truma BLE GATT Server
After=bluetooth.target mosquitto.service
Wants=bluetooth.target

[Service]
Type=simple
User=root
ExecStartPre=/bin/sleep 5
ExecStart=/usr/bin/python3 /usr/local/bin/truma_ble_server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
