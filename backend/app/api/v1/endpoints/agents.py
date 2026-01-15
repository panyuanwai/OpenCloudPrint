"""
OpenCloudPrint - 边缘 Agent 管理 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()


# ========== Request/Response Models ==========
class AgentRegisterRequest(BaseModel):
    """Agent 注册请求"""
    agent_name: str
    agent_version: str = "1.0.0"
    os_info: Optional[str] = None
    arch: Optional[str] = None


class AgentHeartbeatRequest(BaseModel):
    """Agent 心跳请求"""
    agent_id: str
    ip_address: Optional[str] = None


class AgentInfo(BaseModel):
    """Agent 信息"""
    agent_id: str
    agent_name: str
    agent_version: str
    os_info: Optional[str]
    status: str
    last_heartbeat: datetime


# ========== API Endpoints ==========


@router.post("/register")
async def register_agent(
    request: AgentRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Agent 注册

    边缘设备首次启动时调用，返回分配的 agent_id
    """
    # TODO: 生成 UUID 作为 agent_id
    # TODO: 创建 Agent 记录
    return {
        "agent_id": "generated-uuid",
        "message": "Agent registered successfully"
    }


@router.post("/heartbeat")
async def agent_heartbeat(
    request: AgentHeartbeatRequest,
    db: Session = Depends(get_db)
):
    """
    Agent 心跳

    边缘设备定期调用 (建议 30 秒一次)
    用于更新 Agent 在线状态和 IP 地址
    """
    # TODO: 更新 Agent 的 last_heartbeat 和 ip_address
    # TODO: 更新关联的 Printer 状态为 online
    return {"status": "ok"}


@router.get("/", response_model=List[AgentInfo])
async def list_agents(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取 Agent 列表 (管理后台使用)"""
    # TODO: 实现 Agent 列表查询逻辑
    return []


@router.get("/{agent_id}", response_model=AgentInfo)
async def get_agent(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """获取 Agent 详情"""
    # TODO: 实现 Agent 详情查询逻辑
    pass
