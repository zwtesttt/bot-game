#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
自定义AI接口

这个模块允许用户创建自己的AI逻辑来控制游戏角色。
要创建自定义AI，只需继承CustomAIBase类并实现make_decision方法。
"""

import random
import numpy as np
import time
import os

# 动作映射与train_model.py中保持一致
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

class CustomAIBase:
    """自定义AI基类"""
    
    def __init__(self, character):
        """初始化自定义AI
        
        Args:
            character: AI控制的角色
        """
        self.character = character
    
    def update(self, dt, player_character):
        """更新AI逻辑
        
        Args:
            dt: 时间增量（秒）
            player_character: 玩家角色
        """
        # 调用子类实现的决策方法
        self.make_decision(player_character)
    
    def make_decision(self, player_character):
        """根据游戏状态做出决策（子类应该重写此方法）
        
        Args:
            player_character: 玩家角色
        """
        raise NotImplementedError("子类必须实现make_decision方法")


class SimpleCustomAI(CustomAIBase):
    """简单的自定义AI示例"""
    
    def __init__(self, character):
        """初始化简单自定义AI"""
        super().__init__(character)
    
    def make_decision(self, player_character):
        """一个简单的AI决策逻辑示例
        
        Args:
            player_character: 玩家角色
        """
        # 获取AI角色和玩家角色的状态数据
        ai_state = self.character.get_state_data()
        player_state = player_character.get_state_data()
        
        # 计算与玩家的水平距离
        distance = abs(ai_state['x'] - player_state['x'])
        
        # 简单的决策逻辑：接近并攻击
        if distance > 100:
            # 如果距离大于100像素，向玩家移动
            if ai_state['x'] < player_state['x']:
                self.character.move_right()
            else:
                self.character.move_left()
        else:
            # 如果足够近，停止移动并攻击
            self.character.stop_moving()
            
            # 随机选择一种攻击
            attack = random.choice(['light_punch', 'heavy_punch', 'light_kick', 'heavy_kick'])
            
            if attack == 'light_punch':
                self.character.light_punch()
            elif attack == 'heavy_punch':
                self.character.heavy_punch()
            elif attack == 'light_kick':
                self.character.light_kick()
            elif attack == 'heavy_kick':
                self.character.heavy_kick()


class MLBasedAI(CustomAIBase):
    """基于机器学习的AI"""
    
    def __init__(self, character, model_path="models/fighting_ai_model.h5"):
        """初始化基于机器学习的AI
        
        Args:
            character: AI控制的角色
            model_path: 机器学习模型路径
        """
        super().__init__(character)
        
        # 检查模型文件是否存在
        if not os.path.exists(model_path):
            print(f"警告: AI模型文件不存在: {model_path}")
            print("使用简单AI替代")
            self.model = None
            self.fallback_ai = SimpleCustomAI(character)
        else:
            self.model = self._load_model(model_path)
            self.fallback_ai = SimpleCustomAI(character) if self.model is None else None
        
        # 防止AI过于频繁做决策
        self.last_decision_time = 0
        self.decision_interval = 0.2  # 改为每0.2秒做一次决策，提高反应速度
        self.current_action = None
        
        # 动作冷却时间
        self.action_cooldown = {
            "move": 0,
            "attack": 0,
            "block": 0,
            "jump": 0,
            "crouch": 0
        }
        
        # 战斗状态追踪
        self.combo_state = {
            "current_combo": [],      # 当前连招
            "combo_timer": 0,         # 连招计时器
            "last_distance": 0,       # 上次距离
            "last_player_action": 0,  # 上次玩家动作
            "successful_blocks": 0,   # 成功格挡次数
            "attack_success_rate": 0.5, # 攻击成功率
            "player_attack_patterns": {} # 玩家攻击模式
        }
        
        # 行为策略权重
        self.strategy_weights = {
            "aggressive": 0.5,    # 攻击性
            "defensive": 0.3,     # 防御性
            "reactive": 0.2,      # 反应性
            "unpredictable": 0.1  # 不可预测性
        }
        
        # 定义组合技
        self.combos = [
            ["light_punch", "light_punch", "heavy_punch"],  # 连续轻拳接重拳
            ["light_kick", "heavy_kick"],                   # 轻腿接重腿
            ["jump", "heavy_kick"],                         # 跳跃重腿
            ["move_close", "light_punch", "light_kick"]     # 接近+轻拳+轻腿
        ]
    
    def _load_model(self, model_path):
        """加载机器学习模型
        
        Args:
            model_path: 模型路径
            
        Returns:
            加载的模型或None
        """
        try:
            # 导入TensorFlow
            import tensorflow as tf
            from tensorflow.keras.models import load_model
            
            # 加载模型
            print(f"正在加载AI模型: {model_path}")
            model = load_model(model_path)
            print("AI模型加载成功!")
            return model
        except ImportError:
            print("错误: 未找到TensorFlow。请确保已安装tensorflow库。")
            return None
        except Exception as e:
            print(f"加载模型失败: {e}")
            return None
    
    def make_decision(self, player_character):
        """使用机器学习模型和高级策略做出决策
        
        Args:
            player_character: 玩家角色
        """
        # 如果模型加载失败，使用备用AI
        if self.fallback_ai:
            self.fallback_ai.make_decision(player_character)
            return
            
        current_time = time.time()
        
        # 控制决策频率
        if current_time - self.last_decision_time < self.decision_interval:
            return
        
        self.last_decision_time = current_time
        
        # 更新冷却时间
        for action_type in self.action_cooldown:
            if self.action_cooldown[action_type] > 0:
                self.action_cooldown[action_type] -= self.decision_interval
        
        # 获取状态数据
        ai_state = self.character.get_state_data()
        player_state = player_character.get_state_data()
        
        # 计算与玩家的距离
        distance = abs(ai_state['x'] - player_state['x'])
        
        # 更新连招状态
        self._update_combo_state(ai_state, player_state, distance)
        
        # 分析玩家行为模式
        self._analyze_player_behavior(player_state)
        
        # 准备输入数据
        input_data = self._prepare_input_data(player_character)
        
        # 使用模型预测基础动作概率
        base_action_probs = self.model.predict(np.array([input_data]), verbose=0)[0]
        
        # 应用高级策略调整动作概率
        action_probs = self._apply_strategy_adjustments(
            base_action_probs, 
            ai_state, 
            player_state, 
            distance
        )
        
        # 如果正在进行连招，继续连招
        if self.combo_state["current_combo"] and self.combo_state["combo_timer"] < 1.0:
            next_combo_move = self.combo_state["current_combo"][0]
            if self._execute_combo_move(next_combo_move, player_character):
                # 移除已执行的连招动作
                self.combo_state["current_combo"].pop(0)
                self.combo_state["combo_timer"] = 0
                return
        
        # 按概率排序动作
        actions_sorted = [(i, prob) for i, prob in enumerate(action_probs)]
        actions_sorted.sort(key=lambda x: x[1], reverse=True)
        
        # 是否开始新的连招
        if not self.combo_state["current_combo"] and distance < 150 and random.random() < 0.3:
            selected_combo = random.choice(self.combos)
            self.combo_state["current_combo"] = selected_combo.copy()
            self.combo_state["combo_timer"] = 0
            # 执行第一个连招动作
            next_combo_move = self.combo_state["current_combo"].pop(0)
            if self._execute_combo_move(next_combo_move, player_character):
                return
        
        # 尝试执行概率最高的动作，如果在冷却中则尝试下一个
        for action_id, _ in actions_sorted[:3]:  # 只考虑前3个最高概率的动作
            if self._try_execute_action(action_id, player_character):
                break
    
    def _update_combo_state(self, ai_state, player_state, current_distance):
        """更新连招状态
        
        Args:
            ai_state: AI状态
            player_state: 玩家状态
            current_distance: 当前距离
        """
        # 更新连招计时器
        self.combo_state["combo_timer"] += self.decision_interval
        
        # 如果连招超时，重置连招
        if self.combo_state["combo_timer"] > 1.0:
            self.combo_state["current_combo"] = []
        
        # 记录距离变化
        self.combo_state["last_distance"] = current_distance
        
        # 记录玩家动作
        self.combo_state["last_player_action"] = player_state["state"]
    
    def _analyze_player_behavior(self, player_state):
        """分析玩家行为模式
        
        Args:
            player_state: 玩家状态
        """
        # 记录玩家攻击模式
        if player_state["is_attacking"]:
            attack_type = player_state["state"]
            if attack_type not in self.combo_state["player_attack_patterns"]:
                self.combo_state["player_attack_patterns"][attack_type] = 0
            self.combo_state["player_attack_patterns"][attack_type] += 1
    
    def _apply_strategy_adjustments(self, base_probs, ai_state, player_state, distance):
        """应用高级策略调整动作概率
        
        Args:
            base_probs: 基础动作概率
            ai_state: AI状态
            player_state: 玩家状态
            distance: 当前距离
            
        Returns:
            调整后的动作概率
        """
        adjusted_probs = base_probs.copy()
        
        # 根据玩家生命值调整策略
        if player_state["health"] < 30:
            # 玩家血量低时，提高攻击性
            self.strategy_weights["aggressive"] += 0.2
        
        # 根据自身生命值调整策略
        if ai_state["health"] < 30:
            # AI血量低时，提高防御性
            self.strategy_weights["defensive"] += 0.2
        
        # 玩家攻击时提高防御概率
        if player_state["is_attacking"] and distance < 150:
            adjusted_probs[5] *= (1.0 + self.strategy_weights["defensive"] * 2)  # 增加格挡概率
        
        # 根据距离调整动作概率
        if distance > 200:
            # 远距离提高移动和跳跃概率
            move_dir = 1 if ai_state["x"] > player_state["x"] else 2  # 向左或向右
            adjusted_probs[move_dir] *= 1.5
            adjusted_probs[3] *= 1.3  # 提高跳跃概率
        elif distance < 100:
            # 近距离提高攻击概率
            for action_id in [6, 7, 8, 9]:  # 攻击动作
                adjusted_probs[action_id] *= (1.0 + self.strategy_weights["aggressive"])
        
        # 添加一定随机性，避免AI太容易预测
        if random.random() < self.strategy_weights["unpredictable"]:
            random_action = random.randint(0, len(adjusted_probs)-1)
            adjusted_probs[random_action] *= 1.5
        
        # 根据玩家攻击模式，预判和应对
        if self.combo_state["player_attack_patterns"]:
            most_common_attack = max(self.combo_state["player_attack_patterns"].items(), 
                                    key=lambda x: x[1])[0]
            # 如果玩家经常使用某种攻击，提高相应的防御动作概率
            adjusted_probs[5] *= 1.2  # 提高格挡概率
        
        # 归一化概率
        total = sum(adjusted_probs)
        if total > 0:
            adjusted_probs = [p / total for p in adjusted_probs]
        
        return adjusted_probs
    
    def _execute_combo_move(self, move, player_character):
        """执行连招动作
        
        Args:
            move: 连招动作
            player_character: 玩家角色
            
        Returns:
            是否成功执行
        """
        if move == "light_punch":
            if self.action_cooldown["attack"] <= 0:
                self.character.light_punch()
                self.action_cooldown["attack"] = 0.3  # 减少冷却时间，加快连招
                return True
        elif move == "heavy_punch":
            if self.action_cooldown["attack"] <= 0:
                self.character.heavy_punch()
                self.action_cooldown["attack"] = 0.4  # 减少冷却时间
                return True
        elif move == "light_kick":
            if self.action_cooldown["attack"] <= 0:
                self.character.light_kick()
                self.action_cooldown["attack"] = 0.3
                return True
        elif move == "heavy_kick":
            if self.action_cooldown["attack"] <= 0:
                self.character.heavy_kick()
                self.action_cooldown["attack"] = 0.4
                return True
        elif move == "jump":
            if self.action_cooldown["jump"] <= 0:
                self.character.jump()
                self.action_cooldown["jump"] = 0.7
                return True
        elif move == "move_close":
            # 获取状态数据计算方向
            ai_state = self.character.get_state_data()
            player_state = player_character.get_state_data()
            direction = "right" if ai_state["x"] < player_state["x"] else "left"
            if self.action_cooldown["move"] <= 0:
                if direction == "left":
                    self.character.move_left()
                else:
                    self.character.move_right()
                self.action_cooldown["move"] = 0.1
                return True
                
        return False
    
    def _try_execute_action(self, action_id, player_character):
        """尝试执行动作，如果在冷却中则返回False
        
        Args:
            action_id: 动作ID
            player_character: 玩家角色
            
        Returns:
            是否成功执行
        """
        # 检查动作是否在冷却中
        if action_id == 0:  # 无动作
            self.character.stop_moving()
            return True
            
        elif action_id == 1:  # 向左移动
            if self.action_cooldown["move"] <= 0:
                self.character.move_left()
                self.action_cooldown["move"] = 0.1
                return True
                
        elif action_id == 2:  # 向右移动
            if self.action_cooldown["move"] <= 0:
                self.character.move_right()
                self.action_cooldown["move"] = 0.1
                return True
                
        elif action_id == 3:  # 跳跃
            if self.action_cooldown["jump"] <= 0:
                self.character.jump()
                self.action_cooldown["jump"] = 1.0
                return True
                
        elif action_id == 4:  # 蹲下
            if self.action_cooldown["crouch"] <= 0:
                self.character.crouch()
                self.action_cooldown["crouch"] = 0.5
                return True
                
        elif action_id == 5:  # 格挡
            if self.action_cooldown["block"] <= 0:
                self.character.block()
                self.action_cooldown["block"] = 0.5
                return True
                
        elif action_id == 6:  # 轻拳
            if self.action_cooldown["attack"] <= 0:
                self.character.light_punch()
                self.action_cooldown["attack"] = 0.5
                return True
                
        elif action_id == 7:  # 重拳
            if self.action_cooldown["attack"] <= 0:
                self.character.heavy_punch()
                self.action_cooldown["attack"] = 0.7
                return True
                
        elif action_id == 8:  # 轻腿
            if self.action_cooldown["attack"] <= 0:
                self.character.light_kick()
                self.action_cooldown["attack"] = 0.5
                return True
                
        elif action_id == 9:  # 重腿
            if self.action_cooldown["attack"] <= 0:
                self.character.heavy_kick()
                self.action_cooldown["attack"] = 0.7
                return True
                
        return False
    
    def _prepare_input_data(self, player_character):
        """准备模型输入数据
        
        Args:
            player_character: 玩家角色
            
        Returns:
            输入数据数组
        """
        # 获取AI角色和玩家角色的状态数据
        ai_state = self.character.get_state_data()
        player_state = player_character.get_state_data()
        
        # 特征工程：计算相对位置和距离等
        horizontal_distance = player_state['x'] - ai_state['x']
        vertical_distance = player_state['y'] - ai_state['y']
        absolute_distance = np.sqrt(horizontal_distance**2 + vertical_distance**2)
        
        # 距离归一化
        normalized_horizontal_distance = horizontal_distance / 800  # 屏幕宽度
        normalized_vertical_distance = vertical_distance / 600  # 屏幕高度
        normalized_absolute_distance = absolute_distance / 1000
        
        # 构建特征向量 - 调整为10个特征以匹配模型期望
        features = [
            ai_state['x']/800,  # 归一化AI位置x
            ai_state['y']/600,  # 归一化AI位置y
            ai_state['health']/100,  # 归一化AI生命值
            player_state['x']/800,  # 归一化玩家位置x
            player_state['y']/600,  # 归一化玩家位置y
            player_state['health']/100,  # 归一化玩家生命值
            1 if player_state['is_attacking'] else 0,  # 玩家是否攻击中
            1 if ai_state['is_blocking'] else 0,       # AI是否格挡
            abs(horizontal_distance)/800,  # 归一化水平距离
            abs(vertical_distance)/600     # 归一化垂直距离
        ]
        
        return np.array(features) 