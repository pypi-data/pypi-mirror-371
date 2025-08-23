# FLV Timestamp Analyzer

> FLV音视频时间戳分析工具，支持命令行使用和MCP协议集成，可检测FLV文件中的时间戳异常。

## 🚀 快速安装

### 基础安装
```bash
pip install flvmeta-timestamp-analyzer
```

### MCP功能完整支持
如需使用MCP功能，建议安装FastMCP依赖：
```bash
pip install flvmeta-timestamp-analyzer[fastmcp]
```
或分步安装：
```bash
pip install flvmeta-timestamp-analyzer
pip install fastmcp mcp pydantic
```

**依赖要求**：需要安装 [flvmeta](https://github.com/noirotm/flvmeta) 工具：
- macOS: `brew install flvmeta`
- Linux: `sudo apt-get install flvmeta`
- Windows: 下载 [releases](https://github.com/noirotm/flvmeta/releases)

## 💡 使用方法

### 命令行使用
```bash
# 安装后直接使用
flv-timestamp-analyzer input.flv

# 指定输出文件
flv-timestamp-analyzer input.flv analysis.html
```

### 作为Python模块使用
```bash
# 从源码目录运行
python3 flvmeta_timestamp_analyzer/analyzer.py input.flv
```

## 🤖 AI客户端集成 (MCP)

本工具支持 [Model Context Protocol (MCP)](https://modelcontextprotocol.io) 协议，可集成到支持MCP的AI客户端中。

> **重要提示**：
> - 使用MCP功能需要先安装包：`pip install flvmeta-timestamp-analyzer[fastmcp]`
> - 推荐安装FastMCP依赖以获得更好的MCP协议支持和性能
> - 1.0.10+ 版本已解决环境冲突问题，支持全局安装配置

### Claude Desktop 配置

在 `~/.config/claude/claude_desktop_config.json` (Linux/macOS) 或 `%APPDATA%\Claude\claude_desktop_config.json` (Windows) 中添加：

#### 推荐方式 (全局安装，v1.0.10+)
```json
{
  "mcpServers": {
    "flv-timestamp-analyzer": {
      "command": "flv-mcp-server",
      "args": [],
      "env": {}
    }
  }
}
```

#### 兼容方式 (适用于较老版本)
```json
{
  "mcpServers": {
    "flv-timestamp-analyzer": {
      "command": "python3",
      "args": ["-m", "flvmeta_timestamp_analyzer.mcp_server"]
    }
  }
}
```

### Cline (VSCode) 配置

在 VSCode 设置中的 Cline MCP 服务器配置：

#### 推荐方式 (v1.0.10+)
```json
{
  "name": "flv-timestamp-analyzer",
  "command": "flv-mcp-server",
  "args": []
}
```

#### 兼容方式
```json
{
  "name": "flv-timestamp-analyzer",
  "command": "python3",
  "args": ["-m", "flvmeta_timestamp_analyzer.mcp_server"]
}
```

### Continue.dev 配置

在 `~/.continue/config.json` 中添加：

#### 推荐方式 (v1.0.10+)
```json
{
  "experimental": {
    "modelContextProtocol": {
      "servers": [
        {
          "name": "flv-timestamp-analyzer",
          "command": ["flv-mcp-server"]
        }
      ]
    }
  }
}
```

#### 兼容方式
```json
{
  "experimental": {
    "modelContextProtocol": {
      "servers": [
        {
          "name": "flv-timestamp-analyzer",
          "command": ["python3", "-m", "flvmeta_timestamp_analyzer.mcp_server"]
        }
      ]
    }
  }
}
```

### Cursor 配置

在 Cursor 的设置中添加 MCP 服务器：

#### 推荐方式 (v1.0.10+)
```json
{
  "mcp": {
    "servers": {
      "flv-timestamp-analyzer": {
        "command": "flv-mcp-server",
        "args": []
      }
    }
  }
}
```

#### 兼容方式
```json
{
  "mcp": {
    "servers": {
      "flv-timestamp-analyzer": {
        "command": "python3",
        "args": ["-m", "flvmeta_timestamp_analyzer.mcp_server"]
      }
    }
  }
}
```

### 源码部署方式 (开发者)

如果你从源码运行而非pip安装，使用以下配置：

```json
{
  "mcpServers": {
    "flv-timestamp-analyzer": {
      "command": "python3",
      "args": ["/path/to/flvmeta-timestamp-analyzer/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/flvmeta-timestamp-analyzer"
      }
    }
  }
}
```

### 跨平台兼容性

- **Windows**: 使用 `python` 而非 `python3`
- **macOS/Linux**: 使用 `python3`
- **包安装**: 推荐使用 `-m` 方式运行模块
- **路径**: Windows 使用反斜杠 `\`，Unix 系统使用正斜杠 `/`

**Windows 示例**：
```json
{
  "mcpServers": {
    "flv-timestamp-analyzer": {
      "command": "python",
      "args": ["-m", "flvmeta_timestamp_analyzer.mcp_server"]
    }
  }
}
```

## 📊 功能特点

- ✅ **时间戳分析**：检测音视频时间戳异常（回退、跳跃、缺失帧）
- ✅ **可视化报告**：生成交互式HTML图表，支持缩放拖拽
- ✅ **详细统计**：提供帧数、时长、间隔统计信息
- ✅ **命令行工具**：支持批量处理和脚本集成
- ✅ **MCP协议**：可集成到AI客户端作为分析工具
- ✅ **多平台支持**：Windows、macOS、Linux

## 📈 输出示例

### 命令行输出
```
============================================================
FLV音视频时间戳分析报告: test.flv
============================================================
总标签数: 486

[音频统计]
音频帧数: 194
音频时长: 24729ms
平均间隔: 128.13ms | 最大间隔: 204ms | 最小间隔: 58ms

[视频统计]
视频帧数: 291
视频时长: 24820ms
平均间隔: 85.59ms | 最大间隔: 325ms | 最小间隔: 60ms
============================================================
图表已保存至: /path/to/test_timestamp_analysis.html
```

### MCP JSON 响应
```json
{
  "status": "success",
  "data": {
    "filename": "test.flv",
    "metadata": {
      "width": 360,
      "height": 640,
      "framerate": 12,
      "audiocodecid": 10,
      "videocodecid": 7
    },
    "audio": {
      "stats": {
        "avg": 128.13,
        "max": 204,
        "min": 58,
        "anomalies": []
      }
    },
    "video": {
      "stats": {
        "avg": 85.59,
        "max": 325,
        "min": 60,
        "anomalies": []
      }
    },
    "total_tags": 486
  }
}
```

## 🔧 测试MCP集成

```bash
# 克隆仓库
git clone https://github.com/Soar-Coding-Life/flvmeta-timestamp-analyzer.git
cd flvmeta-timestamp-analyzer

# 安装依赖
pip install -r requirements.txt

# 测试MCP服务
python3 test_client.py your_file.flv
```

## 🐛 故障排除

### 常见问题

1. **flvmeta not found**
   ```bash
   # 检查是否安装
   flvmeta -V
   # 如未安装，按平台安装：
   # macOS: brew install flvmeta
   # Linux: sudo apt-get install flvmeta
   # Windows: 下载 https://github.com/noirotm/flvmeta/releases
   ```

2. **Python命令问题**
   ```bash
   # Linux/macOS 使用
   python3 -m flvmeta_timestamp_analyzer.mcp_server
   
   # Windows 使用
   python -m flvmeta_timestamp_analyzer.mcp_server
   ```

3. **MCP连接失败**
   - 确保已安装包: `pip install flvmeta-timestamp-analyzer[fastmcp]`
   - v1.0.10+: 直接使用 `flv-mcp-server` 命令
   - 较老版本: 检查Python命令是否正确 (`python` vs `python3`)
   - 查看 `mcp_server.log` 日志文件
   - 检查AI客户端的MCP配置格式

4. **环境冲突问题**
   ```bash
   # 如遇到环境冲突，使用全局安装方式
   pip install --upgrade flvmeta-timestamp-analyzer[fastmcp]
   # 然后使用 flv-mcp-server 命令而非 python -m 方式
   ```

5. **FastMCP依赖问题**
   ```bash
   # 单独安装FastMCP相关依赖
   pip install fastmcp mcp pydantic
   # 或使用额外依赖安装
   pip install flvmeta-timestamp-analyzer[fastmcp]
   ```

6. **路径问题 (源码运行)**
   ```bash
   # 确保正确设置 PYTHONPATH (仅源码运行需要)
   export PYTHONPATH="/path/to/flvmeta-timestamp-analyzer:$PYTHONPATH"
   ```

### 跨平台兼容性说明

本工具已针对多平台进行优化：

- ✅ **Windows** (Python 3.6+)
- ✅ **macOS** (Python 3.6+) 
- ✅ **Linux** (Python 3.6+)
- ✅ **架构支持**: x86_64, ARM64, 等

**平台差异**:
- Windows: 使用 `python` 命令
- macOS/Linux: 使用 `python3` 命令
- 路径分隔符自动处理
- 编码问题已解决 (UTF-8)

### 调试模式
```bash
# 查看MCP服务日志
tail -f mcp_server.log

# 直接测试分析功能
flv-timestamp-analyzer test.flv

# 测试模块导入
python3 -c "import flvmeta_timestamp_analyzer; print('导入成功')"
```

## 📝 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🔗 相关链接

- [PyPI 包](https://pypi.org/project/flvmeta-timestamp-analyzer/)
- [GitHub 仓库](https://github.com/Soar-Coding-Life/flvmeta-timestamp-analyzer)
- [flvmeta 工具](https://github.com/noirotm/flvmeta)
- [MCP 协议规范](https://modelcontextprotocol.io)