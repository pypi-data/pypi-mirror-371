"""
NoneBot 插件 - BFV群组工具
提供BFV玩家状态查询、自动加群、封禁查询等功能
"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv
from nonebot import on_request, on_notice, on_command, require
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    GroupRequestEvent,
    MessageEvent,
    Message,
    Bot,
    GroupIncreaseNoticeEvent,
    MessageSegment
)

require("nonebot_plugin_localstore")

from .player_status import communitystatus, player_infomation
from .data import Cache, get_personid
from .utils import get_playerdata
from .pb import get_pblist


# 初始化插件
cache = Cache()
load_dotenv()

# 从环境变量获取允许的群号
ALLOWED_GROUPS = set(map(int, os.getenv('ALLOWED_GROUPS', '').split(',')))

# 初始化事件处理器
request_matcher = on_request()
notice_matcher = on_notice()
requests: Dict[int, str] = {}  # 存储加群请求的临时数据

# 初始化命令处理器
banstatus = on_command("player", aliases={"玩家状态"}, priority=5, block=True)
playerpb = on_command("pb=", aliases={"屏蔽="}, priority=5, block=True)


@banstatus.handle()
async def handle_banstatus(
    bot: Bot, 
    event: MessageEvent, 
    arg: Message = CommandArg()
) -> None:
    """
    处理玩家状态查询命令
    
    Args:
        bot: Bot实例
        event: 消息事件
        arg: 命令参数
    """
    name = arg.extract_plain_text().strip()
    message = await communitystatus(name)
    await banstatus.finish(message)


@request_matcher.handle()
async def handle_intogroup(event: GroupRequestEvent, bot: Bot) -> None:
    """
    处理自动加群请求
    
    Args:
        event: 加群请求事件
        bot: Bot实例
    """
    if event.group_id not in ALLOWED_GROUPS:
        return
        
    try:
        # 解析玩家名称
        _, user_name = event.comment.split('\n')
        user_name = user_name.lstrip('答案：').strip()
        
        logger.debug(f"收到玩家 {user_name} 的加群申请")
        response = await get_personid(user_name)
        
        if "error" in response:
            reason = response.get("error", "未知错误")
            await _handle_join_error(event, bot, user_name, reason)
            return
            
        # 处理有效响应
        personid = next(iter(response.values()))
        user_name = next(iter(response.keys()))
        
        # 存储请求信息
        requests[event.user_id] = user_name
        cache.players[user_name] = personid
        cache.save()
        
        logger.debug(f"玩家 {user_name} 的personaid为 {personid}")
        
        # 检查玩家等级
        player_data = await get_playerdata(user_name)
        player_rank = player_data.get('rank')
        
        if player_rank and int(player_rank) > 0:
            await bot.set_group_add_request(
                flag=event.flag, 
                sub_type=event.sub_type, 
                approve=True
            )
        else:
            await bot.send_group_msg(
                group_id=event.group_id,
                message=(
                    f"收到QQ: {event.user_id} 的加群申请\n"
                    f"提供的ID为: {user_name}\n"
                    f"该玩家的等级为 {player_rank}\n"
                    "过滤该请求"
                )
            )
    except Exception as e:
        logger.error(f"处理加群请求时出错: {e}")
        await bot.send_group_msg(
            group_id=event.group_id,
            message=(
                f"处理QQ: {event.user_id} 的加群请求时出错\n"
                f"错误: {str(e)}"
            )
        )


async def _handle_join_error(
    event: GroupRequestEvent,
    bot: Bot,
    user_name: str,
    reason: str
) -> None:
    """
    处理加群请求错误
    
    Args:
        event: 加群请求事件
        bot: Bot实例
        user_name: 玩家名称
        reason: 错误原因
    """
    if reason == "1":
        await bot.set_group_add_request(
            flag=event.flag,
            sub_type=event.sub_type,
            approve=False,
            reason=f'未找到名为 {user_name} 的玩家！请检查输入是否正确。'
        )
        await bot.send_group_msg(
            group_id=event.group_id,
            message=(
                f"收到QQ: {event.user_id} 的加群申请\n"
                f"提供的ID为: {user_name}\n"
                "已自动拒绝 - 原因: 错误的ID"
            )
        )
    else:
        await bot.send_group_msg(
            group_id=event.group_id,
            message=(
                f"收到QQ: {event.user_id} 的加群申请\n"
                f"提供的ID为: {user_name}\n"
                "由于未知错误无法判断,请管理员手动处理\n"
                f"错误原因: {reason}"
            )
        )


@notice_matcher.handle()
async def handle_group_increase(
    event: GroupIncreaseNoticeEvent, 
    bot: Bot
) -> None:
    """
    处理入群通知
    
    Args:
        event: 群成员增加事件
        bot: Bot实例
    """
    if event.group_id not in ALLOWED_GROUPS:
        return
        
    if user_name := requests.pop(event.user_id, None):
        # 设置群名片
        await bot.set_group_card(
            group_id=event.group_id,
            user_id=event.user_id,
            card=user_name
        )
        
        # 发送欢迎消息
        player_info = await player_infomation(user_name)
        await notice_matcher.finish(
            f'欢迎新人加入！已自动修改您的群名片为游戏名称\n{player_info}',
            at_sender=True
        )
    else:
        await notice_matcher.finish(
            '未找到您的申请记录，请联系管理员。',
            at_sender=True
        )


@playerpb.handle()
async def handle_playerpb(
    bot: Bot, 
    event: MessageEvent, 
    arg: Message = CommandArg()
) -> None:
    """
    处理封禁列表查询命令
    
    Args:
        bot: Bot实例
        event: 消息事件
        arg: 命令参数
    """
    name = arg.extract_plain_text().strip()
    image = await get_pblist(name)
    
    if isinstance(image, dict) and "error" in image:
        await playerpb.finish(f"查询失败: {image.get('message', '未知错误')}")
    else:
        await bot.send(
            event,
            MessageSegment.image(image),
            reply_message=event.message,
            at_sender=True
        )