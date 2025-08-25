from mitmproxy import ctx, http

class RedirectAddon:
    def __init__(self):
        self.ssh_tunnel_addr = '127.0.0.1'
        self.ssh_tunnel_port = 8089 # 对应 SSH 隧道脚本的 local_port
        self.clash_addr = '127.0.0.1'
        self.clash_port = 20241 # 对应 Clash 的混合代理端口

    def request(self, flow: http.HTTPFlow):
        # 检查请求是否为需要通过 SSH 隧道的目标地址
        if flow.request.pretty_host == "10.16.202.153":
            ctx.log.info(f"Redirecting request for {flow.request.pretty_host} to SSH tunnel.")
            # 将请求的上游代理设置为你的SSH隧道
            flow.request.set_proxy_upstream(f"http://{self.ssh_tunnel_addr}:{self.ssh_tunnel_port}")
        else:
            ctx.log.info(f"Forwarding request for {flow.request.pretty_host} to Clash.")
            # 将请求的上游代理设置为Clash
            flow.request.set_proxy_upstream(f"http://{self.clash_addr}:{self.clash_port}")

addons = [RedirectAddon()]