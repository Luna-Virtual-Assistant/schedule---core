import time
import os
from dotenv import load_dotenv

load_dotenv(override=True)


from .mqtt_client_connection import MqttClientConnection


def start():
    mqtt_client = MqttClientConnection(
        broker_ip=os.getenv("HOST"),
        port=int(os.getenv("PORT")),
        client_name=os.getenv("CLIENT_NAME"),
        keep_alive=int(os.getenv("KEEP_ALIVE"))
    )
    mqtt_client.start_connection()
    
    while True: 
        try:
            time.sleep(0.001)
        except KeyboardInterrupt:
            mqtt_client.end_connection()
            break