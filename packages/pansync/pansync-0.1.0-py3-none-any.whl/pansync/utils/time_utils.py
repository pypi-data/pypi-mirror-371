#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时间工具模块

提供时间相关的工具函数，统一使用北京时间。
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Union

import pytz
from loguru import logger

# 北京时区
BEIJING_TZ = pytz.timezone('Asia/Shanghai')


def get_beijing_time() -> datetime:
    """获取当前北京时间
    
    Returns:
        北京时间的datetime对象
    """
    return datetime.now(BEIJING_TZ)


def to_beijing_time(dt: datetime) -> datetime:
    """将datetime对象转换为北京时间
    
    Args:
        dt: 要转换的datetime对象
        
    Returns:
        北京时间的datetime对象
    """
    if dt.tzinfo is None:
        # 如果没有时区信息，假设为UTC
        dt = dt.replace(tzinfo=pytz.UTC)
    
    return dt.astimezone(BEIJING_TZ)


def format_time(dt: datetime, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """格式化时间
    
    Args:
        dt: 要格式化的datetime对象
        format_str: 格式字符串
        
    Returns:
        格式化后的时间字符串
    """
    if dt.tzinfo is None:
        dt = to_beijing_time(dt)
    
    return dt.strftime(format_str)


def parse_time(time_str: str, format_str: str = '%Y-%m-%d %H:%M:%S') -> datetime:
    """解析时间字符串
    
    Args:
        time_str: 时间字符串
        format_str: 格式字符串
        
    Returns:
        北京时间的datetime对象
    """
    try:
        dt = datetime.strptime(time_str, format_str)
        return BEIJING_TZ.localize(dt)
    except ValueError as e:
        logger.error(f"时间解析失败: {time_str}, 格式: {format_str}, 错误: {e}")
        raise


def parse_iso_time(time_str: str) -> datetime:
    """解析ISO格式时间字符串
    
    Args:
        time_str: ISO格式时间字符串
        
    Returns:
        北京时间的datetime对象
    """
    try:
        # 处理不同的ISO格式
        if time_str.endswith('Z'):
            # UTC时间
            dt = datetime.fromisoformat(time_str[:-1] + '+00:00')
        elif '+' in time_str or time_str.count('-') > 2:
            # 带时区信息
            dt = datetime.fromisoformat(time_str)
        else:
            # 无时区信息，假设为北京时间
            dt = datetime.fromisoformat(time_str)
            return BEIJING_TZ.localize(dt)
        
        return to_beijing_time(dt)
        
    except ValueError as e:
        logger.error(f"ISO时间解析失败: {time_str}, 错误: {e}")
        raise


def timestamp_to_datetime(timestamp: Union[int, float]) -> datetime:
    """将时间戳转换为北京时间
    
    Args:
        timestamp: Unix时间戳
        
    Returns:
        北京时间的datetime对象
    """
    dt = datetime.fromtimestamp(timestamp, tz=pytz.UTC)
    return to_beijing_time(dt)


def datetime_to_timestamp(dt: datetime) -> float:
    """将datetime对象转换为时间戳
    
    Args:
        dt: datetime对象
        
    Returns:
        Unix时间戳
    """
    if dt.tzinfo is None:
        dt = BEIJING_TZ.localize(dt)
    
    return dt.timestamp()


def is_time_in_range(current_time: Optional[datetime] = None, 
                    start_time: str = '00:00', 
                    end_time: str = '23:59') -> bool:
    """检查当前时间是否在指定范围内
    
    Args:
        current_time: 要检查的时间，默认为当前北京时间
        start_time: 开始时间 (HH:MM格式)
        end_time: 结束时间 (HH:MM格式)
        
    Returns:
        是否在时间范围内
    """
    if current_time is None:
        current_time = get_beijing_time()
    
    try:
        # 解析时间
        start_hour, start_minute = map(int, start_time.split(':'))
        end_hour, end_minute = map(int, end_time.split(':'))
        
        current_minutes = current_time.hour * 60 + current_time.minute
        start_minutes = start_hour * 60 + start_minute
        end_minutes = end_hour * 60 + end_minute
        
        # 处理跨天的情况
        if start_minutes <= end_minutes:
            # 同一天内
            return start_minutes <= current_minutes <= end_minutes
        else:
            # 跨天
            return current_minutes >= start_minutes or current_minutes <= end_minutes
            
    except (ValueError, AttributeError) as e:
        logger.error(f"时间范围检查失败: {e}")
        return True  # 出错时默认允许


def get_next_sync_time(interval: int, 
                      start_time: str = '00:00', 
                      end_time: str = '23:59') -> Optional[datetime]:
    """获取下次同步时间
    
    Args:
        interval: 同步间隔（秒）
        start_time: 允许同步的开始时间
        end_time: 允许同步的结束时间
        
    Returns:
        下次同步时间，如果当前不在允许时间范围内则返回None
    """
    current_time = get_beijing_time()
    
    if not is_time_in_range(current_time, start_time, end_time):
        # 如果当前不在允许时间范围内，计算下次进入范围的时间
        try:
            start_hour, start_minute = map(int, start_time.split(':'))
            
            # 计算今天的开始时间
            today_start = current_time.replace(
                hour=start_hour, minute=start_minute, second=0, microsecond=0
            )
            
            if current_time < today_start:
                # 今天还没到开始时间
                return today_start
            else:
                # 今天已过开始时间，返回明天的开始时间
                tomorrow_start = today_start + timedelta(days=1)
                return tomorrow_start
                
        except ValueError:
            logger.error(f"无效的时间格式: {start_time}")
            return None
    
    # 在允许时间范围内，计算下次同步时间
    next_sync = current_time + timedelta(seconds=interval)
    
    # 检查下次同步时间是否还在允许范围内
    if is_time_in_range(next_sync, start_time, end_time):
        return next_sync
    else:
        # 如果超出范围，返回明天的开始时间
        try:
            start_hour, start_minute = map(int, start_time.split(':'))
            tomorrow_start = (current_time + timedelta(days=1)).replace(
                hour=start_hour, minute=start_minute, second=0, microsecond=0
            )
            return tomorrow_start
        except ValueError:
            return None


def format_duration(seconds: Union[int, float]) -> str:
    """格式化时长
    
    Args:
        seconds: 秒数
        
    Returns:
        格式化的时长字符串
    """
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f}小时"
    else:
        days = seconds / 86400
        return f"{days:.1f}天"


def get_file_age(file_path: str) -> Optional[timedelta]:
    """获取文件年龄
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件年龄，如果文件不存在返回None
    """
    try:
        import os
        if not os.path.exists(file_path):
            return None
        
        mtime = os.path.getmtime(file_path)
        file_time = timestamp_to_datetime(mtime)
        current_time = get_beijing_time()
        
        return current_time - file_time
        
    except Exception as e:
        logger.error(f"获取文件年龄失败: {file_path}, 错误: {e}")
        return None