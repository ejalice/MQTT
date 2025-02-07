# main.py
import paho.mqtt.client as mqtt
import json
import logging
from Publisher import Publisher
from Subscriber import Subscriber
from Logger import Logger
from MQTTClient import MQTTClient

if __name__ == "__main__":
    mqtt_client = MQTTClient(broker = "70.12.247.218")  # MQTT 브로커 연결

    # 샘플 데이터 핸들러 함수
    def handle_sensor_data(payload):
        Logger.log(f"📊 Processing Sensor Data: {payload}")
        if payload.get("ultrasonic", {}).get("general", 0) > 80:
            mqtt_client.publisher.publish("THELEE/rp/trashcan/command/update", {"alert": "Trash Full!"})

    def handle_web_request(payload):
        Logger.log(f"🌍 Processing Web Request: {payload}")

    # 토픽 등록
    mqtt_client.subscriber.subscribe("THELEE/sensor/trashcan/+/response/data/#", handle_sensor_data)
    mqtt_client.subscriber.subscribe("THELEE/web/trashcan/+/request/allocate", handle_web_request)

    mqtt_client.start()  # 실행
