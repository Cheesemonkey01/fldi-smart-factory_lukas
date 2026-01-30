import json
import paho.mqtt.client as mqtt

BROKER_HOST = "localhost"
BROKER_PORT = 1883

TOPIC_TEMPERATURE = "factory/lightcell/telemetry/temperature"
TOPIC_STATE_COOLING = "factory/lightcell/state/cooling"
TOPIC_CMD_SETPOINT = "factory/lightcell/command/setpoint"
TOPIC_CMD_MODE = "factory/lightcell/command/mode"
TOPIC_CMD_COOLING = "factory/lightcell/command/cooling"

# interne Zustände
setpoint = 28.0
mode = "AUTO"  # oder "MANUAL"
cooling_on = False
manual_cooling_on = False  # gespeicherter manueller Zustand (wird beim Wechsel auf MANUAL angewendet)
last_temperature = None  # zuletzt empfangene Temperatur (float)


def evaluate_cooling(temperature: float):
    global cooling_on
    if mode == "AUTO":
        cooling_on = temperature > setpoint
    elif mode == "MANUAL":
        # in MANUAL verwenden wir den gespeicherten manuellen Zustand
        cooling_on = manual_cooling_on
    return cooling_on


def on_connect(client, userdata, flags, rc):
    print("Controller connected with result code", rc)
    client.subscribe(TOPIC_TEMPERATURE)
    client.subscribe(TOPIC_CMD_SETPOINT)
    client.subscribe(TOPIC_CMD_MODE)
    client.subscribe(TOPIC_CMD_COOLING)


def on_message(client, userdata, msg):
    global setpoint, mode, cooling_on, manual_cooling_on, last_temperature
    topic = msg.topic
    payload = msg.payload.decode("utf-8")
    print(f"Received on {topic}: {payload}")

    if topic == TOPIC_TEMPERATURE:
        try:
            data = json.loads(payload)
            temp = float(data.get("temperature"))
        except Exception:
            print("Invalid temperature payload")
            return

        global last_temperature
        last_temperature = temp

        cooling = evaluate_cooling(temp)
        state_payload = json.dumps({
            "cooling_on": cooling,
            "temperature": temp,
            "mode": mode,
            "setpoint": setpoint
        })
        client.publish(TOPIC_STATE_COOLING, state_payload)
        print(f"Published state: {state_payload}")

    elif topic == TOPIC_CMD_SETPOINT:
        try:
            data = json.loads(payload)
            setpoint = float(data.get("setpoint"))
            print(f"Setpoint updated to {setpoint}")
        except Exception:
            print("Invalid setpoint payload")

    elif topic == TOPIC_CMD_MODE:
        try:
            data = json.loads(payload)
            new_mode = str(data.get("mode")).upper()
            if new_mode in ("AUTO", "MANUAL"):
                mode = new_mode
                # beim Wechsel auf MANUAL wird der gespeicherte manuelle Zustand angewendet
                if mode == "MANUAL":
                    cooling_on = manual_cooling_on
                else:  # AUTO
                    if last_temperature is not None:
                        cooling_on = last_temperature > setpoint
                print(f"Mode updated to {mode}")

                # publish current state so HMI kann sofort aktualisieren
                state_payload = json.dumps({
                    "cooling_on": cooling_on,
                    "temperature": last_temperature,
                    "mode": mode,
                    "setpoint": setpoint
                })
                client.publish(TOPIC_STATE_COOLING, state_payload)
                print(f"Published state: {state_payload}")
        except Exception:
            print("Invalid mode payload")

    elif topic == TOPIC_CMD_COOLING:
        try:
            data = json.loads(payload)
            new_cooling = bool(data.get("cooling_on"))
            # immer als 'gewünschter' manueller Zustand speichern
            manual_cooling_on = new_cooling
            if mode == "MANUAL":
                cooling_on = manual_cooling_on
                print(f"Cooling manually set to {cooling_on}")
                # publish current state (include last known temperature if available)
                state_payload = json.dumps({
                    "cooling_on": cooling_on,
                    "temperature": last_temperature,
                    "mode": mode,
                    "setpoint": setpoint
                })
                client.publish(TOPIC_STATE_COOLING, state_payload)
                print(f"Published state: {state_payload}")
            else:
                print("Stored manual preference but ignoring because mode is not MANUAL")
        except Exception:
            print("Invalid cooling command payload")


def main():
    client = mqtt.Client(client_id="controller")
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_forever()


if __name__ == "__main__":
    main()
