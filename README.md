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

Grazie all'hardware impiegato, ho potuto sviluppare l'applicazione che potesse utilizzare tutte le potenzialità radio del Raspberry ossia: Wi-Fi e Bluetooth, dando così la possibilità all'utente di potersi collegare sia da remoto attraverso un broker MQTT in cloud, sia tramite Bluetooth Low Energy (BlE) direttamente sul proprio RV senza bisogno di impiegare alcuna infrastruttura come un riuter di bordo o altro strumento per la collettività verso Internet.

