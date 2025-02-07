import paho.mqtt.client as mqtt
import json

class Processor:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client

    def handle_sensor_data(self, topic, data):
        """ 센서 데이터를 처리 후 Web으로 Publish """
        device_id = data.get("device_id")
        response_topic = f"THELEE/web/trashcan/{device_id}/response/data"
        
        if "ultrasonic" in data:
            data["ultrasonic"] = {key: round(value / 100, 2) for key, value in data["ultrasonic"].items()}
        
        self.mqtt_client.publish(response_topic, json.dumps(data))

        # 경고 메시지 발송 (예: 쓰레기통이 거의 찼을 때)
        if data.get("ultrasonic", {}).get("general", 0) > 0.8:
            alert_payload = {
                "timestamp": data.get("timestamp"),
                "device_id": device_id,
                "alert": "Trash bin is almost full!",
                "ultrasonic": data["ultrasonic"]
            }
            self.mqtt_client.publish("THELEE/web/trashcan/command/update", json.dumps(alert_payload))

    def handle_web_command(self, topic, data):
        """ Web 요청을 받아 Jetson으로 Publish """
        command_mapping = {
            "allocate": "allocate",
            "return_home": "return"
        }
        
        request_type = data.get("request")
        device_id = data.get("device_id")
        
        if request_type in command_mapping:
            jetson_topic = f"THELEE/rp/trashcan/{device_id}/command/{command_mapping[request_type]}"
            self.mqtt_client.publish(jetson_topic, json.dumps(data))

    def handle_jetson_response(self, topic, data):
        """ Jetson 응답을 처리하고 Web으로 전송 """
        device_id = data.get("device_id")
        response_topic = f"THELEE/web/trashcan/{device_id}/response/jetson"
        self.mqtt_client.publish(response_topic, json.dumps(data))

    # def is_request_conflicting(self, request1, request2):
    #     """ 두 개의 요청이 같은 쓰레기통에서 동시에 발생하는지 확인 """
    #     return request1["device_id"] == request2["device_id"] and request1["request"] != request2["request"]
    
    # def process_requests(self, requests):
    #     """ 여러 요청을 동시에 처리하며, 충돌 여부 확인 """
    #     for i in range(len(requests)):
    #         for j in range(i + 1, len(requests)):
    #             if self.is_request_conflicting(requests[i], requests[j]):
    #                 print(f"Conflict detected between {requests[i]} and {requests[j]}")
        
    #     for request in requests:
    #         self.handle_request("", request)
