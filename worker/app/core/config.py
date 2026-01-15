"""
OpenCloudPrint Worker - 配置管理
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Worker 配置类"""

    # ========== Redis 配置 ==========
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "redis_pass"
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self) -> str:
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # ========== MySQL 配置 ==========
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str = "ocp_db"
    MYSQL_USER: str = "ocp_user"
    MYSQL_PASSWORD: str = "ocp_pass"

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

    # ========== MQTT 配置 ==========
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_USERNAME: str = "ocp_mqtt_user"
    MQTT_PASSWORD: str = "ocp_mqtt_pass"
    MQTT_QOS: int = 1

    # ========== 文件存储配置 ==========
    UPLOAD_DIR: str = "/app/uploads"
    CONVERTED_DIR: str = "/app/converted"

    # ========== 环境配置 ==========
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
