from requests.auth import HTTPProxyAuth
import socket


def proxy_load():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    proxies = ''
    if ip[0:7] == '10.244.':
        # 在公司
        proxies = {}
        # auth = HTTPProxyAuth('', '')
        auth = None
    else:
        # 后续补充
        proxies = {}
        auth = None

    return proxies, auth
