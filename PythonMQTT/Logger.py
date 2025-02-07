# Logger.py
import paho.mqtt.client as mqtt
import json
import logging

# Logger 설정
class Logger:
    def __init__(self, log_file="mqtt.log"):
        logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s")
    
    @staticmethod
    def log(message):
        print(message)  # 콘솔 출력
        logging.info(message)  # 파일 저장