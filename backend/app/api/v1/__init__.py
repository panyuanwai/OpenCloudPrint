"""
OpenCloudPrint - API v1 路由聚合
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, printers, jobs, agents

api_router = APIRouter()

# 注册各模块路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(printers.router, prefix="/printers", tags=["打印机"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["打印任务"])
api_router.include_router(agents.router, prefix="/agents", tags=["Agent 管理"])
