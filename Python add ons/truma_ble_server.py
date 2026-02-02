#!/usr/bin/env python3
"""
Truma BLE Server for Raspberry Pi Zero 2W - VERSIONE COMPLETA CON 16 CHARACTERISTICS
"""

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib
import paho.mqtt.client as mqtt
import time
import logging
from typing import Dict, Optional

# Configure logging DETTAGLIATO
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# BLE UUIDs - DEVONO ESSERE UGUALI A iOS APP
TRUMA_SERVICE_UUID = '12345678-1234-5678-1234-56789ABCDEF0'

# Characteristic UUIDs - 11 READ characteristics + 5 WRITE characteristics
CHAR_CURRENT_TEMP_ROOM = '12345678-1234-5678-1234-56789ABCDEF1'
CHAR_CURRENT_TEMP_WATER = '12345678-1234-5678-1234-56789ABCDEF2'
CHAR_HEATING_MODE = '12345678-1234-5678-1234-56789ABCDEF3'
CHAR_POWER_LEVEL = '12345678-1234-5678-1234-56789ABCDEF4'
CHAR_VOLTAGE = '12345678-1234-5678-1234-56789ABCDEF5'
CHAR_ERROR_CODE = '12345678-1234-5678-1234-56789ABCDEF6'
CHAR_TRUMA_ONLINE = '12345678-1234-5678-1234-56789ABCDEF7'
# NUOVE CHARACTERISTICS PER I DATI CHE MANCANO
CHAR_OPERATING_STATUS = '12345678-1234-5678-1234-56789ABCDEF8'  # cp_plus_display_status
CHAR_TARGET_TEMP_ROOM = '12345678-1234-5678-1234-56789ABCDEF9'  # target_temp_room
CHAR_TARGET_TEMP_WATER = '12345678-1234-5678-1234-56789ABCDEFA'  # target_temp_water
CHAR_ENERGY_MIX = '12345678-1234-5678-1234-56789ABCDEFB'  # energy_mix
CHAR_CLOCK = '12345678-1234-5678-1234-56789ABCDEFC'  # clock

# Write Characteristics (comandi)
CHAR_SET_TARGET_TEMP_ROOM = '12345678-1234-5678-1234-56789ABCDEFD'
CHAR_SET_TARGET_TEMP_WATER = '12345678-1234-5678-1234-56789ABCDEFE'
CHAR_SET_ENERGY_MIX = '12345678-1234-5678-1234-56789ABCDEFF'
CHAR_SET_HEATING_MODE = '12345678-1234-5678-1234-56789ABCDF00'
CHAR_SET_EL_POWER_LEVEL = '12345678-1234-5678-1234-56789ABCDF01'

# MQTT Configuration
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC_PREFIX = 'service/truma'

# D-Bus interfaces
BLUEZ_SERVICE_NAME = 'org.bluez'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
LE_ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'
GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE = 'org.bluez.GattCharacteristic1'
GATT_DESC_IFACE = 'org.bluez.GattDescriptor1'

# Advertisement per rendere il dispositivo scopribile
class TrumaAdvertisement(dbus.service.Object):
    PATH_BASE = '/org/bluez/truma/advertisement'

    def __init__(self, bus, index):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.ad_type = 'peripheral'
        self.service_uuids = [TRUMA_SERVICE_UUID]
        self.local_name = 'Truma-BLE'
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            LE_ADVERTISEMENT_IFACE: {
                'Type': self.ad_type,
                'ServiceUUIDs': dbus.Array(self.service_uuids, signature='s'),
                'LocalName': dbus.String(self.local_name),
                'Includes': dbus.Array(['tx-power'], signature='s'),
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != LE_ADVERTISEMENT_IFACE:
            raise dbus.exceptions.DBusException(
                'org.bluez.Error.InvalidArguments',
                'Unknown interface')
        return self.get_properties()[LE_ADVERTISEMENT_IFACE]

    @dbus.service.method(LE_ADVERTISEMENT_IFACE, in_signature='', out_signature='')
    def Release(self):
        logger.info('Advertisement released')


class Application(dbus.service.Object):
    def __init__(self, bus):
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
                descs = chrc.get_descriptors()
                for desc in descs:
                    response[desc.get_path()] = desc.get_properties()
        return response


class Service(dbus.service.Object):
    PATH_BASE = '/org/bluez/truma/service'

    def __init__(self, bus, index, uuid, primary):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []  # <-- RIMANE LISTA!
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            GATT_SERVICE_IFACE: {
                'UUID': self.uuid,
                'Primary': self.primary,
                'Characteristics': dbus.Array(
                    self.get_characteristic_paths(),
                    signature='o')
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_characteristic(self, characteristic):
        self.characteristics.append(characteristic)

    def get_characteristic_paths(self):
        result = []
        for chrc in self.characteristics:
            result.append(chrc.get_path())
        return result

    def get_characteristics(self):
        return self.characteristics

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_SERVICE_IFACE:
            raise dbus.exceptions.DBusException(
                'org.bluez.Error.InvalidArguments',
                'Unknown interface')
        return self.get_properties()[GATT_SERVICE_IFACE]


class Characteristic(dbus.service.Object):
    def __init__(self, bus, index, uuid, flags, service, value=None):
        self.path = service.path + '/char' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.descriptors = []
        self.value = value or []
        self.notifying = False
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            GATT_CHRC_IFACE: {
                'Service': self.service.get_path(),
                'UUID': self.uuid,
                'Flags': self.flags,
                'Descriptors': dbus.Array(
                    self.get_descriptor_paths(),
                    signature='o'),
                'Notifying': dbus.Boolean(self.notifying)
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_descriptor(self, descriptor):
        self.descriptors.append(descriptor)

    def get_descriptor_paths(self):
        result = []
        for desc in self.descriptors:
            result.append(desc.get_path())
        return result

    def get_descriptors(self):
        return self.descriptors

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_CHRC_IFACE:
            raise dbus.exceptions.DBusException(
                'org.bluez.Error.InvalidArguments',
                'Unknown interface')
        return self.get_properties()[GATT_CHRC_IFACE]

    @dbus.service.method(GATT_CHRC_IFACE,
                         in_signature='a{sv}',
                         out_signature='ay')
    def ReadValue(self, options):
        value_str = ''.join([chr(b) for b in self.value]) if self.value else ""
        logger.debug(f'📖 ReadValue on {self.uuid}: "{value_str}"')
        return self.value

    @dbus.service.method(GATT_CHRC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        value_str = ''.join([chr(b) for b in value]) if value else ""
        logger.info(f'✏️ WriteValue on {self.uuid}: "{value_str}"')
        self.value = value
        self.PropertiesChanged(GATT_CHRC_IFACE, {'Value': self.value}, [])
        return value

    @dbus.service.method(GATT_CHRC_IFACE)
    def StartNotify(self):
        logger.info(f'🔔 StartNotify on {self.uuid}')
        if not self.notifying:
            self.notifying = True
            self.PropertiesChanged(GATT_CHRC_IFACE, {'Notifying': True}, [])

    @dbus.service.method(GATT_CHRC_IFACE)
    def StopNotify(self):
        logger.info(f'🔕 StopNotify on {self.uuid}')
        if self.notifying:
            self.notifying = False
            self.PropertiesChanged(GATT_CHRC_IFACE, {'Notifying': False}, [])

    @dbus.service.signal(DBUS_PROP_IFACE,
                        signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass

    def update_value(self, new_value: str):
        """Update characteristic value and send notification with LOGGING"""
        if isinstance(new_value, str):
            self.value = [dbus.Byte(c) for c in new_value.encode()]
        elif isinstance(new_value, (int, float)):
            self.value = [dbus.Byte(c) for c in str(new_value).encode()]
        else:
            self.value = [dbus.Byte(0)]
            logger.warning(f"⚠️ Invalid value type for {self.uuid}: {type(new_value)}")

        value_str = new_value if isinstance(new_value, str) else str(new_value)
        logger.info(f"📤 BLE SENDING - UUID: {self.uuid}, Value: {value_str}")

        # Send notification if clients are subscribed
        if self.notifying:
            logger.debug(f"🔔 Sending notification for {self.uuid}")
            self.PropertiesChanged(GATT_CHRC_IFACE, {'Value': self.value}, [])
        else:
            logger.debug(f"⏸️  Client not subscribed to {self.uuid}, skipping notification")


class ControlCharacteristic(Characteristic):
    """Write characteristic that publishes to MQTT"""
    def __init__(self, bus, index, uuid, service, mqtt_bridge, mqtt_topic):
        Characteristic.__init__(
            self, bus, index, uuid,
            ['write', 'write-without-response'],
            service
        )
        self.mqtt_bridge = mqtt_bridge
        self.mqtt_topic = mqtt_topic

    def WriteValue(self, value, options):
        # Call parent to update value
        super().WriteValue(value, options)

        # Convert byte array to string
        try:
            command = ''.join([chr(b) for b in value])
            logger.info(f"📤 BLE → MQTT: {command} → {self.mqtt_topic}")

            # Publish to MQTT
            if self.mqtt_bridge:
                self.mqtt_bridge.publish(self.mqtt_topic, command)
            else:
                logger.error(f"❌ MQTT bridge not available for {self.uuid}")

        except Exception as e:
            logger.error(f"❌ Error processing BLE command: {e}")
            import traceback
            logger.error(traceback.format_exc())


class TrumaGattService(Service):
    def __init__(self, bus, index):
        Service.__init__(self, bus, index, TRUMA_SERVICE_UUID, True)

        # Inizializza prima il MQTT bridge
        self.mqtt_bridge = None
        
        # Dizionario per mappare UUID → Characteristic (per aggiornamenti rapidi)
        self.characteristics_dict = {}

        # Valori predefiniti per TUTTE le 11 caratteristiche di lettura
        default_values = {
            CHAR_CURRENT_TEMP_ROOM: "20.0",
            CHAR_CURRENT_TEMP_WATER: "40.0",
            CHAR_HEATING_MODE: "off",
            CHAR_POWER_LEVEL: "0",
            CHAR_VOLTAGE: "12.5",
            CHAR_ERROR_CODE: "0",
            CHAR_TRUMA_ONLINE: "1",
            CHAR_OPERATING_STATUS: "standby",
            CHAR_TARGET_TEMP_ROOM: "20.0",
            CHAR_TARGET_TEMP_WATER: "40.0",
            CHAR_ENERGY_MIX: "gas",
            CHAR_CLOCK: "00:00",
        }

        # Creazione di TUTTE le 11 caratteristiche di lettura
        characteristics_config = [
            (0, CHAR_CURRENT_TEMP_ROOM, "Room Temperature"),
            (1, CHAR_CURRENT_TEMP_WATER, "Water Temperature"),
            (2, CHAR_HEATING_MODE, "Heating Mode"),
            (3, CHAR_POWER_LEVEL, "Power Level"),
            (4, CHAR_VOLTAGE, "Voltage"),
            (5, CHAR_ERROR_CODE, "Error Code"),
            (6, CHAR_TRUMA_ONLINE, "Truma Online"),
            (7, CHAR_OPERATING_STATUS, "Operating Status"),
            (8, CHAR_TARGET_TEMP_ROOM, "Target Room Temp"),
            (9, CHAR_TARGET_TEMP_WATER, "Target Water Temp"),
            (10, CHAR_ENERGY_MIX, "Energy Mix"),
            (11, CHAR_CLOCK, "Clock"),
        ]
        
        for index, uuid, desc in characteristics_config:
            chrc = Characteristic(
                bus, index, uuid,
                ['read', 'notify'], self,
                [dbus.Byte(c) for c in default_values[uuid].encode()]
            )
            # Aggiungi alla lista della classe base
            self.add_characteristic(chrc)
            # Aggiungi al dizionario per accesso rapido
            self.characteristics_dict[uuid] = chrc
            logger.info(f"✅ Created BLE characteristic: {desc} ({uuid})")

        logger.info(f"✅ Truma GATT Service created with {len(self.characteristics)} read characteristics")

    def setup_write_characteristics(self, mqtt_bridge):
        """Setup write characteristics after MQTT bridge is created"""
        self.mqtt_bridge = mqtt_bridge

        logger.info("🔧 Setting up write characteristics...")

        # Caratteristiche di scrittura (controllo)
        write_characteristics = [
            (12, CHAR_SET_TARGET_TEMP_ROOM, f'{MQTT_TOPIC_PREFIX}/set/target_temp_room'),
            (13, CHAR_SET_TARGET_TEMP_WATER, f'{MQTT_TOPIC_PREFIX}/set/target_temp_water'),
            (14, CHAR_SET_ENERGY_MIX, f'{MQTT_TOPIC_PREFIX}/set/energy_mix'),
            (15, CHAR_SET_HEATING_MODE, f'{MQTT_TOPIC_PREFIX}/set/heating_mode'),
            (16, CHAR_SET_EL_POWER_LEVEL, f'{MQTT_TOPIC_PREFIX}/set/el_power_level'),
        ]
        
        for index, uuid, topic in write_characteristics:
            chrc = ControlCharacteristic(
                bus=self.bus, index=index, uuid=uuid,
                service=self, mqtt_bridge=mqtt_bridge,
                mqtt_topic=topic
            )
            # Aggiungi alla lista della classe base
            self.add_characteristic(chrc)
            # Aggiungi al dizionario per accesso rapido
            self.characteristics_dict[uuid] = chrc
            logger.info(f"✅ Created write characteristic: {uuid} → {topic}")

        logger.info(f"✅ Total {len(write_characteristics)} write characteristics added")

    def update_characteristic(self, uuid: str, value: str):
        """Update specific characteristic by UUID with LOGGING"""
        if uuid in self.characteristics_dict:
            logger.info(f"🔄 Updating BLE characteristic {uuid} → {value}")
            self.characteristics_dict[uuid].update_value(value)
        else:
            logger.warning(f"⚠️ Unknown BLE UUID for update: {uuid}")


class MQTTBridge:
    def __init__(self, gatt_service: TrumaGattService):
        self.gatt_service = gatt_service
        self.mqtt_client = mqtt.Client(client_id="truma_ble_bridge", protocol=mqtt.MQTTv311)

        # MQTT callbacks
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_message = self._on_message
        self.mqtt_client.on_disconnect = self._on_disconnect

        # Connect to MQTT broker
        self.connect_to_mqtt()

        # Setup write characteristics after bridge is created
        gatt_service.setup_write_characteristics(self)

        logger.info("✅ MQTT Bridge initialized")

    def connect_to_mqtt(self):
        try:
            logger.info(f"🔗 Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.mqtt_client.loop_start()
            logger.info(f"✅ Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to MQTT: {e}")
            # Try to reconnect after 5 seconds
            time.sleep(5)
            self.connect_to_mqtt()

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("✅ MQTT connected successfully")
            # Subscribe to ALL Truma topics
            topics = [
                # Tutti i topic esatti
                ("service/truma/online", 1),
                ("service/truma/display_status/current_temp_room", 1),
                ("service/truma/display_status/current_temp_water", 1),
                ("service/truma/control_status/heating_mode", 1),
                ("service/truma/control_status/el_power_level", 1),
                ("service/truma/display_status/voltage", 1),
                ("service/truma/control_status/clock", 1),
                ("service/truma/display_status/cp_plus_display_status", 1),
                ("service/truma/control_status/target_temp_room", 1),
                ("service/truma/control_status/target_temp_water", 1),
                ("service/truma/control_status/energy_mix", 1),
                ("service/truma/control_status/error_code", 1),
            ]
            client.subscribe(topics)
            logger.info(f"📡 Subscribed to {len(topics)} Truma topics")
        else:
            logger.error(f"❌ MQTT connection failed with code: {rc}")

    def _on_disconnect(self, client, userdata, rc):
        logger.warning(f"⚠️ MQTT disconnected: {rc}")
        if rc != 0:
            logger.info("🔄 Attempting to reconnect in 5 seconds...")
            time.sleep(5)
            self.connect_to_mqtt()

    def _on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode('utf-8')

        logger.info(f"📥 MQTT RECEIVED - Topic: {topic}, Payload: {payload}")

        # Mappatura COMPLETA topic MQTT -> UUID BLE
        topic_to_uuid = {
            # Online Status
            'service/truma/online': CHAR_TRUMA_ONLINE,
            
            # Display Status
            'service/truma/display_status/current_temp_room': CHAR_CURRENT_TEMP_ROOM,
            'service/truma/display_status/current_temp_water': CHAR_CURRENT_TEMP_WATER,
            'service/truma/display_status/voltage': CHAR_VOLTAGE,
            'service/truma/display_status/cp_plus_display_status': CHAR_OPERATING_STATUS,
            
            # Control Status
            'service/truma/control_status/heating_mode': CHAR_HEATING_MODE,
            'service/truma/control_status/el_power_level': CHAR_POWER_LEVEL,
            'service/truma/control_status/error_code': CHAR_ERROR_CODE,
            'service/truma/control_status/target_temp_room': CHAR_TARGET_TEMP_ROOM,
            'service/truma/control_status/target_temp_water': CHAR_TARGET_TEMP_WATER,
            'service/truma/control_status/energy_mix': CHAR_ENERGY_MIX,
            'service/truma/control_status/clock': CHAR_CLOCK,
        }

        # Cerca corrispondenza esatta
        if topic in topic_to_uuid:
            ble_uuid = topic_to_uuid[topic]
            if ble_uuid:
                logger.info(f"🔄 Mapping MQTT → BLE: {topic} → {ble_uuid}")
                self.gatt_service.update_characteristic(ble_uuid, payload)
            else:
                logger.info(f"ℹ️ Topic {topic} received (no BLE mapping): {payload}")
        else:
            logger.warning(f"⚠️ Unexpected topic (not in mapping): {topic}")

    def publish(self, topic: str, message: str):
        try:
            logger.info(f"📤 MQTT PUBLISH - Topic: {topic}, Message: {message}")
            result = self.mqtt_client.publish(topic, message, qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"✅ MQTT published successfully")
            else:
                logger.error(f"❌ MQTT publish failed with code: {result.rc}")
        except Exception as e:
            logger.error(f"❌ MQTT publish exception: {e}")
            import traceback
            logger.error(traceback.format_exc())


def find_adapter(bus):
    """Find Bluetooth adapter"""
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                                DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if GATT_MANAGER_IFACE in props.keys():
            return o

    return None


def find_advertisement_manager(bus):
    """Find LE Advertising Manager"""
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                                DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if LE_ADVERTISING_MANAGER_IFACE in props.keys():
            return o

    return None


def main():
    logger.info("🚀 Starting Truma BLE GATT Server with 16 characteristics...")
    logger.info("📊 SERVICE: 12345678-1234-5678-1234-56789ABCDEF0")
    logger.info("")
    logger.info("📊 READ CHARACTERISTICS (11 total):")
    logger.info(f"  1. {CHAR_CURRENT_TEMP_ROOM} - Inside Temperature")
    logger.info(f"  2. {CHAR_CURRENT_TEMP_WATER} - Water Temperature")
    logger.info(f"  3. {CHAR_HEATING_MODE} - Heating Mode")
    logger.info(f"  4. {CHAR_POWER_LEVEL} - Power Level")
    logger.info(f"  5. {CHAR_VOLTAGE} - Voltage")
    logger.info(f"  6. {CHAR_ERROR_CODE} - Error Code")
    logger.info(f"  7. {CHAR_TRUMA_ONLINE} - Truma Online")
    logger.info(f"  8. {CHAR_OPERATING_STATUS} - Operating Status")
    logger.info(f"  9. {CHAR_TARGET_TEMP_ROOM} - Target Room Temp")
    logger.info(f"  10. {CHAR_TARGET_TEMP_WATER} - Target Water Temp")
    logger.info(f"  11. {CHAR_ENERGY_MIX} - Energy Mix")
    logger.info(f"  12. {CHAR_CLOCK} - Clock")
    logger.info("")
    logger.info("📊 WRITE CHARACTERISTICS (5 total):")
    logger.info(f"  13. {CHAR_SET_TARGET_TEMP_ROOM} - Set Target Room Temp")
    logger.info(f"  14. {CHAR_SET_TARGET_TEMP_WATER} - Set Target Water Temp")
    logger.info(f"  15. {CHAR_SET_ENERGY_MIX} - Set Energy Mix")
    logger.info(f"  16. {CHAR_SET_HEATING_MODE} - Set Heating Mode")
    logger.info(f"  17. {CHAR_SET_EL_POWER_LEVEL} - Set Power Level")
    logger.info("")

    # Setup D-Bus
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()

    # Get adapter
    adapter = find_adapter(bus)
    if not adapter:
        logger.error('❌ Bluetooth adapter not found')
        return

    # Get advertising manager
    ad_manager = find_advertisement_manager(bus)
    if not ad_manager:
        logger.error('❌ LE Advertising Manager not found')
        return

    logger.info(f'✅ Found adapter: {adapter}')
    logger.info(f'✅ Found advertising manager: {ad_manager}')

    # Create application
    app = Application(bus)

    # Create Truma GATT service
    logger.info("🔧 Creating Truma GATT Service...")
    service = TrumaGattService(bus, 0)
    app.add_service(service)

    # Create MQTT bridge
    logger.info("🔧 Creating MQTT Bridge...")
    mqtt_bridge = MQTTBridge(service)

    # Create advertisement
    advertisement = TrumaAdvertisement(bus, 0)

    # Register services
    try:
        # Register GATT application
        service_manager = dbus.Interface(
            bus.get_object(BLUEZ_SERVICE_NAME, adapter),
            GATT_MANAGER_IFACE
        )
        service_manager.RegisterApplication(
            app.get_path(), {},
            reply_handler=lambda: logger.info('✅ GATT application registered'),
            error_handler=lambda e: logger.error(f'❌ GATT registration failed: {e}')
        )

        # Register advertisement
        ad_manager_iface = dbus.Interface(
            bus.get_object(BLUEZ_SERVICE_NAME, ad_manager),
            LE_ADVERTISING_MANAGER_IFACE
        )
        ad_manager_iface.RegisterAdvertisement(
            advertisement.get_path(), {},
            reply_handler=lambda: logger.info('✅ Advertisement registered'),
            error_handler=lambda e: logger.error(f'❌ Advertisement registration failed: {e}')
        )

    except Exception as e:
        logger.error(f'❌ Failed to register services: {e}')
        import traceback
        logger.error(traceback.format_exc())
        return

    # Set Bluetooth adapter properties
    try:
        adapter_props = dbus.Interface(
            bus.get_object(BLUEZ_SERVICE_NAME, adapter),
            DBUS_PROP_IFACE
        )
        adapter_props.Set('org.bluez.Adapter1', 'Powered', dbus.Boolean(1))
        adapter_props.Set('org.bluez.Adapter1', 'Discoverable', dbus.Boolean(1))
        adapter_props.Set('org.bluez.Adapter1', 'DiscoverableTimeout', dbus.UInt32(0))
        adapter_props.Set('org.bluez.Adapter1', 'Pairable', dbus.Boolean(1))
        adapter_props.Set('org.bluez.Adapter1', 'PairableTimeout', dbus.UInt32(0))
        logger.info('✅ Bluetooth adapter configured (Powered, Discoverable, Pairable)')
    except Exception as e:
        logger.error(f'❌ Failed to configure adapter: {e}')

    logger.info('')
    logger.info('🟢 Truma BLE Server running...')
    logger.info('📱 Device name: Truma-BLE')
    logger.info('🔵 Service UUID: ' + TRUMA_SERVICE_UUID)
    logger.info('📡 Subscribed to 12 MQTT topics')
    logger.info('🔄 Bridging MQTT ↔ BLE')
    logger.info('')
    logger.info('📊 COMPLETE MQTT to BLE MAPPING:')
    logger.info(f'  - {CHAR_CURRENT_TEMP_ROOM}: service/truma/display_status/current_temp_room')
    logger.info(f'  - {CHAR_CURRENT_TEMP_WATER}: service/truma/display_status/current_temp_water')
    logger.info(f'  - {CHAR_HEATING_MODE}: service/truma/control_status/heating_mode')
    logger.info(f'  - {CHAR_POWER_LEVEL}: service/truma/control_status/el_power_level')
    logger.info(f'  - {CHAR_VOLTAGE}: service/truma/display_status/voltage')
    logger.info(f'  - {CHAR_ERROR_CODE}: service/truma/control_status/error_code')
    logger.info(f'  - {CHAR_TRUMA_ONLINE}: service/truma/online')
    logger.info(f'  - {CHAR_OPERATING_STATUS}: service/truma/display_status/cp_plus_display_status')
    logger.info(f'  - {CHAR_TARGET_TEMP_ROOM}: service/truma/control_status/target_temp_room')
    logger.info(f'  - {CHAR_TARGET_TEMP_WATER}: service/truma/control_status/target_temp_water')
    logger.info(f'  - {CHAR_ENERGY_MIX}: service/truma/control_status/energy_mix')
    logger.info(f'  - {CHAR_CLOCK}: service/truma/control_status/clock')
    logger.info('')

    # Run main loop
    mainloop = GLib.MainLoop()
    try:
        mainloop.run()
    except KeyboardInterrupt:
        logger.info('⏹️  Server stopped by user')
    finally:
        # Cleanup
        try:
            service_manager.UnregisterApplication(app.get_path())
            ad_manager_iface.UnregisterAdvertisement(advertisement.get_path())
            logger.info('🛑 Services unregistered')
        except:
            pass
        logger.info('🛑 Server shutdown complete')


if __name__ == '__main__':
    main()