# Tru-Control 

<img width="150" alt="Apple Store" src="https://github.com/mk4001/Tru-Control/blob/main/images/New-1024.png">
Available on Apple Store 



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

<img width="350" alt="Raspberry PI Zero 2W" src="https://github.com/mk4001/Tru-Control/blob/main/images/zero2-hero.webp">

Collegato alla Truma Combi™ mediante un'interfaccia UART-LIN "FST T151".

<img width="350" alt="FST T151" src="https://github.com/mk4001/Tru-Control/blob/main/images/FST%20T151.jpg">

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

------------------------------------------------------------------------------------
<img width="50" alt="Apple Store" src="https://github.com/mk4001/Tru-Control/blob/main/images/New-1024.png">

**Configurazione app [Tru-Control]**

Una volta scaricata l'app [Tru-Control] dall'App-Store di Apple (per iPhone e iPad) occorre solamente completare la configurazione che riguarda il broker in cloud.

Nella Sezione [Settings] fornite le credenziali del vostro MQTT broker in cloud salvate e provate.

Qualche delucidazione in merito all'app è d'obbligo: 
- TruControl consente di operare sia in 3G/4G/5G/WiFi che in BLE.
- Entrambe le modalità consentono la ricezione dei valori di status della Truma Combi™ in modo istantaneo.
- Per operare qualsiasi comando è necessario che l'app sia in collegamento con il Raspberri o in modalità "Internet" o in modalità "BLE".
- Se la connessione via BLE è scarsa (troppo lontano dal Raspberry) sarà possibile ricevere i dati ma non sarà consentito operare alcun comando per questioni di sicurezza.
- Per cominciare qualsiasi operazione sulla Truma Combi™ occorre per prima cosa scegliere la modalità di energia nella sezione [Power MIX], poi si potrà proseguire con i comandi in [Hot Water] o in [Inside Temp]
- Per la natura della connettività LIN-BUS con la Truma Combi™ i comandi impartiti dall'APP non vengono subito eseguiti e le conseguenti risposte dalla Truma Combi™ verranno visualizzate un un ritardo di ca 5 sec.
- Eventuali errori che si verificano sulla Truma Combi™ verranno mostrati sul display dell'APP. Cliccando sul messaggio d'errore si potrà leggerne la descrizione completa.
- Nella sezione [Settings] c'è [View Debug Log] che consente di visualizzare i log di connessione sia per BLE che per Internet (MQTT).
- L'app fornisce un utile livello di carica della batteria del leisure, tarata su una scala per batterie AGM, mostra: tensione, percentuale di carica, cambiando colore e status a seconda della fascia di carica raggiunta.
- L'app lavora in background per favorire una migliore experience all'utente. Questa funzionalità non compromette lo stato della batteria dell'iPhone in maniera significativa specialmente se utilizzata in locale (BLE) il consumo è praticamente impercettibile.


Spero possiate trascorrere delle piacevoli viaggi felici a bordo dei vostri mezzi grazie al fatto che ora potrete controllare la vostra Truma Combi™ direttamente dal vostro iPhone ma soprattutto da ogni luogo vi troviate.
