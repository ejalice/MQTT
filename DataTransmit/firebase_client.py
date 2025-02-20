import firebase_admin
from firebase_admin import credentials, firestore
from jetson_handler import JetsonHandler

class FirebaseClient:
    def __init__(self, credential_path):
        cred = credentials.Certificate(credential_path)
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()
        self.call_collection = self.db.collection("Call")
        self.start_listener()

    def start_listener(self):
        self.call_collection.on_snapshot(self.on_firestore_snapshot)
        print("Firestore listener started...")

    def on_firestore_snapshot(self, doc_snapshot, changes, read_time):
        print("Firestore Snapshot detected!")
        for change in changes:
            message_payload = None
            device_id = ""
            if change.type.name == "ADDED":
                print("Firestore: Document added")
                new_doc = change.document.to_dict()
                message_payload = new_doc.get("goal")
                device_id = new_doc.get("robotId")
            elif change.type.name == "MODIFIED":
                print("Firestore: Document modified")
                message_payload = "0"
            if message_payload is not None:
                print(f"Firestore → MQTT: goal={message_payload}")
                device_id = "TC1" # 현재는 무조건 TC1으로 고정하기 위한 코드
                JetsonHandler.send_allocate(device_id, message_payload)
