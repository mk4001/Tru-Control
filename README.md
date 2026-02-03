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

**mqtt_bridge_complete.py**  - Gateway MQTT verso broker in cloud

Questo script deve essere copiato nella directory "/usr/local/bin/mqtt_bridge_complete.py", quindi accorre aggiungere i permessi per l'esecuzione:

**sudo chmod +x /usr/local/bin/mqtt_bridge_complete.py**

Un shell script "mqtt-bridge.service.sh" consente di creare il servizio relativo allo sctipt: "mqtt_bridge_complete.py", una volta eseguito proseguiamo con:

occorre ora configurare il file: "config.json" per completare le credenziali d'accesso ai broker in cloud, con il seguente comando:

**sudo nano /etc/mqtt_bridge/config.json**

nella directory "Python add ons" ci sono 2 file di configurazione d'esempio sia per HiveMQ che per EMQX.

**
sudo systemctl daemon-reload
sudo systemctl enable --now mqtt-bridge
sudo systemctl status mqtt-bridge

sudo journalctl -u mqtt-bridge -f
**
