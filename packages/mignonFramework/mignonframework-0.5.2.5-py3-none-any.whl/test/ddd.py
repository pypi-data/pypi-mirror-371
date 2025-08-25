import sys
import os
import platform

# --- 配置 ---
IP_ADDRESS = '127.0.0.1'
HOSTNAME = '10.16.202.153'
HOSTS_ENTRY = f'{IP_ADDRESS}    {HOSTNAME}'

def get_platform_config():
    """
    根据当前操作系统返回对应的 hosts 文件路径和 DNS 刷新命令。
    """
    system = platform.system().lower()
    if system == 'windows':
        return {
            'hosts_path': r'C:\Windows\System32\drivers\etc\hosts',
            'flush_dns_command': 'ipconfig /flushdns'
        }
    elif system in ['linux', 'darwin']: # darwin is the system name for macOS
        return {
            'hosts_path': '/etc/hosts',
            'flush_dns_command': 'sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder' if system == 'darwin' else 'sudo systemd-resolve --flush-caches || echo "Could not flush DNS"'
        }
    else:
        return None

def manage_hosts_entry(add=True):
    """
    管理 hosts 文件中的指定条目（跨平台）。
    :param add: True 表示添加条目，False 表示移除条目。
    """
    platform_config = get_platform_config()
    if not platform_config:
        print(f"[!] 错误: 不支持的操作系统 '{platform.system()}'。")
        return False

    hosts_path = platform_config['hosts_path']
    flush_dns_command = platform_config['flush_dns_command']
    action = "添加" if add else "移除"

    print(f"[*] 正在尝试 {action} hosts 条目: '{HOSTS_ENTRY}'")
    print(f"[*] 目标 hosts 文件: {hosts_path}")

    try:
        # --- 1. 读取所有行 ---
        with open(hosts_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # --- 2. 检查条目是否存在 ---
        entry_exists = any(HOSTS_ENTRY in line and not line.strip().startswith('#') for line in lines)

        if add:
            if entry_exists:
                print(f"[+] Hosts 条目已存在，无需操作。")
                return True
            else:
                # --- 3. 如果不存在，则添加 ---
                print(f"[*] 正在追加新条目...")
                with open(hosts_path, 'a', encoding='utf-8') as f:
                    f.write(f"\n# Added by Mignon Tunnel Manager\n")
                    f.write(f"{HOSTS_ENTRY}\n")
                print(f"[+] 成功添加 Hosts 条目。")
        else: # 移除逻辑
            if not entry_exists and not any(HOSTNAME in line for line in lines):
                print(f"[-] 未找到相关 Hosts 条目，无需操作。")
                return True
            else:
                # --- 4. 如果存在，则移除 ---
                print(f"[*] 正在移除相关条目...")
                new_lines = []
                for line in lines:
                    # 移除包含 HOSTNAME 的行，不管是注释还是有效条目
                    if HOSTNAME not in line.split():
                        new_lines.append(line)

                with open(hosts_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                print(f"[-] 成功移除 Hosts 条目。")

        # --- 5. 刷新 DNS 缓存 ---
        print("[*] 正在刷新 DNS 缓存...")
        os.system(flush_dns_command)

        return True

    except FileNotFoundError:
        print(f"[!] 错误: hosts 文件未找到，路径: {hosts_path}")
        return False
    except PermissionError:
        print(f"[!] 致命错误: 权限不足。请务必以【管理员/root】身份运行此脚本！")
        # On macOS/Linux, you use 'sudo python your_script.py'
        if platform.system().lower() != 'windows':
            print("[*] 提示: 在 macOS/Linux 上, 请使用 'sudo' 命令来运行。")
        return False
    except Exception as e:
        print(f"[!] 发生未知错误: {e}")
        return False

def main():
    if '--remove' in sys.argv or '-r' in sys.argv:
        manage_hosts_entry(add=False)
    else:
        manage_hosts_entry(add=True)

if __name__ == '__main__':
    main()