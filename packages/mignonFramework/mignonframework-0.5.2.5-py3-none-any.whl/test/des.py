import sys
import socket
import signal
import threading
import time
from typing import List, Callable, Type, TypeVar, Optional

from mignonFramework import JsonConfigManager, injectJson

import paramiko



manager = JsonConfigManager('./config.json')

class SSHConnectionConfig:
    ssh_server_host: str
    ssh_server_port: int
    ssh_username: str
    ssh_password: str
    # jump_host 字段已被移除

class ForwardRule:
    ssh_connection: SSHConnectionConfig
    local_host: str
    local_port: int
    remote_host: str
    remote_port: int
    comment: Optional[str] = None

@injectJson(manager)
class AppConfig:
    forwards: List[ForwardRule]



def forward_data(source: socket.socket, destination):
    """数据转发的工具函数，无状态，保持不变。"""
    try:
        while True:
            data = source.recv(406)
            if not data: break
            destination.sendall(data)
    except (socket.error, EOFError, paramiko.SSHException): pass
    finally:
        if hasattr(destination, 'shutdown_write'):
            try: destination.shutdown_write()
            except Exception: pass


class TunnelHandler:
    def __init__(self, rule: ForwardRule):
        self.rule = rule
        # 简化：现在只有一个SSH客户端
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connection_lock = threading.Lock()

    def _ensure_connection(self) -> bool:
        """ 简化后的连接逻辑，只处理直接连接 """
        transport = self.client.get_transport()
        if transport and transport.is_active():
            return True

        with self.connection_lock:
            transport = self.client.get_transport()
            if transport and transport.is_active():
                return True

            try:
                conn_info = self.rule.ssh_connection
                print(f"[{self.rule.local_port}] 正在连接到 {conn_info.ssh_server_host}...")
                self.client.connect(
                    hostname=conn_info.ssh_server_host,
                    port=conn_info.ssh_server_port,
                    username=conn_info.ssh_username,
                    password=conn_info.ssh_password,
                    timeout=10
                )
                print(f"[{self.rule.local_port}] 连接成功！")

            except Exception as e:
                print(f"[{self.rule.local_port}] 连接 {conn_info.ssh_server_host} 失败: {e}", file=sys.stderr)
                return False
        return True

    def _handle_client_request(self, client_sock: socket.socket):
        channel = None
        remote_addr = (self.rule.remote_host, self.rule.remote_port)
        try:
            if not self._ensure_connection():
                print(f"[{self.rule.local_port}] 无法建立SSH连接，放弃转发。")
                return

            transport = self.client.get_transport()
            channel = transport.open_channel("direct-tcpip", dest_addr=remote_addr, src_addr=client_sock.getpeername())
            if not channel:
                print(f"[{self.rule.local_port}] 无法在连接上打开转发通道。")
                return

            sender = threading.Thread(target=forward_data, args=(client_sock, channel), daemon=True)
            receiver = threading.Thread(target=forward_data, args=(channel, client_sock), daemon=True)
            sender.start()
            receiver.start()
            sender.join()
            receiver.join()
        except paramiko.ssh_exception.ChannelException as e:
            print(f"[{self.rule.local_port}] 转发通道错误: {e}")
        except Exception as e:
            print(f"[{self.rule.local_port}] 转发时发生未知错误: {e}")
        finally:
            if channel: channel.close()
            client_sock.close()

    def start(self):
        if not self._ensure_connection():
            print(f"[{self.rule.local_port}] 因初始连接失败，该隧道将不会启动。")
            return

        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            listener.bind((self.rule.local_host, self.rule.local_port))
            listener.listen(20)

            # 简化后的启动信息
            conn_path = f"{self.rule.ssh_connection.ssh_server_host}"
            print(f"[*] 隧道已就绪: [本地] {self.rule.local_host}:{self.rule.local_port} -> [SSH] {conn_path} -> [远程] {self.rule.remote_host}:{self.rule.remote_port}")

            while True:
                client_socket, _ = listener.accept()
                handler_thread = threading.Thread(target=self._handle_client_request, args=(client_socket,), daemon=True)
                handler_thread.start()
        except OSError as e:
            print(f"[!] 监听器 {self.rule.local_host}:{self.rule.local_port} 启动失败: {e}", file=sys.stderr)
        finally:
            listener.close()
            self.client.close()

# ============================================================================
#  SECTION 3: 主函数 (更新了启动信息)
# ============================================================================
def main():
    print("[*] 正在启动多路独立 SSH 隧道服务...")
    try:
        app_config = AppConfig()
        if not app_config.forwards:
            print("[!] 配置文件 `config.json` 的 forwards 列表为空或不存在。", file=sys.stderr)
            return
    except Exception as e:
        print(f"[!] 加载配置失败: {e}", file=sys.stderr)
        return

    threads = []
    for rule in app_config.forwards:
        print(f"\n--- 正在初始化隧道: {rule.comment or f'本地端口 {rule.local_port}'} ---")
        handler = TunnelHandler(rule)
        thread = threading.Thread(target=handler.start, daemon=True)
        threads.append(thread)
        thread.start()

    time.sleep(1.5)
    print(f"\n[*] 所有隧道任务已派发完毕！请查看上面的日志了解每个隧道的启动状态。")
    print("[*] 按 Ctrl+C 退出。")

    try:
        while any(t.is_alive() for t in threads):
            time.sleep(5)
        print("[!] 所有隧道线程均已停止，主程序退出。")
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        print("\n[*] 正在关闭所有隧道...")
        print("[*] 程序退出。")


if __name__ == '__main__':
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    main()