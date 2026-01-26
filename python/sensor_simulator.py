import time
import random
import json
from datetime import datetime
import paho.mqtt.client as mqtt

BROKER_HOST = "localhost"  # wenn Sensor im Docker-Netz läuft: "mosquitto"
BROKER_PORT = 1883
TOPIC_TEMPERATURE = "factory/lightcell/telemetry/temperature"


def generate_temperature():
    # einfache Simulation: 20–35 °C
    return round(random.uniform(20.0, 35.0), 2)


def main():
    client = mqtt.Client(client_id="sensor-simulator")
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_start()

    try:
        while True:
            temp = generate_temperature()
            payload = {
                "temperature": temp,
                "timestamp": datetime.now().isoformat()
            }
            client.publish(TOPIC_TEMPERATURE, json.dumps(payload), qos=0)
            print(f"Published temperature: {temp} °C at {payload['timestamp']}")
            time.sleep(2)
    except KeyboardInterrupt:
        print("Stopping sensor...")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
