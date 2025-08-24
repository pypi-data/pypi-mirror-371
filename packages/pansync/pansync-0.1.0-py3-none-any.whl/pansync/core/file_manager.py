#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件管理器

处理文件的上传、下载、删除等操作。
"""

import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from loguru import logger

from ..utils.time_utils import get_beijing_time, format_time
from ..utils.hash_utils import HashUtils
from ..utils.file_utils import FileUtils
from ..utils.network_utils import NetworkUtils


class FileManager:
    """文件管理器"""
    
    def __init__(self, config_manager, index_manager):
        """初始化文件管理器
        
        Args:
            config_manager: 配置管理器
            index_manager: 索引管理器
        """
        self.config_manager = config_manager
        self.index_manager = index_manager
        self.hash_utils = HashUtils()
        self.file_utils = FileUtils()
        self.network_utils = NetworkUtils()
        self.bypy_instance = None
        
        # 统计信息
        self.stats = {
            'uploaded_files': 0,
            'downloaded_files': 0,
            'deleted_files': 0,
            'uploaded_bytes': 0,
            'downloaded_bytes': 0,
            'errors': 0
        }
    
    def set_bypy_instance(self, bypy_instance) -> None:
        """设置bypy实例
        
        Args:
            bypy_instance: bypy实例
        """
        self.bypy_instance = bypy_instance
    
    def upload_file(self, local_path: str, remote_path: str, 
                   progress_callback=None) -> bool:
        """上传文件到百度网盘
        
        Args:
            local_path: 本地文件路径
            remote_path: 远程文件路径
            progress_callback: 进度回调函数
            
        Returns:
            是否上传成功
        """
        if self.bypy_instance is None:
            logger.error("bypy实例未设置")
            return False
        
        if not os.path.exists(local_path):
            logger.error(f"本地文件不存在: {local_path}")
            return False
        
        try:
            # 获取文件信息
            file_size = os.path.getsize(local_path)
            rel_path = os.path.relpath(local_path, 
                                     os.path.expanduser(self.config_manager.get('sync.paths.local_root')))
            
            logger.info(f"开始上传文件: {rel_path} ({self.network_utils.format_size(file_size)})")
            
            # 确保远程目录存在
            remote_dir = os.path.dirname(remote_path)
            if remote_dir and remote_dir != '/':
                self.bypy_instance.mkdir(remote_dir)
            
            # 执行上传
            start_time = time.time()
            
            if progress_callback:
                # 使用进度回调的上传方式
                result = self._upload_with_progress(local_path, remote_path, progress_callback)
            else:
                # 直接上传
                result = self.bypy_instance.upload(local_path, remote_path)
            
            upload_time = time.time() - start_time
            
            if result == 0:
                # 上传成功
                upload_speed = file_size / upload_time if upload_time > 0 else 0
                
                logger.info(f"文件上传成功: {rel_path} "
                          f"(耗时: {upload_time:.1f}s, 速度: {self.network_utils.format_speed(upload_speed)})")
                
                # 更新统计
                self.stats['uploaded_files'] += 1
                self.stats['uploaded_bytes'] += file_size
                
                # 更新索引
                file_stat = os.stat(local_path)
                hash_value = self.hash_utils.hash_file(local_path)
                
                self.index_manager.update_file_index(
                    rel_path,
                    size=file_size,
                    mtime=file_stat.st_mtime,
                    hash_value=hash_value,
                    status='synced',
                    remote_path=remote_path
                )
                
                return True
            else:
                logger.error(f"文件上传失败: {rel_path}, 错误码: {result}")
                self.stats['errors'] += 1
                return False
                
        except Exception as e:
            logger.error(f"上传文件时发生异常: {local_path} -> {remote_path}, {e}")
            self.stats['errors'] += 1
            return False
    
    def download_file(self, remote_path: str, local_path: str, 
                     progress_callback=None) -> bool:
        """从百度网盘下载文件
        
        Args:
            remote_path: 远程文件路径
            local_path: 本地文件路径
            progress_callback: 进度回调函数
            
        Returns:
            是否下载成功
        """
        if self.bypy_instance is None:
            logger.error("bypy实例未设置")
            return False
        
        try:
            # 确保本地目录存在
            local_dir = os.path.dirname(local_path)
            os.makedirs(local_dir, exist_ok=True)
            
            rel_path = os.path.relpath(local_path, 
                                     os.path.expanduser(self.config_manager.get('sync.paths.local_root')))
            
            logger.info(f"开始下载文件: {rel_path}")
            
            # 执行下载
            start_time = time.time()
            
            if progress_callback:
                # 使用进度回调的下载方式
                result = self._download_with_progress(remote_path, local_path, progress_callback)
            else:
                # 直接下载
                result = self.bypy_instance.download(remote_path, local_path)
            
            download_time = time.time() - start_time
            
            if result == 0 and os.path.exists(local_path):
                # 下载成功
                file_size = os.path.getsize(local_path)
                download_speed = file_size / download_time if download_time > 0 else 0
                
                logger.info(f"文件下载成功: {rel_path} "
                          f"({self.network_utils.format_size(file_size)}, "
                          f"耗时: {download_time:.1f}s, 速度: {self.network_utils.format_speed(download_speed)})")
                
                # 更新统计
                self.stats['downloaded_files'] += 1
                self.stats['downloaded_bytes'] += file_size
                
                # 更新索引
                file_stat = os.stat(local_path)
                hash_value = self.hash_utils.hash_file(local_path)
                
                self.index_manager.update_file_index(
                    rel_path,
                    size=file_size,
                    mtime=file_stat.st_mtime,
                    hash_value=hash_value,
                    status='synced',
                    remote_path=remote_path
                )
                
                return True
            else:
                logger.error(f"文件下载失败: {rel_path}, 错误码: {result}")
                self.stats['errors'] += 1
                return False
                
        except Exception as e:
            logger.error(f"下载文件时发生异常: {remote_path} -> {local_path}, {e}")
            self.stats['errors'] += 1
            return False
    
    def move_to_remote_trash(self, remote_path: str) -> bool:
        """将远程文件移动到.trash目录
        
        Args:
            remote_path: 远程文件路径
            
        Returns:
            是否移动成功
        """
        if self.bypy_instance is None:
            logger.error("bypy实例未设置")
            return False
        
        try:
            # 获取trash目录配置
            trash_dir = self.config_manager.get('sync.paths.trash_dir', '.trash')
            
            # 构建trash文件路径
            # 如果remote_path以/开头，去掉开头的/
            clean_remote_path = remote_path.lstrip('/')
            # 如果trash_dir以.开头，保持原样；否则确保以/开头
            if trash_dir.startswith('.'):
                trash_path = f"/{trash_dir}/{clean_remote_path}".replace('//', '/')
                trash_base_dir = f"/{trash_dir}".replace('//', '/')
            else:
                trash_path = f"/{trash_dir.lstrip('/')}/{clean_remote_path}".replace('//', '/')
                trash_base_dir = f"/{trash_dir.lstrip('/')}".replace('//', '/')
            
            logger.info(f"将远程文件移动到trash: {remote_path} -> {trash_path}")
            
            # 确保远程trash目录存在
            self._ensure_remote_directory(trash_base_dir)
            
            # 确保trash子目录存在
            trash_subdir = os.path.dirname(trash_path)
            if trash_subdir and trash_subdir != trash_base_dir:
                self._ensure_remote_directory(trash_subdir)
            
            # 如果trash中已存在同名文件，添加时间戳
            if self._remote_file_exists(trash_path):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                name, ext = os.path.splitext(trash_path)
                trash_path = f"{name}_{timestamp}{ext}"
            
            # 移动文件（通过复制+删除实现）
            # 先下载到临时位置
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                # 下载原文件
                download_result = self.bypy_instance.download(remote_path, temp_path)
                if download_result != 0:
                    logger.error(f"下载远程文件失败: {remote_path}, 错误码: {download_result}")
                    return False
                
                # 上传到trash位置
                upload_result = self.bypy_instance.upload(temp_path, trash_path)
                if upload_result != 0:
                    logger.error(f"上传到trash失败: {trash_path}, 错误码: {upload_result}")
                    return False
                
                # 删除原文件
                remove_result = self.bypy_instance.remove(remote_path)
                if remove_result != 0:
                    logger.error(f"删除原文件失败: {remote_path}, 错误码: {remove_result}")
                    # 尝试删除已上传的trash文件
                    self.bypy_instance.remove(trash_path)
                    return False
                
                logger.info(f"远程文件已移动到trash: {remote_path} -> {trash_path}")
                self.stats['deleted_files'] += 1
                return True
                
            finally:
                # 清理临时文件
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                
        except Exception as e:
            logger.error(f"移动远程文件到trash时发生异常: {remote_path}, {e}")
            self.stats['errors'] += 1
            return False
    
    def delete_remote_file(self, remote_path: str) -> bool:
        """删除远程文件（移动到trash）
        
        Args:
            remote_path: 远程文件路径
            
        Returns:
            是否删除成功
        """
        # 使用trash功能代替直接删除
        return self.move_to_remote_trash(remote_path)
    
    # 本地trash功能已移除，因为只使用远程trash
    
    # restore_from_trash方法已移除，因为只使用远程trash
    
    # list_trash_files方法已移除，因为只使用远程trash
    
    # clean_trash方法已移除，因为只使用远程trash
    
    def _upload_with_progress(self, local_path: str, remote_path: str, 
                             progress_callback) -> int:
        """带进度回调的上传
        
        Args:
            local_path: 本地文件路径
            remote_path: 远程文件路径
            progress_callback: 进度回调函数
            
        Returns:
            上传结果码
        """
        # 这里可以实现更详细的进度跟踪
        # 目前先使用基本的上传方式
        file_size = os.path.getsize(local_path)
        
        if progress_callback:
            progress_callback(0, file_size, "开始上传")
        
        result = self.bypy_instance.upload(local_path, remote_path)
        
        if progress_callback:
            if result == 0:
                progress_callback(file_size, file_size, "上传完成")
            else:
                progress_callback(0, file_size, f"上传失败: {result}")
        
        return result
    
    def _ensure_remote_directory(self, remote_dir: str) -> bool:
        """确保远程目录存在
        
        Args:
            remote_dir: 远程目录路径
            
        Returns:
            是否成功
        """
        try:
            # 使用bypy的mkdir命令创建目录
            result = self.bypy_instance.mkdir(remote_dir)
            # 返回码0表示成功，或者目录已存在也算成功
            return result == 0 or result == 31061  # 31061表示目录已存在
        except Exception as e:
            logger.debug(f"创建远程目录失败: {remote_dir}, {e}")
            return False
    
    def _remote_file_exists(self, remote_path: str) -> bool:
        """检查远程文件是否存在
        
        Args:
            remote_path: 远程文件路径
            
        Returns:
            文件是否存在
        """
        try:
            # 使用bypy的list命令检查文件是否存在
            result = self.bypy_instance.list(remote_path)
            return result == 0
        except Exception:
            return False
    
    def _download_with_progress(self, remote_path: str, local_path: str, 
                               progress_callback) -> int:
        """带进度回调的下载
        
        Args:
            remote_path: 远程文件路径
            local_path: 本地文件路径
            progress_callback: 进度回调函数
            
        Returns:
            下载结果码
        """
        # 这里可以实现更详细的进度跟踪
        # 目前先使用基本的下载方式
        if progress_callback:
            progress_callback(0, 0, "开始下载")
        
        result = self.bypy_instance.download(remote_path, local_path)
        
        if progress_callback:
            if result == 0 and os.path.exists(local_path):
                file_size = os.path.getsize(local_path)
                progress_callback(file_size, file_size, "下载完成")
            else:
                progress_callback(0, 0, f"下载失败: {result}")
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取文件操作统计信息
        
        Returns:
            统计信息字典
        """
        return self.stats.copy()
    
    def reset_statistics(self) -> None:
        """重置统计信息"""
        self.stats = {
            'uploaded_files': 0,
            'downloaded_files': 0,
            'deleted_files': 0,
            'uploaded_bytes': 0,
            'downloaded_bytes': 0,
            'errors': 0
        }
        logger.info("文件操作统计信息已重置")
    
    def verify_file_integrity(self, local_path: str, expected_hash: str = None) -> bool:
        """验证文件完整性
        
        Args:
            local_path: 本地文件路径
            expected_hash: 期望的哈希值，None表示从索引获取
            
        Returns:
            文件是否完整
        """
        if not os.path.exists(local_path):
            return False
        
        try:
            if expected_hash is None:
                # 从索引获取期望的哈希值
                local_base = os.path.expanduser(self.config_manager.get('sync.paths.local_root'))
                rel_path = os.path.relpath(local_path, local_base)
                file_index = self.index_manager.get_file_index(rel_path)
                
                if file_index is None or not file_index.hash_value:
                    logger.warning(f"无法获取文件的期望哈希值: {rel_path}")
                    return False
                
                expected_hash = file_index.hash_value
            
            # 计算当前文件哈希值
            current_hash = self.hash_utils.hash_file(local_path)
            
            is_valid = current_hash == expected_hash
            
            if not is_valid:
                logger.warning(f"文件完整性验证失败: {local_path}")
                logger.debug(f"期望哈希: {expected_hash}")
                logger.debug(f"实际哈希: {current_hash}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"验证文件完整性时发生异常: {local_path}, {e}")
            return False