# MQTTClient.py

import paho.mqtt.client as mqtt
import json
import logging
from Publisher import Publisher
from Subscriber import Subscriber
from Logger import Logger

# MQTT Client (메인 클래스)
class MQTTClient:
    def __init__(self, broker = "70.12.247.218", port=1883):
        self.client = mqtt.Client()
        self.publisher = Publisher(self.client)
        self.subscriber = Subscriber(self.client)

        # 콜백 함수 설정
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(broker, port, 60)

    def on_connect(self, client, userdata, flags, rc):
        Logger.log(f"✅ Connected to MQTT Broker (Code: {rc})")

    def on_message(self, client, userdata, msg):
        payload = json.loads(msg.payload.decode())
        Logger.log(f"📥 Received from {msg.topic}: {payload}")
        self.subscriber.handle_message(msg.topic, payload)

    def start(self):
        Logger.log("🚀 MQTT Client Running...")
        self.client.loop_forever()  # 이벤트 루프 실행

