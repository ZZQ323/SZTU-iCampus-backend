"""
流式推送API端点
实现SSE (Server-Sent Events) 推送和增量同步
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from app.api.deps import get_current_user, get_optional_user
from app.core.events import event_queue, start_event_system

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/events")
async def stream_events(
    request: Request,
    current_user = Depends(get_current_user)
):
    """
    SSE事件流推送
    为登录用户提供实时事件推送
    """
    user_id = current_user["person_id"]
    
    async def event_generator():
        """事件流生成器"""
        connection = None
        try:
            # 订阅用户事件流
            connection = await event_queue.subscribe(user_id)
            logger.info(f"用户 {user_id} 开始接收事件流")
            
            # 发送连接成功消息
            yield {
                "event": "connected",
                "data": json.dumps({
                    "status": "connected",
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat()
                })
            }
            
            # 持续推送事件
            while True:
                try:
                    # 检查客户端是否断开连接
                    if await request.is_disconnected():
                        logger.info(f"用户 {user_id} 断开连接")
                        break
                    
                    # 等待事件（带超时的心跳机制）
                    try:
                        event_data = await asyncio.wait_for(connection.get(), timeout=30.0)
                        
                        # 推送事件
                        yield {
                            "event": event_data["event_type"],
                            "data": json.dumps(event_data)
                        }
                        
                    except asyncio.TimeoutError:
                        # 发送心跳
                        yield {
                            "event": "heartbeat",
                            "data": json.dumps({
                                "timestamp": datetime.now().isoformat()
                            })
                        }
                        
                except Exception as e:
                    logger.error(f"事件推送错误 {user_id}: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"事件流错误 {user_id}: {e}")
        finally:
            # 清理连接
            if connection:
                await event_queue.unsubscribe(user_id, connection)
            logger.info(f"用户 {user_id} 事件流结束")
    
    return EventSourceResponse(
        event_generator(),
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )

@router.get("/events/guest")
async def stream_public_events(request: Request):
    """
    公开事件流推送
    为未登录用户提供公开事件推送
    """
    
    async def public_event_generator():
        """公开事件流生成器"""
        connection = None
        try:
            # 使用特殊的guest用户ID
            guest_id = f"guest_{id(request)}"
            connection = await event_queue.subscribe(guest_id)
            logger.info(f"访客 {guest_id} 开始接收公开事件流")
            
            # 发送连接成功消息
            yield {
                "event": "connected",
                "data": json.dumps({
                    "status": "connected",
                    "user_type": "guest",
                    "timestamp": datetime.now().isoformat()
                })
            }
            
            # 持续推送公开事件
            while True:
                try:
                    if await request.is_disconnected():
                        logger.info(f"访客 {guest_id} 断开连接")
                        break
                    
                    try:
                        event_data = await asyncio.wait_for(connection.get(), timeout=60.0)
                        
                        # 只推送公开事件
                        if event_data.get("is_public", False):
                            yield {
                                "event": event_data["event_type"],
                                "data": json.dumps(event_data)
                            }
                        
                    except asyncio.TimeoutError:
                        # 访客心跳间隔更长
                        yield {
                            "event": "heartbeat",
                            "data": json.dumps({
                                "timestamp": datetime.now().isoformat()
                            })
                        }
                        
                except Exception as e:
                    logger.error(f"公开事件推送错误 {guest_id}: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"公开事件流错误: {e}")
        finally:
            if connection:
                await event_queue.unsubscribe(guest_id, connection)
                
    return EventSourceResponse(
        public_event_generator(),
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )

@router.get("/sync")
async def sync_events(
    since: str = Query(..., description="同步起始时间戳 (ISO格式)"),
    current_user = Depends(get_current_user)
):
    """
    增量事件同步
    用于断线重连时获取错过的事件
    """
    user_id = current_user["person_id"]
    
    try:
        # 获取指定时间之后的事件
        events = event_queue.get_events_since(user_id, since)
        
        logger.info(f"用户 {user_id} 增量同步: {len(events)} 个事件")
        
        return {
            "status": 0,
            "msg": "同步成功",
            "data": {
                "events": events,
                "sync_timestamp": datetime.now().isoformat(),
                "count": len(events)
            }
        }
        
    except Exception as e:
        logger.error(f"增量同步失败 {user_id}: {e}")
        raise HTTPException(status_code=500, detail="同步失败")

@router.get("/sync/guest")
async def sync_public_events(
    since: str = Query(..., description="同步起始时间戳 (ISO格式)")
):
    """
    公开事件增量同步
    为未登录用户提供公开事件同步
    """
    try:
        # 获取公开事件
        events = []
        since_time = datetime.fromisoformat(since.replace('Z', '+00:00'))
        
        for event in event_queue.global_queue:
            event_time = datetime.fromisoformat(event.timestamp)
            if event_time > since_time:
                events.append(event.to_dict())
        
        # 按时间排序
        events.sort(key=lambda x: x['timestamp'])
        
        logger.info(f"访客增量同步: {len(events)} 个公开事件")
        
        return {
            "status": 0,
            "msg": "同步成功",
            "data": {
                "events": events,
                "sync_timestamp": datetime.now().isoformat(),
                "count": len(events)
            }
        }
        
    except Exception as e:
        logger.error(f"公开事件同步失败: {e}")
        raise HTTPException(status_code=500, detail="同步失败")

@router.get("/status")
async def get_stream_status(
    current_user = Depends(get_optional_user)
):
    """
    获取推送系统状态
    """
    user_id = current_user["person_id"] if current_user else "guest"
    
    # 检查用户是否在线
    is_online = user_id in event_queue.subscribers
    
    # 获取未读事件数量
    unread_count = 0
    if current_user:
        unread_count = len(event_queue.queues[user_id])
    
    return {
        "status": 0,
        "msg": "获取状态成功",
        "data": {
            "user_id": user_id,
            "is_online": is_online,
            "unread_count": unread_count,
            "system_status": "running",
            "connected_users": len(event_queue.subscribers),
            "total_events": len(event_queue.global_queue)
        }
    } 