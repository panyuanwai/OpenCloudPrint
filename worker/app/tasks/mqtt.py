"""
OpenCloudPrint - MQTT 消息发布任务
"""
import json
from typing import Dict, Any

import paho.mqtt.client as mqtt

from app.tasks.celery_app import celery_app
from app.core.config import settings


@celery_app.task(name="app.tasks.mqtt.publish_print_command")
def publish_print_command(agent_id: str, payload: Dict[str, Any]) -> bool:
    """
    发布打印指令到 Agent

    MQTT Topic: ocp/cmd/{agent_id}

    Payload 格式:
    {
        "job_id": "uuid",
        "printer_name": "Printer Name",
        "file_url": "https://api.example.com/files/xxx.pdf",
        "copies": 1,
        "color_mode": "color",
        "duplex_mode": "simplex"
    }
    """
    try:
        client = mqtt.Client()
        client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
        client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, 60)

        topic = f"ocp/cmd/{agent_id}"
        message = json.dumps(payload)

        result = client.publish(topic, message, qos=settings.MQTT_QOS)

        client.disconnect()

        return result.rc == mqtt.MQTT_ERR_SUCCESS

    except Exception as e:
        print(f"MQTT publish error: {e}")
        return False


@celery_app.task(name="app.tasks.mqtt.publish_cancel_command")
def publish_cancel_command(agent_id: str, job_id: str) -> bool:
    """
    发布取消任务指令到 Agent

    MQTT Topic: ocp/cmd/{agent_id}

    Payload 格式:
    {
        "action": "cancel",
        "job_id": "uuid"
    }
    """
    try:
        client = mqtt.Client()
        client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
        client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, 60)

        topic = f"ocp/cmd/{agent_id}"
        message = json.dumps({"action": "cancel", "job_id": job_id})

        result = client.publish(topic, message, qos=settings.MQTT_QOS)

        client.disconnect()

        return result.rc == mqtt.MQTT_ERR_SUCCESS

    except Exception as e:
        print(f"MQTT publish error: {e}")
        return False
