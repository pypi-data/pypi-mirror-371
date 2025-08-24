from typing import Any, Dict, Optional
import httpx
from aiocache import cached


async def fetch_json(url: str, timeout: int = 20) -> Optional[Dict[str, Any]]:
    """
    异步请求JSON数据
    
    Args:
        url: 请求的URL地址
        timeout: 请求超时时间(秒)，默认20秒
        
    Returns:
        成功时返回JSON数据字典，失败时返回包含错误信息的字典
        
    Raises:
        httpx.RequestError: 当请求发生错误时抛出
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=timeout)
            if response.status_code == 200:
                return response.json()
            return {
                "error": f"请求失败，状态码: {response.status_code}",
                "details": response.text
            }
    except httpx.RequestError as e:
        return {"error": f"请求发生错误", "details": str(e)}


@cached(ttl=600)
async def get_playerdata(playername: str) -> Optional[Dict[str, Any]]:
    """
    获取玩家游戏数据
    
    Args:
        playername: 玩家名称
        
    Returns:
        包含玩家游戏数据的字典，或包含错误信息的字典
    """
    server_url = (
        f"https://api.gametools.network/bfv/stats/"
        f"?format_values=true&name={playername}&platform=pc"
        f"&skip_battlelog=false&lang=zh-cn"
    )
    return await fetch_json(server_url)


async def get_persona_id(username: str) -> Optional[Dict[str, Any]]:
    """
    通过玩家名称获取玩家ID
    
    Args:
        username: 玩家名称
        
    Returns:
        成功时返回包含personaId和name的字典
        失败时返回包含错误信息的字典
        
    Error Codes:
        1: 玩家不存在
        2: API请求错误
    """
    url = f"https://api.bfvrobot.net/api/v2/bfv/checkPlayer?name={username}"
    try:
        user_data = await fetch_json(url)
        
        # 处理空响应或无效数据
        if not user_data:
            return {"error": "1", "message": "玩家不存在"}
            
        # 处理成功响应
        if user_data.get("status") == 1:
            data = user_data.get("data", {})
            if not data:
                return {"error": "1", "message": "玩家不存在"}
                
            return {
                "personaId": data.get("personaId"),
                "name": data.get("name")
            }
            
        # 处理其他情况
        return {"error": "1", "message": "玩家不存在"}
        
    except Exception as e:
        return {"error": "2", "message": f"API请求错误: {str(e)}"}


@cached(ttl=600)
async def get_ban_data(person_id: str) -> Optional[Dict[str, Any]]:
    """
    获取玩家封禁状态
    
    Args:
        person_id: 玩家ID
        
    Returns:
        包含封禁状态数据的字典
    """
    url = f"https://api.bfban.com/api/player?personaId={person_id}"
    return await fetch_json(url)


@cached(ttl=600)
async def get_community_status(persona_id: str) -> Optional[Dict[str, Any]]:
    """
    获取玩家在社区的状态
    
    Args:
        persona_id: 玩家ID
        
    Returns:
        包含社区状态数据的字典
    """
    url = f"https://api.bfvrobot.net/api/player/getCommunityStatus?personaId={persona_id}"
    return await fetch_json(url)


async def getpblist(personid: str) -> Optional[Dict[str, Any]]:
    """
    获取玩家封禁记录
    
    Args:
        personid: 玩家ID
        
    Returns:
        包含封禁记录数据的字典
    """
    url = f"https://api.bfvrobot.net/api/player/getBannedLogsByPersonaId?personaId={personid}"
    return await fetch_json(url)