# Tru-Control

Questo progetto è stato ispirato dal lavoro di DamielFett e più precisamente da questo:

https://github.com/danielfett/inetbox.py

------------------------------------------------------------------------------------

**Disclaimer:**
This project is for educational and recreation purposes only.
All intellectual property, trademarks, and copyrights related to the Lin-BUS codes and protocols belong to Truma Gerätetechnik GmbH & Co. KG Putzbrunn. 
No part of this project is intended to infringe on Truma’s rights or facilitate unauthorized access, modification, or misuse of their proprietary systems. 
The information provided here is shared solely for learning and understanding vehicle communication protocols. Any use of this data is at the user's own risk and responsibility.


------------------------------------------------------------------------------------
Il desiderio di avere un'app (solo IOS per ora) che funzionasse in simbiosi con il lavoro di DanielFett mi ha ispirato al punto di aver creato l'interfaccia giusta per tutti gli utenti di Truma Combi™.

Ciò che a mio parere era necessario per rendere l'applicazione "inetbox.py" che gira su Raspberry PI davvero utilizzabile era un'app nativa che potesse consentire l'accesso sia locale che remoto alla gestione Truma.

Ho usato un Raspberry PI Zero 2W

![images/zero2-hero.webp](https://github.com/mk4001/Tru-Control/blob/main/images/zero2-hero.webp)

Grazie all'hardware impiegato, ho potuto sviluppare l'applicazione che potesse utilizzare tutte le potenzialità radio del Raspberry ossia: Wi-Fi e Bluetooth, dando così la possibilità all'utente di potersi collegare sia da remoto attraverso un broker MQTT in cloud, sia tramite Bluetooth Low Energy (BLE) direttamente sul proprio RV, Camper, VAN, senza bisogno di impiegare alcuna infrastruttura come un riuter di bordo o altro strumento per la connettività verso Internet.

Per quanto concerne l'installazione del Raspberry, dell'interfaccia LIN-UART e del ssoftware di base vi rimando al link originale di DanielFett:

https://github.com/danielfett/inetbox.py

Quando avrete terminato con successo l'installazione e i test di HW/SW del protocollo "inetbox.py" dovrete aggiungere i seguenti script Python che fungono da gateway sia verso i broker MQTT in cloud che verso l'interfaccia BLE del raspberry.

------------------------------------------------------------------------------------

<img width="50" alt="WiFi" src="https://github.com/mk4001/Tru-Control/blob/main/images/WiFi%20icon.jpg">

**mqtt_bridge_complete.py**  - Gateway MQTT verso il broker in cloud

Per consentire l'accesso remoto del broker MQTT mosquitto installato localmente sul Raspberry, occorre duplicare alcuni topic su un MQTT broker in cloud.

Io ne ho provati 2, gratuiti, che se non si fa un uso estremamente intensivo dell'app possono tranquillamente servire al nostro scopo, e sono:

https://www.emqx.com/en

https://www.hivemq.com


Una volta scelto il vostro MQTT broker in cloud e creato un cluster gratuito, riceverete le credenziali per l'accesso remoto: conservatele con cura, ci serviranno tra poco.

Cominciamo quindi ad installare lo script che funge da gateway tra il broker Mosquitto locale sul Raspberry e il broker MQTT in cloud che avete scelto.

Nella directory: "Python add ons", troverete lo script in questione; esso deve essere copiato nella directory "/usr/local/bin/mqtt_bridge_complete.py" del Raspberry come segue:

**sudo nano /usr/local/bin/mqtt_bridge_complete.py**

Occorre quindi aggiungere i permessi per l'esecuzione:

**sudo chmod +x /usr/local/bin/mqtt_bridge_complete.py**

Uno shell-script "mqtt-bridge.service.sh" consente di creare il servizio relativo allo sctipt: "mqtt_bridge_complete.py", una volta eseguito proseguiamo con la configurazione dei parametri di comunicazione con il broker in cloud.

Editiamo il file: "config.json" per completare le credenziali d'accesso ai broker in cloud, con il seguente comando:

**sudo nano /etc/mqtt_bridge/config.json**

nella directory "Python add ons" ci sono 2 file di configurazione d'esempio sia per HiveMQ che per EMQX. Sostituite le vostre credenziali **SENZA CAMBIARE NIENT'ALTRO.**

Quando avrete completato la congiurazione proseguimo quindi con:

**sudo systemctl daemon-reload**

**sudo systemctl enable --now mqtt-bridge**

**sudo systemctl status mqtt-bridge**

A qusto punto lo script "mqtt_bridge_complete.py", divenuto un servizio di sistema chiamato: "mqtt-bridge.service" dovrebbe essere up & running e lo potete verificare con il seguente comando:

**sudo journalctl -u mqtt-bridge -f**

------------------------------------------------------------------------------------

<img width="50" alt="BLE" src="https://github.com/mk4001/Tru-Control/blob/main/images/BLE%20icon.png">

**truma_ble_server.py** - Server BLE per funzionamento in locale senza alcuna infrastruttura (peer 2 peer)

Per consentire la connettività tra l'app IOS e il raspberry in modo diretto, senza l'ausilio di router o accessori vari di comunicazione verso internet, bisogna installare uno script python che troverete sempre in "truma_ble_server.py" e si chiama: "truma_ble_server.py".

Prima di procedere all'installazione dello script, occorre attivare il servizio bluetooth sul raspberry, come segue:

**sudo apt-get install -y bluetooth bluez python3-dbus python3-gi**

modificare quindi il relativo file: 

**sudo nano /etc/bluetooth/main.conf**

…

[General]

Name = Truma-BLE

Class = 0x000100

DiscoverableTimeout = 0

Discoverable = yes

AlwaysPairable = yes

…

**sudo reboot**

Quindi, come per lo script precedente copiamolo con il seguente comando, sul Raspberry:

**sudo nano /usr/local/bin/truma_ble_server.py**

Occorre quindi aggiungere i permessi per l'esecuzione:

**sudo chmod +x /usr/local/bin/truma_ble_server.py**

Uno shell-script "truma-ble.service.sh" consente di creare il servizio relativo allo sctipt: "truma_ble_server.py", una volta eseguito proseguiamo con i solti comandi:

**sudo systemctl daemon-reload**

**sudo systemctl enable --now truma_ble_server.service**

**sudo systemctl status truma_ble_server.service**

A qusto punto lo script "truma_ble_server.py", divenuto un servizio di sistema chiamato: "truma_ble_server.service" dovrebbe essere up & running e lo potete verificare con il seguente comando:

**sudo journalctl -u truma_ble_server.service -f**

