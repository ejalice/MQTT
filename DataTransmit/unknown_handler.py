
class UnknownHandler:
    @staticmethod
    def handle_message(device_id, msg_type, payload, topic):
        print(f"Unknown sender type received. Topic: {topic}, Device ID: {device_id}, Message Type: {msg_type}, Payload: {payload}")
