#!/bin/bash

# 设置conda环境
echo "初始化conda环境..."
source $(conda info --base)/etc/profile.d/conda.sh || true

# 检查并创建conda环境
if ! conda env list | grep -q "fighting-game"; then
    echo "创建conda环境: fighting-game"
    conda env create -f environment.yml
fi

# 激活环境
echo "激活conda环境..."
conda activate fighting-game

# 检查并安装必要的依赖
echo "检查并安装依赖..."
pip install pygame numpy tensorflow pillow opencv-python

# 创建模型目录
mkdir -p models

# 检查是否已经有模型
if [ ! -f "models/fighting_ai_model.h5" ]; then
    echo "训练AI模型..."
    python src/ai/train_model.py
else
    echo "AI模型已存在，跳过训练步骤。"
fi

# 运行游戏
echo "启动游戏..."
python main.py

# 添加帮助信息
echo "
游戏操作说明:
- 在主菜单中选择'对战机器学习AI'可以与训练好的AI对战
- 如果要重新训练模型，请删除models/fighting_ai_model.h5文件，或选择'训练AI模型'选项
" 