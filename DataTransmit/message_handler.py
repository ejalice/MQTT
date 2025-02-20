

class MessageHandler:
    @staticmethod
    def process_message(message):
        import json
        from sensor_handler import SensorHandler
        from jetson_handler import JetsonHandler
        from web_handler import WebHandler
        from unknown_handler import UnknownHandler
        try:
            payload = json.loads(message.payload)
            topic_parts = message.topic.split("/")
            if len(topic_parts) < 4:
                raise ValueError("Unexpected Topic Structure")

            sender_type = topic_parts[1]
            device_id = topic_parts[2]
            msg_type = topic_parts[3]
            print(f"\nReceived Topic: {message.topic}")

            handler_mapping = {
                "sensor": SensorHandler,
                "jetson": JetsonHandler,
                "web": WebHandler
            }
            handler = handler_mapping.get(sender_type, UnknownHandler)
            handler.handle_message(device_id, msg_type, payload, message.topic)
        except Exception as e:
            print(f"Message Processing Error: {e}")