import socket
import sys
import threading
import time
from ssh2.session import Session
from mignonFramework.utils.ConfigReader import ConfigManager, inject

# --- 配置部分 (保持不变) ---
ssh_config_manager = ConfigManager(filename='./config.ini', section='ssh_tunnel')
forward_config_manager = ConfigManager(filename="./forword.ini")

@inject(forward_config_manager)
class ForwardConfig:
    local_host: str
    local_port: int
    remote_host: str
    remote_port: int

@inject(ssh_config_manager)
class SSHConnectionConfig:
    ssh_server_host: str
    ssh_server_port: int = 22
    ssh_username: str
    ssh_password: str = None
    ssh_private_key_path: str = None

# --- 核心逻辑部分 (已重写并修正) ---

def forward_data(source, destination):
    """一个方向的数据转发循环"""
    try:
        while True:
            # 【【【 最重要的修改在这里 】】】
            if isinstance(source, socket.socket):
                data = source.recv(4096)
            else:  # source is a channel
                # channel.read() 返回一个 (size, data) 元组
                # 我们需要解包它，只取数据部分
                size, data = source.read(4096)

            if not data:
                break

            if isinstance(destination, socket.socket):
                destination.sendall(data)
            else:
                destination.write(data)

    except (socket.error, EOFError):
        pass  # 连接关闭时的正常现象
    finally:
        # 关闭写端，以通知对方连接已断开
        if isinstance(destination, socket.socket):
            try:
                destination.shutdown(socket.SHUT_WR)
            except socket.error:
                pass # 有可能已经关闭

def handle_client_connection(client_sock, ssh_session, remote_addr):
    """
    为每一个进来的客户端连接，创建两个线程进行双向数据转发。
    """
    channel = None
    try:
        channel = ssh_session.direct_tcpip(remote_addr[0], remote_addr[1])
        if not channel:
            print("[!] 无法在 SSH 服务器上打开转发通道。")
            return

        print(f"[+] 隧道已连接: {client_sock.getpeername()} <--> SSH <--> {remote_addr}")

        sender_thread = threading.Thread(target=forward_data, args=(client_sock, channel))
        receiver_thread = threading.Thread(target=forward_data, args=(channel, client_sock))

        sender_thread.daemon = True
        receiver_thread.daemon = True

        sender_thread.start()
        receiver_thread.start()

        sender_thread.join()
        receiver_thread.join()

    except Exception as e:
        print(f"[-] 处理连接时发生未知错误: {e}")
    finally:
        if channel: channel.close()
        client_sock.close()
        print(f"[-] 连接已完全关闭。")


def main():
    print("[*] 正在启动 Mignon 集成式SSH隧道服务...")
    try:
        ssh_config = ssh_config_manager.getInstance(SSHConnectionConfig)
        forward_config = forward_config_manager.getInstance(ForwardConfig)
    except Exception as e:
        print(f"[!] 致命错误：加载配置失败: {e}", file=sys.stderr)
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ssh_config.ssh_server_host, ssh_config.ssh_server_port))
    except Exception as e:
        print(f"[!] 连接到 SSH 服务器失败: {e}")
        return

    session = Session()
    session.handshake(sock)
    try:
        session.userauth_password(ssh_config.ssh_username, ssh_config.ssh_password)
    except Exception as e:
        print(f"[!] SSH 认证失败: {e}")
        sock.close()
        return

    print("[*] SSH 认证成功！会话已建立。")

    local_bind_addr = (forward_config.local_host, forward_config.local_port)
    remote_dest_addr = (forward_config.remote_host, forward_config.remote_port)

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        listener.bind(local_bind_addr)
        listener.listen(10)
        print(f"[*] 隧道服务已启动，正在本地 {local_bind_addr[0]}:{local_bind_addr[1]} 监听...")
    except socket.error as e:
        print(f"[!] 启动本地监听失败: {e}")
        sock.close()
        return

    try:
        while True:
            client_socket, addr = listener.accept()
            print(f"\n[+] 接收到来自 {addr[0]}:{addr[1]} 的新连接...")

            handler_thread = threading.Thread(
                target=handle_client_connection,
                args=(client_socket, session, remote_dest_addr)
            )
            handler_thread.daemon = True
            handler_thread.start()

    except KeyboardInterrupt:
        print("\n[*] 用户中断程序...")
    finally:
        listener.close()
        sock.close()
        print("[*] 服务已关闭。")

if __name__ == '__main__':
    main()