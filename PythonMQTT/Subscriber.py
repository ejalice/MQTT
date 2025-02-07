# Subscriber.py
import paho.mqtt.client as mqtt
import json
import logging
import re
from Logger import Logger

# MQTT Subscriber (메시지 구독)
class Subscriber:
    def __init__(self, client):
        self.client = client
        self.subscribers = {}  # { "토픽": 핸들러 함수 }

    def subscribe(self, topic, handler):
        regex_topic = self._convert_to_regex(topic) # WildCard 포함
        self.subscribers[regex_topic] = handler
        self.client.subscribe(topic)
        Logger.log(f"🔔 Subscribed to {topic}")

    def handle_message(self, topic, payload):
        for pattern, handler in self.subscribers.items():
            if re.fullmatch(pattern, topic):
                handler(payload)
                return
        if topic in self.subscribers:
            self.subscribers[topic](payload)  # 등록된 핸들러 실행
        else:
            Logger.log(f"⚠️ No handler for topic: {topic}")

    def _convert_to_regex(self, topic):
        topic = topic.replace("+", r"[^/]+")  # `+`는 한 단계 경로와 매칭
        topic = topic.replace("#", r".*")  # `#`는 모든 하위 경로와 매칭
        return topic