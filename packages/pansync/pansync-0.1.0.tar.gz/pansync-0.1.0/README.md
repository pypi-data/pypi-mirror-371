# PanSync - 百度网盘同步工具

基于 bypy 的多客户端百度网盘同步工具，支持定时同步、冲突检测和分布式锁管理。

## 功能特性

- 🔄 **智能同步**: 基于文件哈希和时间戳的双向同步
- 🔒 **分布式锁**: 防止多客户端同时操作的锁机制
- 🗑️ **垃圾回收**: 本地删除的文件移至云端 trash 目录
- ⚙️ **灵活配置**: 支持定时同步、限速、并发控制
- 🖥️ **多客户端**: 自动客户端注册和管理
- 📊 **状态管理**: 二进制索引文件记录文件状态
- 🚀 **服务化**: 支持 Supervisor 管理和开机自启

## 安装

```bash
# 克隆项目
git clone <repository-url>
cd pansync

# 安装依赖
pip install -r requirements.txt

# 安装项目
pip install -e .
```

## 配置

配置文件位于 `~/.pansync/config.yaml`，首次运行会自动创建。

## 使用

```bash
# 启动同步服务
pansync start

# 停止同步服务
pansync stop

# 查看状态
pansync status

# 手动同步
pansync sync
```

## 架构设计

### 多客户端同步协议

1. **锁获取**: 客户端通过 `.pansync/.config/lock.txt` 获取分布式锁
2. **索引同步**: 上传本地索引到 `.pansync/.index.dat`
3. **文件同步**: 根据索引差异进行文件上传/下载
4. **状态同步**: 通过 `.pansync/.config/.index.dat` 维护文件状态

### 文件同步逻辑

- **云端删除** → 本地删除
- **本地删除** → 移至云端 trash 目录
- **双向修改** → 冲突检测和报告

## 开发

```bash
# 开发模式安装
pip install -e .[dev]

# 运行测试
pytest tests/

# 代码格式化
black src/
flake8 src/
```

## 许可证

MIT License