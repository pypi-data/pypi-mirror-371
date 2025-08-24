#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PanSync - 百度网盘多客户端同步工具

基于 bypy 的智能同步工具，支持多客户端协作和冲突检测。
"""

__version__ = "0.1.0"
__author__ = "PanSync Team"
__email__ = "pansync@example.com"
__description__ = "百度网盘多客户端同步工具"

# 导出主要类和函数
from .core.sync_engine import SyncEngine
from .config.config_manager import ConfigManager
from .config.client_manager import ClientManager

__all__ = [
    "SyncEngine",
    "ConfigManager",
    "ClientManager",
    "__version__",
]