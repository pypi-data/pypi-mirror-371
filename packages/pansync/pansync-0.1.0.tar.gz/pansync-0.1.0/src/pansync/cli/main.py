#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令行接口主模块

提供完整的命令行功能，包括同步、配置管理、状态查看等。
"""

import os
import sys
import time
import signal
import argparse
from pathlib import Path
from typing import Optional

from loguru import logger

from ..core import SyncEngine
from ..config import ConfigManager, ClientManager
from ..utils.time_utils import format_time, get_beijing_time
from ..utils.file_utils import FileUtils
from ..utils.network_utils import NetworkUtils


class PanSyncCLI:
    """PanSync命令行接口"""
    
    def __init__(self):
        self.sync_engine: Optional[SyncEngine] = None
        self.config_path: Optional[str] = None
        self.verbose = False
        
        # 信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        logger.info(f"收到信号 {signum}，正在停止...")
        if self.sync_engine:
            self.sync_engine.stop_daemon()
        sys.exit(0)
    
    def _setup_logging(self, verbose: bool = False, log_file: str = None):
        """设置日志"""
        # 移除默认处理器
        logger.remove()
        
        # 控制台日志
        log_level = "DEBUG" if verbose else "INFO"
        logger.add(
            sys.stderr,
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )
        
        # 文件日志
        if log_file:
            logger.add(
                log_file,
                level="DEBUG",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
                rotation="10 MB",
                retention="30 days"
            )
    
    def _get_config_path(self, config_path: str = None) -> str:
        """获取配置文件路径"""
        if config_path:
            return os.path.abspath(config_path)
        
        # 默认配置路径
        default_paths = [
            os.path.join(os.getcwd(), 'config.yaml'),
            os.path.expanduser('~/.pansync/config.yaml'),
            '/etc/pansync/config.yaml'
        ]
        
        for path in default_paths:
            if os.path.exists(path):
                return path
        
        # 返回默认路径（即使不存在）
        return default_paths[1]
    
    def cmd_init(self, args) -> int:
        """初始化配置"""
        config_path = self._get_config_path(args.config)
        
        if os.path.exists(config_path) and not args.force:
            logger.error(f"配置文件已存在: {config_path}")
            logger.info("使用 --force 参数强制覆盖")
            return 1
        
        try:
            # 确保配置目录存在
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # 创建配置管理器
            config_manager = ConfigManager(config_path)
            
            # 创建默认配置
            config_manager._create_default_config()
            logger.info(f"配置文件已创建: {config_path}")
            logger.info("请编辑配置文件，设置百度网盘API信息和同步路径")
            return 0
                
        except Exception as e:
            logger.error(f"初始化配置失败: {e}")
            return 1
    
    def cmd_sync(self, args) -> int:
        """执行同步"""
        try:
            config_path = self._get_config_path(args.config)
            
            if not os.path.exists(config_path):
                logger.error(f"配置文件不存在: {config_path}")
                logger.info("请先运行 'pansync init' 初始化配置")
                return 1
            
            # 创建同步引擎
            self.sync_engine = SyncEngine(config_path)
            
            # 设置进度回调
            if not args.quiet:
                def progress_callback(current, total, message):
                    if total > 0:
                        percent = (current / total) * 100
                        print(f"\r进度: {current}/{total} ({percent:.1f}%) - {message}", end="", flush=True)
                    else:
                        print(f"\r{message}", end="", flush=True)
                
                self.sync_engine.set_progress_callback(progress_callback)
            
            # 执行同步
            if args.force:
                success = self.sync_engine.force_sync()
            else:
                success = self.sync_engine.sync_once()
            
            if not args.quiet:
                print()  # 换行
            
            if success:
                logger.info("同步完成")
                return 0
            else:
                logger.error("同步失败")
                return 1
                
        except KeyboardInterrupt:
            logger.info("同步被用户中断")
            return 1
        except Exception as e:
            logger.error(f"同步过程中发生异常: {e}")
            return 1
    
    def cmd_daemon(self, args) -> int:
        """守护进程模式"""
        try:
            config_path = self._get_config_path(args.config)
            
            if not os.path.exists(config_path):
                logger.error(f"配置文件不存在: {config_path}")
                logger.info("请先运行 'pansync init' 初始化配置")
                return 1
            
            # 创建同步引擎
            self.sync_engine = SyncEngine(config_path)
            
            # 启动守护进程
            if not self.sync_engine.start_daemon():
                logger.error("启动守护进程失败")
                return 1
            
            logger.info("守护进程已启动，按 Ctrl+C 停止")
            
            # 保持运行
            try:
                while self.sync_engine.is_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("收到停止信号")
            
            # 停止守护进程
            self.sync_engine.stop_daemon()
            logger.info("守护进程已停止")
            return 0
            
        except Exception as e:
            logger.error(f"守护进程运行异常: {e}")
            return 1
    
    def cmd_status(self, args) -> int:
        """查看状态"""
        try:
            config_path = self._get_config_path(args.config)
            
            if not os.path.exists(config_path):
                logger.error(f"配置文件不存在: {config_path}")
                return 1
            
            # 创建同步引擎（仅用于获取状态）
            sync_engine = SyncEngine(config_path)
            
            if not sync_engine.initialize():
                logger.error("初始化失败")
                return 1
            
            # 获取状态信息
            status = sync_engine.get_status()
            
            # 显示状态
            print("=== PanSync 状态 ===")
            print(f"运行状态: {'运行中' if status['is_running'] else '已停止'}")
            print(f"同步状态: {'同步中' if status['is_syncing'] else '空闲'}")
            print(f"客户端ID: {status['client_id']}")
            print(f"客户端名称: {status['client_name']}")
            print(f"持有锁: {'是' if status['lock_held'] else '否'}")
            
            if status['last_sync_time']:
                print(f"上次同步: {status['last_sync_time']}")
            else:
                print("上次同步: 从未同步")
            
            if status['next_sync_time']:
                print(f"下次同步: {status['next_sync_time']}")
            else:
                print("下次同步: 未计划")
            
            # 同步统计
            sync_stats = status['sync_stats']
            print("\n=== 同步统计 ===")
            print(f"总同步次数: {sync_stats['total_syncs']}")
            print(f"成功次数: {sync_stats['successful_syncs']}")
            print(f"失败次数: {sync_stats['failed_syncs']}")
            print(f"上次同步耗时: {sync_stats['last_sync_duration']:.1f}秒")
            print(f"总同步时间: {sync_stats['total_sync_time']:.1f}秒")
            
            # 文件统计
            file_stats = status['file_stats']
            print("\n=== 文件统计 ===")
            print(f"上传文件数: {file_stats['uploaded_files']}")
            print(f"下载文件数: {file_stats['downloaded_files']}")
            print(f"删除文件数: {file_stats['deleted_files']}")
            print(f"上传字节数: {NetworkUtils.format_size(file_stats['uploaded_bytes'])}")
            print(f"下载字节数: {NetworkUtils.format_size(file_stats['downloaded_bytes'])}")
            print(f"错误次数: {file_stats['errors']}")
            
            # 索引统计
            index_stats = status['index_stats']
            print("\n=== 索引统计 ===")
            print(f"总文件数: {index_stats['total']}")
            print(f"已同步: {index_stats['synced']}")
            print(f"新文件: {index_stats['new']}")
            print(f"已修改: {index_stats['modified']}")
            print(f"已删除: {index_stats['deleted']}")
            
            # 百度网盘配额信息
            try:
                print("\n=== 百度网盘配额 ===")
                # bypy的quota方法会直接输出配额信息到控制台
                sync_engine.bypy_instance.quota()
            except Exception as e:
                print(f"获取配额信息失败: {e}")
            
            # 锁信息
            if status['lock_info']:
                lock_info = status['lock_info']
                print("\n=== 锁信息 ===")
                print(f"锁持有者: {lock_info.get('client_name', 'unknown')}")
                print(f"锁定时间: {lock_info.get('locked_at', 'unknown')}")
                print(f"过期时间: {lock_info.get('expires_at', 'unknown')}")
                print(f"操作类型: {lock_info.get('operation', 'unknown')}")
            
            return 0
            
        except Exception as e:
            logger.error(f"获取状态失败: {e}")
            return 1
    
    def cmd_config(self, args) -> int:
        """配置管理"""
        try:
            config_path = self._get_config_path(args.config)
            
            if not os.path.exists(config_path):
                logger.error(f"配置文件不存在: {config_path}")
                return 1
            
            config_manager = ConfigManager(config_path)
            
            if args.action == 'show':
                # 显示配置
                if args.key:
                    value = config_manager.get(args.key)
                    if value is not None:
                        print(f"{args.key}: {value}")
                    else:
                        logger.error(f"配置项不存在: {args.key}")
                        return 1
                else:
                    # 显示所有配置（隐藏敏感信息）
                    config = config_manager.get_all_config()
                    self._print_config(config)
            
            elif args.action == 'set':
                # 设置配置
                if not args.key or not args.value:
                    logger.error("设置配置需要指定 key 和 value")
                    return 1
                
                config_manager.set(args.key, args.value)
                if config_manager.save():
                    logger.info(f"配置已更新: {args.key} = {args.value}")
                else:
                    logger.error("保存配置失败")
                    return 1
            
            elif args.action == 'validate':
                # 验证配置
                if config_manager.validate_config():
                    logger.info("配置验证通过")
                else:
                    logger.error("配置验证失败")
                    return 1
            
            return 0
            
        except Exception as e:
            logger.error(f"配置操作失败: {e}")
            return 1
    
    def cmd_trash(self, args) -> int:
        """trash管理"""
        try:
            config_path = self._get_config_path(args.config)
            
            if not os.path.exists(config_path):
                logger.error(f"配置文件不存在: {config_path}")
                return 1
            
            sync_engine = SyncEngine(config_path)
            if not sync_engine.initialize():
                logger.error("初始化失败")
                return 1
            
            file_manager = sync_engine.file_manager
            
            if args.action == 'list':
                # 列出trash文件
                trash_files = file_manager.list_trash_files()
                
                if not trash_files:
                    print("trash目录为空")
                    return 0
                
                print(f"trash目录中有 {len(trash_files)} 个文件:")
                print(f"{'文件路径':<50} {'大小':<10} {'删除时间':<20}")
                print("-" * 80)
                
                for file_info in trash_files:
                    size_str = NetworkUtils.format_size(file_info['size'])
                    time_str = format_time(file_info['mtime'])
                    print(f"{file_info['path']:<50} {size_str:<10} {time_str:<20}")
            
            elif args.action == 'clean':
                # 清理trash
                if args.days is not None:
                    cleaned_count = file_manager.clean_trash(args.days)
                    if cleaned_count >= 0:
                        logger.info(f"清理了 {cleaned_count} 个超过 {args.days} 天的文件")
                    else:
                        logger.info("trash目录已完全清理")
                else:
                    # 清理所有文件
                    if input("确定要清理所有trash文件吗？(y/N): ").lower() == 'y':
                        file_manager.clean_trash()
                        logger.info("trash目录已完全清理")
                    else:
                        logger.info("操作已取消")
            
            elif args.action == 'restore':
                # 恢复文件
                if not args.file:
                    logger.error("恢复文件需要指定文件路径")
                    return 1
                
                if file_manager.restore_from_trash(args.file):
                    logger.info(f"文件已恢复: {args.file}")
                else:
                    logger.error(f"恢复文件失败: {args.file}")
                    return 1
            
            return 0
            
        except Exception as e:
            logger.error(f"trash操作失败: {e}")
            return 1
    

    
    def _print_config(self, config, prefix="", level=0):
        """递归打印配置"""
        indent = "  " * level
        
        for key, value in config.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            # 隐藏敏感信息
            if any(sensitive in key.lower() for sensitive in ['key', 'secret', 'password', 'token']):
                value = "***"
            
            if isinstance(value, dict):
                print(f"{indent}{key}:")
                self._print_config(value, full_key, level + 1)
            else:
                print(f"{indent}{key}: {value}")
    
    def run(self, args=None) -> int:
        """运行CLI"""
        parser = argparse.ArgumentParser(
            prog='pansync',
            description='基于bypy的百度网盘同步工具',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # 全局参数
        parser.add_argument('-c', '--config', help='配置文件路径')
        parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
        parser.add_argument('--log-file', help='日志文件路径')
        
        # 子命令
        subparsers = parser.add_subparsers(dest='command', help='可用命令')
        
        # init命令
        init_parser = subparsers.add_parser('init', help='初始化配置文件')
        init_parser.add_argument('--force', action='store_true', help='强制覆盖现有配置')
        
        # sync命令
        sync_parser = subparsers.add_parser('sync', help='执行一次同步')
        sync_parser.add_argument('--force', action='store_true', help='强制同步（忽略锁）')
        sync_parser.add_argument('-q', '--quiet', action='store_true', help='静默模式')
        
        # daemon命令
        daemon_parser = subparsers.add_parser('daemon', help='守护进程模式')
        
        # status命令
        status_parser = subparsers.add_parser('status', help='查看状态')
        
        # config命令
        config_parser = subparsers.add_parser('config', help='配置管理')
        config_parser.add_argument('action', choices=['show', 'set', 'validate'], help='操作类型')
        config_parser.add_argument('key', nargs='?', help='配置键')
        config_parser.add_argument('value', nargs='?', help='配置值')
        
        # trash命令
        trash_parser = subparsers.add_parser('trash', help='trash管理')
        trash_parser.add_argument('action', choices=['list', 'clean', 'restore'], help='操作类型')
        trash_parser.add_argument('--days', type=int, help='清理天数（仅用于clean）')
        trash_parser.add_argument('--file', help='文件路径（仅用于restore）')
        

        
        # 解析参数
        parsed_args = parser.parse_args(args)
        
        # 设置日志
        self._setup_logging(parsed_args.verbose, parsed_args.log_file)
        self.verbose = parsed_args.verbose
        self.config_path = parsed_args.config
        
        # 执行命令
        if not parsed_args.command:
            parser.print_help()
            return 1
        
        command_map = {
            'init': self.cmd_init,
            'sync': self.cmd_sync,
            'daemon': self.cmd_daemon,
            'status': self.cmd_status,
            'config': self.cmd_config,
            'trash': self.cmd_trash,

        }
        
        command_func = command_map.get(parsed_args.command)
        if command_func:
            return command_func(parsed_args)
        else:
            logger.error(f"未知命令: {parsed_args.command}")
            return 1


def cli():
    """CLI入口点"""
    app = PanSyncCLI()
    return app.run()


def main():
    """主入口点"""
    sys.exit(cli())


if __name__ == '__main__':
    main()