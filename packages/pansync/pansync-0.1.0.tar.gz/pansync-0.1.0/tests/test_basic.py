#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础功能测试
"""

import os
import tempfile
import unittest
from unittest.mock import Mock, patch

from src.pansync.config import ConfigManager, ClientManager
from src.pansync.core import IndexManager, LockManager, FileManager
from src.pansync.utils import HashUtils, FileUtils, NetworkUtils, time_utils


class TestConfigManager(unittest.TestCase):
    """配置管理器测试"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, 'test_config.yaml')
        self.config_manager = ConfigManager(self.config_path)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_default_config(self):
        """测试创建默认配置"""
        self.config_manager._create_default_config()
        self.assertTrue(os.path.exists(self.config_path))
    
    def test_get_set_config(self):
        """测试配置读写"""
        self.config_manager._create_default_config()
        
        # 测试设置和获取
        self.config_manager.set('test.key', 'test_value')
        value = self.config_manager.get('test.key')
        self.assertEqual(value, 'test_value')
        
        # 测试默认值
        value = self.config_manager.get('nonexistent.key', 'default')
        self.assertEqual(value, 'default')
    
    def test_validate_config(self):
        """测试配置验证"""
        self.config_manager._create_default_config()
        
        # 设置必需的配置项
        self.config_manager.set('baidu.app_id', 'test_app_id')
        self.config_manager.set('baidu.app_key', 'test_app_key')
        self.config_manager.set('baidu.secret_key', 'test_secret_key')
        
        result = self.config_manager.validate_config()
        self.assertTrue(result)


class TestClientManager(unittest.TestCase):
    """客户端管理器测试"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, 'test_config.yaml')
        self.config_manager = ConfigManager(self.config_path)
        self.config_manager._create_default_config()
        self.client_manager = ClientManager(self.config_manager)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_client_id_generation(self):
        """测试客户端ID生成"""
        client_id = self.client_manager.get_client_id()
        self.assertIsNotNone(client_id)
        self.assertIsInstance(client_id, str)
        self.assertTrue(len(client_id) > 0)
        
        # 多次调用应返回相同ID
        client_id2 = self.client_manager.get_client_id()
        self.assertEqual(client_id, client_id2)
    
    def test_client_info(self):
        """测试客户端信息"""
        client_name = self.client_manager.get_client_name()
        self.assertIsNotNone(client_name)
        
        client_ip = self.client_manager.get_client_ip()
        self.assertIsNotNone(client_ip)
        
        platform = self.client_manager.get_platform()
        self.assertIsNotNone(platform)


class TestHashUtils(unittest.TestCase):
    """哈希工具测试"""
    
    def setUp(self):
        self.hash_utils = HashUtils()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_string_hash(self):
        """测试字符串哈希"""
        test_string = "Hello, World!"
        hash_value = self.hash_utils.calculate_string_hash(test_string)
        
        self.assertIsNotNone(hash_value)
        self.assertIsInstance(hash_value, str)
        self.assertTrue(len(hash_value) > 0)
        
        # 相同字符串应产生相同哈希
        hash_value2 = self.hash_utils.calculate_string_hash(test_string)
        self.assertEqual(hash_value, hash_value2)
    
    def test_file_hash(self):
        """测试文件哈希"""
        # 创建测试文件
        test_file = os.path.join(self.temp_dir, 'test.txt')
        test_content = "This is a test file content."
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # 计算文件哈希
        hash_value = self.hash_utils.calculate_file_hash(test_file)
        
        self.assertIsNotNone(hash_value)
        self.assertIsInstance(hash_value, str)
        self.assertTrue(len(hash_value) > 0)
        
        # 验证文件哈希
        is_valid = self.hash_utils.verify_file_hash(test_file, hash_value)
        self.assertTrue(is_valid)
    
    def test_hash_validation(self):
        """测试哈希值验证"""
        valid_md5 = "5d41402abc4b2a76b9719d911017c592"
        valid_sha256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        
        self.assertTrue(self.hash_utils.is_valid_hash(valid_md5, 'md5'))
        self.assertTrue(self.hash_utils.is_valid_hash(valid_sha256, 'sha256'))
        
        invalid_hash = "invalid_hash"
        self.assertFalse(self.hash_utils.is_valid_hash(invalid_hash, 'md5'))


class TestFileUtils(unittest.TestCase):
    """文件工具测试"""
    
    def setUp(self):
        self.file_utils = FileUtils()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_ensure_directory(self):
        """测试确保目录存在"""
        test_dir = os.path.join(self.temp_dir, 'subdir', 'nested')
        
        self.assertFalse(os.path.exists(test_dir))
        
        result = self.file_utils.ensure_directory(test_dir)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(test_dir))
    
    def test_safe_copy(self):
        """测试安全复制"""
        # 创建源文件
        src_file = os.path.join(self.temp_dir, 'source.txt')
        dst_file = os.path.join(self.temp_dir, 'destination.txt')
        test_content = "Test file content"
        
        with open(src_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # 复制文件
        result = self.file_utils.safe_copy(src_file, dst_file)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(dst_file))
        
        # 验证内容
        with open(dst_file, 'r', encoding='utf-8') as f:
            copied_content = f.read()
        
        self.assertEqual(test_content, copied_content)
    
    def test_format_size(self):
        """测试文件大小格式化"""
        self.assertEqual(self.file_utils.format_size(0), "0 B")
        self.assertEqual(self.file_utils.format_size(1024), "1.0 KB")
        self.assertEqual(self.file_utils.format_size(1024 * 1024), "1.0 MB")
        self.assertEqual(self.file_utils.format_size(1024 * 1024 * 1024), "1.0 GB")
    
    def test_find_files(self):
        """测试文件查找"""
        # 创建测试文件
        test_files = ['test1.txt', 'test2.py', 'subdir/test3.txt']
        
        for file_path in test_files:
            full_path = os.path.join(self.temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write('test')
        
        # 查找所有文件
        found_files = list(self.file_utils.find_files(self.temp_dir))
        self.assertEqual(len(found_files), 3)
        
        # 查找特定扩展名
        txt_files = list(self.file_utils.find_files(
            self.temp_dir, 
            include_patterns=['*.txt']
        ))
        self.assertEqual(len(txt_files), 2)


class TestTimeUtils(unittest.TestCase):
    """时间工具测试"""
    
    def test_beijing_time(self):
        """测试北京时间"""
        beijing_time = time_utils.get_beijing_time()
        self.assertIsNotNone(beijing_time)
        
        # 检查时区
        self.assertEqual(beijing_time.tzinfo.utcoffset(None).total_seconds(), 8 * 3600)
    
    def test_time_formatting(self):
        """测试时间格式化"""
        beijing_time = time_utils.get_beijing_time()
        formatted = time_utils.format_time(beijing_time)
        
        self.assertIsNotNone(formatted)
        self.assertIsInstance(formatted, str)
        self.assertTrue(len(formatted) > 0)
    
    def test_iso_time_parsing(self):
        """测试ISO时间解析"""
        test_iso = "2023-12-01T12:00:00+08:00"
        parsed_time = time_utils.parse_iso_time(test_iso)
        
        self.assertIsNotNone(parsed_time)
        self.assertEqual(parsed_time.hour, 12)
        self.assertEqual(parsed_time.day, 1)
        self.assertEqual(parsed_time.month, 12)


class TestNetworkUtils(unittest.TestCase):
    """网络工具测试"""
    
    def setUp(self):
        self.network_utils = NetworkUtils()
    
    @patch('socket.create_connection')
    def test_check_network(self, mock_connection):
        """测试网络连接检查"""
        # 模拟网络连接成功
        mock_connection.return_value = Mock()
        result = self.network_utils.check_network()
        self.assertTrue(result)
        
        # 模拟网络连接失败
        mock_connection.side_effect = Exception("Connection failed")
        result = self.network_utils.check_network()
        self.assertFalse(result)
    
    def test_format_speed(self):
        """测试速度格式化"""
        self.assertEqual(self.network_utils.format_speed(0), "0 B/s")
        self.assertEqual(self.network_utils.format_speed(1024), "1.0 KB/s")
        self.assertEqual(self.network_utils.format_speed(1024 * 1024), "1.0 MB/s")
    
    def test_parse_speed_limit(self):
        """测试速度限制解析"""
        self.assertEqual(self.network_utils.parse_speed_limit("1MB"), 1024 * 1024)
        self.assertEqual(self.network_utils.parse_speed_limit("500KB"), 500 * 1024)
        self.assertEqual(self.network_utils.parse_speed_limit("0"), 0)


class TestIndexManager(unittest.TestCase):
    """索引管理器测试"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, 'test_config.yaml')
        
        # 创建配置管理器
        self.config_manager = ConfigManager(self.config_path)
        self.config_manager._create_default_config()
        self.config_manager.set('sync.paths.local', self.temp_dir)
        
        self.index_manager = IndexManager(self.config_manager)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_scan_local_files(self):
        """测试本地文件扫描"""
        # 创建测试文件
        test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('test content')
        
        # 扫描文件
        changed_files = self.index_manager.scan_local_files()
        
        self.assertIsInstance(changed_files, list)
        self.assertIn('test.txt', changed_files)
        
        # 检查索引
        file_index = self.index_manager.get_file_index('test.txt')
        self.assertIsNotNone(file_index)
        self.assertEqual(file_index.status, 'new')
    
    def test_file_index_operations(self):
        """测试文件索引操作"""
        # 创建测试文件
        test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('test content')
        
        # 扫描文件
        self.index_manager.scan_local_files()
        
        # 测试更新索引
        self.index_manager.update_file_index('test.txt', status='synced')
        file_index = self.index_manager.get_file_index('test.txt')
        self.assertEqual(file_index.status, 'synced')
        
        # 测试标记为已同步
        self.index_manager.mark_file_synced('test.txt')
        file_index = self.index_manager.get_file_index('test.txt')
        self.assertEqual(file_index.status, 'synced')
        
        # 测试获取统计信息
        stats = self.index_manager.get_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn('total', stats)
        self.assertIn('synced', stats)


if __name__ == '__main__':
    unittest.main()