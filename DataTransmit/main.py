import time
from mqtt_client import MqttClient
from firebase_client import FirebaseClient

if __name__ == "__main__":
    firebase_client = FirebaseClient("service_key.json")
    mqtt_client = MqttClient("70.12.108.82", 1883, 60)
    mqtt_client.connect()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
        mqtt_client.client.loop_stop()
        mqtt_client.client.disconnect()