#!/bin/bash

# 检查并创建conda环境
if ! conda env list | grep -q "fighting-game"; then
    echo "创建conda环境: fighting-game"
    conda env create -f environment.yml
fi

# 激活环境并运行游戏
echo "激活环境并运行游戏..."
conda activate fighting-game && python main.py 