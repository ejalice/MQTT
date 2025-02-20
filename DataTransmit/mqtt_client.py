import json
import paho.mqtt.client as mqtt
from message_handler import MessageHandler

class MqttClient:
    _instance = None

    def __new__(cls, broker, port, keep_alive):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.broker = broker
            cls._instance.port = port
            cls._instance.keep_alive = keep_alive
            cls._instance.client = mqtt.Client()
            cls._instance._setup_callbacks()
        return cls._instance

    def _setup_callbacks(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def connect(self):
        self.client.connect(self.broker, self.port, self.keep_alive)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print(f"MQTT Connected! Status Code: {rc}")
        client.subscribe("THELEE/+/+/response/#")

    def on_disconnect(self, client, userdata, rc):
        print(f"MQTT Disconnected! Status Code: {rc}")

    def on_message(self, client, userdata, message):
        MessageHandler.process_message(message)

    @staticmethod
    def publish(topic, payload, qos=1):
        if MqttClient._instance is not None:
            MqttClient._instance.client.publish(topic, json.dumps(payload))
            print(f"Published to {topic} with QOS {qos}: {payload}")
        else:
            print("MQTT Client is not initialized!")
