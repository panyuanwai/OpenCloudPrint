"""
OpenCloudPrint - 数据库连接配置
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings


# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 自动检测连接是否有效
    pool_recycle=3600,   # 连接回收时间 (秒)
    echo=settings.ENVIRONMENT == "development",  # 开发环境打印 SQL
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建模型基类
Base = declarative_base()


async def init_db():
    """初始化数据库表结构 (生产环境建议使用 Alembic 迁移)"""
    # 这里只是示例，生产环境建议使用 Alembic
    pass


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话 (依赖注入)

    用法:
        @app.get("/users")
        def read_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
