#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络工具模块

提供网络相关的工具函数。
"""

import socket
import time
from typing import Optional, Tuple
from urllib.parse import urlparse

import requests
from loguru import logger


class NetworkUtils:
    """网络工具类"""
    
    DEFAULT_TIMEOUT = 10
    
    @classmethod
    def check_internet_connection(cls, timeout: int = None) -> bool:
        """检查网络连接
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            是否有网络连接
        """
        if timeout is None:
            timeout = cls.DEFAULT_TIMEOUT
        
        try:
            # 尝试连接到多个知名DNS服务器
            test_hosts = [
                ('8.8.8.8', 53),      # Google DNS
                ('114.114.114.114', 53),  # 114 DNS
                ('1.1.1.1', 53),      # Cloudflare DNS
            ]
            
            for host, port in test_hosts:
                try:
                    with socket.create_connection((host, port), timeout=timeout):
                        logger.debug(f"网络连接正常: {host}:{port}")
                        return True
                except (socket.timeout, socket.error):
                    continue
            
            logger.warning("网络连接检查失败")
            return False
            
        except Exception as e:
            logger.error(f"网络连接检查异常: {e}")
            return False
    
    @classmethod
    def check_url_accessible(cls, url: str, timeout: int = None) -> bool:
        """检查URL是否可访问
        
        Args:
            url: 要检查的URL
            timeout: 超时时间（秒）
            
        Returns:
            URL是否可访问
        """
        if timeout is None:
            timeout = cls.DEFAULT_TIMEOUT
        
        try:
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            accessible = response.status_code < 400
            
            if accessible:
                logger.debug(f"URL可访问: {url} (状态码: {response.status_code})")
            else:
                logger.warning(f"URL不可访问: {url} (状态码: {response.status_code})")
            
            return accessible
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"URL访问检查失败: {url}, 错误: {e}")
            return False
        except Exception as e:
            logger.error(f"URL访问检查异常: {url}, 错误: {e}")
            return False
    
    @classmethod
    def get_public_ip(cls, timeout: int = None) -> Optional[str]:
        """获取公网IP地址
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            公网IP地址，获取失败返回None
        """
        if timeout is None:
            timeout = cls.DEFAULT_TIMEOUT
        
        # 多个IP查询服务
        ip_services = [
            'https://api.ipify.org',
            'https://icanhazip.com',
            'https://ipecho.net/plain',
            'https://myexternalip.com/raw',
        ]
        
        for service in ip_services:
            try:
                response = requests.get(service, timeout=timeout)
                if response.status_code == 200:
                    ip = response.text.strip()
                    if cls._is_valid_ip(ip):
                        logger.debug(f"获取公网IP成功: {ip} (来源: {service})")
                        return ip
            except Exception as e:
                logger.debug(f"IP服务访问失败: {service}, 错误: {e}")
                continue
        
        logger.warning("获取公网IP失败")
        return None
    
    @classmethod
    def get_local_ip(cls) -> Optional[str]:
        """获取本地IP地址
        
        Returns:
            本地IP地址，获取失败返回None
        """
        try:
            # 连接到外部地址获取本地IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(('8.8.8.8', 80))
                local_ip = s.getsockname()[0]
                logger.debug(f"获取本地IP成功: {local_ip}")
                return local_ip
        except Exception:
            try:
                # 备选方案：获取hostname对应的IP
                local_ip = socket.gethostbyname(socket.gethostname())
                if local_ip != '127.0.0.1':
                    logger.debug(f"获取本地IP成功(备选): {local_ip}")
                    return local_ip
            except Exception:
                pass
        
        logger.warning("获取本地IP失败")
        return None
    
    @classmethod
    def _is_valid_ip(cls, ip: str) -> bool:
        """验证IP地址格式
        
        Args:
            ip: IP地址字符串
            
        Returns:
            是否为有效的IP地址
        """
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False
    
    @classmethod
    def ping_host(cls, host: str, timeout: int = None) -> Tuple[bool, Optional[float]]:
        """Ping主机
        
        Args:
            host: 主机地址
            timeout: 超时时间（秒）
            
        Returns:
            (是否可达, 响应时间)
        """
        if timeout is None:
            timeout = cls.DEFAULT_TIMEOUT
        
        try:
            start_time = time.time()
            
            # 尝试TCP连接
            with socket.create_connection((host, 80), timeout=timeout):
                response_time = (time.time() - start_time) * 1000  # 转换为毫秒
                logger.debug(f"Ping成功: {host} ({response_time:.2f}ms)")
                return True, response_time
                
        except (socket.timeout, socket.error) as e:
            logger.debug(f"Ping失败: {host}, 错误: {e}")
            return False, None
        except Exception as e:
            logger.error(f"Ping异常: {host}, 错误: {e}")
            return False, None
    
    @classmethod
    def download_file(cls, url: str, local_path: str, 
                     timeout: int = None, 
                     chunk_size: int = 8192) -> bool:
        """下载文件
        
        Args:
            url: 文件URL
            local_path: 本地保存路径
            timeout: 超时时间（秒）
            chunk_size: 分块大小
            
        Returns:
            下载是否成功
        """
        if timeout is None:
            timeout = cls.DEFAULT_TIMEOUT
        
        try:
            logger.info(f"开始下载文件: {url} -> {local_path}")
            
            with requests.get(url, stream=True, timeout=timeout) as response:
                response.raise_for_status()
                
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
            
            logger.info(f"文件下载成功: {local_path}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"文件下载失败: {url}, 错误: {e}")
            return False
        except Exception as e:
            logger.error(f"文件下载异常: {url}, 错误: {e}")
            return False
    
    @classmethod
    def get_network_info(cls) -> dict:
        """获取网络信息
        
        Returns:
            网络信息字典
        """
        info = {
            'hostname': socket.gethostname(),
            'local_ip': cls.get_local_ip(),
            'public_ip': None,
            'internet_connected': False,
            'dns_working': False
        }
        
        try:
            # 检查网络连接
            info['internet_connected'] = cls.check_internet_connection()
            
            if info['internet_connected']:
                # 获取公网IP
                info['public_ip'] = cls.get_public_ip()
                
                # 检查DNS
                try:
                    socket.gethostbyname('www.baidu.com')
                    info['dns_working'] = True
                except socket.error:
                    info['dns_working'] = False
            
            logger.debug(f"网络信息: {info}")
            return info
            
        except Exception as e:
            logger.error(f"获取网络信息失败: {e}")
            return info
    
    @classmethod
    def parse_speed_limit(cls, speed_str: str) -> Optional[int]:
        """解析速度限制字符串
        
        Args:
            speed_str: 速度字符串，如 '10MB/s', '1.5GB/s'
            
        Returns:
            每秒字节数，解析失败返回None
        """
        try:
            speed_str = speed_str.upper().strip()
            
            # 移除 '/S' 后缀
            if speed_str.endswith('/S'):
                speed_str = speed_str[:-2]
            
            # 解析数值和单位
            units = {
                'B': 1,
                'KB': 1024,
                'MB': 1024 * 1024,
                'GB': 1024 * 1024 * 1024,
                'TB': 1024 * 1024 * 1024 * 1024
            }
            
            for unit, multiplier in units.items():
                if speed_str.endswith(unit):
                    value_str = speed_str[:-len(unit)].strip()
                    value = float(value_str)
                    bytes_per_second = int(value * multiplier)
                    logger.debug(f"速度限制解析: {speed_str} -> {bytes_per_second} bytes/s")
                    return bytes_per_second
            
            # 如果没有单位，假设为字节
            bytes_per_second = int(float(speed_str))
            logger.debug(f"速度限制解析(无单位): {speed_str} -> {bytes_per_second} bytes/s")
            return bytes_per_second
            
        except (ValueError, AttributeError) as e:
            logger.error(f"速度限制解析失败: {speed_str}, 错误: {e}")
            return None
    
    @classmethod
    def format_speed(cls, bytes_per_second: float) -> str:
        """格式化传输速度
        
        Args:
            bytes_per_second: 每秒字节数
            
        Returns:
            格式化的速度字符串
        """
        if bytes_per_second < 1024:
            return f"{bytes_per_second:.1f} B/s"
        elif bytes_per_second < 1024 * 1024:
            return f"{bytes_per_second / 1024:.1f} KB/s"
        elif bytes_per_second < 1024 * 1024 * 1024:
            return f"{bytes_per_second / (1024 * 1024):.1f} MB/s"
        else:
            return f"{bytes_per_second / (1024 * 1024 * 1024):.1f} GB/s"
    
    @classmethod
    def format_size(cls, bytes_size: int) -> str:
        """格式化文件大小
        
        Args:
            bytes_size: 字节数
            
        Returns:
            格式化的大小字符串
        """
        if bytes_size < 1024:
            return f"{bytes_size} B"
        elif bytes_size < 1024 * 1024:
            return f"{bytes_size / 1024:.1f} KB"
        elif bytes_size < 1024 * 1024 * 1024:
            return f"{bytes_size / (1024 * 1024):.1f} MB"
        else:
            return f"{bytes_size / (1024 * 1024 * 1024):.1f} GB"