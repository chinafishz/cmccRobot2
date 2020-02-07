from requests.auth import HTTPProxyAuth
import socket
import configparser
import logging
import os

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


def load_config_setting(section, item, type='item'):
    config = configparser.ConfigParser()
    config.read('config.ini')
    section_path = dict(config.items('path'))
    setting_file_path = section_path.get('setting_file')

    if os.path.exists(setting_file_path + 'config.ini') is True:
        config.read(setting_file_path + 'config.ini')
    else:
        config.read('config.ini')

    try:
        section_path = dict(config.items(section))
        if type == 'item':
            result = section_path.get(item)
        elif type == 'section':
            result = section_path
    except:
        result = None

    return result



