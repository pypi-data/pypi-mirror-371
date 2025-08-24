#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步引擎

核心同步逻辑，协调各个组件完成文件同步。
"""

import os
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any

from loguru import logger

from .lock_manager import LockManager
from .index_manager import IndexManager
from .file_manager import FileManager
from ..config import ConfigManager, ClientManager
from ..utils.time_utils import get_beijing_time, format_time, get_next_sync_time
from ..utils.network_utils import NetworkUtils


class SyncEngine:
    """同步引擎"""
    
    def __init__(self, config_path: str = None):
        """初始化同步引擎
        
        Args:
            config_path: 配置文件路径
        """
        # 初始化组件
        self.config_manager = ConfigManager(config_path)
        self.client_manager = ClientManager(self.config_manager)
        self.index_manager = IndexManager(self.config_manager)
        self.lock_manager = LockManager(self.config_manager, self.client_manager)
        self.file_manager = FileManager(self.config_manager, self.index_manager)
        self.network_utils = NetworkUtils()
        
        # 状态管理
        self.is_running = False
        self.is_syncing = False
        self.last_sync_time: Optional[datetime] = None
        self.next_sync_time: Optional[datetime] = None
        self.sync_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # bypy实例
        self.bypy_instance = None
        
        # 回调函数
        self.progress_callback: Optional[Callable] = None
        self.status_callback: Optional[Callable] = None
        
        # 统计信息
        self.sync_stats = {
            'total_syncs': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'last_sync_duration': 0,
            'total_sync_time': 0
        }
    
    def initialize(self) -> bool:
        """初始化同步引擎
        
        Returns:
            是否初始化成功
        """
        try:
            logger.info("正在初始化同步引擎...")
            
            # 检查网络连接
            if not self.network_utils.check_internet_connection():
                logger.error("网络连接不可用")
                return False
            
            # 初始化bypy
            if not self._initialize_bypy():
                logger.error("bypy初始化失败")
                return False
            
            # 设置bypy实例到其他组件
            self.lock_manager.set_bypy_instance(self.bypy_instance)
            self.file_manager.set_bypy_instance(self.bypy_instance)
            
            # 注册客户端
            if not self.client_manager.register_client(self.bypy_instance):
                logger.warning("客户端注册失败，但继续运行")
            
            # 确保本地目录存在
            local_path = os.path.expanduser(self.config_manager.get('sync.paths.local_root'))
            os.makedirs(local_path, exist_ok=True)
            
            # 确保远程目录存在
            remote_path = self.config_manager.get('sync.paths.remote_root')
            self.bypy_instance.mkdir(remote_path)
            
            # 确保远程.pansync目录存在
            pansync_dir = self.config_manager.get('sync.paths.pansync_dir', '.pansync')
            self.bypy_instance.mkdir(pansync_dir)
            
            logger.info("同步引擎初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"初始化同步引擎失败: {e}")
            return False
    
    def start_daemon(self) -> bool:
        """启动守护进程模式
        
        Returns:
            是否启动成功
        """
        if self.is_running:
            logger.warning("同步引擎已在运行")
            return True
        
        if not self.initialize():
            return False
        
        self.is_running = True
        self.stop_event.clear()
        
        # 启动同步线程
        self.sync_thread = threading.Thread(target=self._daemon_loop, daemon=True)
        self.sync_thread.start()
        
        logger.info("同步引擎守护进程已启动")
        return True
    
    def stop_daemon(self) -> None:
        """停止守护进程"""
        if not self.is_running:
            logger.warning("同步引擎未在运行")
            return
        
        logger.info("正在停止同步引擎...")
        
        self.is_running = False
        self.stop_event.set()
        
        # 等待同步线程结束
        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=30)
        
        # 释放锁
        if self.lock_manager.is_lock_held():
            self.lock_manager.release_lock()
        
        logger.info("同步引擎已停止")
    
    def sync_once(self, force: bool = False) -> bool:
        """执行一次同步
        
        Args:
            force: 是否强制同步（忽略锁等限制）
            
        Returns:
            是否同步成功
        """
        if self.is_syncing:
            logger.warning("同步正在进行中")
            return False
        
        if not self.bypy_instance and not self.initialize():
            logger.error("同步引擎未初始化")
            return False
        
        self.is_syncing = True
        sync_start_time = time.time()
        
        try:
            logger.info("开始执行同步")
            
            # 更新状态
            if self.status_callback:
                self.status_callback("正在获取分布式锁...")
            
            # 获取分布式锁
            if not force and not self.lock_manager.acquire_lock('sync'):
                logger.error("无法获取分布式锁，同步取消")
                return False
            
            try:
                # 执行同步步骤
                success = self._perform_sync()
                
                # 更新统计信息
                sync_duration = time.time() - sync_start_time
                self.sync_stats['total_syncs'] += 1
                self.sync_stats['last_sync_duration'] = sync_duration
                self.sync_stats['total_sync_time'] += sync_duration
                
                if success:
                    self.sync_stats['successful_syncs'] += 1
                    self.last_sync_time = get_beijing_time()
                    logger.info(f"同步完成，耗时: {sync_duration:.1f}秒")
                else:
                    self.sync_stats['failed_syncs'] += 1
                    logger.error(f"同步失败，耗时: {sync_duration:.1f}秒")
                
                return success
                
            finally:
                # 释放分布式锁
                if not force:
                    self.lock_manager.release_lock()
        
        except Exception as e:
            logger.error(f"同步过程中发生异常: {e}")
            self.sync_stats['failed_syncs'] += 1
            return False
        
        finally:
            self.is_syncing = False
            
            # 更新状态
            if self.status_callback:
                self.status_callback("同步完成" if success else "同步失败")
    
    def _daemon_loop(self) -> None:
        """守护进程主循环"""
        logger.info("守护进程循环开始")
        
        # 计算下次同步时间
        self._calculate_next_sync_time()
        
        while self.is_running and not self.stop_event.is_set():
            try:
                current_time = get_beijing_time()
                
                # 检查是否需要同步
                if self.next_sync_time and current_time >= self.next_sync_time:
                    logger.info(f"定时同步触发: {format_time(current_time)}")
                    
                    # 执行同步
                    success = self.sync_once()
                    
                    # 计算下次同步时间
                    self._calculate_next_sync_time()
                    
                    if success and self.lock_manager.is_lock_held():
                        # 同步成功且持有锁，延长锁的过期时间
                        self.lock_manager.extend_lock()
                
                # 等待一段时间再检查
                check_interval = self.config_manager.get('sync.schedule.check_interval', 60)
                self.stop_event.wait(check_interval)
                
            except Exception as e:
                logger.error(f"守护进程循环中发生异常: {e}")
                # 等待一段时间后继续
                self.stop_event.wait(300)  # 5分钟
        
        logger.info("守护进程循环结束")
    
    def _perform_sync(self) -> bool:
        """执行同步操作
        
        Returns:
            是否同步成功
        """
        try:
            # 1. 扫描本地文件变更
            if self.status_callback:
                self.status_callback("正在扫描本地文件...")
            
            # 先扫描本地文件变更
            self.index_manager.scan_local_files()
            
            # 获取需要同步的文件
            changed_files = self.index_manager.get_changed_files()
            logger.info(f"发现 {len(changed_files)} 个文件变更")

            if not changed_files:
                logger.info("没有文件需要同步")
                return True

            # 2. 处理文件变更
            total_files = len(changed_files)
            processed_files = 0
            success_count = 0

            for file_index in changed_files:
                try:
                    if self.stop_event.is_set():
                        logger.info("收到停止信号，中断同步")
                        break
                    
                    # 更新进度
                    processed_files += 1
                    if self.progress_callback:
                        self.progress_callback(processed_files, total_files, f"处理文件: {file_index.path}")
                    
                    # 根据文件状态处理
                    if file_index.status == 'new' or file_index.status == 'modified':
                        # 上传文件
                        local_full_path = os.path.join(
                            os.path.expanduser(self.config_manager.get('sync.paths.local_root')),
                            file_index.path
                        )
                        
                        if self.file_manager.upload_file(local_full_path, file_index.remote_path):
                            success_count += 1
                            
                            # 延长锁的过期时间（用户要求的功能）
                            if self.lock_manager.is_lock_held():
                                self.lock_manager.extend_lock()
                        
                    elif file_index.status == 'deleted':
                        # 根据配置决定是否删除远程文件
                        delete_remote = self.config_manager.get('sync.behavior.delete_remote_on_local_delete', True)
                        
                        if delete_remote:
                            if self.file_manager.delete_remote_file(file_index.remote_path):
                                success_count += 1
                                # 从索引中移除
                                self.index_manager.remove_file_index(file_index.path)
                                
                                # 延长锁的过期时间
                                if self.lock_manager.is_lock_held():
                                    self.lock_manager.extend_lock()
                        else:
                            # 只标记为已同步
                            self.index_manager.mark_file_synced(file_index.path)
                            success_count += 1
                    
                except Exception as e:
                    logger.error(f"处理文件失败 {file_index.path}: {e}")
                    continue
            
            # 3. 保存索引
            self.index_manager.save()
            
            # 4. 同步索引文件到远程
            if self._sync_index_file():
                logger.debug("索引文件同步成功")
            else:
                logger.warning("索引文件同步失败")
            
            # 5. 更新客户端状态
            self.client_manager.update_client_status(self.bypy_instance, 'active')
            
            logger.info(f"同步完成: 处理 {processed_files} 个文件，成功 {success_count} 个")
            return success_count == processed_files
            
        except Exception as e:
            logger.error(f"执行同步时发生异常: {e}")
            return False
    
    def _sync_index_file(self) -> bool:
        """同步索引文件到远程
        
        Returns:
            是否同步成功
        """
        try:
            # 获取本地索引文件路径
            local_index_path = self.index_manager._get_index_file_path()
            
            if not os.path.exists(local_index_path):
                logger.debug("本地索引文件不存在，跳过同步")
                return True
            
            # 构建远程索引文件路径
            pansync_dir = self.config_manager.get('sync.paths.pansync_dir', '.pansync')
            remote_index_path = f"{pansync_dir}/.index.dat"
            
            # 确保远程.pansync目录存在
            self.bypy_instance.mkdir(pansync_dir)
            
            # 上传索引文件
            result = self.bypy_instance.upload(local_index_path, remote_index_path)
            
            if result == 0:
                logger.debug(f"索引文件上传成功: {remote_index_path}")
                return True
            else:
                logger.warning(f"索引文件上传失败: {remote_index_path}, 错误码: {result}")
                return False
                
        except Exception as e:
            logger.error(f"同步索引文件时发生异常: {e}")
            return False
    
    def _initialize_bypy(self) -> bool:
        """初始化bypy实例
        
        Returns:
            是否初始化成功
        """
        try:
            import bypy
            import os
            from pathlib import Path
            
            # 检查bypy配置文件是否存在
            bypy_config_path = self.config_manager.get('baidu.config_file', '~/.bypy/bypy.json')
            bypy_config_path = os.path.expanduser(bypy_config_path)
            
            if not os.path.exists(bypy_config_path):
                logger.error(f"bypy配置文件不存在: {bypy_config_path}")
                logger.error("请先运行 'bypy info' 命令进行授权，或确保已有有效的bypy token")
                return False
            
            # 创建bypy实例（bypy会自动加载~/.bypy/bypy.json中的token）
            self.bypy_instance = bypy.ByPy()
            
            # 测试连接
            logger.info("正在测试bypy连接...")
            result = self.bypy_instance.list('/')
            if result != 0:
                logger.error(f"bypy连接测试失败，错误码: {result}")
                logger.error("可能的原因：")
                logger.error("1. token已过期，请重新运行 'bypy info' 进行授权")
                logger.error("2. 网络连接问题")
                logger.error("3. 百度网盘服务异常")
                return False
            
            logger.info("bypy初始化成功")
            return True
            
        except ImportError:
            logger.error("bypy模块未安装，请运行: pip install bypy")
            return False
        except Exception as e:
            logger.error(f"初始化bypy失败: {e}")
            return False
    
    def _calculate_next_sync_time(self) -> None:
        """计算下次同步时间"""
        schedule_config = self.config_manager.get('sync.schedule', {})
        
        if not schedule_config.get('enabled', False):
            self.next_sync_time = None
            return
        
        current_time = get_beijing_time()
        
        # 获取同步间隔
        interval_minutes = schedule_config.get('interval_minutes', 60)
        
        if self.last_sync_time:
            # 基于上次同步时间计算
            self.next_sync_time = self.last_sync_time + timedelta(minutes=interval_minutes)
        else:
            # 首次同步，立即执行
            self.next_sync_time = current_time
        
        # 确保不早于当前时间
        if self.next_sync_time <= current_time:
            self.next_sync_time = current_time + timedelta(minutes=1)
        
        logger.info(f"下次同步时间: {format_time(self.next_sync_time)}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取同步引擎状态
        
        Returns:
            状态信息字典
        """
        return {
            'is_running': self.is_running,
            'is_syncing': self.is_syncing,
            'last_sync_time': format_time(self.last_sync_time) if self.last_sync_time else None,
            'next_sync_time': format_time(self.next_sync_time) if self.next_sync_time else None,
            'client_id': self.client_manager.get_client_id(),
            'client_name': self.client_manager.get_client_name(),
            'lock_held': self.lock_manager.is_lock_held(),
            'lock_info': self.lock_manager.get_lock_info(),
            'sync_stats': self.sync_stats.copy(),
            'file_stats': self.file_manager.get_statistics(),
            'index_stats': self.index_manager.get_statistics()
        }
    
    def set_progress_callback(self, callback: Callable) -> None:
        """设置进度回调函数
        
        Args:
            callback: 回调函数 (current, total, message)
        """
        self.progress_callback = callback
    
    def set_status_callback(self, callback: Callable) -> None:
        """设置状态回调函数
        
        Args:
            callback: 回调函数 (status_message)
        """
        self.status_callback = callback
    
    def force_sync(self) -> bool:
        """强制执行同步（忽略锁）
        
        Returns:
            是否同步成功
        """
        logger.warning("执行强制同步（忽略分布式锁）")
        return self.sync_once(force=True)
    
    def cleanup(self) -> None:
        """清理资源"""
        logger.info("正在清理同步引擎资源...")
        
        # 停止守护进程
        if self.is_running:
            self.stop_daemon()
        
        # 清理索引中的过期删除记录
        cleanup_days = self.config_manager.get('sync.cleanup.deleted_files_days', 30)
        if cleanup_days > 0:
            cleaned_count = self.index_manager.cleanup_deleted_files(cleanup_days)
            if cleaned_count > 0:
                logger.info(f"清理了 {cleaned_count} 个过期的删除记录")
        
        logger.info("同步引擎资源清理完成")
    
    def __enter__(self):
        """上下文管理器入口"""
        if not self.initialize():
            raise RuntimeError("同步引擎初始化失败")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup()