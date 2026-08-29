# Tru-Control — Installazione Hardware (gateway Truma ↔ Raspberry Pi)

> Guida riorganizzata a partire dalla documentazione hardware del progetto open source [danielfett/inetbox.py](https://github.com/danielfett/inetbox.py) (README + cartella `docs/`), che questo gateway usa come riferimento per il bus LIN della Truma Combi. Per lo schema fotografico originale e il pinout fisico dell'RJ12, vedi i file [`connections.png`](https://github.com/danielfett/inetbox.py/blob/master/docs/connections.png), [`pinout.jpg`](https://github.com/danielfett/inetbox.py/blob/master/docs/pinout.jpg) e [`cpplus.jpg`](https://github.com/danielfett/inetbox.py/blob/master/docs/cpplus.jpg) nel repository originale.

## Cosa realizza questa installazione

Tru-Control non parla mai direttamente con la caldaia: si affida a un **gateway self-hosted** (un Raspberry Pi) che si inserisce fisicamente sul bus LIN tra la Truma Combi e il pannello di controllo CP Plus, traduce quel traffico in MQTT/BLE, ed è quel gateway a cui l'app poi si connette. Questa guida copre solo il lato elettrico di quel gateway — non il software del gateway stesso, né l'app.

## Requisiti hardware

| Componente | Note |
|---|---|
| Truma Combi (4/6 o E) | Testato dall'autore originale su Combi 4; Combi 6/E dovrebbero funzionare con lo stesso bus |
| Pannello CP Plus | Deve essere marcato **"inet ready"** — i pannelli CP Plus più vecchi non espongono il bus necessario |
| Raspberry Pi | Qualsiasi modello recente con GPIO e UART disponibile |
| Modulo transceiver LIN→UART | Adatta i livelli elettrici del bus LIN della Truma ai pin seriali 3.3V del Raspberry Pi |
| Cavo RJ12 (6P6C, 6 pin) | Cavo standard per telefonia, usato dal bus Truma |
| Splitter RJ12 (opzionale) | Solo se si vuole derivare il segnale senza scollegare il cavo esistente tra Combi e CP Plus |
| Alimentazione 12V | Condivisa con quella che già alimenta Combi e CP Plus |

## Cablaggio: transceiver ↔ Raspberry Pi

| Pin sul transceiver | Collegato a |
|---|---|
| 12V | Alimentazione 12V esterna (la stessa di Combi/CP Plus) |
| TX | GPIO 15 del Raspberry Pi (RX del Pi) |
| RX | GPIO 14 del Raspberry Pi (TX del Pi) |
| GND (secondo pin GND) | Un pin di massa del Raspberry Pi |
| INH, SLP | Non collegati |

**Punto facile da sbagliare**: TX del transceiver va su RX del Pi e viceversa — è un collegamento incrociato (come su qualunque bus seriale), non 1:1.

## Cablaggio: transceiver ↔ bus Truma (RJ12)

| Pin sul transceiver | Pin sul connettore RJ12 |
|---|---|
| LIN | Pin 3 |
| GND | Pin 5 |

Il connettore RJ12 si collega a **una qualsiasi porta libera sulla Truma Combi**, oppure — se non ce n'è una libera — si inserisce con uno splitter direttamente nel cavo già esistente tra Combi e pannello CP Plus, senza doverlo tagliare o modificare.

## Preparazione software sul Raspberry Pi (prerequisiti, prima del gateway vero e proprio)

1. Abilitare l'UART hardware sul Raspberry Pi (disabilitando la console seriale di default) — la procedura varia leggermente per modello/versione di Raspberry Pi OS, seguire la guida ufficiale per il proprio modello.
2. Dare all'utente che eseguirà il gateway l'accesso alla porta seriale:
   ```bash
   sudo adduser pi dialout
   ```
3. Disconnettersi e riconnettersi (o riavviare) perché il permesso venga applicato.

## Note di sicurezza

- L'alimentazione 12V del transceiver deve essere la **stessa massa/riferimento** di quella di Combi e CP Plus — massa flottante o alimentazioni separate non referenziate possono dare letture del bus instabili o danneggiare il transceiver.
- Verificare che il pannello sia davvero "inet ready" **prima** di aprire qualsiasi connettore: su un pannello non compatibile il bus esposto potrebbe non essere lo stesso, con rischio di cortocircuiti tra pin non previsti per quell'uso.
- Come per qualsiasi intervento sull'impianto elettrico del camper/RV: scollegare l'alimentazione della Truma prima di inserire o rimuovere connettori RJ12.

## Compatibilità nota

- Testato dall'autore originale su **Truma Combi 4**; Combi 6 ed E dovrebbero condividere lo stesso protocollo di bus ma non sono stati verificati direttamente da lui.
- Il pannello CP Plus deve esporre la funzione **"inet ready"** — è il prerequisito che rende disponibile fisicamente il bus LIN usato da questa guida.
