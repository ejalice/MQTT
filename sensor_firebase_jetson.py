import firebase_admin
from firebase_admin import credentials, firestore
import paho.mqtt.client as mqtt
import json
import time
import threading

# Firebase Admin SDK 인증
cred = credentials.Certificate("service_key.json")  # Firestore 키 파일 경로 지정
firebase_admin.initialize_app(cred)

# Firestore 초기화
db = firestore.client()
call_collection = db.collection("Call")  # 감지할 Firestore 컬렉션

# MQTT 설정
BROKER = "SECRET"
PORT = 1883
KEEP_ALIVE_INTERVAL = 60

# 전역 변수
goal_sent = False
last_sent_time = 0

# 초음파 및 악취 센서 임계값 설정
MAX_ULTRASONIC_VALUE = 60
ULTRASONIC_THRESHOLD = MAX_ULTRASONIC_VALUE * 0.8
MAX_NH4 = 30
MAX_CO2 = 800
NH4_THRESHOLD = MAX_NH4 * 0.7
CO2_THRESHOLD = MAX_CO2 * 0.7

# MQTT 클라이언트 설정
mqtt_client = mqtt.Client()

# Firestore 실시간 리스너 함수
def on_firestore_snapshot(doc_snapshot, changes, read_time):
    print("Firestore Snapshot 감지!")

    for change in changes:
        message_payload = None

        if change.type.name == "ADDED":
            print("Firestore: 문서 추가됨")
            new_doc = change.document.to_dict()
            message_payload = new_doc.get("goal")

        elif change.type.name == "MODIFIED":
            print("Firestore: 문서 수정됨")
            message_payload = "0"  # 기본적으로 0 전송

        if message_payload is not None:
            print(f"Firestore → MQTT: goal={message_payload}")
            send_jetson_allocate(message_payload)

# Firestore 리스너 실행 함수
def start_firestore_listener():
    try:
        doc_watch = call_collection.on_snapshot(on_firestore_snapshot)
        print("Firestore 리스너 실행 중...")
    except Exception as e:
        print(f"Firestore 리스너 실행 실패: {e}")

# MQTT 메시지 전송 함수
def send_jetson_allocate(payload):
    print("Jetson으로로 메시지 전송 중...")
    if mqtt_client.is_connected():
        MQTT_TOPIC = "THELEE/jetson/TC1/request/command"
        mqtt_client.publish(MQTT_TOPIC, json.dumps({"goal": payload}), qos=1)
        print(f"MQTT 메시지 전송 완료: {payload}")
    else:
        print("MQTT 클라이언트가 연결되지 않았습니다.")

# MQTT 메시지 수신 콜백 함수
def on_mqtt_message(client, userdata, message):
    global goal_sent, last_sent_time

    try:
        payload = json.loads(message.payload)

        if message.topic.startswith("THELEE/sensor/TC1/response/data"):
            process_sensor_data(payload)

        elif message.topic.startswith("THELEE/sensor/TC1/response/event"):
            process_event_data(payload)

        elif message.topic.startswith("THELEE/jetson/TC1/response/command"):
            if payload.get("response", {}).get("details", {}).get("status") == "arrived":
                print("Robot arrived, resetting goal_sent status.")
                goal_sent = False
                last_sent_time = 0

    except Exception as e:
        print(f"메시지 처리 오류: {e}")

# 초음파 및 악취 센서 데이터 처리
def process_sensor_data(data):
    print("PROCESS SENSOR DATA")
    global goal_sent, last_sent_time

    # 초음파 데이터 처리
    ultrasonic_data = data["sensors"].get("ultrasonic")
    print(ultrasonic_data)
    if ultrasonic_data:
        if any(value > ULTRASONIC_THRESHOLD for value in ultrasonic_data.values()):
            if not goal_sent or time.time() - last_sent_time > 30:
                send_jetson_allocate(0)
                last_sent_time = time.time()
                goal_sent = True

    # 악취 센서 데이터 처리
    odor_data = data["sensors"].get("odor")
    if odor_data:
        nh4_value = odor_data.get("NH4", 0)
        co2_value = odor_data.get("CO2", 0)

        if nh4_value > NH4_THRESHOLD or co2_value > CO2_THRESHOLD:
            if not goal_sent or time.time() - last_sent_time > 30:
                send_jetson_allocate(0)
                last_sent_time = time.time()
                goal_sent = True

# 이벤트 데이터 처리 함수
def process_event_data(data):
    event_type = data.get("event")
    if event_type == "trash_detected":
        print(f"Trash detected: {data['trash']['type']}")
        # TODO: 필요하면 추가적인 MQTT 메시지 전송

# MQTT 연결 성공 시 호출되는 콜백 함수
def on_mqtt_connect(client, userdata, flags, rc):
    print(f"MQTT 연결 성공! 상태 코드: {rc}")
    client.subscribe("THELEE/sensor/TC1/response/data")
    client.subscribe("THELEE/sensor/TC1/response/event")
    client.subscribe("THELEE/web/admin/response/command")
    client.subscribe("THELEE/jetson/TC1/response/command")

# MQTT 연결 끊김 시 호출되는 콜백 함수
def on_mqtt_disconnect(client, userdata, rc):
    print(f"MQTT 연결 해제! 상태 코드: {rc}")

# MQTT 설정
mqtt_client.on_connect = on_mqtt_connect
mqtt_client.on_message = on_mqtt_message
mqtt_client.on_disconnect = on_mqtt_disconnect
mqtt_client.connect(BROKER, PORT, KEEP_ALIVE_INTERVAL)

# 실행 함수 (MQTT & Firestore 병렬 실행)
def main():
    # Firestore 리스너 실행 (쓰레드 사용)
    firestore_thread = threading.Thread(target=start_firestore_listener)
    firestore_thread.daemon = True
    firestore_thread.start()

    # MQTT 메시지 수신 시작
    mqtt_client.loop_start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("프로그램 종료 중...")
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

if __name__ == "__main__":
    main()
