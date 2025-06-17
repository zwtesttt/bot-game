#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import os

# 创建目录
os.makedirs('assets/fonts', exist_ok=True)

# 下载思源黑体
font_url = 'https://github.com/adobe-fonts/source-han-sans/raw/release/OTF/SimplifiedChinese/SourceHanSansSC-Regular.otf'
font_path = 'assets/fonts/simhei.ttf'

print(f'正在下载中文字体...')
response = requests.get(font_url, stream=True)
response.raise_for_status()

with open(font_path, 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)

print(f'字体下载成功，保存到 {font_path}') 