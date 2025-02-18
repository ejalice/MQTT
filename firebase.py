import firebase_admin
from firebase_admin import credentials, firestore
import paho.mqtt.client as mqtt
import json

# Firebase Admin SDK 인증
cred = credentials.Certificate("service_key.json")  # key.json 경로를 지정
firebase_admin.initialize_app(cred)

# Firestore 초기화
db = firestore.client()
call_collection = db.collection('Call')

# MQTT 연결 설정
mqtt_broker = "70.12.108.82"  # MQTT 브로커 호스트
mqtt_port = 1883  # MQTT 포트 (기본: 1883)
mqtt_topic = "THELEE/rp/trashcan/TC1/command/allocate"

mqtt_client = mqtt.Client()

# Firestore 실시간 리스너 함수
def on_snapshot(doc_snapshot, changes, read_time):
    print("Snapshot 받음!")
    print(f"변경 사항: {changes}")  # 변경 사항을 출력하여 확인
    if not changes:
        print("변경 사항이 없습니다.")
    
    for change in changes:
        message_payload = None

        if change.type.name == 'ADDED':
            print("문서 추가됨")
            # 문서 추가 시
            new_doc = change.document.to_dict()
            # goal 필드만 가져오기
            message_payload = new_doc.get('goal')  # goal 값을 가져옴
        elif change.type.name == 'MODIFIED':
            print("문서 수정됨")
            # 문서 수정 시
            message_payload = -1  # 수정된 경우 -1 전송

        if message_payload is not None:
            send_mqtt_message(message_payload)

# MQTT 메시지 전송 함수
def send_mqtt_message(payload):
    print("MQTT 메시지 전송 중...")
    if mqtt_client.is_connected():
        mqtt_client.publish(mqtt_topic, json.dumps({"payload": payload}), qos=1)
        print(f"MQTT 메시지 전송 완료: {payload}")
    else:
        print("MQTT 클라이언트가 연결되지 않았습니다.")

# MQTT 연결 성공 여부를 출력하는 콜백 함수
def on_connect(client, userdata, flags, rc):
    print(f"MQTT 연결 성공! 상태 코드: {rc}")
    client.subscribe(mqtt_topic)

mqtt_client.on_connect = on_connect

# Firestore 컬렉션에 실시간 리스너 추가
call_collection.on_snapshot(on_snapshot)

# MQTT 연결 및 유지
mqtt_client.connect(mqtt_broker, mqtt_port, 60)
mqtt_client.loop_forever()
