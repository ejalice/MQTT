from jetson_handler import JetsonHandler

class WebHandler:

    @staticmethod
    def handle_message(device_id, msg_type, payload, topic):
        if msg_type == "response":
            WebHandler.handle_command(payload)
        else:
            print(f"Unhandled web message type: {msg_type}")
    
    @staticmethod
    def handle_command(data):
        command_data = data.get("command").get("type", "")
        device_id = data.get("device_id", "TC1")
        if command_data == "return":
            JetsonHandler.send_allocate(device_id, -1)