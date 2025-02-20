import time, json
from mqtt_client import MqttClient
from jetson_handler import JetsonHandler
from topic_transformer import TopicTransformer

# 초음파 및 악취 센서 임계값 설정
MAX_ULTRASONIC_VALUE = 60
ULTRASONIC_THRESHOLD = MAX_ULTRASONIC_VALUE * 0.8
MAX_NH4 = 0.12
MAX_CO2 = 600
NH4_THRESHOLD = MAX_NH4 * 0.7
CO2_THRESHOLD = MAX_CO2 * 0.7

class SensorHandler:
    latest_sensor_data = {}

    @staticmethod
    def handle_message(device_id, msg_type, payload, topic):
        if "data" in topic:
            SensorHandler.handle_data(payload, topic)
        elif "event" in topic:
            SensorHandler.handle_event(payload)
        else:
            print(f"Unhandled web message type: {msg_type}")

    @staticmethod
    def handle_data(data, topic):
        publish_topic = TopicTransformer.transform_publish_topic(topic)
        SensorHandler.store_data(data)

        sensor_data = data.get("sensors", {})
        device_id = data.get("device_id", "TC1")
        transmit_payload = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "device_id": device_id,
            "type": "sensor_data",
            "sensors": sensor_data
        }
        
        # 초음파 처리
        ultrasonic_data = sensor_data.get("ultrasonic")
        print(f"ultrasonic: {ultrasonic_data}")
        
        if ultrasonic_data:
            print(f"초음파 데이터 감지: {ultrasonic_data}")
            proccessed_ultrasonic_data = {key: round(value * 0.7, 2) for key, value in ultrasonic_data.items()}
            transmit_payload["sensors"]["ultrasonic"] = proccessed_ultrasonic_data
            print(f"보정된 초음파 데이터 감지: {proccessed_ultrasonic_data}")
            MqttClient.publish(publish_topic, json.dumps(transmit_payload), qos=1)

            print(f"초음파 데이터 WEB 전송: {publish_topic}\n")
            if any(value > ULTRASONIC_THRESHOLD for value in ultrasonic_data.values()):
                if not JetsonHandler.goal_sent:
                    JetsonHandler.send_allocate(device_id, -1)
                    goal_sent = True

        # 악취 센서 데이터 처리
        odor_data = sensor_data.get("odor")
        print(f"odor: {odor_data}")
        if odor_data:
            nh4_value = odor_data.get("NH4", 0)
            co2_value = odor_data.get("CO2", 0)

            MqttClient.publish(publish_topic, json.dumps(transmit_payload), qos=1)
            print(f"악취 데이터 WEB 전송: {publish_topic}\n")

            if nh4_value > NH4_THRESHOLD or co2_value > CO2_THRESHOLD:
                transmit_payload["sensors"]["odor"] = odor_data
                
                if not JetsonHandler.goal_sent:
                    JetsonHandler.send_allocate(device_id, -1)
                    JetsonHandler.goal_sent = True

    

    @staticmethod
    def handle_event(data):
        if not SensorHandler.latest_sensor_data:
            print("최신 데이터 없음")
            return
        
        event_type = data.get("event")
        if event_type == "trash_detected":
            trash_data = data["trash"].get("type")
            print(f"Trash detected: {trash_data}")

            total_data = SensorHandler.latest_sensor_data.copy()
            total_data["trash"] = trash_data

            publish_topic = "THELEE/web/+/transmit/event"
            MqttClient.publish(publish_topic, json.dumps(total_data), qos=1)
            print(f"web으로 event data 전송 완료: {publish_topic}")


    
    @staticmethod
    def store_data(data):
        if not SensorHandler.latest_sensor_data:
            SensorHandler.latest_sensor_data = {
                "timestamp": data.get("timestamp", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())),
                "device_id": data.get("device_id", ""),
                "status": data.get("status", {}),
                "sensors": {},
                "trash": {}
            }
        
        SensorHandler.latest_sensor_data["timestamp"] = data.get("timestamp", SensorHandler.latest_sensor_data["timestamp"])
        SensorHandler.latest_sensor_data["device_id"] = data.get("device_id", SensorHandler.latest_sensor_data["device_id"])
        SensorHandler.latest_sensor_data["status"] = data.get("status", SensorHandler.latest_sensor_data["status"])

        
        incoming_sensors = data.get("sensors", {})
        for key, value in incoming_sensors.items():
            SensorHandler.latest_sensor_data["sensors"][key] = value
        
        SensorHandler.latest_sensor_data["trash"] = data.get("trash", SensorHandler.latest_sensor_data["trash"]) 


