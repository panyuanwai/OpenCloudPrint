"""
OpenCloudPrint - 配置管理
使用 pydantic-settings 进行环境变量配置
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置类"""

    # ========== 数据库配置 ==========
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str = "ocp_db"
    MYSQL_USER: str = "ocp_user"
    MYSQL_PASSWORD: str = "ocp_pass"

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

    # ========== Redis 配置 ==========
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "redis_pass"
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self) -> str:
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # ========== MQTT 配置 ==========
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_USERNAME: str = "ocp_mqtt_user"
    MQTT_PASSWORD: str = "ocp_mqtt_pass"
    MQTT_QOS: int = 1

    @property
    def MQTT_BROKER_URL(self) -> str:
        return f"{self.MQTT_BROKER_HOST}:{self.MQTT_BROKER_PORT}"

    # MQTT 主题
    MQTT_TOPIC_CMD: str = "ocp/cmd/+"      # 云端 -> Agent 指令
    MQTT_TOPIC_STATUS: str = "ocp/status/+"  # Agent -> 云端 状态上报
    MQTT_TOPIC_HEARTBEAT: str = "ocp/heartbeat/+"  # Agent 心跳

    # ========== JWT 配置 ==========
    JWT_SECRET_KEY: str = "your-secret-key-change-this"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 天

    # ========== 文件存储配置 ==========
    UPLOAD_DIR: str = "/app/uploads"
    CONVERTED_DIR: str = "/app/converted"
    MAX_UPLOAD_SIZE: int = 52428800  # 50MB

    # ========== 微信小程序配置 ==========
    WECHAT_APP_ID: Optional[str] = None
    WECHAT_APP_SECRET: Optional[str] = None

    # 微信登录 API
    WECHAT_LOGIN_URL: str = "https://api.weixin.qq.com/sns/jscode2session"

    # ========== 环境配置 ==========
    ENVIRONMENT: str = "development"  # development | production
    LOG_LEVEL: str = "INFO"

    # ========== 应用配置 ==========
    APP_NAME: str = "OpenCloudPrint"
    APP_VERSION: str = "1.0.0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()
