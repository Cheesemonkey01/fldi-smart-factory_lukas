import json
import paho.mqtt.client as mqtt

BROKER_HOST = "localhost"
BROKER_PORT = 1883

TOPIC_TEMPERATURE = "factory/lightcell/telemetry/temperature"
TOPIC_STATE_COOLING = "factory/lightcell/state/cooling"
TOPIC_CMD_SETPOINT = "factory/lightcell/command/setpoint"
TOPIC_CMD_MODE = "factory/lightcell/command/mode"

# interne Zustände
setpoint = 28.0
mode = "AUTO"  # oder "MANUAL"
cooling_on = False


def evaluate_cooling(temperature: float):
    global cooling_on
    if mode == "AUTO":
        cooling_on = temperature > setpoint
    # in MANUAL könnte später HMI direkt schalten
    return cooling_on


def on_connect(client, userdata, flags, rc):
    print("Controller connected with result code", rc)
    client.subscribe(TOPIC_TEMPERATURE)
    client.subscribe(TOPIC_CMD_SETPOINT)
    client.subscribe(TOPIC_CMD_MODE)


def on_message(client, userdata, msg):
    global setpoint, mode
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
                print(f"Mode updated to {mode}")
        except Exception:
            print("Invalid mode payload")


def main():
    client = mqtt.Client(client_id="controller")
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_forever()


if __name__ == "__main__":
    main()
