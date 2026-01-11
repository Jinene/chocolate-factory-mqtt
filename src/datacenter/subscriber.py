from __future__ import annotations
import json
import paho.mqtt.client as mqtt

from src.common.settings import BROKER_HOST, BROKER_PORT
from src.datacenter.storage import init_db, store_message

SUBSCRIBE_FILTER = "factory/+/+/+/+/+"  # everything under factory

def on_connect(client, userdata, flags, rc):
    client.subscribe(SUBSCRIBE_FILTER, qos=1)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except Exception:
        payload = {"ts": None, "raw": msg.payload.decode("utf-8", errors="replace")}

    store_message(msg.topic, payload)
    print(f"[INGEST] {msg.topic} -> ts={payload.get('ts')}")

def main() -> None:
    init_db()

    client = mqtt.Client(client_id="datacenter-subscriber", clean_session=False)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER_HOST, BROKER_PORT, keepalive=30)
    client.loop_forever()

if __name__ == "__main__":
    main()

