# ====================================================
# Project: mcp2tcp
# Description: A protocol conversion tool that enables 
#              hardware devices to communicate with 
#              large language models (LLM) through serial ports.
# Repository: https://github.com/mcp2everything/mcp2tcp.git
# License: MIT License
# Author: mcp2everything
# Copyright (c) 2024 mcp2everything
#
# Permission is hereby granted, free of charge, to any person 
# obtaining a copy of this software and associated documentation 
# files (the "Software"), to deal in the Software without restriction, 
# including without limitation the rights to use, copy, modify, merge, 
# publish, distribute, sublicense, and/or sell copies of the Software, 
# and to permit persons to whom the Software is furnished to do so, 
# subject to the following conditions:
#
# The above copyright notice and this permission shall be 
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, 
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES 
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, 
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS 
# IN THE SOFTWARE.
# ====================================================
from typing import Any, Optional, Tuple, Dict, List
import asyncio
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
import logging
import yaml
import os
from dataclasses import dataclass, field
import time
import socket

# 设置日志级别为 DEBUG
logging.basicConfig(
    level=logging.DEBUG,  # 改为 DEBUG 级别以显示更多信息
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 添加版本号常量
VERSION = "0.1.0"  # 添加了自动\r\n和更详细的错误信息

# 创建MCP服务器实例
server = Server("mcp2tcp")
config = None

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools."""
    if config is None:
        return []
        
    tools = []
    for cmd_id, command in config.commands.items():
        # 从命令字符串中提取命令名（去掉CMD_前缀）
        cmd_name = command.command.split()[0].replace("CMD_", "").lower()
        
        # 构建参数描述
        properties = {}
        required = []
        
        # 使用配置文件中的参数定义
        if hasattr(command, 'parameters'):
            for param in command.parameters:
                properties[param['name']] = {
                    "type": param['type'],
                    "description": param['description'],
                    **({"enum": param['enum']} if 'enum' in param else {})
                }
                if param.get('required', False):
                    required.append(param['name'])
        else:
            # 如果没有参数定义，从命令字符串中提取
            import re
            param_names = re.findall(r'\{(\w+)\}', command.command)
            for param_name in param_names:
                properties[param_name] = {
                    "type": "string",
                    "description": f"Parameter {param_name} for the {cmd_name} command",
                    "examples": [p.format(**{param_name: "value"}) for p in command.prompts if "{" + param_name + "}" in p]
                }
                required.append(param_name)

        tool = types.Tool(
            name=cmd_name,  # 使用命令名作为工具名
            description=command.prompts[0] if command.prompts else f"Execute {cmd_name} command",
            inputSchema={
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False
            }
        )
        tools.append(tool)
        logger.debug(f"Registered tool: {cmd_name} with parameters: {properties}")
    
    return tools

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any] | None) -> List[types.TextContent]:
    """Handle tool execution requests."""
    if config is None:
        return [types.TextContent(
            type="text",
            text="Error: Configuration not loaded"
        )]
        
    try:
        logger.info(f"Tool call received - Name: {name}, Arguments: {arguments}")
        
        # 查找对应的命令
        cmd_found = None
        for cmd_id, command in config.commands.items():
            cmd_name = command.command.split()[0].replace("CMD_", "").lower()
            if cmd_name == name:
                cmd_found = command
                break
        
        if cmd_found is None:
            error_msg = f"Error: Unknown tool '{name}'\n"
            error_msg += "Please check:\n"
            error_msg += "1. Tool name is correct\n"
            error_msg += "2. Tool is configured in config.yaml"
            logger.error(error_msg)
            return [types.TextContent(
                type="text",
                text=error_msg
            )]

        if arguments is None:
            arguments = {}
        
        # 验证必需的参数
        import re
        param_names = re.findall(r'\{(\w+)\}', cmd_found.command)
        missing_params = [param for param in param_names if param not in arguments]
        if missing_params:
            error_msg = f"Error: Missing required parameters: {', '.join(missing_params)}\n"
            error_msg += "Please provide all required parameters."
            logger.error(error_msg)
            return [types.TextContent(
                type="text",
                text=error_msg
            )]
        
        # 发送命令并等待响应
        try:
            response = tcp_connection.send_command(cmd_found, arguments)
            logger.debug(f"Command response: {response}")
            return response
        except ConnectionError as e:
            error_msg = f"Error: Connection failed - {str(e)}\n"
            error_msg += "Please check:\n"
            error_msg += "1. TCP server is running\n"
            error_msg += "2. Connection settings are correct"
            logger.error(error_msg)
            return [types.TextContent(
                type="text",
                text=error_msg
            )]
        except TimeoutError as e:
            error_msg = f"Error: Command timeout - {str(e)}\n"
            error_msg += "Please check:\n"
            error_msg += "1. Device is responding\n"
            error_msg += "2. Timeout settings are appropriate"
            logger.error(error_msg)
            return [types.TextContent(
                type="text",
                text=error_msg
            )]
        
    except Exception as e:
        error_msg = f"Error: {str(e)}\n"
        error_msg += "Please check:\n"
        error_msg += "1. Configuration is correct\n"
        error_msg += "2. Device is functioning properly"
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]

@dataclass
class Command:
    """Configuration for a serial command."""
    command: str
    need_parse: bool
    data_type: str
    prompts: List[str]

@dataclass
class Config:
    """Configuration for mcp2tcp service."""
    remote_ip: Optional[str] = None
    port: int = 12345
    connect_timeout: float = 3.0
    receive_timeout: float = 3.0
    timeout: float = 1.0
    read_timeout: float = 1.0
    response_start_string: str = "OK"  # 新增：可配置的应答开始字符串
    communication_type: str = "client"  # 新增：通信类型
    commands: Dict[str, Command] = field(default_factory=dict)

    @staticmethod
    def load(config_path: str = "config.yaml") -> 'Config':
        """Load configuration from YAML file."""
        try:
            logger.info(f"Opening configuration file: {config_path}")
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f)
                logger.info("Successfully parsed YAML configuration")
            
            # 加载 TCP 配置
            tcp_config = data.get('tcp', {})
            logger.info("Loading TCP configuration...")
            config = Config(
                remote_ip=tcp_config.get('remote_ip'),
                port=tcp_config.get('port', 12345),
                connect_timeout=tcp_config.get('connect_timeout', 3.0),
                receive_timeout=tcp_config.get('receive_timeout', 3.0),
                response_start_string=tcp_config.get('response_start_string', 'OK'),
                communication_type=tcp_config.get('communication_type', 'client')
            )
            logger.info("TCP configuration loaded")
            
            # 加载命令配置
            logger.info("Loading commands configuration...")
            commands_count = 0
            for cmd_id, cmd_data in data.get('commands', {}).items():
                logger.info(f"Loading command: {cmd_id}")
                raw_command = cmd_data.get('command', '')
                logger.debug(f"Command string: '{raw_command}'")
                config.commands[cmd_id] = Command(
                    command=raw_command,
                    need_parse=cmd_data.get('need_parse', False),
                    data_type=cmd_data.get('data_type', 'ascii'),
                    prompts=cmd_data.get('prompts', [])
                )
                commands_count += 1
            logger.info(f"Loaded {commands_count} commands")
            
            return config
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise

class TCPConnection:
    """TCP connection manager."""
    
    def __init__(self):
        self.socket: Optional[socket.socket] = None
        self.remote_ip: str = None
        self.port: int = None
        self.connect_timeout: float = None
        self.receive_timeout: float = None
        self.response_start_string: str = None

    def connect(self) -> bool:
        """Attempt to connect to the TCP server."""
        try:
            if self.socket:
                self.socket.close()
            self.socket = socket.create_connection(
                (self.remote_ip, self.port), 
                timeout=self.connect_timeout
            )
            logger.info(f"Connected to TCP server at {self.remote_ip}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to TCP server: {str(e)}")
            return False

    def send_command(self, command: Command, arguments: dict[str, Any] | None) -> list[types.TextContent]:
        """Send a command to the TCP server and return result according to MCP protocol."""
        try:
            if not self.socket:
                if not self.connect():
                    return [types.TextContent(
                        type="text",
                        text=f"Failed to connect to TCP server at {self.remote_ip}:{self.port}"
                    )]
            if command.data_type == "ascii":
                # 准备命令
                cmd_str = command.command.format(**arguments)
                # 确保命令以\r\n结尾
                cmd_str = cmd_str.rstrip() + '\r\n'  # 移除可能的空白字符，强制添加\r\n
                command_bytes = cmd_str.encode()
                logger.info(f"Sending command: {cmd_str.strip()}")
                logger.info(f"Sent command: {command_bytes.strip().decode('ascii')}")
                self.socket.sendall(command_bytes)

            elif command.data_type == "hex":
                command_bytes = bytes.fromhex(command.command.replace(" ", ""))
                logger.info(f"Sent command: {command.command}")
                self.socket.sendall(command_bytes)
            self.socket.settimeout(self.receive_timeout)
            responses = []
            while True:
                try:
                    response = self.socket.recv(4096)
                    if response:
                        logger.debug(f"Received data: {response}")
                        responses.append(response)
                        if command.data_type == "ascii" and response.endswith(b'\r\n'):
                            break
                        elif command.data_type == "hex":
                            break
                    else:
                        break
                except socket.timeout as e:
                    logger.error(f"TCP receive timeout: {str(e)}")
                    return [types.TextContent(
                        type="text",
                        text=f"TCP receive timeout: {str(e)}"
                    )]

            if not responses:
                return [types.TextContent(
                    type="text",
                    text=f"No response received from TCP server within {self.receive_timeout} seconds"
                )]

            first_response = responses[0].decode().strip()
            logger.info(f"Received response: {first_response}")

            if self.response_start_string in first_response:
                return [types.TextContent(
                    type="text",
                    text=first_response
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Invalid response: {first_response}"
                )]

        except socket.timeout as e:
            logger.error(f"TCP send timeout: {str(e)}")
            return [types.TextContent(
                type="text",
                text=f"TCP send timeout: {str(e)}"
            )]
        except Exception as e:
            logger.error(f"TCP error: {str(e)}")
            return [types.TextContent(
                type="text",
                text=f"TCP error: {str(e)}"
            )]

    def close(self) -> None:
        """Close the TCP connection if open."""
        if self.socket:
            self.socket.close()
            logger.info(f"Closed TCP connection to {self.remote_ip}:{self.port}")
            self.socket = None

tcp_connection = TCPConnection()

def send_command(command, arguments):
    response = tcp_connection.send_command(command,arguments)
    logger.info(f"Received response: {response}")
    print(f"Received response: {response}")
    return response

async def main(config_name: str = None) -> None:
    """Run the MCP server.
    
    Args:
        config_name: Optional configuration name. If not provided, uses default config.yaml
    """
    try:
        # 加载配置
        config_path = config_name if config_name else "config.yaml"
        if not os.path.isfile(config_path):
            config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.yaml')
        
        logger.info(f"Loading configuration from {config_path}")
        if not os.path.isfile(config_path):
            logger.error(f"Configuration file not found: {config_path}")
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
        global config
        config = Config.load(config_path)
        logger.info("Configuration loaded successfully")
        logger.info(f"TCP Remote IP: {config.remote_ip}")
        logger.info(f"TCP Port: {config.port}")
        logger.info(f"Available commands: {list(config.commands.keys())}")
        
        tcp_connection.remote_ip = config.remote_ip
        tcp_connection.port = config.port
        tcp_connection.connect_timeout = config.connect_timeout
        tcp_connection.receive_timeout = config.receive_timeout * 5  # 增加接收超时时间
        tcp_connection.response_start_string = config.response_start_string
        
        # 运行 MCP 服务器
        logger.info("Starting MCP server...")
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="mcp2tcp",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    import sys
    config_name = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(main(config_name))