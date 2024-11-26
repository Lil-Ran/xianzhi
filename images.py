from datetime import datetime
import os
import re
import requests
import sys
import time
from tqdm import tqdm
import urllib3

if not os.path.exists(f'output'):
    print('[!] Please run pages.py to download html first', file=sys.stderr)
    exit(1)

CONTINUOUS_ERROR = 0

target = sorted(map(int, os.listdir('output')))[::-1]
for i in tqdm(target):
    if not os.path.isdir(f'output/{i}'):
        continue
    if os.path.exists(f'output/{i}/.imgdownloaded'):
        continue
    target_files = os.listdir(f'output/{i}')
    for j in target_files:
        if not j.endswith('.html') or not j.startswith(str(i)):
            continue
        
        with open(f'output/{i}/{j}', 'r', encoding='utf-8') as f:
            content = f.read()

        imgs = re.findall(r'<img src="https://xzfile.aliyuncs.com/media/upload/picture/([^#"]+)', content)
        for img in imgs:
            no_br_filename = img.replace('\r', '').replace('\n', '')
            flag = True
            while flag:
                try:
                    response = requests.get(f'https://xzfile.aliyuncs.com/media/upload/picture/{no_br_filename}')
                    flag = False
                except (urllib3.exceptions.MaxRetryError, 
                        urllib3.exceptions.ConnectTimeoutError, 
                        requests.exceptions.ConnectionError, 
                        requests.exceptions.ConnectTimeout):
                    print(f'[!] {datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')} {i} {img} ConnectTimeout', file=sys.stderr)
                    time.sleep(60)
            if response.status_code != 200:
                print(f'[!] {i} {img} download failed with {response.status_code = }', file=sys.stderr)
                CONTINUOUS_ERROR += 1
                if CONTINUOUS_ERROR > 3:
                    exit(1)
                continue
            CONTINUOUS_ERROR = 0
            with open(f'output/{i}/{no_br_filename}', 'wb') as f:
                f.write(response.content)
            content = content.replace(f'https://xzfile.aliyuncs.com/media/upload/picture/{img}', no_br_filename)

        with open(f'output/{i}/{j}', 'w', encoding='utf-8') as f:
            f.write(content)

        open(f'output/{i}/.imgdownloaded', 'w').close()
