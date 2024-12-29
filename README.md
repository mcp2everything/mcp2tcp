# mcp2tcp: 连接物理世界与AI大模型的桥梁 

[English](README_EN.md) | 简体中文

<div align="center">
    <img src="docs/images/logo.png" alt="mcp2tcp Logo" width="200"/>
    <p>通过自然语言控制硬件，开启物联网新纪元</p>
</div>

## 系统架构

<div align="center">
    <img src="docs/images/stru_chs.png" alt="系统架构图" width="800"/>
    <p>mcp2tcp 系统架构图</p>
</div>

## 工作流程

<div align="center">
    <img src="docs/images/workflow_chs.png" alt="工作流程图" width="800"/>
    <p>mcp2tcp 工作流程图</p>
</div>

## 项目愿景

mcp2tcp 将TCP设备接入AI大模型的项目，它通过 Model Context Protocol (MCP) 将物理世界与 AI 大模型无缝连接。最终实现：
- 用自然语言控制你的硬件设备
- AI 实时响应并调整物理参数
- 让你的设备具备理解和执行复杂指令的能力

## 主要特性

- **智能TCP通信**
  - 自动检测和配置TCP设备 用户也可指定TCP号
  - 支持多种波特率（默认 115200）
  - 实时状态监控和错误处理

- **MCP 协议集成**
  - 完整支持 Model Context Protocol
  - 支持资源管理和工具调用
  - 灵活的提示词系统

## 支持的客户端

mcp2tcp 支持所有实现了 MCP 协议的客户端，包括：

| 客户端 | 特性支持 | 说明 |
|--------|----------|------|
| Claude Desktop | 完整支持 | 推荐使用，支持所有 MCP 功能 |
| Continue | 完整支持 | 优秀的开发工具集成 |
| Cline | 资源+工具 | 支持多种 AI 提供商 |
| Zed | 基础支持 | 支持提示词命令 |
| Sourcegraph Cody | 资源支持 | 通过 OpenCTX 集成 |
| Firebase Genkit | 部分支持 | 支持资源列表和工具 |

## 支持的 AI 模型

得益于灵活的客户端支持，mcp2tcp 可以与多种 AI 模型协同工作：

### 云端模型
- OpenAI (GPT-4, GPT-3.5)
- Anthropic Claude
- Google Gemini
- AWS Bedrock
- Azure OpenAI
- Google Cloud Vertex AI

### 本地模型
- LM Studio 支持的所有模型
- Ollama 支持的所有模型
- 任何兼容 OpenAI API 的模型

### 准备
Python3.11 或更高版本
Claude Desktop 或 Cline


## 快速开始

### 1. 安装

#### Windows用户
下载 [install.py](https://raw.githubusercontent.com/mcp2everything/mcp2tcp/main/install.py) 
```bash
python install.py
```
#### macOS用户
```bash
# 下载安装脚本
curl -O https://raw.githubusercontent.com/mcp2everything/mcp2tcp/main/install_macos.py

# 运行安装脚本
python3 install_macos.py
```

#### Ubuntu/Raspberry Pi用户
```bash
# 下载安装脚本
curl -O https://raw.githubusercontent.com/mcp2everything/mcp2tcp/main/install_ubuntu.py

# 运行安装脚本
python3 install_ubuntu.py
```

安装脚本会自动完成以下操作：
- ✅ 检查系统环境
- ✅ 安装必要的依赖
- ✅ 创建默认配置文件
- ✅ 配置Claude桌面版（如果已安装）
- ✅ 检查TCP设备

### 手动分步安装依赖
```bash
windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
MacOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```
主要依赖uv工具，所以当python和uv以及Claude或Cline安装好后就可以了。

### 基本配置
在你的 MCP 客户端（如 Claude Desktop 或 Cline）配置文件中添加以下内容：
注意：如果使用的自动安装那么会自动配置Calude Desktop无需此步。
使用默认配置文件：
```json
{
    "mcpServers": {
        "mcp2tcp": {
            "command": "uvx",
            "args": [
                "mcp2tcp"
            ]
        }
    }
}
```
> 注意：修改配置后需要重启Cline或者Claude客户端软件

配置TCP和命令：
注意下面的配置默认为COM11 需要根据实际进行修改
```yaml
# config.yaml
tcp:
  # TCP服务器配置
  remote_ip: "127.0.0.1"  # 远端IP地址
  port: 9999  # 端口号
  connect_timeout: 3.0  # 连接超时时间，单位为秒
  receive_timeout: 2.0  # 接收超时时间，单位为秒
  communication_type: "client"  # 通信类型，client或server
  response_start_string: "CMD"  # 可选，TCP应答的开始字符串，默认为OK

commands:
  # PWM控制命令
  set_pwm:
    command: "CMD_PWM {frequency}"  # frequency为0-100的整数，表示PWM占空比
    need_parse: false  # 不需要解析响应内容
    data_type: "ascii"  # 数据类型，ascii或hex
    parameters:
      - name: "frequency"
        type: "integer"
        description: "PWM frequency value (0-100)"
        required: true
    prompts:
      - "把PWM调到最大 (frequency=100)"
      - "把PWM调到最小 (frequency=0)"
      - "请将PWM设置为{frequency} (0-100的整数)"
      - "关闭PWM (frequency=0)"
      - "把PWM调到一半 (frequency=50)"
```
## 配置说明
### 配置文件位置
配置文件（`config.yaml`）可以放在位置：
用户主目录（推荐个人使用）
```bash
# Windows系统
C:\Users\用户名\.mcp2tcp\config.yaml

# macOS系统
/Users/用户名/.mcp2tcp/config.yaml

# Linux系统
/home/用户名/.mcp2tcp/config.yaml
```
- 适用场景：个人配置
- 需要创建 `.mcp2tcp` 目录：
  ```bash
  # Windows系统（在命令提示符中）
  mkdir "%USERPROFILE%\.mcp2tcp"
  
  # macOS/Linux系统
  mkdir -p ~/.mcp2tcp
  ```

### TCP配置 命令配置进阶
在 `config.yaml` 中添加自定义命令：


使用真实TCP
```yaml
# config.yaml
 # PICO信息查询命令
  get_pico_info:
    command: "CMD_PICO_INFO"  # 实际发送的命令格式，server会自动添加\r\n
    need_parse: true  # 需要解析响应内容
    data_type: "ascii"  # 数据类型，ascii或hex
    prompts:
      - "查询Pico板信息"
      - "显示开发板状态"
```
指定配置文件：
比如指定加载Pico配置文件：Pico_config.yaml
```json
{
    "mcpServers": {
        "mcp2tcp": {
            "command": "uvx",
            "args": [
                "mcp2tcp",
                "--config",
                "Pico"  //指定配置文件名，不需要添加_config.yaml后缀
            ]
        }
    }
}
```
为了能使用多个TCP，我们可以新增多个mcp2tcp的服务 指定不同的配置文件名即可。
如果要接入多个设备，如有要连接第二个设备：
指定加载Pico2配置文件：Pico2_config.yaml
```json
{
    "mcpServers": {
        "mcp2tcp2": {
            "command": "uvx",
            "args": [
                "mcp2tcp",
                "--config",
                "Pico2"  //指定配置文件名，不需要添加_config.yaml后缀
            ]
        }
    }
}
```


## 测试

在开始使用之前，建议先进行测试以确保一切正常工作。

#### 1. 启动测试服务器

首先，启动测试目录下的 TCP 服务器来模拟硬件设备：

```bash
# 进入项目目录
cd tests

# 启动测试服务器
python tcp_server.py
```

服务器将在本地启动，监听端口 9999。你会看到类似这样的输出：
```
TCP server started on 127.0.0.1:9999
Waiting for connections...
```


### 启动客户端Claude 桌面版或Cline
<div align="center">
    <img src="docs/images/test_output.png" alt="Cline Configuration Example" width="600"/>
    <p>Example in Cline</p>
</div>

### 从源码快速开始
1. 从源码安装
```bash
# 通过源码安装：
git clone https://github.com/mcp2everything/mcp2tcp.git
cd mcp2tcp

# 创建虚拟环境
uv venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 安装开发依赖
uv pip install --editable .
```


如果使用真实TCP
```yaml
# config.yaml
tcp:
  # TCP服务器配置
  remote_ip: "127.0.0.1"  # 远端IP地址
  port: 9999  # 端口号
  connect_timeout: 3.0  # 连接超时时间，单位为秒
  receive_timeout: 2.0  # 接收超时时间，单位为秒
  communication_type: "client"  # 通信类型，client或server
  response_start_string: "CMD"  # 可选，TCP应答的开始字符串，默认为OK

commands:
  # PWM控制命令
  set_pwm:
    command: "CMD_PWM {frequency}"  # frequency为0-100的整数，表示PWM占空比
    need_parse: false  # 不需要解析响应内容
    data_type: "ascii"  # 数据类型，ascii或hex
    parameters:
      - name: "frequency"
        type: "integer"
        description: "PWM frequency value (0-100)"
        required: true
    prompts:
      - "把PWM调到最大 (frequency=100)"
      - "把PWM调到最小 (frequency=0)"
      - "请将PWM设置为{frequency} (0-100的整数)"
      - "关闭PWM (frequency=0)"
      - "把PWM调到一半 (frequency=50)"
```



### MCP客户端配置

在使用支持MCP协议的客户端（如Claude Desktop或Cline）时，需要在客户端的配置文件中添加以下内容：
直接自动安装的配置方式
源码开发的配置方式
#### 使用默认演示参数：
```json
{
    "mcpServers": {
        "mcp2tcp": {
            "command": "uv",
            "args": [
                "--directory",
                "你的实际路径/mcp2tcp",  // 例如: "C:/Users/Administrator/Documents/develop/my-mcp-server/mcp2tcp"
                "run",
                "mcp2tcp"
            ]
        }
    }
}
```
#### 指定参数文件名
```json
{
    "mcpServers": {
        "mcp2tcp": {
            "command": "uv",
            "args": [
                "--directory",
                "你的实际路径/mcp2tcp",  // 例如: "C:/Users/Administrator/Documents/develop/my-mcp-server/mcp2tcp"
                "run",
                "mcp2tcp",
                "--config", // 可选参数，指定配置文件名
                "Pico"  // 可选参数，指定配置文件名，不需要添加_config.yaml后缀
            ]
        }
    }
}
```
### 配置文件位置
配置文件（`config.yaml`）可以放在不同位置，程序会按以下顺序查找：

#### 1. 当前工作目录（适合开发测试）
- 路径：`./config.yaml`
- 示例：如果你在 `C:\Projects` 运行程序，它会查找 `C:\Projects\config.yaml`
- 适用场景：开发和测试
- 不需要特殊权限

#### 2. 用户主目录（推荐个人使用）
```bash
# Windows系统
C:\Users\用户名\.mcp2tcp\config.yaml

# macOS系统
/Users/用户名/.mcp2tcp/config.yaml

# Linux系统
/home/用户名/.mcp2tcp/config.yaml
```
- 适用场景：个人配置
- 需要创建 `.mcp2tcp` 目录：
  ```bash
  # Windows系统（在命令提示符中）
  mkdir "%USERPROFILE%\.mcp2tcp"
  
  # macOS/Linux系统
  mkdir -p ~/.mcp2tcp
  ```

#### 3. 系统级配置（适合多用户环境）
```bash
# Windows系统（需要管理员权限）
C:\ProgramData\mcp2tcp\config.yaml

# macOS/Linux系统（需要root权限）
/etc/mcp2tcp/config.yaml
```
- 适用场景：多用户共享配置
- 创建目录并设置权限：
  ```bash
  # Windows系统（以管理员身份运行）
  mkdir "C:\ProgramData\mcp2tcp"
  
  # macOS/Linux系统（以root身份运行）
  sudo mkdir -p /etc/mcp2tcp
  sudo chown root:root /etc/mcp2tcp
  sudo chmod 755 /etc/mcp2tcp
  ```

程序会按照上述顺序查找配置文件，使用找到的第一个有效配置文件。根据你的需求选择合适的位置：
- 开发测试：使用当前目录
- 个人使用：建议使用用户主目录（推荐）
- 多用户环境：使用系统级配置（ProgramData或/etc）

3. 运行服务器：
```bash
# 确保已激活虚拟环境
.venv\Scripts\activate

# 运行服务器（使用默认配置config.yaml 案例中用的LOOP_BACK 模拟TCP，无需真实TCP和TCP设备）
uv run src/mcp2tcp/server.py
或
uv run mcp2tcp
# 运行服务器（使用指定配置Pico_config.yaml）
uv run src/mcp2tcp/server.py --config Pico
或
uv run mcp2tcp --config Pico
```


## 文档

- [安装指南](./docs/zh/installation.md)
- [API文档](./docs/zh/api.md)
- [配置说明](./docs/zh/configuration.md)