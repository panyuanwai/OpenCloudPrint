"""
OpenCloudPrint - 认证相关 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import httpx

from app.core.config import settings

router = APIRouter()


# ========== Request/Response Models ==========
class WechatLoginRequest(BaseModel):
    """微信登录请求"""
    code: str  # 微信小程序登录凭证


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    openid: str


# ========== API Endpoints ==========


@router.post("/wechat/login", response_model=LoginResponse)
async def wechat_login(request: WechatLoginRequest):
    """
    微信小程序登录

    通过微信小程序的 login code 获取用户 openid，
    并返回系统的 JWT access token
    """
    # 调用微信 API 获取 session
    async with httpx.AsyncClient() as client:
        wechat_url = f"{settings.WECHAT_LOGIN_URL}?appid={settings.WECHAT_APP_ID}&secret={settings.WECHAT_APP_SECRET}&js_code={request.code}&grant_type=authorization_code"
        response = await client.get(wechat_url)

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect to WeChat API"
        )

    data = response.json()

    if "errcode" in data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"WeChat API error: {data.get('errmsg')}"
        )

    openid = data.get("openid")
    session_key = data.get("session_key")

    # TODO: 实现 JWT token 生成逻辑
    # TODO: 创建或更新用户记录

    return LoginResponse(
        access_token="temp_token",  # 需要实现真实的 token 生成
        user_id=1,
        openid=openid
    )
