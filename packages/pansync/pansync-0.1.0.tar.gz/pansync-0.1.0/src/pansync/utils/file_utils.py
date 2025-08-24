#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件工具模块

提供文件操作相关的工具函数。
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional, Union, Generator
import fnmatch

from loguru import logger


class FileUtils:
    """文件工具类"""
    
    @classmethod
    def ensure_dir(cls, dir_path: Union[str, Path]) -> bool:
        """确保目录存在
        
        Args:
            dir_path: 目录路径
            
        Returns:
            目录是否存在或创建成功
        """
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"创建目录失败: {dir_path}, 错误: {e}")
            return False
    
    @classmethod
    def safe_remove(cls, file_path: Union[str, Path]) -> bool:
        """安全删除文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            删除是否成功
        """
        try:
            file_path = Path(file_path)
            if file_path.exists():
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
                logger.debug(f"文件删除成功: {file_path}")
            return True
        except Exception as e:
            logger.error(f"文件删除失败: {file_path}, 错误: {e}")
            return False
    
    @classmethod
    def safe_copy(cls, src: Union[str, Path], dst: Union[str, Path]) -> bool:
        """安全复制文件
        
        Args:
            src: 源文件路径
            dst: 目标文件路径
            
        Returns:
            复制是否成功
        """
        try:
            src_path = Path(src)
            dst_path = Path(dst)
            
            if not src_path.exists():
                logger.error(f"源文件不存在: {src_path}")
                return False
            
            # 确保目标目录存在
            cls.ensure_dir(dst_path.parent)
            
            if src_path.is_file():
                shutil.copy2(src_path, dst_path)
            elif src_path.is_dir():
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            
            logger.debug(f"文件复制成功: {src_path} -> {dst_path}")
            return True
            
        except Exception as e:
            logger.error(f"文件复制失败: {src} -> {dst}, 错误: {e}")
            return False
    
    @classmethod
    def safe_move(cls, src: Union[str, Path], dst: Union[str, Path]) -> bool:
        """安全移动文件
        
        Args:
            src: 源文件路径
            dst: 目标文件路径
            
        Returns:
            移动是否成功
        """
        try:
            src_path = Path(src)
            dst_path = Path(dst)
            
            if not src_path.exists():
                logger.error(f"源文件不存在: {src_path}")
                return False
            
            # 确保目标目录存在
            cls.ensure_dir(dst_path.parent)
            
            shutil.move(str(src_path), str(dst_path))
            logger.debug(f"文件移动成功: {src_path} -> {dst_path}")
            return True
            
        except Exception as e:
            logger.error(f"文件移动失败: {src} -> {dst}, 错误: {e}")
            return False
    
    @classmethod
    def get_file_size(cls, file_path: Union[str, Path]) -> Optional[int]:
        """获取文件大小
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件大小（字节），文件不存在返回None
        """
        try:
            return Path(file_path).stat().st_size
        except Exception:
            return None
    
    @classmethod
    def get_file_mtime(cls, file_path: Union[str, Path]) -> Optional[float]:
        """获取文件修改时间
        
        Args:
            file_path: 文件路径
            
        Returns:
            修改时间戳，文件不存在返回None
        """
        try:
            return Path(file_path).stat().st_mtime
        except Exception:
            return None
    
    @classmethod
    def is_file_newer(cls, file1: Union[str, Path], file2: Union[str, Path]) -> Optional[bool]:
        """比较两个文件的修改时间
        
        Args:
            file1: 第一个文件路径
            file2: 第二个文件路径
            
        Returns:
            file1是否比file2新，任一文件不存在返回None
        """
        mtime1 = cls.get_file_mtime(file1)
        mtime2 = cls.get_file_mtime(file2)
        
        if mtime1 is None or mtime2 is None:
            return None
        
        return mtime1 > mtime2
    
    @classmethod
    def find_files(cls, root_dir: Union[str, Path], 
                  pattern: str = '*', 
                  recursive: bool = True) -> Generator[Path, None, None]:
        """查找文件
        
        Args:
            root_dir: 根目录
            pattern: 文件名模式（支持通配符）
            recursive: 是否递归查找
            
        Yields:
            匹配的文件路径
        """
        try:
            root_path = Path(root_dir)
            
            if not root_path.exists() or not root_path.is_dir():
                logger.warning(f"目录不存在或不是目录: {root_path}")
                return
            
            if recursive:
                for file_path in root_path.rglob(pattern):
                    if file_path.is_file():
                        yield file_path
            else:
                for file_path in root_path.glob(pattern):
                    if file_path.is_file():
                        yield file_path
                        
        except Exception as e:
            logger.error(f"查找文件失败: {root_dir}, 错误: {e}")
    
    @classmethod
    def filter_files(cls, file_paths: List[Union[str, Path]], 
                    ignore_patterns: List[str] = None,
                    ignore_dirs: List[str] = None,
                    max_size: Optional[int] = None) -> List[Path]:
        """过滤文件列表
        
        Args:
            file_paths: 文件路径列表
            ignore_patterns: 忽略的文件模式列表
            ignore_dirs: 忽略的目录名列表
            max_size: 最大文件大小（字节）
            
        Returns:
            过滤后的文件路径列表
        """
        if ignore_patterns is None:
            ignore_patterns = []
        if ignore_dirs is None:
            ignore_dirs = []
        
        filtered_files = []
        
        for file_path in file_paths:
            path = Path(file_path)
            
            try:
                # 检查文件是否存在
                if not path.exists() or not path.is_file():
                    continue
                
                # 检查文件大小
                if max_size is not None:
                    file_size = cls.get_file_size(path)
                    if file_size is not None and file_size > max_size:
                        logger.debug(f"文件过大，跳过: {path} ({file_size} bytes)")
                        continue
                
                # 检查忽略模式
                file_name = path.name
                if any(fnmatch.fnmatch(file_name, pattern) for pattern in ignore_patterns):
                    logger.debug(f"文件匹配忽略模式，跳过: {path}")
                    continue
                
                # 检查忽略目录
                path_parts = path.parts
                if any(ignore_dir in path_parts for ignore_dir in ignore_dirs):
                    logger.debug(f"文件在忽略目录中，跳过: {path}")
                    continue
                
                filtered_files.append(path)
                
            except Exception as e:
                logger.warning(f"处理文件时出错，跳过: {path}, 错误: {e}")
                continue
        
        logger.debug(f"文件过滤完成: {len(file_paths)} -> {len(filtered_files)}")
        return filtered_files
    
    @classmethod
    def create_temp_file(cls, suffix: str = '', prefix: str = 'pansync_') -> str:
        """创建临时文件
        
        Args:
            suffix: 文件后缀
            prefix: 文件前缀
            
        Returns:
            临时文件路径
        """
        try:
            fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
            os.close(fd)  # 关闭文件描述符
            logger.debug(f"临时文件创建成功: {temp_path}")
            return temp_path
        except Exception as e:
            logger.error(f"创建临时文件失败: {e}")
            raise
    
    @classmethod
    def create_temp_dir(cls, prefix: str = 'pansync_') -> str:
        """创建临时目录
        
        Args:
            prefix: 目录前缀
            
        Returns:
            临时目录路径
        """
        try:
            temp_dir = tempfile.mkdtemp(prefix=prefix)
            logger.debug(f"临时目录创建成功: {temp_dir}")
            return temp_dir
        except Exception as e:
            logger.error(f"创建临时目录失败: {e}")
            raise
    
    @classmethod
    def normalize_path(cls, path: Union[str, Path]) -> str:
        """标准化路径
        
        Args:
            path: 原始路径
            
        Returns:
            标准化后的路径
        """
        try:
            # 展开用户目录和环境变量
            expanded_path = os.path.expanduser(os.path.expandvars(str(path)))
            # 标准化路径分隔符
            normalized_path = os.path.normpath(expanded_path)
            # 转换为绝对路径
            absolute_path = os.path.abspath(normalized_path)
            return absolute_path
        except Exception as e:
            logger.error(f"路径标准化失败: {path}, 错误: {e}")
            return str(path)
    
    @classmethod
    def get_relative_path(cls, file_path: Union[str, Path], 
                         base_path: Union[str, Path]) -> Optional[str]:
        """获取相对路径
        
        Args:
            file_path: 文件路径
            base_path: 基础路径
            
        Returns:
            相对路径，计算失败返回None
        """
        try:
            file_path = Path(cls.normalize_path(file_path))
            base_path = Path(cls.normalize_path(base_path))
            
            relative_path = file_path.relative_to(base_path)
            return str(relative_path).replace('\\', '/')
            
        except ValueError:
            # 文件不在基础路径下
            logger.debug(f"文件不在基础路径下: {file_path} (base: {base_path})")
            return None
        except Exception as e:
            logger.error(f"计算相对路径失败: {file_path} (base: {base_path}), 错误: {e}")
            return None
    
    @classmethod
    def is_hidden_file(cls, file_path: Union[str, Path]) -> bool:
        """检查是否为隐藏文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否为隐藏文件
        """
        path = Path(file_path)
        
        # 检查文件名是否以点开头
        if path.name.startswith('.'):
            return True
        
        # 在Windows上检查隐藏属性
        if os.name == 'nt':
            try:
                import stat
                attrs = os.stat(path).st_file_attributes
                return bool(attrs & stat.FILE_ATTRIBUTE_HIDDEN)
            except (AttributeError, OSError):
                pass
        
        return False
    
    @classmethod
    def get_directory_size(cls, dir_path: Union[str, Path]) -> int:
        """获取目录大小
        
        Args:
            dir_path: 目录路径
            
        Returns:
            目录总大小（字节）
        """
        total_size = 0
        
        try:
            for file_path in cls.find_files(dir_path, recursive=True):
                file_size = cls.get_file_size(file_path)
                if file_size is not None:
                    total_size += file_size
        except Exception as e:
            logger.error(f"计算目录大小失败: {dir_path}, 错误: {e}")
        
        return total_size
    
    @classmethod
    def backup_file(cls, file_path: Union[str, Path], 
                   backup_suffix: str = '.bak') -> Optional[str]:
        """备份文件
        
        Args:
            file_path: 要备份的文件路径
            backup_suffix: 备份文件后缀
            
        Returns:
            备份文件路径，备份失败返回None
        """
        try:
            src_path = Path(file_path)
            
            if not src_path.exists() or not src_path.is_file():
                logger.error(f"源文件不存在: {src_path}")
                return None
            
            # 生成备份文件名
            backup_path = src_path.with_suffix(src_path.suffix + backup_suffix)
            
            # 如果备份文件已存在，添加时间戳
            if backup_path.exists():
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = src_path.with_suffix(f'{src_path.suffix}.{timestamp}{backup_suffix}')
            
            # 复制文件
            if cls.safe_copy(src_path, backup_path):
                logger.info(f"文件备份成功: {src_path} -> {backup_path}")
                return str(backup_path)
            else:
                return None
                
        except Exception as e:
            logger.error(f"文件备份失败: {file_path}, 错误: {e}")
            return None