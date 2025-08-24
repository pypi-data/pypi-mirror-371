from typing import Any, Dict, Optional, Union
from nonebot.log import logger
from aiocache import cached

from .utils import get_playerdata, get_ban_data, get_community_status
from .data import get_personid


# 封禁状态描述映射
status_descriptions = {
    0: "未处理", 
    1: "石锤", 
    2: "待自证", 
    3: "MOSS自证", 
    4: "无效举报",
    5: "讨论中", 
    6: "等待确认", 
    7: "空", 
    8: "刷枪", 
    9: "上诉", 
    'None': "无记录", 
    'null': "无记录",
}


async def communitystatus(name: str) -> str:
    """
    获取玩家社区状态信息
    
    Args:
        name: 玩家名称
        
    Returns:
        格式化的状态信息字符串
        
    Raises:
        返回错误信息字符串
    """
    userdata = await get_personid(name)
    if "error" in userdata:
        return userdata["message"]
        
    persona_id = next(iter(userdata.values()))
    playername = next(iter(userdata.keys()))
    
    # 获取封禁状态
    bandata = await get_ban_data(persona_id)
    ban_status = "无记录"
    has_ban_url = False
    
    if bandata and bandata.get("data"):
        status = bandata["data"].get("status")
        if status not in (None, 'null'):
            ban_status = status_descriptions.get(status, "未知状态")
            has_ban_url = True
    
    # 获取机器人服状态
    robotdata = await get_community_status(persona_id)
    robot_status = robotdata.get("data", {}).get("operationStatusName", "未知")
    robot_reason = robotdata.get("data", {}).get("reasonStatusName", "未知")
    
    # 构建返回信息
    base_info = f"EAID: {playername}\nPID: {persona_id}\n"
    ban_info = f"BFBAN状态: {ban_status}\n"
    robot_info = (
        f"机器人服游戏状态: {robot_status}\n"
        f"机器人服数据库状态: {robot_reason}"
    )
    
    if has_ban_url:
        return f"{base_info}{ban_info}{robot_info}\n————BFBAN链接————\nhttps://bfban.com/player/{persona_id}"
    return f"{base_info}{ban_info}{robot_info}"


async def player_infomation(user_name: str) -> str:
    """
    获取玩家完整信息并格式化输出
    
    Args:
        user_name: 玩家名称
        
    Returns:
        格式化的玩家信息字符串
        
    Raises:
        返回错误信息字符串
    """
    userdata = await get_playerdata(user_name)
    if "error" in userdata:
        return userdata["message"]
        
    # 提取玩家基础数据
    stats = {
        "等级": userdata.get('rank', '未知'),
        "命中率": userdata.get('accuracy', '未知'),
        "爆头率": userdata.get('headshots', '未知'),
        "KD": userdata.get('killDeath', '未知'),
        "KP": userdata.get('infantryKillsPerMinute', '未知')
    }
    
    # 格式化基础数据
    stats_str = "\n".join(f"{k}: {v}" for k, v in stats.items())
    
    # 获取社区状态
    community_status = await communitystatus(user_name)
    if isinstance(community_status, dict):
        return community_status
        
    return (
        f"欢迎来到本群组\n"
        f"查询到 {userdata.get('userName', '未知')} 的基础数据如下：\n"
        f"{stats_str}\n"
        f"{community_status}"
    )
