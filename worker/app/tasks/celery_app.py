"""
OpenCloudPrint - Celery 应用配置
"""
from celery import Celery

from app.core.config import settings

# 创建 Celery 应用
celery_app = Celery(
    "ocp_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.conversion", "app.tasks.mqtt"]
)

# Celery 配置
celery_app.conf.update(
    # 任务结果过期时间 (秒)
    result_expires=3600,
    # 任务序列化方式
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # 时区设置
    timezone="Asia/Shanghai",
    enable_utc=True,
    # 任务路由
    task_routes={
        "app.tasks.conversion.convert_document": {"queue": "conversion"},
        "app.tasks.mqtt.publish_print_command": {"queue": "mqtt"},
    },
    # Worker 并发数
    worker_concurrency=2,
    # 任务执行时间限制 (秒)
    task_time_limit=300,
    task_soft_time_limit=280,
)
