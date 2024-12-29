import socket
import json
import time

'''
tcp_server.py
模拟硬件设备的TCP服务器，根据接收到的命令返回相应的响应。
支持的命令：
- CMD_PWM {frequency}: 设置PWM频率
- CMD_PICO_INFO: 查询Pico板信息
- CMD_LED {state}: 控制LED状态
'''

class DeviceState:
    def __init__(self):
        self.pwm_frequency = 0
        self.led_state = "off"
        self.start_time = time.time()
    
    def set_pwm(self, frequency):
        try:
            self.pwm_frequency = int(frequency)
            return f"CMD PWM frequency set to {frequency}Hz\r\n"
        except ValueError:
            return f"CMD Error: Invalid frequency value\r\n"
    
    def get_pico_info(self):
        uptime = int(time.time() - self.start_time)
        info = {
            "device": "Raspberry Pi Pico",
            "firmware_version": "1.0.0",
            "current_pwm": self.pwm_frequency,
            "led_state": self.led_state,
            "uptime_seconds": uptime
        }
        return f"CMD {json.dumps(info)}\r\n"
    
    def set_led(self, state):
        if state.lower() in ["on", "off"]:
            self.led_state = state.lower()
            return f"CMD LED state set to {state}\r\n"
        return f"CMD Error: Invalid LED state. Use 'on' or 'off'\r\n"

def handle_command(device_state: DeviceState, command: str) -> str:
    """处理接收到的命令并返回响应"""
    command = command.strip()
    
    # 处理PWM命令
    if command.startswith("CMD_PWM"):
        try:
            frequency = command.split()[1]
            return device_state.set_pwm(frequency)
        except IndexError:
            return "CMD Error: Missing frequency parameter\r\n"
    
    # 处理Pico信息查询命令
    elif command == "CMD_PICO_INFO":
        return device_state.get_pico_info()
    
    # 处理LED控制命令
    elif command.startswith("CMD_LED"):
        try:
            state = command.split()[1]
            return device_state.set_led(state)
        except IndexError:
            return "CMD Error: Missing LED state parameter\r\n"
    
    # 未知命令
    else:
        return f"CMD Error: Unknown command '{command}'\r\n"

def start_server(host='127.0.0.1', port=9999):
    device_state = DeviceState()
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"TCP Server listening on {host}:{port}")
        print("Supported commands:")
        print("- CMD_PWM {frequency}")
        print("- CMD_PICO_INFO")
        print("- CMD_LED {state}")

        while True:
            client_socket, client_address = server_socket.accept()
            with client_socket:
                print(f"Client connected from {client_address}")
                while True:
                    try:
                        data = client_socket.recv(1024)
                        if not data:
                            break
                        
                        command = data.decode('ascii').strip()
                        print(f"Received: {command}")
                        
                        # 处理命令并发送响应
                        response = handle_command(device_state, command)
                        client_socket.sendall(response.encode('ascii'))
                        print(f"Sent: {response.strip()}")
                        
                    except UnicodeDecodeError:
                        error_response = "CMD Error: Invalid ASCII data\r\n"
                        client_socket.sendall(error_response.encode('ascii'))
                    except Exception as e:
                        error_response = f"CMD Error: {str(e)}\r\n"
                        client_socket.sendall(error_response.encode('ascii'))
                
                print(f"Client {client_address} disconnected")

if __name__ == "__main__":
    start_server()
