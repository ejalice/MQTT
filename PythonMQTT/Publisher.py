# Publisher.py
import paho.mqtt.client as mqtt
import json
from Logger import Logger

# MQTT Publisher (메시지 발행)
class Publisher:
    def __init__(self, client):
        self.client = client

    def publish(self, topic, message):
        payload = json.dumps(message)
        self.client.publish(topic, payload)
        Logger.log(f"📤 Published to {topic}: {payload}")
