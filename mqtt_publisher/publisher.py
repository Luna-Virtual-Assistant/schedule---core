import os
import paho.mqtt.client as mqtt
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


mqtt_client = mqtt.Client(os.getenv("PUBLISHER_NAME"))
mqtt_client.connect(host=os.getenv("HOST"), port=int(os.getenv("PORT")))

def publish(text: str):
    print(f"[{datetime.now().strftime('%Y-%m-%d - %H:%M:%S')}] publishing to {os.getenv('RES_TOPIC')}")
    mqtt_client.publish(topic=os.getenv("RES_TOPIC"), payload=text)