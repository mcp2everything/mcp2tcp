# mcp2tcp Service

English | [简体中文](README.md)

<div align="center">
    <img src="docs/images/logo.png" alt="mcp2tcp Logo" width="200"/>
</div>

mcp2tcp is a serial communication server based on the MCP service interface protocol, designed for communication with serial devices. It provides a simple configuration approach for defining and managing serial commands.

## Features

- 🔌 Automatic serial port detection and connection management
- 📝 Simple YAML configuration
- 🛠️ Customizable commands and response parsing
- 🌐 Multi-language prompt support
- 🚀 Asynchronous communication support
- Auto-detect and connect to serial ports at 115200 baud rate
- Control PWM frequency (range: 0-100)
- Compliant with Claude MCP protocol
- Comprehensive error handling and status feedback
- Cross-platform support (Windows, Linux, macOS)

## System Architecture

<div align="center">
    <img src="docs/images/stru_chs.png" alt="System Architecture" width="800"/>
    <p>mcp2tcp System Architecture</p>
</div>

## Workflow

<div align="center">
    <img src="docs/images/workflow_chs.png" alt="Workflow Diagram" width="800"/>
    <p>mcp2tcp Workflow Diagram</p>
</div>

## Quick Start

### Prepare
Python>=3.11 
Claude Desktop or Cline+Vscode


### Installation

#### For Windows Users
```bash
# Download the installation script
curl -O https://raw.githubusercontent.com/mcp2everything/mcp2tcp/main/install.py

# Run the installation script
python install.py
```

#### For macOS Users
```bash
# Download the installation script
curl -O https://raw.githubusercontent.com/mcp2everything/mcp2tcp/main/install_macos.py

# Run the installation script
python3 install_macos.py
```

#### For Ubuntu/Raspberry Pi Users
```bash
# Download the installation script
curl -O https://raw.githubusercontent.com/mcp2everything/mcp2tcp/main/install_ubuntu.py

# Run the installation script
python3 install_ubuntu.py
```

The installation script will automatically:
- ✅ Check system environment
- ✅ Install required dependencies
- ✅ Create default configuration file
- ✅ Configure Claude Desktop (if installed)
- ✅ Check serial devices

### Configuration File Location

The configuration file (`config.yaml`) can be placed in different locations depending on your needs:

#### 1. Current Working Directory (For Development)
- Path: `./config.yaml`
- Example: If you run the program from `C:\Projects`, it will look for `C:\Projects\config.yaml`
- Best for: Development and testing
- No special permissions required

#### 2. User's Home Directory (Recommended for Personal Use)
```bash
# Windows
C:\Users\YourName\.mcp2tcp\config.yaml

# macOS
/Users/YourName/.mcp2tcp/config.yaml

# Linux
/home/username/.mcp2tcp/config.yaml
```
- Best for: Personal configuration
- Create the `.mcp2tcp` directory if it doesn't exist:
  ```bash
  # Windows (in Command Prompt)
  mkdir "%USERPROFILE%\.mcp2tcp"
  
  # macOS/Linux
  mkdir -p ~/.mcp2tcp
  ```

#### 3. System-wide Configuration (For Multi-user Setup)
```bash
# Windows (requires admin rights)
C:\ProgramData\mcp2tcp\config.yaml

# macOS/Linux (requires sudo/root)
/etc/mcp2tcp/config.yaml
```
- Best for: Shared configuration in multi-user environments
- Create the directory with appropriate permissions:
  ```bash
  # Windows (as administrator)
  mkdir "C:\ProgramData\mcp2tcp"
  
  # macOS/Linux (as root)
  sudo mkdir -p /etc/mcp2tcp
  sudo chown root:root /etc/mcp2tcp
  sudo chmod 755 /etc/mcp2tcp
  ```

The program searches for the configuration file in this order and uses the first valid file it finds. Choose the location based on your needs:
- For testing: use current directory
- For personal use: use home directory (recommended)
- For system-wide settings: use ProgramData or /etc

### Serial Port Configuration

Configure serial port and commands in `config.yaml`:
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

### Testing

Before using the service in production, it's recommended to test it to ensure everything works correctly.

#### 1. Start the Test Server

First, start the TCP server in the tests directory to simulate a hardware device:

```bash
# Go to the tests directory
cd tests

# Start the test server
python tcp_server.py
```

The server will start locally, listening on port 9999. You should see output like this:
```
TCP server started on 127.0.0.1:9999
Waiting for connections...
```

#### 2. Start the MCP Server

Open a new terminal window and start the MCP server:

```bash
# Make sure you're in the project root directory
mcp2tcp
```

The server will start and load the configuration file. You should see output like this:
```
Loading configuration from config.yaml
Configuration loaded successfully
TCP Remote IP: 127.0.0.1
TCP Port: 9999
Available commands: ['set_pwm', 'get_pico_info', 'led_control']
Starting MCP server...
```

#### 3. Test Commands

Now you can use an MCP protocol-compatible client (like Claude Desktop or Cline) to test the following commands:

1. PWM Control:
   ```
   Set PWM to maximum
   Set PWM to minimum
   Set PWM to 50
   ```

2. LED Control:
   ```
   Turn on LED
   Turn off LED
   ```

3. Device Information:
   ```
   Get Pico board info
   ```

#### 4. Verify Results

- In the test server terminal window, you should see the received commands
- In the MCP server terminal window, you should see the command execution status
- In your client, you should see the command execution results

#### 5. Common Issues

1. If you see a "Connection refused" error:
   - Check if the test server is running
   - Verify that port 9999 is not being used by another program

2. If you see an "Unknown tool" error:
   - Check if the configuration file is loaded correctly
   - Verify that command names match the configuration file

3. If you see an "Invalid parameter" error:
   - Check if the parameter format is correct
   - PWM frequency must be an integer between 0 and 100
   - LED state must be either "on" or "off"

3.MCP json Configuration
Add the following to your MCP client (like Claude Desktop or Cline) configuration file, making sure to update the path to your actual installation path:

```json
{
    "mcpServers": {
        "mcp2tcp": {
            "command": "uvx",
            "args": ["mcp2tcp"]
        }
    }
}
```
if you want to develop locally, you can use the following configuration:
```json
{
    "mcpServers": {
        "mcp2tcp": {
            "command": "uv",
            "args": [
                "--directory",
                "your project path/mcp2tcp",  // ex: "C:/Users/Administrator/Documents/develop/my-mcp-server/mcp2tcp"
                "run",
                "mcp2tcp"
            ]
        }
    }
}
```

> **Important Notes:**
> 1. Use absolute paths only
> 2. Use forward slashes (/) or double backslashes (\\) as path separators
> 3. Ensure the path points to your actual project installation directory



4. launch your client(claude desktop or cline):


## Interacting with Claude

Once the service is running, you can control PWM through natural language conversations with Claude. Here are some example prompts:

- "Set PWM to 50%"
- "Turn PWM to maximum"
- "Turn off PWM output"
- "Adjust PWM frequency to 75%"
- "Can you set PWM to 25%?"

Claude will understand your intent and automatically invoke the appropriate commands. No need to remember specific command formats - just express your needs in natural language.

<div align="center">
    <img src="docs/images/test_output.png" alt="Cline Configuration Example" width="600"/>
    <p>Example in Cline</p>
</div>

## Documentation

- [Installation Guide](./docs/en/installation.md)
- [API Documentation](./docs/en/api.md)
- [Configuration Guide](./docs/en/configuration.md)

## Examples

### 1. Simple Command Configuration
```yaml
commands:
  led_control:
    command: "LED {state}\n"
    need_parse: false
    prompts:
      - "Turn on LED"
      - "Turn off LED"
```

## Requirements

- Python 3.11+
- mcp

## Installation from source code
 
#### Manual Installation
```bash
# Install from source:
git clone https://github.com/mcp2everything/mcp2tcp.git
cd mcp2tcp

# Create virtual environment
uv venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install development dependencies
uv pip install --editable .
```

## Running the Service

Use the `uv run` command to automatically build, install, and run the service:

```bash
uv run src/mcp2tcp/server.py
```

This command will:
1. Build the mcp2tcp package
2. Install it in the current environment
3. Start the server


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

### Development Setup

1. Fork and clone the repository
2. Create a virtual environment:
   ```bash
   uv venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```
3. Install development dependencies:
   ```bash
   uv pip install -e ".[dev]"
   ```

## License

[MIT](LICENSE)

## Acknowledgments

- Thanks to the [Claude](https://claude.ai) team for the MCP protocol
- All contributors and users of this project

## Support
If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/mcp2everything/mcp2tcp/issues) page
2. Read our [Wiki](https://github.com/mcp2everything/mcp2tcp/wiki)
3. Create a new issue if needed
