import json
from typing import Dict, Any, Optional
from pathlib import Path
from nonebot.log import logger
from nonebot import require

require('nonebot_plugin_localstore')
import nonebot_plugin_localstore as store
from .utils import get_persona_id


# 获取插件数据文件路径
data_file = store.get_plugin_data_file("grouptools.json")
# 获取插件缓存文件路径
cache_file = store.get_plugin_cache_file("grouptools.json")


class Data:
    """处理插件持久化数据存储"""
    
    def __init__(self):
        """初始化数据存储"""
        self.players: Dict[str, Any] = {}
        self.data_file = data_file
        if not self.data_file.exists():
            self.data_file.parent.mkdir(exist_ok=True)
            self.save()
        else:
            self.load()

    def load(self) -> None:
        """从文件加载数据"""
        try:
            data = self.data_file.read_text('utf-8')
            self.players = json.loads(data)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f"加载数据文件失败: {e}")
            self.players = {}

    def save(self) -> None:
        """保存数据到文件"""
        try:
            data = json.dumps(self.players, ensure_ascii=False)
            self.data_file.write_text(data, 'utf-8')
        except (TypeError, IOError) as e:
            logger.error(f"保存数据文件失败: {e}")


class Cache:
    """处理插件缓存数据"""
    
    def __init__(self):
        """初始化缓存"""
        self.players: Dict[str, Any] = {}
        self.cache_file = cache_file
        if not self.cache_file.exists():
            self.cache_file.parent.mkdir(exist_ok=True)
            self.save()
        else:
            self.load()

    def load(self) -> None:
        """从文件加载缓存"""
        try:
            data = self.cache_file.read_text('utf-8')
            self.players = json.loads(data)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f"加载缓存文件失败: {e}")
            self.players = {}

    def save(self) -> None:
        """保存缓存到文件"""
        try:
            data = json.dumps(self.players, ensure_ascii=False)
            self.cache_file.write_text(data, 'utf-8')
        except (TypeError, IOError) as e:
            logger.error(f"保存缓存文件失败: {e}")


local_cache = Cache()


async def get_personid(name: str) -> Dict[str, Any]:
    """
    获取玩家ID，优先从缓存中读取
    
    Args:
        name: 玩家名称
        
    Returns:
        成功时返回包含玩家名称和ID的字典
        失败时返回包含错误信息的字典
    """
    name = name.strip().lower()
    if not name:
        return {"error": "1", "message": "Empty name"}
        
    # 检查缓存
    if name in local_cache.players:
        logger.debug(f"从缓存获取玩家ID: {name}")
        return {name: local_cache.players[name]}
    
    # 缓存中没有，从API获取
    logger.debug(f"缓存中没有玩家 {name} 的ID，从API获取")
    user_data = await get_persona_id(name)
    
    if "error" in user_data:
        return user_data
        
    if not user_data:
        return {"error": "1", "message": "Player not found"}
        
    # 更新缓存
    player_name = user_data.get("name")
    persona_id = user_data.get("personaId")
    if player_name and persona_id:
        local_cache.players[player_name.lower()] = persona_id
        local_cache.save()
        logger.debug(f"添加玩家 {player_name} 的ID到缓存: {persona_id}")
        return {player_name: persona_id}
        
    return {"error": "1", "message": "Invalid player data"}