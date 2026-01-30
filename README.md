# fldi-smart-factory_lukas
Abschlussprojekt_5AAME

## ________________

    In diesem 8-stufigen Projekt entwickeln die Schüler eine vernetzte Smart-Factory-Zelle als CPS. Das System wird technisch umgesetzt, digital modelliert und über GitHub versioniert weiterentwickelt.

    Das Projekt bildet bewusst eine realitätsnahe, dynamsiche Entwicklungsumgebung ab, in der sich Anforderungen, Lösungswege und Entscheidungen im Projektverlauf verändern können.

### _______________

## 🚀 Command Cheat Sheet - Alle Commands zum Ausführen

### Einmalig: Abhängigkeiten installieren

```bash
# Flutter Dependencies installieren
cd flutter_hmi/
flutter pub get
cd ..

# Python Dependencies installieren
pip install -r requirements.txt
```

### Projekt starten (4 Terminal-Fenster)

**Terminal 1 - Docker Mosquitto Broker**:
```bash
cd Docker/
docker-compose up -d
```

**Terminal 2 - Sensor Simulator**:
```bash
cd python/
python sensor_simulator.py
```

**Terminal 3 - Controller**:
```bash
cd python/
python controller.py
```

**Terminal 4 - Flutter HMI**:
```bash
cd flutter_hmi/
flutter run -d windows
```

### Projekt stoppen

```bash
# Alle Python-Prozesse beenden
# (Strg+C in den Terminal-Fenstern drücken)

# Docker stoppen
cd Docker/
docker-compose down
```

### Häufige Befehle

```bash
# Flutter Project neu erstellen (falls pubspec.yaml fehlt)
cd flutter_hmi/
flutter create .

# Flutter HMI debuggen/bauen
flutter build windows          # Build für Windows Desktop
flutter pub get                # Dependencies aktualisieren
flutter clean                  # Cache löschen

# Docker-Status prüfen
docker ps                      # Laufende Container
docker logs mosquitto          # Mosquitto Logs anschauen
docker-compose ps             # Compose-Services prüfen

# Python MQTT Test (optional - außerhalb von controller.py)
python -c "import paho.mqtt.client; print('MQTT OK')"
```

---

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

---

## Projektarchitektur

Das Smart Factory-System besteht aus drei Hauptkomponenten:

```
┌─────────────────────────────────────────────────────────┐
│                    Flutter HMI                          │
│          (User Interface / Dashboard)                   │
│                                                         │
│  • Temperaturanzeige                                    │
│  • Kühlungsstatus                                       │
│  • Mode-Auswahl (AUTO/MANUAL)                          │
│  • Setpoint-Eingabe                                     │
└─────────────────┬───────────────────────────────────────┘
                  │
                  │ MQTT (Port 1883)
                  │
┌─────────────────┴───────────────────────────────────────┐
│                  Mosquitto MQTT Broker                  │
│          (Message Queue Telemetry Transport)            │
│                                                         │
│  • MQTT Protocol (Port 1883)                            │
│  • WebSocket Support (Port 9001)                        │
│  • Konfiguration via mosquitto.conf                     │
└─────────────────┬───────────────────────────────────────┘
       ┌───────────┴────────────────┐
       │                            │
       ▼                            ▼
  Python Controller           Sensor Simulator
  (Logic & State)             (Daten-Generator)
```

---

## 1. Python Backend

### 1.1 Sensor Simulator (`sensor_simulator.py`)

**Zweck**: Simuliert IoT-Sensoren durch Generierung realistischer Temperaturwerte

**Funktionalität**:
- Erzeugt Temperaturwerte im Bereich 20–35 °C
- Publiziert Werte mit Timestamp im ISO-Format
- Intervall: Alle 2 Sekunden
- Format: `{"temperature": 25.34, "timestamp": "2026-01-26T10:30:45.123456"}`

**Topic**: `factory/lightcell/telemetry/temperature`

**Start**:
```bash
cd python/
python sensor_simulator.py
```

---

### 1.2 Controller (`controller.py`)

**Zweck**: Zentrale Steuerlogik für die Smart Factory-Zelle

**Funktionalität**:
- **Zustandsverwaltung**: Speichert aktuell Setpoint, Mode, Kühlungsstatus
- **Temperaturüberwachung**: Empfängt Sensordaten
- **Kühlungslogik**: 
  - Im AUTO-Mode: Kühlung EIN, wenn Temperatur > Setpoint
  - Im MANUAL-Mode: Kan manuell gesteuert werden
- **Kommandoverarbeitung**: Verarbeitet Befehle vom HMI (Setpoint, Mode)
- **Statusübertragung**: Publiziert aktuellen Zustand

**Topics**:
- **Empfangen**:
  - `factory/lightcell/telemetry/temperature` (vom Sensor)
  - `factory/lightcell/command/setpoint` (vom HMI)
  - `factory/lightcell/command/mode` (vom HMI)
- **Senden**:
  - `factory/lightcell/state/cooling` (an HMI)

**Start**:
```bash
cd python/
python controller.py
```

---

## 2. Flutter HMI (Human-Machine Interface)

### 2.1 Architektur

**Datei**: `flutter_hmi/lib/main.dart`

**Klassen**:
- `SmartFactoryApp`: Root Widget
- `DashboardPage`: Stateful Widget für die HMI
- `_DashboardPageState`: State mit MQTT-Logik

**Abhängigkeiten** (pubspec.yaml):
- `flutter` (Material Design UI)
- `mqtt_client: ^9.7.0` (MQTT-Kommunikation)

---

### 2.2 Funktionalität

#### MQTT-Verbindung
```dart
client = MqttServerClient('localhost', 'flutter-hmi');
client.port = 1883;
await client.connect();
```

#### Abonnierte Topics
- `factory/lightcell/telemetry/temperature` - Empfängt Temperaturwerte
- `factory/lightcell/state/cooling` - Empfängt Kühlungsstatus und Mode

#### Benutzeroberfläche

**Anzeige-Bereich**:
- Aktuelle Temperatur (live aktualisiert)
- Kühlungsstatus (EIN/AUS)
- Aktueller Mode (AUTO/MANUAL)
- Eingestellter Setpoint

**Steuerelement - Setpoint ändern**:
- Textfeld für neue Setpoint-Eingabe (°C)
- Senden-Button publiziert: `factory/lightcell/command/setpoint`
- Payload: `{"setpoint": 28.5}`

**Steuerelement - Mode wählen**:
- AUTO-Button: Publiziert `{"mode": "AUTO"}`
- MANUAL-Button: Publiziert `{"mode": "MANUAL"}`
- Topic: `factory/lightcell/command/mode`

---

### 2.3 Key Functions

**`_connect()`**: Etabliert MQTT-Verbindung und abonniert Topics
```dart
Future<void> _connect() async
```

**`_publishSetpoint()`**: Sendet neuen Setpoint-Wert zum Controller
```dart
void _publishSetpoint()
```

**`_publishMode(String newMode)`**: Sendet Mode-Änderung
```dart
void _publishMode(String newMode)
```

**`build()`**: Baut UI mit MaterialApp, Scaffold und Widgets

---

### 2.4 Installation & Start

**Installation**:
```bash
cd flutter_hmi/
flutter pub get
```

**Ausführung (Windows Desktop)**:
```bash
flutter run -d windows
```

**Verfügbare Targets**:
```bash
flutter devices                  # Geräte anzeigen
flutter run -d windows          # Windows Desktop
flutter run -d chrome           # Web Browser
```

---

## 3. Docker & Mosquitto

### 3.1 Docker-Compose Setup

**Datei**: `Docker/docker-compose.yml`

```yaml
version: "3.8"
services:
  mosquitto:
    image: eclipse-mosquitto:2
    container_name: mosquitto
    ports:
      - "1883:1883"      # MQTT
      - "9001:9001"      # WebSocket
    volumes:
      - ./mosquitto.conf:/mosquitto/config/mosquitto.conf
    restart: unless-stopped
```

**Start**:
```bash
cd Docker/
docker-compose up -d
```

**Stop**:
```bash
docker-compose down
```

**Logs anschauen**:
```bash
docker-compose logs -f mosquitto
```

---

### 3.2 Mosquitto Konfiguration

**Datei**: `Docker/mosquitto.conf`

```properties
listener 1883              # MQTT Port
allow_anonymous true       # Anonyme Verbindungen erlaubt
persistence true           # Nachrichten persistieren
persistence_location /mosquitto/data/
log_dest file /mosquitto/log/mosquitto.log
protocol mqtt

listener 9001              # WebSocket Port
protocol websockets
```

---

## 4. Datenfluss & Message Topics

### 4.1 Topic-Struktur

```
factory/
├── lightcell/
│   ├── telemetry/
│   │   └── temperature          ← Sensor publiziert
│   ├── command/
│   │   ├── setpoint             ← HMI publiziert
│   │   └── mode                 ← HMI publiziert
│   └── state/
│       └── cooling              ← Controller publiziert
```

### 4.2 Message Flow

```
Sensor                          Controller                      HMI
  │                                │                             │
  ├──temperature──────────────────►│                             │
  │                                │                             │
  │                                ├──state/cooling────────────►│
  │                                │   (mit temp, mode, setpoint)
  │                                │                             │
  │                                │◄────command/setpoint───────┤
  │                                │                             │
  │                                │◄────command/mode───────────┤
  │                                │                             │
```

---

## 5. Hindernisse & Lessons Learned

Im Verlauf des Projekts sind mehrere Hindernisse aufgetreten. Nachfolgend eine strukturierte Auflistung mit Symptomen, vermuteter Ursache und praktischen Gegenmaßnahmen:

- **Netzwerk & MQTT-Verbindungen (Windows Firewall / Ports)**
  - Symptom: HMI oder Simulator kann sich nicht mit Broker verbinden (Timeouts, Connection refused).
  - Ursache: Windows-Firewall oder Docker-Portbindung blockiert Port 1883/9001.
  - Gegenmaßnahme: Firewall-Regeln anpassen, Ports in `docker-compose.yml` prüfen, Broker-Logs auswerten.

- **Docker & Volume/Permission Issues**
  - Symptom: Mosquitto lädt Konfiguration nicht oder bricht mit Zugriffsfehlern ab.
  - Ursache: Volume-Mounts (z. B. OneDrive) oder fehlende Schreibrechte für Log-/Data-Verzeichnisse.
  - Gegenmaßnahme: Volumes prüfen, ggf. Ordner außerhalb von OneDrive verwenden und Berechtigungen korrigieren.

- **OneDrive / Datei-Synchronisation**
  - Symptom: Dateien werden gesperrt, Builds schlagen fehl oder Dateien werden unerwartet überschrieben.
  - Ursache: Workspace liegt in OneDrive; Background-Sync sperrt Dateien.
  - Gegenmaßnahme: Projekt temporär lokal außerhalb von OneDrive bearbeiten oder Sync pausieren.

- **MQTT-Payload / JSON-Inkompatibilitäten**
  - Symptom: Parser-Fehler im Controller/HMI oder fehlende Felder.
  - Ursache: Unterschiedliche Payload-Formate zwischen Komponenten.
  - Gegenmaßnahme: Payload-Schema dokumentieren, Validierung (try/catch) und Tests hinzufügen.

- **Stabile MQTT-Verbindungen / Reconnect-Strategien**
  - Symptom: Verbindungsabbrüche bei Netzwerkunterbrechungen.
  - Ursache: Fehlende oder ineffektive Reconnect-Logik.
  - Gegenmaßnahme: Reconnect-Strategie + Backoff implementieren; Status in UI anzeigen.

- **Timing & Race Conditions (Simulator vs Controller)**
  - Symptom: Kühlung flackert oder Zustand springt bei hoher Nachrichtenrate.
  - Ursache: Keine Hysterese/Debounce in der Steuerlogik.
  - Gegenmaßnahme: Hysterese einbauen, Nachrichtenrate begrenzen, Zustandsupdates debouncen.

- **Entwicklungs-Toolchain (Flutter Windows Build)**
  - Symptom: Build- oder Laufzeitfehler beim Start der HMI auf Windows.
  - Ursache: Fehlende native Toolchain (Visual Studio Build Tools) oder falsche Flutter-Version.
  - Gegenmaßnahme: `flutter doctor` ausführen, Visual Studio C++ Build Tools installieren, Dokumentation ergänzen.

- **Sicherheit & Persistenz (Mosquitto)**
  - Symptom: Unverschlüsselte, anonyme Verbindungen sind standardmäßig möglich.
  - Ursache: `allow_anonymous true` in Default-Konfiguration.
  - Gegenmaßnahme: Für produktive Umgebungen Authentifizierung/TLS konfigurieren und Persistenz prüfen.

- **Abhängigkeits- & Versionskonflikte (Python / Dart)**
  - Symptom: Laufzeitfehler durch inkompatible Paketversionen.
  - Gegenmaßnahme: `requirements.txt` und `pubspec.yaml` pflegen, CI-Tests einrichten und Versionsbereiche einschränken.

---

**Tipps & Empfehlungen**

- Dokumentiere reproduzierbare Schritte mit Logausgaben und Zeitstempeln für jeden Fehlerfall. ✅
- Führe einfache Integrationstests für Topics und Payload-Formate ein (Smoke Tests). ✅
- Bei Problemen mit OneDrive: temporär außerhalb von OneDrive arbeiten oder Sync pausieren. ⚠️

---

---

## 5. Python Requirements

**Datei**: `requirements.txt`

```
paho-mqtt==1.6.1
```

**Installation**:
```bash
pip install -r requirements.txt
```

---

## 6. Quick Start Guide

### Schritt 1: Docker starten (MQTT Broker)
```bash
cd Docker/
docker-compose up -d
```

### Schritt 2: Sensor Simulator starten
```bash
cd python/
python sensor_simulator.py
```

### Schritt 3: Controller starten (in neuem Terminal)
```bash
cd python/
python controller.py
```

### Schritt 4: Flutter HMI starten (in neuem Terminal)
```bash
cd flutter_hmi/
flutter run -d windows
```

**Ergebnis**: 
- HMI zeigt live Temperaturwerte vom Sensor
- Sie können den Setpoint und Mode über die UI ändern
- Controller steuert die Kühlung automatisch

---

## 7. Systemanforderungen

- **Python**: 3.7+
- **Flutter**: 3.0+
- **Docker**: Docker Desktop (Windows)
- **MQTT Broker**: Eclipse Mosquitto 2.0+ (via Docker)

---

## 8. Troubleshooting

| Problem | Lösung |
|---------|--------|
| `pubspec.yaml nicht gefunden` | `flutter create .` im flutter_hmi Verzeichnis ausführen |
| `Connection failed` (HMI) | Docker-Compose läuft nicht → `docker-compose up -d` |
| Keine Sensordaten | `sensor_simulator.py` läuft nicht → in `python/` starten |
| Mode ändert sich nicht | Controller läuft nicht → `python controller.py` starten |
| MQTT Port 1883 belegt | `docker-compose down` und neu starten |