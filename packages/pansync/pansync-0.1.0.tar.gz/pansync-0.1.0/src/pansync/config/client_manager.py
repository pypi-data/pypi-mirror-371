#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户端管理器

负责管理多客户端的注册、状态更新和配置同步。
"""

import os
import socket
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import psutil
import yaml
from loguru import logger

from ..utils.time_utils import get_beijing_time


class ClientManager:
    """客户端管理器"""
    
    def __init__(self, config_manager):
        """初始化客户端管理器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self._client_id: Optional[str] = None
        self._client_name: Optional[str] = None
        self._client_info: Dict = {}
    
    def get_client_id(self) -> str:
        """获取客户端ID
        
        Returns:
            客户端ID (MAC地址)
        """
        if self._client_id is None:
            configured_id = self.config_manager.get('client.id')
            
            if configured_id and configured_id != 'auto':
                self._client_id = configured_id
            else:
                # 使用MAC地址作为客户端ID
                self._client_id = self._get_mac_address()
        
        return self._client_id
    
    def get_client_name(self) -> str:
        """获取客户端名称
        
        Returns:
            客户端名称 (机器名)
        """
        if self._client_name is None:
            configured_name = self.config_manager.get('client.name')
            
            if configured_name and configured_name != 'auto':
                self._client_name = configured_name
            else:
                # 使用机器名作为客户端名称
                self._client_name = socket.gethostname()
        
        return self._client_name
    
    def get_client_info(self) -> Dict:
        """获取客户端信息
        
        Returns:
            客户端信息字典
        """
        if not self._client_info:
            self._client_info = {
                'id': self.get_client_id(),
                'name': self.get_client_name(),
                'ip': self._get_local_ip(),
                'hostname': socket.gethostname(),
                'platform': self._get_platform_info(),
                'description': self.config_manager.get('client.description', ''),
                'last_seen': get_beijing_time().isoformat(),
                'status': 'active',
                'version': self._get_version()
            }
        
        return self._client_info.copy()
    
    def _get_mac_address(self) -> str:
        """获取MAC地址
        
        Returns:
            格式化的MAC地址
        """
        try:
            # 获取主网卡的MAC地址
            mac = uuid.getnode()
            mac_str = ':'.join([f'{(mac >> i) & 0xff:02x}' for i in range(0, 48, 8)][::-1])
            return mac_str
        except Exception as e:
            logger.warning(f"获取MAC地址失败: {e}")
            # 生成随机ID作为备选
            return str(uuid.uuid4())
    
    def _get_local_ip(self) -> str:
        """获取本地IP地址
        
        Returns:
            本地IP地址
        """
        try:
            # 连接到外部地址获取本地IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(('8.8.8.8', 80))
                return s.getsockname()[0]
        except Exception:
            try:
                # 备选方案：获取hostname对应的IP
                return socket.gethostbyname(socket.gethostname())
            except Exception:
                return '127.0.0.1'
    
    def _get_platform_info(self) -> Dict:
        """获取平台信息
        
        Returns:
            平台信息字典
        """
        try:
            import platform
            return {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'python_version': platform.python_version()
            }
        except Exception as e:
            logger.warning(f"获取平台信息失败: {e}")
            return {'system': 'unknown'}
    
    def _get_version(self) -> str:
        """获取PanSync版本
        
        Returns:
            版本号
        """
        try:
            from .. import __version__
            return __version__
        except ImportError:
            return '0.1.0'
    
    def register_client(self, bypy_instance) -> bool:
        """注册客户端到服务器
        
        Args:
            bypy_instance: bypy实例，用于访问网盘
            
        Returns:
            注册是否成功
        """
        try:
            logger.info("开始注册客户端")
            
            # 获取客户端信息
            client_info = self.get_client_info()
            client_id = client_info['id']
            
            # 读取服务器配置
            server_config = self._load_server_config(bypy_instance)
            
            # 检查客户端是否已注册
            clients = server_config.get('clients', [])
            existing_client = None
            
            for i, client in enumerate(clients):
                if client.get('id') == client_id:
                    existing_client = i
                    break
            
            # 更新客户端信息
            if existing_client is not None:
                logger.info(f"更新现有客户端信息: {client_id}")
                clients[existing_client] = client_info
            else:
                logger.info(f"注册新客户端: {client_id}")
                clients.append(client_info)
            
            # 更新服务器配置
            server_config['clients'] = clients
            server_config['last_updated'] = get_beijing_time().isoformat()
            
            # 保存服务器配置
            self._save_server_config(bypy_instance, server_config)
            
            logger.info(f"客户端注册成功: {client_info['name']} ({client_id})")
            return True
            
        except Exception as e:
            logger.error(f"客户端注册失败: {e}")
            return False
    
    def _load_server_config(self, bypy_instance) -> Dict:
        """从网盘加载服务器配置
        
        Args:
            bypy_instance: bypy实例
            
        Returns:
            服务器配置字典
        """
        try:
            config_dir = self.config_manager.get('sync.paths.config_dir', '.config')
            server_config_path = f"{config_dir}/server.yaml"
            
            # 尝试从网盘下载配置文件
            temp_file = "/tmp/server_config.yaml"
            
            try:
                # 下载服务器配置文件
                result = bypy_instance.download(server_config_path, temp_file)
                
                if result == 0:  # 下载成功
                    with open(temp_file, 'r', encoding='utf-8') as f:
                        server_config = yaml.safe_load(f) or {}
                    
                    # 清理临时文件
                    os.unlink(temp_file)
                    
                    logger.info("服务器配置加载成功")
                    return server_config
                    
            except Exception as e:
                logger.debug(f"下载服务器配置失败: {e}")
            
            # 如果下载失败，返回默认配置
            logger.info("使用默认服务器配置")
            return self._get_default_server_config()
            
        except Exception as e:
            logger.error(f"加载服务器配置失败: {e}")
            return self._get_default_server_config()
    
    def _save_server_config(self, bypy_instance, server_config: Dict) -> None:
        """保存服务器配置到网盘
        
        Args:
            bypy_instance: bypy实例
            server_config: 服务器配置
        """
        try:
            config_dir = self.config_manager.get('sync.paths.config_dir', '.config')
            server_config_path = f"{config_dir}/server.yaml"
            
            # 保存到临时文件
            temp_file = "/tmp/server_config.yaml"
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                yaml.dump(server_config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            
            # 确保远程目录存在
            bypy_instance.mkdir(config_dir)
            
            # 上传到网盘
            result = bypy_instance.upload(temp_file, server_config_path)
            
            # 清理临时文件
            os.unlink(temp_file)
            
            if result == 0:
                logger.info("服务器配置保存成功")
            else:
                logger.error(f"服务器配置保存失败，错误码: {result}")
                
        except Exception as e:
            logger.error(f"保存服务器配置失败: {e}")
            raise
    
    def _get_default_server_config(self) -> Dict:
        """获取默认服务器配置
        
        Returns:
            默认服务器配置
        """
        return {
            'version': '1.0',
            'created_at': get_beijing_time().isoformat(),
            'last_updated': get_beijing_time().isoformat(),
            'clients': [],
            'settings': {
                'max_clients': 10,
                'lock_timeout': 3600,
                'sync_interval': 300,
                'conflict_resolution': 'timestamp_priority'
            },
            'statistics': {
                'total_syncs': 0,
                'total_conflicts': 0,
                'last_sync': None
            }
        }
    
    def get_registered_clients(self, bypy_instance) -> List[Dict]:
        """获取已注册的客户端列表
        
        Args:
            bypy_instance: bypy实例
            
        Returns:
            客户端列表
        """
        try:
            server_config = self._load_server_config(bypy_instance)
            return server_config.get('clients', [])
        except Exception as e:
            logger.error(f"获取客户端列表失败: {e}")
            return []
    
    def update_client_status(self, bypy_instance, status: str = 'active') -> bool:
        """更新客户端状态
        
        Args:
            bypy_instance: bypy实例
            status: 客户端状态
            
        Returns:
            更新是否成功
        """
        try:
            client_info = self.get_client_info()
            client_info['status'] = status
            client_info['last_seen'] = get_beijing_time().isoformat()
            
            # 更新内存中的客户端信息
            self._client_info = client_info
            
            # 重新注册以更新服务器端信息
            return self.register_client(bypy_instance)
            
        except Exception as e:
            logger.error(f"更新客户端状态失败: {e}")
            return False
    
    def is_client_registered(self, bypy_instance) -> bool:
        """检查客户端是否已注册
        
        Args:
            bypy_instance: bypy实例
            
        Returns:
            是否已注册
        """
        try:
            clients = self.get_registered_clients(bypy_instance)
            client_id = self.get_client_id()
            
            return any(client.get('id') == client_id for client in clients)
            
        except Exception as e:
            logger.error(f"检查客户端注册状态失败: {e}")
            return False