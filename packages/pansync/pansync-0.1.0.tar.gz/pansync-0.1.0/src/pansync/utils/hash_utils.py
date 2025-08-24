#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
哈希工具模块

提供文件和字符串的哈希计算功能。
"""

import hashlib
import os
from pathlib import Path
from typing import Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

from loguru import logger


class HashUtils:
    """哈希工具类"""
    
    DEFAULT_ALGORITHM = 'sha256'
    CHUNK_SIZE = 8192  # 8KB chunks for file reading
    
    @classmethod
    def hash_string(cls, text: str, algorithm: str = None) -> str:
        """计算字符串哈希
        
        Args:
            text: 要计算哈希的字符串
            algorithm: 哈希算法，默认为sha256
            
        Returns:
            十六进制哈希值
        """
        if algorithm is None:
            algorithm = cls.DEFAULT_ALGORITHM
        
        try:
            hasher = hashlib.new(algorithm)
            hasher.update(text.encode('utf-8'))
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"字符串哈希计算失败: {e}")
            raise
    
    @classmethod
    def hash_file(cls, file_path: Union[str, Path], algorithm: str = None) -> Optional[str]:
        """计算文件哈希
        
        Args:
            file_path: 文件路径
            algorithm: 哈希算法，默认为sha256
            
        Returns:
            十六进制哈希值，文件不存在或读取失败返回None
        """
        if algorithm is None:
            algorithm = cls.DEFAULT_ALGORITHM
        
        file_path = Path(file_path)
        
        if not file_path.exists() or not file_path.is_file():
            logger.warning(f"文件不存在或不是文件: {file_path}")
            return None
        
        try:
            hasher = hashlib.new(algorithm)
            
            with open(file_path, 'rb') as f:
                while chunk := f.read(cls.CHUNK_SIZE):
                    hasher.update(chunk)
            
            hash_value = hasher.hexdigest()
            logger.debug(f"文件哈希计算完成: {file_path} -> {hash_value[:16]}...")
            return hash_value
            
        except Exception as e:
            logger.error(f"文件哈希计算失败: {file_path}, 错误: {e}")
            return None
    
    @classmethod
    def hash_file_parallel(cls, file_path: Union[str, Path], 
                          algorithm: str = None, 
                          num_threads: int = 4) -> Optional[str]:
        """并行计算大文件哈希
        
        Args:
            file_path: 文件路径
            algorithm: 哈希算法，默认为sha256
            num_threads: 线程数
            
        Returns:
            十六进制哈希值，文件不存在或读取失败返回None
        """
        if algorithm is None:
            algorithm = cls.DEFAULT_ALGORITHM
        
        file_path = Path(file_path)
        
        if not file_path.exists() or not file_path.is_file():
            logger.warning(f"文件不存在或不是文件: {file_path}")
            return None
        
        try:
            file_size = file_path.stat().st_size
            
            # 小文件直接使用单线程
            if file_size < 10 * 1024 * 1024:  # 10MB
                return cls.hash_file(file_path, algorithm)
            
            # 大文件使用多线程
            chunk_size = max(file_size // num_threads, cls.CHUNK_SIZE)
            chunks = []
            
            # 分割文件为多个块
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    chunks.append(chunk)
            
            # 并行计算每个块的哈希
            hasher = hashlib.new(algorithm)
            
            def hash_chunk(chunk_data):
                chunk_hasher = hashlib.new(algorithm)
                chunk_hasher.update(chunk_data)
                return chunk_hasher.digest()
            
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = [executor.submit(hash_chunk, chunk) for chunk in chunks]
                
                # 按顺序收集结果
                for future in futures:
                    chunk_hash = future.result()
                    hasher.update(chunk_hash)
            
            hash_value = hasher.hexdigest()
            logger.debug(f"并行文件哈希计算完成: {file_path} -> {hash_value[:16]}...")
            return hash_value
            
        except Exception as e:
            logger.error(f"并行文件哈希计算失败: {file_path}, 错误: {e}")
            return None
    
    @classmethod
    def hash_path(cls, path: str, algorithm: str = None) -> str:
        """计算路径哈希
        
        Args:
            path: 文件路径
            algorithm: 哈希算法，默认为sha256
            
        Returns:
            十六进制哈希值
        """
        if algorithm is None:
            algorithm = cls.DEFAULT_ALGORITHM
        
        # 标准化路径
        normalized_path = os.path.normpath(path).replace('\\', '/')
        return cls.hash_string(normalized_path, algorithm)
    
    @classmethod
    def verify_file_hash(cls, file_path: Union[str, Path], 
                        expected_hash: str, 
                        algorithm: str = None) -> bool:
        """验证文件哈希
        
        Args:
            file_path: 文件路径
            expected_hash: 期望的哈希值
            algorithm: 哈希算法，默认为sha256
            
        Returns:
            哈希是否匹配
        """
        actual_hash = cls.hash_file(file_path, algorithm)
        
        if actual_hash is None:
            return False
        
        return actual_hash.lower() == expected_hash.lower()
    
    @classmethod
    def get_file_signature(cls, file_path: Union[str, Path]) -> Optional[dict]:
        """获取文件签名信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            包含文件哈希、大小、修改时间的字典
        """
        file_path = Path(file_path)
        
        if not file_path.exists() or not file_path.is_file():
            return None
        
        try:
            stat = file_path.stat()
            
            return {
                'path': str(file_path),
                'size': stat.st_size,
                'mtime': stat.st_mtime,
                'hash': cls.hash_file(file_path)
            }
            
        except Exception as e:
            logger.error(f"获取文件签名失败: {file_path}, 错误: {e}")
            return None
    
    @classmethod
    def compare_files(cls, file1: Union[str, Path], 
                     file2: Union[str, Path]) -> dict:
        """比较两个文件
        
        Args:
            file1: 第一个文件路径
            file2: 第二个文件路径
            
        Returns:
            比较结果字典
        """
        sig1 = cls.get_file_signature(file1)
        sig2 = cls.get_file_signature(file2)
        
        result = {
            'file1_exists': sig1 is not None,
            'file2_exists': sig2 is not None,
            'same_size': False,
            'same_hash': False,
            'same_mtime': False
        }
        
        if sig1 and sig2:
            result['same_size'] = sig1['size'] == sig2['size']
            result['same_hash'] = sig1['hash'] == sig2['hash']
            result['same_mtime'] = abs(sig1['mtime'] - sig2['mtime']) < 1.0  # 1秒误差
        
        return result
    
    @classmethod
    def batch_hash_files(cls, file_paths: list, 
                        algorithm: str = None, 
                        max_workers: int = 4) -> dict:
        """批量计算文件哈希
        
        Args:
            file_paths: 文件路径列表
            algorithm: 哈希算法，默认为sha256
            max_workers: 最大工作线程数
            
        Returns:
            文件路径到哈希值的映射字典
        """
        if algorithm is None:
            algorithm = cls.DEFAULT_ALGORITHM
        
        results = {}
        
        def hash_single_file(file_path):
            return file_path, cls.hash_file(file_path, algorithm)
        
        try:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(hash_single_file, fp) for fp in file_paths]
                
                for future in as_completed(futures):
                    file_path, hash_value = future.result()
                    results[file_path] = hash_value
            
            logger.info(f"批量哈希计算完成，处理了 {len(file_paths)} 个文件")
            return results
            
        except Exception as e:
            logger.error(f"批量哈希计算失败: {e}")
            return results
    
    @classmethod
    def is_hash_valid(cls, hash_value: str, algorithm: str = None) -> bool:
        """验证哈希值格式是否有效
        
        Args:
            hash_value: 哈希值
            algorithm: 哈希算法，默认为sha256
            
        Returns:
            哈希值是否有效
        """
        if not hash_value or not isinstance(hash_value, str):
            return False
        
        if algorithm is None:
            algorithm = cls.DEFAULT_ALGORITHM
        
        # 获取算法的预期长度
        expected_lengths = {
            'md5': 32,
            'sha1': 40,
            'sha224': 56,
            'sha256': 64,
            'sha384': 96,
            'sha512': 128
        }
        
        expected_length = expected_lengths.get(algorithm.lower())
        if expected_length is None:
            return False
        
        # 检查长度和字符
        if len(hash_value) != expected_length:
            return False
        
        try:
            int(hash_value, 16)  # 尝试解析为十六进制
            return True
        except ValueError:
            return False