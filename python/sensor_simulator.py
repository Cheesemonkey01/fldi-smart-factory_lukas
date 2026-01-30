import time
import random
import json
from datetime import datetime
import paho.mqtt.client as mqtt

BROKER_HOST = "localhost"  # wenn Sensor im Docker-Netz läuft: "mosquitto"
BROKER_PORT = 1883
TOPIC_TEMPERATURE = "factory/lightcell/telemetry/temperature"
TOPIC_STATE = "factory/lightcell/state/cooling"

# Simulation state
current_temp = 30.0
cooling_on = False
MIN_TEMP = 15.0
MAX_TEMP = 40.0
COOLING_RATE = 0.5   # °C per cycle when cooling
HEATING_RATE = 0.2   # °C per cycle when not cooling


def generate_temperature():
    global current_temp, cooling_on
    noise = random.uniform(-0.1, 0.1)
    if cooling_on:
        # actively cool down
        current_temp = max(MIN_TEMP, current_temp - COOLING_RATE + noise)
    else:
        # drift upwards slowly
        current_temp = min(MAX_TEMP, current_temp + HEATING_RATE + noise)
    return round(current_temp, 2)


def on_message(client, userdata, msg):
    global cooling_on, current_temp
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        # state message may contain cooling_on and optionally temperature
        if 'cooling_on' in payload:
            cooling_on = bool(payload.get('cooling_on'))
            print(f"Simulator: cooling_on set to {cooling_on} from state topic")
        if 'temperature' in payload and payload.get('temperature') is not None:
            # optionally sync simulator temperature to controller state
            try:
                current_temp = float(payload.get('temperature'))
            except Exception:
                pass
    except Exception as e:
        print(f"Simulator failed to parse state message: {e}")


def main():
    client = mqtt.Client(client_id="sensor-simulator")
    client.on_message = on_message
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_start()
    client.subscribe(TOPIC_STATE)

    try:
        while True:
            temp = generate_temperature()
            payload = {
                "temperature": temp,
                "timestamp": datetime.now().isoformat()
            }
            client.publish(TOPIC_TEMPERATURE, json.dumps(payload), qos=0)
            print(f"Published temperature: {temp} °C at {payload['timestamp']} (cooling_on={cooling_on})")
            time.sleep(2)
    except KeyboardInterrupt:
        print("Stopping sensor...")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
