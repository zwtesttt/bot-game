#!/bin/bash

# 设置conda环境
echo "初始化conda环境..."
source $(conda info --base)/etc/profile.d/conda.sh || true

# 激活环境
echo "激活conda环境..."
conda activate fighting-game

# 检查并安装必要的依赖
echo "检查并安装依赖..."
pip install pygame numpy tensorflow pillow opencv-python

# 创建模型目录
mkdir -p models

# 删除旧模型（如果存在）
if [ -f "models/fighting_ai_model.h5" ]; then
    echo "删除旧模型..."
    rm models/fighting_ai_model.h5
fi

# 训练新模型
echo "开始训练新的AI模型..."
python src/ai/train_model.py

# 完成提示
echo "
训练完成!
现在可以运行 python main.py 来与新训练的AI对战。

AI难度级别:
- 简单: 推荐初学者
- 中等: 有一些格斗游戏经验的玩家
- 困难: 挑战高手

提示: 如果AI表现不佳，可以多次运行本脚本重新训练，每次训练会产生不同性能的AI。
" 