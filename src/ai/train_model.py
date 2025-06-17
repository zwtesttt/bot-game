#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
格斗游戏AI模型训练脚本
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM, BatchNormalization
from tensorflow.keras.optimizers import Adam
import random
import math

# 创建模型保存目录
os.makedirs("models", exist_ok=True)

# 定义动作空间
ACTIONS = {
    0: "无动作",
    1: "向左移动",
    2: "向右移动",
    3: "跳跃",
    4: "蹲下",
    5: "格挡",
    6: "轻拳",
    7: "重拳",
    8: "轻腿",
    9: "重腿"
}

def create_model(use_lstm=False):
    """创建神经网络模型
    
    Args:
        use_lstm: 是否使用LSTM网络（需要更多训练数据）
    
    Returns:
        训练好的模型
    """
    if use_lstm:
        # LSTM模型 - 考虑时序信息
        model = Sequential([
            LSTM(64, input_shape=(1, 10), return_sequences=False),
            Dropout(0.2),
            Dense(64, activation='relu'),
            BatchNormalization(),
            Dropout(0.2),
            Dense(32, activation='relu'),
            Dropout(0.2),
            Dense(len(ACTIONS), activation='softmax')  # 输出动作概率
        ])
    else:
        # 普通前馈网络 - 更容易训练
        model = Sequential([
            Dense(128, activation='relu', input_shape=(10,)),  # 10个特征输入，增加神经元数量
            BatchNormalization(),
            Dropout(0.2),
            Dense(64, activation='relu'),
            BatchNormalization(),
            Dropout(0.2),
            Dense(32, activation='relu'),
            Dropout(0.2),
            Dense(len(ACTIONS), activation='softmax')  # 输出动作概率
        ])
    
    model.compile(
        optimizer=Adam(learning_rate=0.0005),  # 降低学习率，提高训练稳定性
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def generate_advanced_training_data(num_samples=10000):
    """生成高级训练数据，融入更多格斗游戏策略
    
    Args:
        num_samples: 生成的样本数量
        
    Returns:
        特征和标签
    """
    X = []  # 特征
    y = []  # 标签
    
    for _ in range(num_samples):
        # 生成随机状态
        ai_x = random.randint(0, 800)
        ai_y = random.randint(200, 400)
        ai_health = random.randint(1, 100)
        player_x = random.randint(0, 800)
        player_y = random.randint(200, 400)
        player_health = random.randint(1, 100)
        player_attacking = random.choice([0, 1])
        ai_blocking = random.choice([0, 1])
        
        # 计算距离
        horizontal_distance = player_x - ai_x
        abs_horizontal_distance = abs(horizontal_distance)
        vertical_distance = player_y - ai_y
        
        # 构建特征向量
        features = [
            ai_x/800,  # 归一化AI位置x
            ai_y/600,  # 归一化AI位置y
            ai_health/100,  # 归一化AI生命值
            player_x/800,  # 归一化玩家位置x
            player_y/600,  # 归一化玩家位置y
            player_health/100,  # 归一化玩家生命值
            player_attacking,  # 玩家是否攻击
            ai_blocking,  # AI是否格挡
            abs_horizontal_distance/800,  # 归一化水平距离
            abs(vertical_distance)/600  # 归一化垂直距离
        ]
        
        # 根据状态生成高级策略标签
        action = _decide_action_with_advanced_strategy(
            ai_x, ai_y, ai_health, 
            player_x, player_y, player_health, 
            horizontal_distance, vertical_distance,
            player_attacking, ai_blocking
        )
        
        # 添加到训练数据
        X.append(features)
        
        # 将动作转换为one-hot编码
        action_onehot = [0] * len(ACTIONS)
        action_onehot[action] = 1
        y.append(action_onehot)
    
    return np.array(X), np.array(y)

def _decide_action_with_advanced_strategy(
    ai_x, ai_y, ai_health, 
    player_x, player_y, player_health, 
    horizontal_distance, vertical_distance,
    player_attacking, ai_blocking
):
    """使用高级策略决定动作
    
    返回:
        动作ID
    """
    abs_horizontal_distance = abs(horizontal_distance)
    
    # 模拟决策树对不同情况的处理
    
    # 1. 如果玩家在攻击
    if player_attacking:
        # 近距离时大概率格挡
        if abs_horizontal_distance < 120:
            if random.random() < 0.75:  # 75%概率格挡
                return 5  # 格挡
            elif random.random() < 0.5:
                return 3  # 跳跃躲避
            else:
                return 4  # 蹲下躲避
        
        # 中距离时有可能后退
        elif abs_horizontal_distance < 250:
            if random.random() < 0.4:  # 40%概率后退
                return 1 if ai_x > player_x else 2  # 向相反方向移动
            elif random.random() < 0.4:
                return 5  # 格挡
            else:
                # 逆向思维：攻击是最好的防守
                return random.choice([6, 7, 8, 9])
    
    # 2. 处理距离因素
    # 太近，需要拉开距离
    if abs_horizontal_distance < 50:
        # 血量低的时候更倾向于拉开距离
        if ai_health < player_health and random.random() < 0.7:
            return 1 if ai_x < player_x else 2  # 向远离玩家的方向移动
        # 否则更倾向于攻击
        else:
            # 根据玩家位置选择合适的攻击
            if abs(vertical_distance) > 50:  # 垂直距离较大时
                return random.choice([8, 9])  # 使用腿法攻击，范围更大
            else:
                return random.choice([6, 7])  # 使用拳法攻击，速度更快
    
    # 近距离，适合攻击
    elif abs_horizontal_distance < 120:
        # 攻击判断
        if ai_health > player_health or random.random() < 0.7:
            # 健康时更激进
            attack_chance = 0.8
        else:
            # 血量低时更保守
            attack_chance = 0.3
        
        if random.random() < attack_chance:
            # 垂直距离影响攻击选择
            if abs(vertical_distance) > 50:
                return random.choice([8, 9])  # 使用腿法
            else:
                return random.choice([6, 7])  # 使用拳法
        else:
            return 5  # 格挡
    
    # 中等距离，需要接近或保持距离
    elif abs_horizontal_distance < 300:
        # 血量高于玩家时更倾向于靠近
        if ai_health >= player_health:
            if random.random() < 0.7:  # 70%概率接近玩家
                return 2 if ai_x < player_x else 1  # 向玩家方向移动
            elif random.random() < 0.2:
                return 3  # 跳跃接近
            else:
                return 0  # 站立不动，等待玩家接近
        # 血量低于玩家时更倾向于保持距离
        else:
            if random.random() < 0.6:  # 60%概率保持距离
                return 1 if ai_x < player_x else 2  # 向远离玩家方向移动
            elif random.random() < 0.3:
                return 5  # 尝试格挡
            else:
                return 0  # 站立不动，评估形势
    
    # 远距离，需要靠近
    else:
        approach_chance = 0.8
        # 如果健康状况好，更倾向于接近
        if ai_health < player_health * 0.5:  # 血量低于玩家一半
            approach_chance = 0.5
        
        if random.random() < approach_chance:
            # 大部分时候选择移动接近
            if random.random() < 0.8:
                return 2 if ai_x < player_x else 1  # 向玩家方向移动
            else:
                return 3  # 跳跃接近
        else:
            return 0  # 站立不动，可能是等待时机
    
    # 默认行为：随机选择
    return random.randrange(len(ACTIONS))

def train_model():
    """训练模型并保存"""
    print("开始训练AI模型...")
    
    # 创建模型
    use_lstm = False  # 使用普通前馈网络，因为LSTM需要更多数据
    model = create_model(use_lstm)
    
    # 生成高级训练数据
    print("生成训练数据...")
    X_train, y_train = generate_advanced_training_data(20000)  # 增加到20000个样本
    
    # 生成验证数据
    X_val, y_val = generate_advanced_training_data(3000)  # 增加到3000个样本
    
    # 训练回调
    callbacks = [
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=0.00001
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
    ]
    
    # 训练模型
    print("训练模型中...")
    model.fit(
        X_train, y_train,
        epochs=30,  # 增加到30轮
        batch_size=128,
        validation_data=(X_val, y_val),
        verbose=1,
        callbacks=callbacks
    )
    
    # 保存模型
    model.save('models/fighting_ai_model.h5')
    print("模型已保存到 models/fighting_ai_model.h5")
    
    # 评估模型
    loss, accuracy = model.evaluate(X_val, y_val)
    print(f"验证集上的准确率: {accuracy*100:.2f}%")
    
    return model

if __name__ == "__main__":
    train_model() 