sudo mkdir -p /etc/mqtt_bridge

sudo tee /etc/mqtt_bridge/config.json << 'EOF'
{
  "version": "1.0",
  "local_broker": {
    "host": "localhost",
    "port": 1883,
    "client_id": "bridge_local"
  },
  "cloud_broker": {
    "host": "broker.emqx.io",
    "port": 8883,
    "username": "",
    "password": "",
    "client_id": "bridge_cloud",
    "use_tls": true,
    "verify_certificate": false,
    "keepalive": 60
  },
  "topics": {
    "local_to_cloud": [
      "sensors/temperature/#",
      "sensors/humidity/#",
      "test/#"
    ],
    "cloud_to_local": [
      "commands/#",
      "config/#"
    ]
  },
  "options": {
    "enable_local_retain": false,
    "cloud_retain": true,
    "qos": 1,
    "rate_limit_seconds": 2.0,
    "reconnect_delay": 5,
    "log_level": "INFO",
    "debug_messages": true
  }
}
EOF