sudo tee /etc/systemd/system/mqtt-bridge.service << 'EOF'
[Unit]
Description=MQTT Bidirectional Bridge
After=mosquitto.service network.target
Wants=network-online.target

[Service]
Type=simple
User=nobody
ExecStart=/usr/bin/python3 /usr/local/bin/mqtt_bridge_complete.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
Environment=PYTHONUNBUFFERED=1

# Limiti risorse per Pi Zero
MemoryMax=100M
CPUQuota=30%

[Install]
WantedBy=multi-user.target
EOF