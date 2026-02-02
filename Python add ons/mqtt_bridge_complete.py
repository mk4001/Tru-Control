#!/usr/bin/python3
"""
MQTT Bridge Completo con Configurazione JSON
Locale ↔ Cloud EMQX con TLS e filtri
"""
import json
import paho.mqtt.client as mqtt
import ssl
import time
import logging
import sys
from pathlib import Path
from datetime import datetime

# ============ CARICA CONFIGURAZIONE ============
CONFIG_PATH = Path("/etc/mqtt_bridge/config.json")

try:
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    
    # Config locale
    LOCAL = config["local_broker"]
    LOCAL_HOST = LOCAL["host"]
    LOCAL_PORT = LOCAL["port"]
    LOCAL_CLIENT_ID = LOCAL.get("client_id", "mqtt_bridge_local")
    
    # Config cloud
    CLOUD = config["cloud_broker"]
    CLOUD_HOST = CLOUD["host"]
    CLOUD_PORT = CLOUD["port"]
    CLOUD_USERNAME = CLOUD.get("username", "")
    CLOUD_PASSWORD = CLOUD.get("password", "")
    CLOUD_CLIENT_ID = CLOUD.get("client_id", "mqtt_bridge_cloud")
    USE_TLS = CLOUD.get("use_tls", True)
    VERIFY_CERT = CLOUD.get("verify_certificate", False)
    
    # Topic
    TOPICS = config["topics"]
    LOCAL_TO_CLOUD = TOPICS["local_to_cloud"]
    CLOUD_TO_LOCAL = TOPICS["cloud_to_local"]
    
    # Opzioni
    OPTIONS = config["options"]
    ENABLE_LOCAL_RETAIN = OPTIONS.get("enable_local_retain", False)
    CLOUD_RETAIN = OPTIONS.get("cloud_retain", True)
    QOS = OPTIONS.get("qos", 1)
    RATE_LIMIT = OPTIONS.get("rate_limit_seconds", 2.0)
    RECONNECT_DELAY = OPTIONS.get("reconnect_delay", 5)
    LOG_LEVEL = OPTIONS.get("log_level", "INFO")
    DEBUG_MSGS = OPTIONS.get("debug_messages", True)
    
except Exception as e:
    print(f"❌ Errore caricamento configurazione {CONFIG_PATH}: {e}")
    sys.exit(1)

# ============ SETUP LOGGING ============
log_levels = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR
}

logging.basicConfig(
    level=log_levels.get(LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# ============ CLASSE BRIDGE ============
class MQTTBridge:
    def __init__(self):
        self.last_sent = {}
        self.message_count = {
            "local_to_cloud": 0,
            "cloud_to_local": 0,
            "errors": 0
        }
        
        # Inizializza client
        self.setup_clients()
        
    def setup_clients(self):
        """Configura i client MQTT"""
        # Client LOCALE
        self.local = mqtt.Client(client_id=LOCAL_CLIENT_ID)
        self.local.on_connect = self.on_local_connect
        self.local.on_message = self.on_local_message
        self.local.on_disconnect = self.on_local_disconnect
        
        # Client CLOUD
        self.cloud = mqtt.Client(client_id=CLOUD_CLIENT_ID)
        self.cloud.on_connect = self.on_cloud_connect
        self.cloud.on_message = self.on_cloud_message
        self.cloud.on_disconnect = self.on_cloud_disconnect
        
        # Configura TLS per cloud se richiesto
        if USE_TLS and CLOUD_PORT in [8883, 8884]:
            try:
                self.cloud.tls_set(
                    ca_certs=None,  # Usa certificati di sistema
                    cert_reqs=ssl.CERT_REQUIRED if VERIFY_CERT else ssl.CERT_NONE,
                    tls_version=ssl.PROTOCOL_TLS
                )
                self.cloud.tls_insecure_set(not VERIFY_CERT)
                logger.info(f"TLS {'con' if VERIFY_CERT else 'senza'} verifica certificato")
            except Exception as e:
                logger.error(f"Errore configurazione TLS: {e}")
        
        # Autenticazione cloud
        if CLOUD_USERNAME and CLOUD_PASSWORD:
            self.cloud.username_pw_set(CLOUD_USERNAME, CLOUD_PASSWORD)
            logger.info(f"Autenticazione cloud: {CLOUD_USERNAME}")
    
    def rate_limit_check(self, topic):
        """Controlla rate limiting"""
        now = time.time()
        if topic in self.last_sent:
            elapsed = now - self.last_sent[topic]
            if elapsed < RATE_LIMIT:
                return False
        self.last_sent[topic] = now
        return True
    
    # ============ CALLBACKS LOCAL ============
    def on_local_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info(f"✅ Connesso al broker LOCALE ({LOCAL_HOST}:{LOCAL_PORT})")
            # Sottoscrizione ai topic
            for topic in LOCAL_TO_CLOUD:
                client.subscribe(topic, qos=QOS)
                logger.debug(f"  📡 Sottoscritto a: {topic}")
        else:
            logger.error(f"❌ Errore connessione LOCALE: {rc}")
    
    def on_local_message(self, client, userdata, msg):
        """Messaggio ricevuto dal broker LOCALE → invia al CLOUD"""
        if DEBUG_MSGS:
            payload_preview = msg.payload.decode()[:50] + "..." if len(msg.payload) > 50 else msg.payload.decode()
            logger.debug(f"📨 LOCALE: {msg.topic} = {payload_preview}")
        
        # Controlla se deve essere inoltrato
        forward = False
        for pattern in LOCAL_TO_CLOUD:
            if mqtt.topic_matches_sub(pattern, msg.topic):
                forward = True
                break
        
        if not forward:
            return
        
        # Rate limiting
        if not self.rate_limit_check(msg.topic):
            logger.debug(f"⏭️  Rate limit per: {msg.topic}")
            return
        
        try:
            # Invia al CLOUD
            result = self.cloud.publish(
                topic=msg.topic,
                payload=msg.payload,
                qos=QOS,
                retain=CLOUD_RETAIN
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.message_count["local_to_cloud"] += 1
                if self.message_count["local_to_cloud"] % 10 == 0:
                    logger.info(f"☁️  Inviati al cloud: {self.message_count['local_to_cloud']}")
                elif DEBUG_MSGS:
                    logger.debug(f"⬆️  {msg.topic} → cloud")
            else:
                self.message_count["errors"] += 1
                logger.warning(f"⚠️  Errore pubblicazione cloud: {result.rc}")
                
        except Exception as e:
            self.message_count["errors"] += 1
            logger.error(f"❌ Eccezione local→cloud: {e}")
    
    def on_local_disconnect(self, client, userdata, rc):
        if rc != 0:
            logger.warning(f"🔌 Disconnesso da LOCALE: {rc}")
    
    # ============ CALLBACKS CLOUD ============
    def on_cloud_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info(f"✅ Connesso al broker CLOUD ({CLOUD_HOST}:{CLOUD_PORT})")
            # Sottoscrizione ai topic
            for topic in CLOUD_TO_LOCAL:
                client.subscribe(topic, qos=QOS)
                logger.debug(f"  ☁️  Sottoscritto a: {topic}")
        else:
            logger.error(f"❌ Errore connessione CLOUD: {rc}")
            logger.error("  Verifica: 1) TLS 2) Credenziali 3) Porta 4) Hostname")
    
    def on_cloud_message(self, client, userdata, msg):
        """Messaggio ricevuto dal CLOUD → invia al LOCALE"""
        if DEBUG_MSGS:
            payload_preview = msg.payload.decode()[:50] + "..." if len(msg.payload) > 50 else msg.payload.decode()
            logger.debug(f"📨 CLOUD: {msg.topic} = {payload_preview}")
        
        # Controlla se deve essere inoltrato
        forward = False
        for pattern in CLOUD_TO_LOCAL:
            if mqtt.topic_matches_sub(pattern, msg.topic):
                forward = True
                break
        
        if not forward:
            return
        
        try:
            # Invia al LOCALE (SENZA RETAIN per comandi)
            result = self.local.publish(
                topic=msg.topic,
                payload=msg.payload,
                qos=QOS,
                retain=False  # IMPORTANTE: comandi senza retain
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.message_count["cloud_to_local"] += 1
                logger.info(f"⬇️  Comando cloud→locale: {msg.topic}")
            else:
                self.message_count["errors"] += 1
                logger.warning(f"⚠️  Errore pubblicazione locale: {result.rc}")
                
        except Exception as e:
            self.message_count["errors"] += 1
            logger.error(f"❌ Eccezione cloud→local: {e}")
    
    def on_cloud_disconnect(self, client, userdata, rc):
        if rc != 0:
            logger.warning(f"🔌 Disconnesso da CLOUD: {rc}")
    
    # ============ GESTIONE BRIDGE ============
    def print_stats(self):
        """Stampa statistiche"""
        logger.info("\n" + "="*50)
        logger.info("📊 STATISTICHE BRIDGE:")
        logger.info(f"  Locale → Cloud: {self.message_count['local_to_cloud']}")
        logger.info(f"  Cloud → Locale: {self.message_count['cloud_to_local']}")
        logger.info(f"  Errori: {self.message_count['errors']}")
        logger.info(f"  Config: {CONFIG_PATH}")
        logger.info("="*50)
    
    def run(self):
        """Avvia il bridge"""
        logger.info("🚀 Avvio MQTT Bridge")
        logger.info(f"📍 Locale: {LOCAL_HOST}:{LOCAL_PORT}")
        logger.info(f"☁️  Cloud: {CLOUD_HOST}:{CLOUD_PORT}")
        logger.info(f"⬆️  Local→Cloud: {len(LOCAL_TO_CLOUD)} topic")
        logger.info(f"⬇️  Cloud→Local: {len(CLOUD_TO_LOCAL)} topic")
        
        attempt = 0
        
        while True:
            attempt += 1
            try:
                logger.info(f"\n🔌 Tentativo di connessione #{attempt}")
                
                # Connetti al CLOUD
                logger.info(f"Connessione a CLOUD ({CLOUD_HOST}:{CLOUD_PORT})...")
                self.cloud.connect(CLOUD_HOST, CLOUD_PORT, 60)
                self.cloud.loop_start()
                
                # Connetti al LOCALE
                logger.info(f"Connessione a LOCALE ({LOCAL_HOST}:{LOCAL_PORT})...")
                self.local.connect(LOCAL_HOST, LOCAL_PORT, 60)
                self.local.loop_start()
                
                logger.info("✅ Bridge attivo e bidirezionale")
                
                # Loop di mantenimento
                last_stats = time.time()
                while True:
                    time.sleep(1)
                    
                    # Log statistiche ogni 30 secondi
                    if time.time() - last_stats > 30:
                        self.print_stats()
                        last_stats = time.time()
                
            except KeyboardInterrupt:
                logger.info("\n⏹️  Arresto richiesto")
                break
                
            except Exception as e:
                logger.error(f"💥 Errore: {e}")
                logger.info(f"🔄 Riprovo in {RECONNECT_DELAY} secondi...")
                
                # Cleanup
                try:
                    self.local.loop_stop()
                    self.cloud.loop_stop()
                    self.local.disconnect()
                    self.cloud.disconnect()
                except:
                    pass
                
                time.sleep(RECONNECT_DELAY)
        
        # Shutdown pulito
        self.print_stats()
        logger.info("👋 Bridge terminato")

# ============ AVVIO ============
if __name__ == "__main__":
    try:
        bridge = MQTTBridge()
        bridge.run()
    except Exception as e:
        logger.error(f"❌ Errore fatale: {e}")
        sys.exit(1)