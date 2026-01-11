from __future__ import annotations
import json
import time
from typing import Optional

import paho.mqtt.client as mqtt

from src.common.settings import BROKER_HOST, BROKER_PORT

class MqttPublisher:
    def __init__(self, client_id: str, lwt_topic: str, lwt_payload: dict):
        self.client = mqtt.Client(client_id=client_id, clean_session=False)

        # Last Will: if client disconnects unexpectedly, broker publishes OFFLINE
        self.client.will_set(
            topic=lwt_topic,
            payload=json.dumps(lwt_payload),
            qos=1,
            retain=True,
        )

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

    def connect(self) -> None:
        self.client.connect(BROKER_HOST, BROKER_PORT, keepalive=30)
        self.client.loop_start()
        time.sleep(0.2)

    def publish(self, topic: str, payload: dict, qos: int = 0, retain: bool = False) -> None:
        self.client.publish(topic, json.dumps(payload), qos=qos, retain=retain)

    def close(self) -> None:
        self.client.loop_stop()
        self.client.disconnect()

    @staticmethod
    def _on_connect(client, userdata, flags, rc):
        # rc == 0 means success
        pass

    @staticmethod
    def _on_disconnect(client, userdata, rc):
        pass
