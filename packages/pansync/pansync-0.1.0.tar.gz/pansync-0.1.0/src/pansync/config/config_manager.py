#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理器

负责读取、写入和管理配置文件。
"""

import os
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from loguru import logger


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化配置管理器
        
        Args:
            config_path: 配置文件路径，默认为 ~/pansync/config.yaml
        """
        if config_path is None:
            config_path = os.path.expanduser("~/pansync/config.yaml")
        
        self.config_path = Path(config_path)
        self.config_dir = self.config_path.parent
        self._config: Dict[str, Any] = {}
        
        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载配置
        self._load_config()
    
    def _load_config(self) -> None:
        """加载配置文件"""
        try:
            if not self.config_path.exists():
                logger.info(f"配置文件不存在，创建默认配置: {self.config_path}")
                self._create_default_config()
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
            
            logger.info(f"配置文件加载成功: {self.config_path}")
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            self._config = self._get_default_config()
    
    def _create_default_config(self) -> None:
        """创建默认配置文件"""
        try:
            # 从项目模板复制默认配置
            template_path = Path(__file__).parent.parent.parent.parent / "config" / "config.yaml"
            
            if template_path.exists():
                shutil.copy2(template_path, self.config_path)
                logger.info(f"默认配置文件创建成功: {self.config_path}")
            else:
                # 如果模板不存在，创建基本配置
                default_config = self._get_default_config()
                self.save_config(default_config)
                
        except Exception as e:
            logger.error(f"创建默认配置文件失败: {e}")
            # 使用内置默认配置
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "sync": {
                "schedule": {
                    "enabled": True,
                    "start_time": "08:00",
                    "end_time": "22:00",
                    "interval": 300,
                    "timezone": "Asia/Shanghai"
                },
                "limits": {
                    "max_speed": "10MB/s",
                    "max_concurrent": 5,
                    "chunk_size": "4MB",
                    "retry_times": 3,
                    "timeout": 300
                },
                "paths": {
                    "local_root": "~/Documents/BaiduPan",
                    "remote_root": "/",
                    "trash_dir": "trash",
                    "config_dir": ".config"
                },
                "filters": {
                    "ignore_patterns": [
                        "*.tmp", "*.swp", ".DS_Store", "Thumbs.db", "*.pyc", "__pycache__"
                    ],
                    "ignore_dirs": [".git", ".svn", "node_modules"],
                    "max_file_size": 1073741824
                }
            },
            "client": {
                "id": "auto",
                "name": "auto",
                "description": "",
                "lock": {
                    "timeout": 3600,
                    "retry_interval": 30,
                    "max_retries": 10
                }
            },
            "baidu": {
                "config_file": "~/.bypy/bypy.json",
                "api": {
                    "timeout": 60,
                    "retry_times": 3,
                    "rate_limit": 10
                }
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": {
                    "enabled": True,
                    "path": "~/pansync/logs/pansync.log",
                    "max_size": "10MB",
                    "backup_count": 5,
                    "rotation": "daily"
                },
                "console": {
                    "enabled": True,
                    "level": "INFO"
                }
            },
            "notifications": {
                "enabled": False,
                "system": {
                    "enabled": True,
                    "on_sync_complete": True,
                    "on_conflict": True,
                    "on_error": True
                }
            },
            "advanced": {
                "index": {
                    "file_name": ".index.dat",
                    "backup_enabled": True,
                    "backup_count": 3
                },
                "performance": {
                    "use_memory_cache": True,
                    "cache_size": 1000,
                    "parallel_hash": True,
                    "hash_algorithm": "sha256"
                },
                "debug": {
                    "enabled": False,
                    "log_api_calls": False,
                    "save_temp_files": False
                }
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值
        
        Args:
            key: 配置键，支持点分隔的嵌套键 (如 'sync.schedule.enabled')
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值
        
        Args:
            key: 配置键，支持点分隔的嵌套键
            value: 配置值
        """
        keys = key.split('.')
        config = self._config
        
        # 创建嵌套字典结构
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_config(self, config: Optional[Dict[str, Any]] = None) -> None:
        """保存配置到文件
        
        Args:
            config: 要保存的配置，如果为None则保存当前配置
        """
        try:
            if config is not None:
                self._config = config
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            
            logger.info(f"配置文件保存成功: {self.config_path}")
            
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            raise
    
    def reload(self) -> None:
        """重新加载配置文件"""
        logger.info("重新加载配置文件")
        self._load_config()
    
    def get_config(self) -> Dict[str, Any]:
        """获取完整配置"""
        return self._config.copy()
    
    def get_all_config(self) -> Dict[str, Any]:
        """获取所有配置（用于显示）"""
        config = self._config.copy()
        
        # 隐藏敏感信息
        if 'baidu' in config:
            if 'app_id' in config['baidu']:
                config['baidu']['app_id'] = '***' + str(config['baidu']['app_id'])[-4:] if config['baidu']['app_id'] else None
            if 'app_key' in config['baidu']:
                config['baidu']['app_key'] = '***' + str(config['baidu']['app_key'])[-4:] if config['baidu']['app_key'] else None
            if 'secret_key' in config['baidu']:
                config['baidu']['secret_key'] = '***' + str(config['baidu']['secret_key'])[-4:] if config['baidu']['secret_key'] else None
        
        return config
    
    def save(self) -> bool:
        """保存当前配置到文件
        
        Returns:
            是否保存成功
        """
        try:
            self.save_config()
            return True
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False
    
    def validate_config(self) -> bool:
        """验证配置文件的有效性
        
        Returns:
            配置是否有效
        """
        try:
            # 检查必需的配置项
            required_keys = [
                'sync.paths.local_root',
                'sync.paths.remote_root',
                'client.id',
                'baidu.config_file'
            ]
            
            for key in required_keys:
                if self.get(key) is None:
                    logger.error(f"缺少必需的配置项: {key}")
                    return False
            
            # 检查路径是否有效
            local_root = os.path.expanduser(self.get('sync.paths.local_root'))
            if not os.path.exists(os.path.dirname(local_root)):
                logger.error(f"本地同步根目录的父目录不存在: {local_root}")
                return False
            
            # 检查时间格式
            start_time = self.get('sync.schedule.start_time')
            end_time = self.get('sync.schedule.end_time')
            
            if start_time and end_time:
                try:
                    from datetime import datetime
                    datetime.strptime(start_time, '%H:%M')
                    datetime.strptime(end_time, '%H:%M')
                except ValueError:
                    logger.error("时间格式无效，应为 HH:MM 格式")
                    return False
            
            logger.info("配置文件验证通过")
            return True
            
        except Exception as e:
            logger.error(f"配置文件验证失败: {e}")
            return False
    
    @property
    def config_path_str(self) -> str:
        """获取配置文件路径字符串"""
        return str(self.config_path)