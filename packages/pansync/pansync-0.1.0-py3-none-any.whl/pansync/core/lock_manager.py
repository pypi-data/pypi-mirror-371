#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分布式锁管理器

实现基于文件的分布式锁机制，防止多客户端同时操作。
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from loguru import logger

from ..utils.time_utils import get_beijing_time, datetime_to_timestamp, timestamp_to_datetime


class LockManager:
    """分布式锁管理器"""
    
    def __init__(self, config_manager, client_manager):
        """初始化锁管理器
        
        Args:
            config_manager: 配置管理器
            client_manager: 客户端管理器
        """
        self.config_manager = config_manager
        self.client_manager = client_manager
        self.lock_file_path = None
        self.current_lock: Optional[Dict] = None
        self.bypy_instance = None
    
    def set_bypy_instance(self, bypy_instance) -> None:
        """设置bypy实例
        
        Args:
            bypy_instance: bypy实例
        """
        self.bypy_instance = bypy_instance
        
        # 构建锁文件路径
        config_dir = self.config_manager.get('sync.paths.config_dir', '.config')
        self.lock_file_path = f"{config_dir}/lock.txt"
    
    def acquire_lock(self, operation: str = 'sync', timeout: Optional[int] = None) -> bool:
        """获取分布式锁
        
        Args:
            operation: 操作类型
            timeout: 锁超时时间（秒），None使用配置值
            
        Returns:
            是否成功获取锁
        """
        if self.bypy_instance is None:
            logger.error("bypy实例未设置")
            return False
        
        if timeout is None:
            timeout = self.config_manager.get('client.lock.timeout', 3600)
        
        max_retries = self.config_manager.get('client.lock.max_retries', 10)
        retry_interval = self.config_manager.get('client.lock.retry_interval', 30)
        
        client_id = self.client_manager.get_client_id()
        client_name = self.client_manager.get_client_name()
        
        logger.info(f"尝试获取分布式锁: {operation} (客户端: {client_name})")
        
        for attempt in range(max_retries):
            try:
                # 检查现有锁
                existing_lock = self._load_lock_file()
                
                if existing_lock:
                    # 检查锁是否过期
                    if self._is_lock_expired(existing_lock):
                        logger.info(f"发现过期锁，强制获取: {existing_lock.get('locked_by')}")
                        # 删除过期锁
                        self._delete_lock_file()
                    else:
                        # 检查是否是同一客户端的锁
                        if existing_lock.get('locked_by') == client_id:
                            logger.info("发现自己的锁，直接使用")
                            self.current_lock = existing_lock
                            return True
                        else:
                            # 锁被其他客户端持有
                            locked_by = existing_lock.get('locked_by', 'unknown')
                            expires_at = existing_lock.get('expires_at', 'unknown')
                            
                            logger.info(f"锁被其他客户端持有: {locked_by}, 过期时间: {expires_at}")
                            
                            if attempt < max_retries - 1:
                                logger.info(f"等待 {retry_interval} 秒后重试 ({attempt + 1}/{max_retries})")
                                time.sleep(retry_interval)
                                continue
                            else:
                                logger.error("获取锁失败，达到最大重试次数")
                                return False
                
                # 创建新锁
                current_time = get_beijing_time()
                expires_time = current_time + timedelta(seconds=timeout)
                
                lock_data = {
                    'locked_by': client_id,
                    'client_name': client_name,
                    'locked_at': current_time.isoformat(),
                    'expires_at': expires_time.isoformat(),
                    'operation': operation,
                    'version': '1.0'
                }
                
                # 尝试创建锁文件
                if self._create_lock_file(lock_data):
                    self.current_lock = lock_data
                    logger.info(f"分布式锁获取成功: {operation} (过期时间: {expires_time})")
                    return True
                else:
                    logger.warning(f"创建锁文件失败，重试 ({attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        time.sleep(retry_interval)
                        continue
                    else:
                        return False
                        
            except Exception as e:
                logger.error(f"获取锁时发生异常: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_interval)
                    continue
                else:
                    return False
        
        return False
    
    def release_lock(self) -> bool:
        """释放分布式锁
        
        Returns:
            是否成功释放锁
        """
        if self.current_lock is None:
            logger.warning("没有持有锁，无需释放")
            return True
        
        try:
            client_id = self.client_manager.get_client_id()
            
            # 验证锁的所有权
            if self.current_lock.get('locked_by') != client_id:
                logger.error(f"尝试释放不属于自己的锁: {self.current_lock.get('locked_by')}")
                return False
            
            # 删除锁文件
            if self._delete_lock_file():
                operation = self.current_lock.get('operation', 'unknown')
                logger.info(f"分布式锁释放成功: {operation}")
                self.current_lock = None
                return True
            else:
                logger.error("删除锁文件失败")
                return False
                
        except Exception as e:
            logger.error(f"释放锁时发生异常: {e}")
            return False
    
    def extend_lock(self, additional_seconds: int = 3600) -> bool:
        """延长锁的过期时间
        
        Args:
            additional_seconds: 延长的秒数，默认1小时
            
        Returns:
            是否成功延长锁
        """
        if self.current_lock is None:
            logger.warning("没有持有锁，无法延长")
            return False
        
        try:
            client_id = self.client_manager.get_client_id()
            
            # 验证锁的所有权
            if self.current_lock.get('locked_by') != client_id:
                logger.error(f"尝试延长不属于自己的锁: {self.current_lock.get('locked_by')}")
                return False
            
            # 计算新的过期时间
            current_time = get_beijing_time()
            new_expires_time = current_time + timedelta(seconds=additional_seconds)
            
            # 更新锁数据
            updated_lock = self.current_lock.copy()
            updated_lock['expires_at'] = new_expires_time.isoformat()
            updated_lock['last_extended'] = current_time.isoformat()
            
            # 更新锁文件
            if self._update_lock_file(updated_lock):
                self.current_lock = updated_lock
                logger.info(f"锁延长成功，新过期时间: {new_expires_time}")
                return True
            else:
                logger.error("更新锁文件失败")
                return False
                
        except Exception as e:
            logger.error(f"延长锁时发生异常: {e}")
            return False
    
    def is_lock_held(self) -> bool:
        """检查是否持有锁
        
        Returns:
            是否持有有效的锁
        """
        if self.current_lock is None:
            return False
        
        # 检查锁是否过期
        if self._is_lock_expired(self.current_lock):
            logger.warning("持有的锁已过期")
            self.current_lock = None
            return False
        
        return True
    
    def get_lock_info(self) -> Optional[Dict]:
        """获取当前锁信息
        
        Returns:
            锁信息字典，没有锁返回None
        """
        return self.current_lock.copy() if self.current_lock else None
    
    def _load_lock_file(self) -> Optional[Dict]:
        """从网盘加载锁文件
        
        Returns:
            锁数据字典，文件不存在或加载失败返回None
        """
        try:
            # 创建临时文件
            temp_file = "/tmp/pansync_lock.txt"
            
            # 尝试下载锁文件
            result = self.bypy_instance.download(self.lock_file_path, temp_file)
            
            if result == 0:  # 下载成功
                with open(temp_file, 'r', encoding='utf-8') as f:
                    lock_data = json.load(f)
                
                # 清理临时文件
                os.unlink(temp_file)
                
                logger.debug(f"锁文件加载成功: {lock_data.get('locked_by')}")
                return lock_data
            else:
                # 文件不存在或下载失败
                logger.debug("锁文件不存在或下载失败")
                return None
                
        except Exception as e:
            logger.debug(f"加载锁文件失败: {e}")
            return None
    
    def _create_lock_file(self, lock_data: Dict) -> bool:
        """创建锁文件
        
        Args:
            lock_data: 锁数据
            
        Returns:
            是否创建成功
        """
        try:
            # 再次检查是否已有锁文件（防止竞争条件）
            existing_lock = self._load_lock_file()
            if existing_lock and not self._is_lock_expired(existing_lock):
                logger.warning("检测到其他客户端刚刚创建了锁")
                return False
            
            # 创建临时文件
            temp_file = "/tmp/pansync_lock.txt"
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(lock_data, f, indent=2, ensure_ascii=False)
            
            # 确保远程配置目录存在
            config_dir = self.config_manager.get('sync.paths.config_dir', '.config')
            self.bypy_instance.mkdir(config_dir)
            
            # 上传锁文件
            result = self.bypy_instance.upload(temp_file, self.lock_file_path)
            
            # 清理临时文件
            os.unlink(temp_file)
            
            if result == 0:
                logger.debug("锁文件创建成功")
                return True
            else:
                logger.error(f"锁文件上传失败，错误码: {result}")
                return False
                
        except Exception as e:
            logger.error(f"创建锁文件失败: {e}")
            return False
    
    def _update_lock_file(self, lock_data: Dict) -> bool:
        """更新锁文件
        
        Args:
            lock_data: 更新的锁数据
            
        Returns:
            是否更新成功
        """
        try:
            # 创建临时文件
            temp_file = "/tmp/pansync_lock.txt"
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(lock_data, f, indent=2, ensure_ascii=False)
            
            # 上传更新的锁文件
            result = self.bypy_instance.upload(temp_file, self.lock_file_path)
            
            # 清理临时文件
            os.unlink(temp_file)
            
            if result == 0:
                logger.debug("锁文件更新成功")
                return True
            else:
                logger.error(f"锁文件更新失败，错误码: {result}")
                return False
                
        except Exception as e:
            logger.error(f"更新锁文件失败: {e}")
            return False
    
    def _delete_lock_file(self) -> bool:
        """删除锁文件
        
        Returns:
            是否删除成功
        """
        try:
            result = self.bypy_instance.remove(self.lock_file_path)
            
            if result == 0:
                logger.debug("锁文件删除成功")
                return True
            else:
                logger.warning(f"锁文件删除失败，错误码: {result}")
                # 即使删除失败也返回True，因为可能文件已经不存在
                return True
                
        except Exception as e:
            logger.error(f"删除锁文件失败: {e}")
            return False
    
    def _is_lock_expired(self, lock_data: Dict) -> bool:
        """检查锁是否过期
        
        Args:
            lock_data: 锁数据
            
        Returns:
            锁是否过期
        """
        try:
            expires_at_str = lock_data.get('expires_at')
            if not expires_at_str:
                logger.warning("锁数据中没有过期时间")
                return True
            
            # 解析过期时间
            from ..utils.time_utils import parse_iso_time
            expires_at = parse_iso_time(expires_at_str)
            current_time = get_beijing_time()
            
            is_expired = current_time >= expires_at
            
            if is_expired:
                logger.debug(f"锁已过期: {expires_at} < {current_time}")
            
            return is_expired
            
        except Exception as e:
            logger.error(f"检查锁过期时间失败: {e}")
            # 出错时认为锁已过期
            return True
    
    def __enter__(self):
        """上下文管理器入口"""
        if not self.acquire_lock():
            raise RuntimeError("获取分布式锁失败")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.release_lock()