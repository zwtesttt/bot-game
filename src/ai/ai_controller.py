#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import time
import math
from src.engine.config import AI_REACTION_TIME, AI_DECISION_INTERVAL

class AIController:
    """AI控制器，负责控制AI角色的行为"""
    
    def __init__(self, character, difficulty=1, behavior_mode=None):
        """初始化AI控制器
        
        Args:
            character: AI控制的角色
            difficulty: AI难度 (1-3)
            behavior_mode: AI行为模式 ("aggressive", "defensive", "balanced", None)
        """
        self.character = character
        self.difficulty = min(max(difficulty, 1), 3)  # 确保难度在1-3之间
        self.reaction_time = AI_REACTION_TIME[self.difficulty]
        self.decision_interval = AI_DECISION_INTERVAL[self.difficulty]
        
        # AI状态
        self.last_decision_time = 0
        self.current_action = None
        self.action_start_time = 0
        self.action_duration = 0
        self.next_action_queue = []
        
        # 添加更多状态控制变量
        self.last_attack_time = time.time() - 10  # 记录上次攻击时间，初始化为过去时间
        self.min_attack_interval = 2.5  # 最小攻击间隔（秒）
        self.avoid_overlap_counter = 0  # 避免重叠计数器
        self.is_repositioning = False  # 是否正在重新定位
        
        # 根据行为模式设置决策参数
        if behavior_mode == "aggressive":
            self.aggression = 0.6 + (self.difficulty * 0.1)  # 攻击性 (0.7-0.9)
            self.defense = 0.1 + (self.difficulty * 0.1)     # 防御性 (0.2-0.4)
            self.movement = 0.5 + (self.difficulty * 0.1)    # 移动性 (0.6-0.8)
        elif behavior_mode == "defensive":
            self.aggression = 0.2 + (self.difficulty * 0.1)  # 攻击性 (0.3-0.5)
            self.defense = 0.5 + (self.difficulty * 0.1)     # 防御性 (0.6-0.8)
            self.movement = 0.3 + (self.difficulty * 0.1)    # 移动性 (0.4-0.6)
        elif behavior_mode == "balanced":
            self.aggression = 0.4 + (self.difficulty * 0.1)  # 攻击性 (0.5-0.7)
            self.defense = 0.4 + (self.difficulty * 0.1)     # 防御性 (0.5-0.7)
            self.movement = 0.4 + (self.difficulty * 0.1)    # 移动性 (0.5-0.7)
        else:
            # 默认行为
            self.aggression = 0.3 + (self.difficulty * 0.2)  # 攻击性 (0.5-0.9)
            self.defense = 0.2 + (self.difficulty * 0.2)     # 防御性 (0.4-0.8)
            self.movement = 0.4 + (self.difficulty * 0.1)    # 移动性 (0.5-0.7)
            
        # 降低总体攻击性，提高防御性和移动性
        self.aggression *= 0.6  # 降低攻击欲望
        self.defense *= 1.2     # 提高防御性
        self.movement *= 1.3    # 提高移动性
        
        # 攻击计数和限制
        self.attack_count = 0   # 连续攻击计数
        self.max_consecutive_attacks = 2  # 最大连续攻击次数
    
    def update(self, dt, player_character):
        """更新AI逻辑
        
        Args:
            dt: 时间增量（秒）
            player_character: 玩家角色
        """
        current_time = time.time()
        
        # 获取角色状态数据
        ai_state = self.character.get_state_data()
        player_state = player_character.get_state_data()
        distance = abs(ai_state['x'] - player_state['x'])
        
        # 紧急避免重叠检测 - 每帧都检查以确保快速反应
        if distance < 100 and not self.character.is_attacking and not player_character.is_attacking:
            # 如果太近并且没有在攻击，立即采取紧急避让行动
            self.current_action = None  # 取消当前动作
            self.next_action_queue = []  # 清空动作队列
            self.avoid_overlap_counter += 1
            
            # 根据重叠计数器选择不同的避让策略
            if self.avoid_overlap_counter > 5:
                # 如果连续多次触发重叠避让，尝试更激进的策略
                self.is_repositioning = True
                
                # 添加跳跃后退的组合动作
                self._execute_action(self._jump, 0.5)
                
                # 确定后退方向
                direction = 'left' if ai_state['x'] > player_state['x'] else 'right'
                self.next_action_queue.append((lambda: self._move(direction), 0.8))
                
                # 可能的再次跳跃
                if random.random() < 0.4:
                    self.next_action_queue.append((self._jump, 0.5))
                    self.next_action_queue.append((lambda: self._move(direction), 0.5))
                
                # 重置计数器，避免无限循环
                self.avoid_overlap_counter = 0
            else:
                # 简单后退
                direction = 'left' if ai_state['x'] > player_state['x'] else 'right'
                self._move(direction)  # 直接调用移动而不是通过_execute_action
            
            # 设置标记以记录正在重新定位
            self.is_repositioning = True
            return  # 直接返回，不执行其他决策
        else:
            # 如果没有重叠，逐渐重置计数器
            if self.avoid_overlap_counter > 0:
                self.avoid_overlap_counter -= 1
            
            # 如果距离足够大，重置重新定位标记
            if distance > 200:
                self.is_repositioning = False
        
        # 执行当前动作
        if self.current_action:
            # 检查动作是否完成
            if current_time - self.action_start_time > self.action_duration:
                self.current_action = None
                
                # 如果有排队的下一个动作，执行它
                if self.next_action_queue:
                    next_action, duration = self.next_action_queue.pop(0)
                    
                    # 如果是攻击动作，检查冷却是否结束和攻击间隔是否满足
                    if next_action.__name__ == '_attack':
                        attack_interval = current_time - self.last_attack_time
                        if self.character.attack_cooldown > 0 or attack_interval < self.min_attack_interval:
                            # 攻击冷却未结束或间隔太短，跳过此动作
                            if self.next_action_queue:
                                next_action, duration = self.next_action_queue.pop(0)
                                self._execute_action(next_action, duration)
                        else:
                            # 执行攻击动作
                            self._execute_action(next_action, duration)
                            self.last_attack_time = current_time
                            self.attack_count += 1
                    else:
                        # 执行非攻击动作
                        self._execute_action(next_action, duration)
                        
                        # 如果是移动动作，重置攻击计数
                        if next_action.__name__ == '_move':
                            self.attack_count = 0
        
        # 如果没有当前动作，而且已经过了决策间隔，做出新决策
        if not self.current_action and (current_time - self.last_decision_time > self.decision_interval):
            self._make_decision(player_character)
            self.last_decision_time = current_time
    
    def _make_decision(self, player_character):
        """根据游戏状态做出决策
        
        Args:
            player_character: 玩家角色
        """
        current_time = time.time()
        ai_state = self.character.get_state_data()
        player_state = player_character.get_state_data()
        
        # 计算与玩家的距离
        distance = abs(ai_state['x'] - player_state['x'])
        
        # 检查攻击冷却时间和间隔时间
        can_attack = self.character.attack_cooldown <= 0
        attack_interval = current_time - self.last_attack_time
        
        # 强制攻击机制：每10秒必须尝试攻击一次，防止AI永远不攻击的情况
        force_attack = (attack_interval > 10.0)
        if force_attack:
            print(f"{self.character.name} 触发强制攻击机制!")
        
        # 如果正在重新定位，优先考虑移动和保持距离
        if self.is_repositioning and not force_attack:
            # 保持距离，直到定位完成
            direction = 'left' if ai_state['x'] > player_state['x'] else 'right'
            self._execute_action(lambda: self._move(direction), 0.8)
            
            # 随机跳跃以避免卡位
            if random.random() < 0.3:
                self.next_action_queue.append((self._jump, 0.6))
            
            # 有一定概率重置重新定位状态
            if random.random() < 0.2:
                self.is_repositioning = False
            
            return
        
        # 检查是否重叠或距离过近，如果是则先拉开距离
        if distance < 120 and not force_attack:  # 扩大距离检测范围
            # 向远离对方的方向移动，更长时间以确保拉开足够距离
            direction = 'left' if ai_state['x'] > player_state['x'] else 'right'
            self._execute_action(lambda: self._move(direction), 1.0)
            # 增加跳跃的概率，避免水平方向的卡位
            if random.random() < 0.5:  # 提高跳跃概率
                self.next_action_queue.append((self._jump, 0.6))
            return
        
        # 控制攻击频率和连续攻击次数
        allow_attack = (can_attack and 
                       (attack_interval >= self.min_attack_interval or force_attack) and 
                       (self.attack_count < self.max_consecutive_attacks or force_attack))
                       
        # 在可以攻击的情况下，提高攻击概率
        # 如果两个AI一段时间没有攻击，增加攻击概率
        attack_chance = 0.65  # 提高攻击概率（原为0.25）
        
        # 如果是AI对战AI模式（根据名称判断），进一步增加攻击概率
        if hasattr(self.character, 'name') and self.character.name.startswith('AI'):
            attack_chance += 0.15
            
            # 如果双方距离适中，额外增加攻击概率
            if 120 <= distance <= 220:
                attack_chance += 0.15
        
        # 根据时间动态调整攻击间隔
        if attack_interval < self.min_attack_interval * 1.5 and not force_attack:
            attack_chance *= 0.7  # 如果刚过最小间隔不久，减少攻击概率
        
        # 优先考虑防御，但降低优先级，增加攻击机会
        if player_state['is_attacking'] and random.random() < self.defense * 1.2 and not force_attack:
            # 对手正在攻击，有一定概率防御
            self._execute_action(self._block, 0.7)
            # 防御后立即安排后续行动，后退或跳跃
            if random.random() < 0.7:
                direction = 'left' if ai_state['x'] > player_state['x'] else 'right'
                self.next_action_queue.append((lambda: self._move(direction), 0.6))
            return
        
        # 检查是否满足攻击条件并决定是否进行攻击
        if (allow_attack and random.random() < attack_chance) or force_attack:
            # 接近对手的中距离（不要太近，避免重叠）
            ideal_attack_distance = 150  # 理想攻击距离
            
            if abs(distance - ideal_attack_distance) > 50 and not force_attack:
                # 先调整到理想攻击距离
                direction = 'right' if ai_state['x'] < player_state['x'] - ideal_attack_distance else 'left'
                self._execute_action(lambda: self._move(direction), 0.5)
                
                # 安排攻击
                # 根据角色个性和随机性选择攻击类型
                if hasattr(self.character, 'name') and 'AI 1' in self.character.name:
                    # AI 1偏好拳击
                    attack_choices = ['light_punch', 'heavy_punch', 'light_punch', 'light_kick']
                elif hasattr(self.character, 'name') and 'AI 2' in self.character.name:
                    # AI 2偏好腿法
                    attack_choices = ['light_kick', 'heavy_kick', 'light_kick', 'light_punch']
                else:
                    # 随机选择，但轻型攻击更常见
                    attack_choices = ['light_punch', 'light_kick', 'heavy_punch', 'heavy_kick']
                    
                attack_type = random.choice(attack_choices)
                self.next_action_queue.append((lambda: self._attack(attack_type), 0.4))
                
                # 攻击后后退
                back_direction = 'left' if ai_state['x'] > player_state['x'] else 'right'
                self.next_action_queue.append((lambda: self._move(back_direction), 0.6))
            else:
                # 在理想距离或强制攻击情况下，直接攻击
                # 根据角色个性和随机性选择攻击类型
                if hasattr(self.character, 'name') and 'AI 1' in self.character.name:
                    # AI 1偏好拳击
                    attack_choices = ['light_punch', 'heavy_punch', 'light_punch', 'light_kick']
                elif hasattr(self.character, 'name') and 'AI 2' in self.character.name:
                    # AI 2偏好腿法
                    attack_choices = ['light_kick', 'heavy_kick', 'light_kick', 'light_punch']
                else:
                    # 随机选择，但轻型攻击更常见
                    attack_choices = ['light_punch', 'light_kick', 'heavy_punch', 'heavy_kick']
                    
                attack_type = random.choice(attack_choices)
                self._execute_action(lambda: self._attack(attack_type), 0.5)
                self.last_attack_time = current_time
                self.attack_count += 1
                
                # 攻击后后退
                direction = 'left' if ai_state['x'] > player_state['x'] else 'right'
                self.next_action_queue.append((lambda: self._move(direction), 0.7))
            return
        
        # 如果不攻击，则以更高的概率进行移动和跳跃等动作
        # 更多随机移动，保持战场活跃度
        move_chance = self.movement * 1.2  # 提高移动概率
        
        if random.random() < move_chance:
            # 随机决定动作：后退、接近或跳跃
            # 为AI角色分配不同的行为偏好，增加个性差异
            if hasattr(self.character, 'name') and 'AI 1' in self.character.name:
                # AI 1更喜欢接近和跳跃
                weights = [0.5, 0.2, 0.2, 0.1]  # [approach, retreat, jump, idle]
            elif hasattr(self.character, 'name') and 'AI 2' in self.character.name:
                # AI 2更喜欢后退和等待
                weights = [0.3, 0.4, 0.1, 0.2]  # [approach, retreat, jump, idle]
            else:
                # 默认权重
                weights = [0.4, 0.3, 0.2, 0.1]  # [approach, retreat, jump, idle]
                
            action_type = random.choices(
                ['approach', 'retreat', 'jump', 'idle'], 
                weights=weights
            )[0]
            
            if action_type == 'approach':
                # 靠近对手，但保持适当距离
                direction = 'right' if ai_state['x'] < player_state['x'] - 150 else 'left'
                self._execute_action(lambda: self._move(direction), random.uniform(0.5, 0.8))
                
                # 接近后随机跳跃
                if random.random() < 0.3:
                    self.next_action_queue.append((self._jump, 0.5))
                    
            elif action_type == 'retreat':
                # 后退拉开距离
                direction = 'left' if ai_state['x'] > player_state['x'] - 200 else 'right'
                self._execute_action(lambda: self._move(direction), random.uniform(0.6, 1.0))
                
            elif action_type == 'jump':
                # 跳跃移动
                self._execute_action(self._jump, 0.6)
                
                # 跳跃时随机移动
                if random.random() < 0.7:
                    direction = random.choice(['left', 'right'])
                    self.next_action_queue.append((lambda: self._move(direction), 0.4))
                    
            else:  # idle
                # 短暂原地等待，然后准备下一个动作
                self._execute_action(self._stop_moving, 0.3)
                
                # 随机决定下一步行动
                if random.random() < 0.5:
                    self.next_action_queue.append((self._jump, 0.5))
                else:
                    direction = random.choice(['left', 'right'])
                    self.next_action_queue.append((lambda: self._move(direction), 0.5))
        else:
            # 防御或者观察
            if random.random() < self.defense and distance < 250:
                # 在适当距离内随机防御
                self._execute_action(self._block, random.uniform(0.3, 0.7))
                
                # 防御后立即准备移动
                direction = 'left' if ai_state['x'] > player_state['x'] else 'right'
                self.next_action_queue.append((lambda: self._move(direction), 0.5))
            else:
                # 短暂等待观察
                self._execute_action(self._stop_moving, 0.2)
                
                # 随后进行移动
                direction = 'right' if ai_state['x'] < player_state['x'] else 'left'
                self.next_action_queue.append((lambda: self._move(direction), 0.4))
    
    def _execute_action(self, action_func, duration):
        """执行动作
        
        Args:
            action_func: 要执行的动作函数
            duration: 动作持续时间
        """
        action_func()
        self.current_action = action_func
        self.action_start_time = time.time()
        self.action_duration = duration
    
    def _move(self, direction):
        """移动
        
        Args:
            direction: 移动方向 ('left' 或 'right')
        """
        if direction == 'left':
            self.character.move_left()
        else:
            self.character.move_right()
    
    def _jump(self):
        """跳跃"""
        self.character.jump()
    
    def _crouch(self):
        """下蹲"""
        self.character.crouch()
    
    def _stand_up(self):
        """站立"""
        self.character.stand_up()
    
    def _block(self):
        """格挡"""
        self.character.block()
    
    def _stop_blocking(self):
        """停止格挡"""
        self.character.stop_blocking()
    
    def _attack(self, attack_type):
        """攻击
        
        Args:
            attack_type: 攻击类型
            
        Returns:
            bool: 是否成功执行攻击
        """
        # 调试信息 - 记录攻击尝试
        print(f"AI尝试攻击: {attack_type}, 冷却状态: {self.character.attack_cooldown}")
        
        # 只有在攻击冷却结束时才执行攻击
        if self.character.attack_cooldown <= 0:
            if attack_type == 'light_punch':
                self.character.light_punch()
            elif attack_type == 'heavy_punch':
                self.character.heavy_punch()
            elif attack_type == 'light_kick':
                self.character.light_kick()
            elif attack_type == 'heavy_kick':
                self.character.heavy_kick()
            print(f"AI成功执行攻击: {attack_type}")
            return True
        else:
            print(f"AI攻击失败: 冷却未结束, 剩余: {self.character.attack_cooldown:.2f}秒")
        return False
    
    def _stop_moving(self):
        """停止移动"""
        self.character.stop_moving() 