import consul
import socket
import os
import requests
import struct

consul_client = None  # 全局 Consul 客户端实例


def init_app(app):
    global consul_client

    # 优先从 Flask 配置获取，否则从环境变量获取
    consul_host = app.config.get("CONSUL_HOST") or os.environ.get("CONSUL_HOST")
    consul_port = app.config.get("CONSUL_PORT") or os.environ.get("CONSUL_PORT")
    consul_token = app.config.get("CONSUL_TOKEN") or os.environ.get("CONSUL_TOKEN")

    service_name = app.config.get("PRODUCT_KEY")
    service_port = app.config.get("RUN_PORT")

    # 初始化 python-consul2 客户端
    consul_client = consul.Consul(
        host=consul_host, port=consul_port, token=consul_token
    )

    # 初始化配置（从 Consul KV 获取）
    kv_prefix_list = ["config/common/", f"config/{service_name}/"]
    for kv_prefix in kv_prefix_list:
        # 获取所有以 kv_prefix 开头的 key
        index, kvs = consul_client.kv.get(kv_prefix, recurse=True)
        if kvs:
            for item in kvs:
                key = item["Key"]
                value = item["Value"]
                # Consul KV 返回的是 bytes 类型，需要解码为字符串
                if isinstance(value, bytes):
                    try:
                        value = value.decode("utf-8")
                    except Exception:
                        pass  # 解码失败则保留原值
                config_key = key.replace(kv_prefix, "").upper()
                app.config[config_key] = value

    # 注册服务 - Docker 部署时优先使用环境变量配置的服务地址
    service_host = (
        app.config.get("SERVICE_HOST") or
        os.environ.get("SERVICE_HOST") or
        app.config.get("HOST") or
        get_local_ip()
    )

    # Docker 部署时可能需要使用映射后的端口
    external_service_port = (
        app.config.get("SERVICE_PORT") or
        os.environ.get("SERVICE_PORT") or
        service_port
    )

    # 健康检查地址，Docker 部署时可能需要使用外部可访问的地址
    check_url = f"http://{service_host}:{external_service_port}/"
    check = consul.Check.http(check_url, interval="60s")

    consul_client.agent.service.register(
        name=service_name,
        service_id=service_name,
        address=service_host,
        port=int(external_service_port),
        check=check,
    )

    # 获取注册名
    url = get_service_url(service_name)  # 确保服务已注册
    print(f"Consul service {service_name} registered at {url}")
    print(f"Health check URL: {check_url}")


def get_local_ip():
    """自动获取本机 IP 地址（Docker 环境下尝试获取宿主机 IP）"""

    # 方法1: 检查是否在 Docker 环境中，尝试通过网关获取宿主机 IP
    try:
        # 读取 Docker 默认网关
        with open('/proc/net/route', 'r') as f:
            for line in f:
                fields = line.strip().split()
                if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                    continue
                gateway_ip = socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))
                # 如果网关是 Docker 网关（通常是 172.x.x.1），尝试获取宿主机 IP
                if gateway_ip.startswith('172.'):
                    # 尝试通过网关获取外部 IP
                    try:
                        response = requests.get('http://checkip.amazonaws.com/', timeout=5)
                        if response.status_code == 200:
                            return response.text.strip()
                    except:
                        pass
                break
    except:
        pass


    # 方法3: 传统方法获取本地 IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]

        # 如果获取到的是 Docker 内部 IP，尝试其他方法
        if ip.startswith('172.') and 'DOCKER_HOST' in os.environ:
            # 从 DOCKER_HOST 环境变量解析
            docker_host = os.environ.get('DOCKER_HOST', '')
            if '://' in docker_host:
                host_part = docker_host.split('://')[1]
                if ':' in host_part:
                    return host_part.split(':')[0]

        return ip
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def get_service_url(service_name):
    """获取指定服务的健康实例地址"""
    global consul_client
    if not consul_client:
        raise RuntimeError("Consul 客户端未初始化，请先调用 init_app。")  # 中文报错

    index, nodes = consul_client.health.service(service_name, passing=True)
    if not nodes:
        return None

    # 返回第一个健康实例的地址和端口
    node = nodes[0]
    address = node["Service"]["Address"]
    port = node["Service"]["Port"]



    return f"http://{address}:{port}/"    # 返回完整的 URL    return f"http://{address}:{port}"
