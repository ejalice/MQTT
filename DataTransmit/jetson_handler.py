from mqtt_client import MqttClient

class JetsonHandler:
    # current_request = None
    # request_queue = []

    @staticmethod
    def handle_message(device_id, msg_type, payload, topic):
        if msg_type == "response":
            JetsonHandler.handle_command(payload)
        else:
            print(f"Unhandled web message type: {msg_type}")
        
    @staticmethod
    def handle_command(data):
        response_data = data.get("response", {}).get("details", {}).get("status") == "arrived"
        if response_data == "arrived":
            print("Robot arrived, resetting goal_sent status.")
            # JetsonHandler.goal_sent = False
            # JetsonHandler.process_next_request()
            JetsonHandler.send_allocate(-1)
    
    @staticmethod
    def send_allocate(device_id, payload):
        print(f"Sending command to Jetson: {payload}")
        publish_topic = f"THELEE/jetson/{device_id}/request/command"
        if payload == -1: 
            payload = "b"
        MqttClient.publish(publish_topic, {"goal": payload}, qos=1)

    # def add_to_queue(payload):
    #     if not JetsonHandler.goal_sent:
    #         device_id = "TC1"
    #         JetsonHandler.send_allocate(device_id, payload)
    #     else:
    #         JetsonHandler.request_queue.append(payload)
    #         print(f"Added to queue: {payload}")

    # def cancel_request(payload):
    #     if payload in JetsonHandler.request_queue:
    #         JetsonHandler.request_queue.remove(payload)
    #         print(f"Cancelled request: {payload}")
    #     elif JetsonHandler.goal_sent:
    #         print("Cannot Cancel, request is already being proccesed")

    # @staticmethod
    # def process_next_request():
    #     if JetsonHandler.request_queue:
    #         next_request = JetsonHandler.request_queue.pop(0)
    #         print(f"Processing next request: {next_request}")
    #         JetsonHandler.send_allocate(next_request)
    #     else:
    #         print("No pending requests")