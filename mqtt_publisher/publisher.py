import os
import paho.mqtt.client as mqtt
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


mqtt_client = mqtt.Client(os.getenv("PUBLISHER_NAME"))
mqtt_client.connect(host=os.getenv("HOST"), port=int(os.getenv("PORT")))

def publish(text: str) -> None:
    topic = os.getenv("RES_TOPIC")
    print(f"[{datetime.now().strftime('%Y-%m-%d - %H:%M:%S')}] publishing to {topic}")
    mqtt_client.publish(topic=topic, payload=text)