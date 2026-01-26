# fldi-smart-factory_lukas
Abschlussprojekt_5AAME

## ________________

    In diesem 8-stufigen Projekt entwickeln die Schüler eine vernetzte Smart-Factory-Zelle als CPS. Das System wird technisch umgesetzt, digital modelliert und über GitHub versioniert weiterentwickelt.

    Das Projekt bildet bewusst eine realitätsnahe, dynamsiche Entwicklungsumgebung ab, in der sich Anforderungen, Lösungswege und Entscheidungen im Projektverlauf verändern können.

### _______________

## Mosquitto Integration Branch

Dieser Branch enthält die Anpassungen für die Integration der **Mosquitto MQTT Broker** Konfiguration in die Docker-Compose Umgebung.

### Änderungen in diesem Branch:

- **docker-compose.yml** aktualisiert: Mosquitto Container nutzt jetzt die `mosquitto.conf` Datei direkt aus dem Host-System
- Die Konfiguration wird als Volume in den Container gemountet: `./mosquitto.conf:/mosquitto/config/mosquitto.conf`
- Entfernte Datenvolumes für Persistierung (mosquitto.data und mosquitto.log)

### Mosquitto MQTT Broker

Der Mosquitto Service läuft im Docker Container mit folgenden Konfigurationen:

- **Port 1883**: MQTT Protokoll für IoT-Geräte und Sensoren
- **Port 9001**: WebSocket Protokoll für Web-basierte Clients
- **Image**: eclipse-mosquitto:2
- **Restart Policy**: unless-stopped (Neustart bei Fehler)

### Konfiguration (mosquitto.conf)

Die Konfigurationsdatei definiert:
- MQTT Listener auf Port 1883
- WebSocket Listener auf Port 9001
- Anonyme Verbindungen erlaubt (`allow_anonymous true`)
- Persistierung aktiviert (`persistence true`)
- Log-Ausgabe in Datei (`/mosquitto/log/mosquitto.log`)

### Verwendung

Zum Starten des Mosquitto Containers:

```bash
docker-compose up -d
```

Zum Stoppen:

```bash
docker-compose down
```

### Verbindung zu Mosquitto

- **MQTT-Clients**: localhost:1883
- **WebSocket-Clients**: localhost:9001