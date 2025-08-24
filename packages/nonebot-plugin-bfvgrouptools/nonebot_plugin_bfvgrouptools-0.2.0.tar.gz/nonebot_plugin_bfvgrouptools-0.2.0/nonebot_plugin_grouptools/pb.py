from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from typing import Any, Dict, Optional, Union

from .data import get_personid
from .utils import getpblist


# 封禁类型映射表
BanType = {
    '0': '',
    '1': 'BFBAN实锤或即将实锤',
    '2': 'ROBOT全局黑名单',
    '3': '自定义原因',
    '4': '',
    '5': '',
    '6': '',
    '7': '',
    '8': '',
    '9': '数据异常',
    '10': '',
    '11': '小电视屏蔽/踢人',
    '12': '',
    '13': '',
}


async def create_text_image_bytes(text: str, font_path: str, font_size: int) -> bytes:
    """
    创建包含文本的图片并返回PNG字节数据
    
    Args:
        text: 要渲染的文本内容
        font_path: 字体文件路径
        font_size: 字体大小
        
    Returns:
        图片的PNG字节数据
        
    Raises:
        FileNotFoundError: 当字体文件不存在时
        OSError: 当图片生成失败时
    """
    try:
        # 计算图片高度，每行高度为字体大小+10像素
        line_height = font_size + 10
        img_height = 100 + (len(text.split('\n')) + 1) * line_height
        
        # 创建黑色背景图片
        img = Image.new('RGBA', (800, img_height), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(font_path, font_size)

        y = 100  # 起始Y坐标
        for line in text.split('\n'):
            # 计算文本边界和居中位置
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (img.width - text_width) / 2
            
            # 绘制白色文本
            draw.text((x, y), line, fill=(255, 255, 255), font=font)
            y += bbox[3] - bbox[1] + 10  # 更新Y坐标

        # 转换为PNG字节数据
        with BytesIO() as byte_io:
            img.save(byte_io, format="PNG")
            return byte_io.getvalue()
    except FileNotFoundError as e:
        raise FileNotFoundError(f"字体文件未找到: {font_path}") from e
    except Exception as e:
        raise OSError(f"图片生成失败: {e}") from e


async def format_iso_time(time_str: str, fmt: str = "%Y年%m月%d日 %H:%M:%S") -> str:
    """
    将ISO时间字符串格式化为指定格式
    
    Args:
        time_str: ISO格式时间字符串
        fmt: 输出格式，默认为"YYYY年MM月DD日 HH:MM:SS"
        
    Returns:
        格式化后的时间字符串
        
    Raises:
        ValueError: 当时间字符串格式无效时
    """
    try:
        # 处理时区信息并解析时间
        dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        return dt.strftime(fmt)
    except ValueError as e:
        raise ValueError(f"无效的时间格式: {time_str}") from e


async def get_pblist(name: str) -> Union[Dict[str, Any], bytes]:
    """
    获取玩家封禁列表并生成图片
    
    Args:
        name: 玩家名称
        
    Returns:
        错误时返回包含错误信息的字典
        成功时返回封禁列表图片的字节数据
    """
    userdata = await get_personid(name)
    if "error" in userdata:
        return userdata
        
    personid = next(iter(userdata.values()))
    name = next(iter(userdata.keys()))
    pblist = await getpblist(personid)
    
    if not pblist or not pblist.get('data'):
        # 没有封禁记录的情况
        message = f"玩家 {name}({personid}) 没有封禁记录"
        try:
            return await create_text_image_bytes(
                text=message, 
                font_path="STXINWEI.TTF", 
                font_size=24
            )
        except Exception as e:
            return {"error": str(e)}
    
    # 生成封禁记录文本
    text_lines = []
    for idx, record in enumerate(pblist['data'], 1):
        ban_type = str(record.get('banType', ''))
        text_lines.extend([
            f"--- 第 {idx} 条封禁记录 ---",
            f"服务器: {record.get('serverName', '未知')}",
            f"封禁类型: {BanType.get(ban_type, '未知类型')} ({ban_type})",
            f"原因: {record.get('reason', '未知')}",
            f"时间: {await format_iso_time(record.get('createTime', ''))}",
            ""
        ])
    
    try:
        return await create_text_image_bytes(
            text="\n".join(text_lines),
            font_path="STXINWEI.TTF",
            font_size=24
        )
    except Exception as e:
        return {"error": str(e)}