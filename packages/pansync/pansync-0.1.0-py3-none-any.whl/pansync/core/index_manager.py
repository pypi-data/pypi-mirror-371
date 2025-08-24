#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件索引管理器

管理本地文件索引，跟踪文件状态和变更。
"""

import json
import os
import pickle
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

from loguru import logger

from ..utils.time_utils import get_beijing_time, format_time
from ..utils.hash_utils import HashUtils
from ..utils.file_utils import FileUtils


class FileIndex:
    """文件索引项"""
    
    def __init__(self, path: str, size: int = 0, mtime: float = 0, 
                 hash_value: str = '', sync_time: Optional[datetime] = None,
                 status: str = 'unknown', remote_path: str = ''):
        """初始化文件索引项
        
        Args:
            path: 本地文件路径
            size: 文件大小
            mtime: 修改时间戳
            hash_value: 文件哈希值
            sync_time: 同步时间
            status: 文件状态 (synced, modified, new, deleted)
            remote_path: 远程文件路径
        """
        self.path = path
        self.size = size
        self.mtime = mtime
        self.hash_value = hash_value
        self.sync_time = sync_time or get_beijing_time()
        self.status = status
        self.remote_path = remote_path
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'path': self.path,
            'size': self.size,
            'mtime': self.mtime,
            'hash_value': self.hash_value,
            'sync_time': self.sync_time.isoformat() if self.sync_time else None,
            'status': self.status,
            'remote_path': self.remote_path
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileIndex':
        """从字典创建"""
        from ..utils.time_utils import parse_iso_time
        
        sync_time = None
        if data.get('sync_time'):
            sync_time = parse_iso_time(data['sync_time'])
        
        return cls(
            path=data.get('path', ''),
            size=data.get('size', 0),
            mtime=data.get('mtime', 0),
            hash_value=data.get('hash_value', ''),
            sync_time=sync_time,
            status=data.get('status', 'unknown'),
            remote_path=data.get('remote_path', '')
        )
    
    def is_modified(self, current_size: int, current_mtime: float) -> bool:
        """检查文件是否被修改
        
        Args:
            current_size: 当前文件大小
            current_mtime: 当前修改时间
            
        Returns:
            文件是否被修改
        """
        return self.size != current_size or abs(self.mtime - current_mtime) > 1
    
    def __str__(self) -> str:
        return f"FileIndex(path={self.path}, status={self.status}, size={self.size})"


class IndexManager:
    """文件索引管理器"""
    
    def __init__(self, config_manager):
        """初始化索引管理器
        
        Args:
            config_manager: 配置管理器
        """
        self.config_manager = config_manager
        self.index_file_path = None
        self.index_data: Dict[str, FileIndex] = {}
        self.hash_utils = HashUtils()
        self.file_utils = FileUtils()
        self._load_index()
    
    def _get_index_file_path(self) -> str:
        """获取索引文件路径"""
        if self.index_file_path is None:
            local_path = self.config_manager.get('sync.paths.local_root', '~/tmp/pansync')
            local_path = os.path.expanduser(local_path)
            self.index_file_path = os.path.join(local_path, '.index.dat')
        return self.index_file_path
    
    def _load_index(self) -> None:
        """加载索引文件"""
        index_file = self._get_index_file_path()
        
        try:
            if os.path.exists(index_file):
                # 尝试加载二进制格式（pickle）
                try:
                    with open(index_file, 'rb') as f:
                        data = pickle.load(f)
                        if isinstance(data, dict):
                            # 转换为FileIndex对象
                            for path, item_data in data.items():
                                if isinstance(item_data, dict):
                                    self.index_data[path] = FileIndex.from_dict(item_data)
                                elif isinstance(item_data, FileIndex):
                                    self.index_data[path] = item_data
                            logger.info(f"索引文件加载成功: {len(self.index_data)} 个文件")
                            return
                except (pickle.UnpicklingError, EOFError):
                    logger.warning("二进制索引文件损坏，尝试JSON格式")
                
                # 尝试加载JSON格式（兼容性）
                try:
                    with open(index_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        for path, item_data in data.items():
                            self.index_data[path] = FileIndex.from_dict(item_data)
                        logger.info(f"JSON索引文件加载成功: {len(self.index_data)} 个文件")
                        # 转换为二进制格式保存
                        self._save_index()
                        return
                except (json.JSONDecodeError, KeyError):
                    logger.warning("JSON索引文件也损坏，创建新索引")
            
            # 创建新索引
            self.index_data = {}
            logger.info("创建新的文件索引")
            
        except Exception as e:
            logger.error(f"加载索引文件失败: {e}")
            self.index_data = {}
    
    def _save_index(self) -> bool:
        """保存索引文件
        
        Returns:
            是否保存成功
        """
        index_file = self._get_index_file_path()
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(index_file), exist_ok=True)
            
            # 转换为字典格式
            data = {}
            for path, file_index in self.index_data.items():
                data[path] = file_index.to_dict()
            
            # 保存为二进制格式（更快）
            with open(index_file, 'wb') as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            logger.debug(f"索引文件保存成功: {len(self.index_data)} 个文件")
            return True
            
        except Exception as e:
            logger.error(f"保存索引文件失败: {e}")
            return False
    
    def scan_local_files(self, force_hash: bool = False) -> List[str]:
        """扫描本地文件
        
        Args:
            force_hash: 是否强制重新计算哈希值
            
        Returns:
            发生变更的文件路径列表
        """
        local_path = self.config_manager.get('sync.paths.local_root', '~/tmp/pansync')
        local_path = os.path.expanduser(local_path)
        
        if not os.path.exists(local_path):
            logger.warning(f"本地同步目录不存在: {local_path}")
            return []
        
        logger.info(f"开始扫描本地文件: {local_path}")
        
        # 获取过滤规则
        ignore_patterns = self.config_manager.get('sync.filters.ignore_patterns', [])
        ignore_dirs = self.config_manager.get('sync.filters.ignore_dirs', [])
        max_file_size = self.config_manager.get('sync.filters.max_file_size', None)
        
        # 扫描文件
        current_files = set()
        changed_files = []
        
        try:
            # 先找到所有文件
            all_files = list(self.file_utils.find_files(local_path, recursive=True))
            
            # 应用过滤规则
            filtered_files = self.file_utils.filter_files(
                all_files,
                ignore_patterns=ignore_patterns,
                ignore_dirs=ignore_dirs,
                max_size=max_file_size
            )
            
            for file_path in filtered_files:
                # 获取相对路径
                rel_path = os.path.relpath(file_path, local_path)
                current_files.add(rel_path)
                
                # 获取文件信息
                try:
                    stat = os.stat(file_path)
                    current_size = stat.st_size
                    current_mtime = stat.st_mtime
                    
                    # 检查是否在索引中
                    if rel_path in self.index_data:
                        file_index = self.index_data[rel_path]
                        
                        # 检查是否修改
                        if file_index.is_modified(current_size, current_mtime) or force_hash:
                            # 计算哈希值
                            hash_value = self.hash_utils.hash_file(file_path)
                            
                            if hash_value != file_index.hash_value or force_hash:
                                # 更新索引
                                file_index.size = current_size
                                file_index.mtime = current_mtime
                                file_index.hash_value = hash_value
                                file_index.status = 'modified'
                                file_index.sync_time = get_beijing_time()
                                
                                changed_files.append(rel_path)
                                logger.debug(f"文件已修改: {rel_path}")
                    else:
                        # 新文件
                        hash_value = self.hash_utils.hash_file(file_path)
                        
                        # 构建远程路径
                        remote_base = self.config_manager.get('sync.paths.remote_root', '/')
                        remote_path = f"{remote_base}/{rel_path}".replace('\\', '/').replace('//', '/')
                        
                        file_index = FileIndex(
                            path=rel_path,
                            size=current_size,
                            mtime=current_mtime,
                            hash_value=hash_value,
                            status='new',
                            remote_path=remote_path
                        )
                        
                        self.index_data[rel_path] = file_index
                        changed_files.append(rel_path)
                        logger.debug(f"发现新文件: {rel_path}")
                        
                except OSError as e:
                    logger.warning(f"无法访问文件 {file_path}: {e}")
                    continue
            
            # 检查已删除的文件
            indexed_files = set(self.index_data.keys())
            deleted_files = indexed_files - current_files
            
            for rel_path in deleted_files:
                file_index = self.index_data[rel_path]
                if file_index.status != 'deleted':
                    file_index.status = 'deleted'
                    file_index.sync_time = get_beijing_time()
                    changed_files.append(rel_path)
                    logger.debug(f"文件已删除: {rel_path}")
            
            # 保存索引
            if changed_files:
                self._save_index()
                logger.info(f"文件扫描完成，发现 {len(changed_files)} 个变更")
            else:
                logger.info("文件扫描完成，没有发现变更")
            
            return changed_files
            
        except Exception as e:
            logger.error(f"扫描本地文件失败: {e}")
            return []
    
    def get_file_index(self, path: str) -> Optional[FileIndex]:
        """获取文件索引
        
        Args:
            path: 文件路径（相对路径）
            
        Returns:
            文件索引，不存在返回None
        """
        return self.index_data.get(path)
    
    def update_file_index(self, path: str, **kwargs) -> None:
        """更新文件索引
        
        Args:
            path: 文件路径（相对路径）
            **kwargs: 要更新的字段
        """
        if path in self.index_data:
            file_index = self.index_data[path]
            
            # 更新字段
            for key, value in kwargs.items():
                if hasattr(file_index, key):
                    setattr(file_index, key, value)
            
            # 更新同步时间
            file_index.sync_time = get_beijing_time()
            
            logger.debug(f"文件索引已更新: {path}")
        else:
            logger.warning(f"文件索引不存在: {path}")
    
    def mark_file_synced(self, path: str) -> None:
        """标记文件为已同步
        
        Args:
            path: 文件路径（相对路径）
        """
        self.update_file_index(path, status='synced')
    
    def mark_file_deleted(self, path: str) -> None:
        """标记文件为已删除
        
        Args:
            path: 文件路径（相对路径）
        """
        self.update_file_index(path, status='deleted')
    
    def remove_file_index(self, path: str) -> bool:
        """移除文件索引
        
        Args:
            path: 文件路径（相对路径）
            
        Returns:
            是否移除成功
        """
        if path in self.index_data:
            del self.index_data[path]
            logger.debug(f"文件索引已移除: {path}")
            return True
        return False
    
    def get_files_by_status(self, status: str) -> List[FileIndex]:
        """根据状态获取文件列表
        
        Args:
            status: 文件状态
            
        Returns:
            文件索引列表
        """
        return [file_index for file_index in self.index_data.values() 
                if file_index.status == status]
    
    def get_changed_files(self) -> List[FileIndex]:
        """获取有变更的文件列表
        
        Returns:
            变更文件索引列表
        """
        changed_statuses = ['new', 'modified', 'deleted']
        return [file_index for file_index in self.index_data.values() 
                if file_index.status in changed_statuses]
    
    def get_statistics(self) -> Dict[str, int]:
        """获取索引统计信息
        
        Returns:
            统计信息字典
        """
        stats = {
            'total': len(self.index_data),
            'synced': 0,
            'new': 0,
            'modified': 0,
            'deleted': 0,
            'unknown': 0
        }
        
        for file_index in self.index_data.values():
            status = file_index.status
            if status in stats:
                stats[status] += 1
            else:
                stats['unknown'] += 1
        
        return stats
    
    def cleanup_deleted_files(self, days: int = 30) -> int:
        """清理已删除文件的索引记录
        
        Args:
            days: 保留天数
            
        Returns:
            清理的记录数
        """
        from datetime import timedelta
        
        cutoff_time = get_beijing_time() - timedelta(days=days)
        deleted_paths = []
        
        for path, file_index in self.index_data.items():
            if (file_index.status == 'deleted' and 
                file_index.sync_time and 
                file_index.sync_time < cutoff_time):
                deleted_paths.append(path)
        
        # 移除过期的删除记录
        for path in deleted_paths:
            del self.index_data[path]
        
        if deleted_paths:
            self._save_index()
            logger.info(f"清理了 {len(deleted_paths)} 个过期的删除记录")
        
        return len(deleted_paths)
    
    def export_index(self, export_path: str, format: str = 'json') -> bool:
        """导出索引数据
        
        Args:
            export_path: 导出文件路径
            format: 导出格式 (json, csv)
            
        Returns:
            是否导出成功
        """
        try:
            if format.lower() == 'json':
                data = {}
                for path, file_index in self.index_data.items():
                    data[path] = file_index.to_dict()
                
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    
            elif format.lower() == 'csv':
                import csv
                
                with open(export_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # 写入标题行
                    writer.writerow(['Path', 'Size', 'ModTime', 'Hash', 'SyncTime', 'Status', 'RemotePath'])
                    
                    # 写入数据行
                    for file_index in self.index_data.values():
                        writer.writerow([
                            file_index.path,
                            file_index.size,
                            format_time(datetime.fromtimestamp(file_index.mtime)) if file_index.mtime else '',
                            file_index.hash_value,
                            format_time(file_index.sync_time) if file_index.sync_time else '',
                            file_index.status,
                            file_index.remote_path
                        ])
            else:
                logger.error(f"不支持的导出格式: {format}")
                return False
            
            logger.info(f"索引数据导出成功: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出索引数据失败: {e}")
            return False
    
    def save(self) -> bool:
        """保存索引
        
        Returns:
            是否保存成功
        """
        return self._save_index()
    
    def reload(self) -> None:
        """重新加载索引"""
        self._load_index()
    
    def clear(self) -> None:
        """清空索引"""
        self.index_data.clear()
        self._save_index()
        logger.info("文件索引已清空")