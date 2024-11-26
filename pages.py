import ctypes
from datetime import datetime
import os
import re
import requests
import sys
import time
import urllib3

from config import COOKIES, RANGE

if COOKIES['acw_sc__v3'] == '':
    print('[!] Please fill in the cookies in config.py', file=sys.stderr)
    exit(1)

HEADERS = {
    'Cookie': '; '.join([f'{k}={v}' for k, v in COOKIES.items()]),
    'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Accept-Language': 'zh-CN',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.89 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Accept-Encoding': 'gzip, deflate, br',
    'Priority': 'u=0, i',
    'Connection': 'keep-alive',
}

CONTINUOUS_ERROR = 0

for i in RANGE:
    if os.path.exists(f'output/{i}'):
        continue
    
    url = f'https://xz.aliyun.com/t/{i}'
    flag = True
    while flag:
        try:
            response = requests.get(url, headers=HEADERS)
            flag = False
        except (urllib3.exceptions.MaxRetryError, 
                urllib3.exceptions.ConnectTimeoutError, 
                requests.exceptions.ConnectionError, 
                requests.exceptions.ConnectTimeout):
            print(f'[!] {datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')} {i} ConnectTimeout', file=sys.stderr)
            time.sleep(60)
    
    if response.status_code == 404:
        continue

    if response.status_code != 200 or '<!-- main content begin -->' not in response.text:
        with open(f'error-{CONTINUOUS_ERROR}.txt', 'w', encoding='utf-8') as f:
            f.write(url)
            f.write('\n' + '='*32 + '\n')
            f.write(f'{response.status_code = }')
            f.write('\n' + '='*32 + '\n')
            f.write(f'{response.headers = }')
            f.write('\n' + '='*32 + '\n')
            f.write(response.text)
        CONTINUOUS_ERROR += 1
        if CONTINUOUS_ERROR > 3:
            exit(1)
        ctypes.windll.user32.MessageBoxW(0, f'{i = }\n{response.status_code = }', 'Error', 1)
        continue

    CONTINUOUS_ERROR = 0
    
    os.makedirs(f'output/{i}', exist_ok=True)
    title = re.search(r'<title>(.*?)</title>', response.text).group(1)
    title = re.sub(r'[\\/:*?"<>|]', '_', title)
    with open(f'output/{i}/{i} - {title}.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
