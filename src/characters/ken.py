#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pygame
from src.characters.character import Character, CharacterState, Direction

class Ken(Character):
    """Ken角色类"""
    
    def __init__(self, x, y):
        """初始化Ken角色"""
        super().__init__(x, y, "Ken")
    
    def _load_sprites(self):
        """加载Ken的精灵图"""
        sprites = {}
        
        # 检查是否存在实际的图像资源
        base_path = os.path.join("assets", "images", "characters", "ken")
        has_sprite_images = os.path.exists(base_path)
        
        # 为每个状态和方向创建图像
        for state in CharacterState:
            sprites[state] = {Direction.RIGHT: [], Direction.LEFT: []}
            
            # 每个状态的帧数
            frames = 1
            if state == CharacterState.IDLE:
                frames = 4
            elif state == CharacterState.WALKING:
                frames = 4  # 使用IDLE动画
            elif state == CharacterState.RUNNING:
                frames = 4  # 使用WALKING或IDLE动画
            elif state == CharacterState.JUMPING:
                frames = 3
            elif state in [CharacterState.LIGHT_PUNCH, CharacterState.HEAVY_PUNCH,
                          CharacterState.LIGHT_KICK, CharacterState.HEAVY_KICK]:
                frames = 3
            
            # 使用实际的精灵图（如果存在）
            if has_sprite_images:
                try:
                    # 根据状态选择不同的精灵表
                    sprite_sheet_path = None
                    if state == CharacterState.IDLE:
                        sprite_sheet_path = os.path.join(base_path, "idle.png")
                    elif state == CharacterState.WALKING:
                        # 对于行走状态，也使用idle精灵图
                        sprite_sheet_path = os.path.join(base_path, "idle.png")
                    elif state == CharacterState.RUNNING:
                        # 对于奔跑状态，尝试使用run精灵图，如果没有则使用walk或idle
                        run_path = os.path.join(base_path, "run.png")
                        if os.path.exists(run_path):
                            sprite_sheet_path = run_path
                        else:
                            # 回退到walk或idle
                            walk_path = os.path.join(base_path, "walk.png")
                            sprite_sheet_path = walk_path if os.path.exists(walk_path) else os.path.join(base_path, "idle.png")
                    elif state == CharacterState.JUMPING or state == CharacterState.FALLING:
                        # 对于跳跃和下落状态，使用jump精灵图
                        sprite_sheet_path = os.path.join(base_path, "jump.png")
                    elif state in [CharacterState.LIGHT_PUNCH, CharacterState.HEAVY_PUNCH]:
                        sprite_sheet_path = os.path.join(base_path, "punch.png")
                    elif state in [CharacterState.LIGHT_KICK, CharacterState.HEAVY_KICK]:
                        sprite_sheet_path = os.path.join(base_path, "kick.png")
                    elif state == CharacterState.CROUCHING:
                        # 对于蹲下状态，使用idle精灵图
                        sprite_sheet_path = os.path.join(base_path, "idle.png")
                    elif state == CharacterState.BLOCKING:
                        # 对于格挡状态，使用idle精灵图
                        sprite_sheet_path = os.path.join(base_path, "idle.png")
                    elif state == CharacterState.HIT:
                        # 对于受击状态，使用hit精灵图
                        sprite_sheet_path = os.path.join(base_path, "hit.png")
                    elif state == CharacterState.DEFEATED:
                        # 对于击败状态，使用hit精灵图
                        sprite_sheet_path = os.path.join(base_path, "hit.png")
                    
                    # 如果有对应的精灵表，加载它
                    if sprite_sheet_path and os.path.exists(sprite_sheet_path):
                        sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
                        # 精灵表尺寸
                        sprite_width = sprite_sheet.get_width() // frames
                        sprite_height = sprite_sheet.get_height()
                        
                        # 从精灵表中提取每一帧
                        for i in range(frames):
                            # 创建一个新的Surface并将精灵的一部分绘制到其上
                            frame = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)
                            frame.blit(sprite_sheet, (0, 0), (i * sprite_width, 0, sprite_width, sprite_height))
                            
                            # 确保尺寸正确 - 保持原始宽高比
                            scale_factor = min(self.width / sprite_width, self.height / sprite_height)
                            new_width = int(sprite_width * scale_factor)
                            new_height = int(sprite_height * scale_factor)
                            
                            # 缩放图像
                            frame = pygame.transform.scale(frame, (new_width, new_height))
                            
                            # 创建一个空白图像，尺寸为角色尺寸
                            final_frame = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                            
                            # 将精灵图放置在空白图像的底部中央
                            x_offset = (self.width - new_width) // 2
                            y_offset = self.height - new_height
                            final_frame.blit(frame, (x_offset, y_offset))
                            
                            # 添加到右方向
                            sprites[state][Direction.RIGHT].append(final_frame)
                            
                            # 翻转作为左方向
                            flipped = pygame.transform.flip(final_frame, True, False)
                            sprites[state][Direction.LEFT].append(flipped)
                        
                        # 如果成功加载了精灵，跳过下面的默认矩形生成
                        continue
                except Exception as e:
                    print(f"加载Ken精灵图失败: {e}")
            
            # 如果没有实际图像或加载失败，生成默认矩形
            # 生成每个状态的颜色
            color = (255, 255, 255)  # 默认白色
            if state == CharacterState.IDLE:
                color = (255, 0, 0)  # 红色 (Ken的颜色)
            elif state == CharacterState.WALKING:
                color = (0, 255, 0)  # 绿色
            elif state == CharacterState.RUNNING:
                color = (200, 200, 0)  # 暗黄色
            elif state == CharacterState.JUMPING:
                color = (255, 255, 0)  # 黄色
            elif state == CharacterState.FALLING:
                color = (255, 165, 0)  # 橙色
            elif state == CharacterState.CROUCHING:
                color = (128, 0, 128)  # 紫色
            elif state == CharacterState.LIGHT_PUNCH:
                color = (255, 0, 0)  # 红色
            elif state == CharacterState.HEAVY_PUNCH:
                color = (220, 20, 60)  # 深红色
            elif state == CharacterState.LIGHT_KICK:
                color = (0, 255, 255)  # 青色
            elif state == CharacterState.HEAVY_KICK:
                color = (0, 128, 255)  # 深青色
            elif state == CharacterState.BLOCKING:
                color = (128, 128, 128)  # 灰色
            elif state == CharacterState.HIT:
                color = (255, 0, 255)  # 粉色
            elif state == CharacterState.DEFEATED:
                color = (0, 0, 0)  # 黑色
            
            # 创建帧
            for i in range(frames):
                # 创建临时画面
                temp_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                pygame.draw.rect(temp_surf, color, (0, 0, self.width, self.height))
                
                # 添加帧号文本
                font = pygame.font.SysFont(None, 24)
                text = font.render(f"{state.name} {i+1}", True, (255, 255, 255))
                temp_surf.blit(text, (10, 10))
                
                # 添加到两个方向
                sprites[state][Direction.RIGHT].append(temp_surf)
                
                # 翻转作为左方向
                flipped = pygame.transform.flip(temp_surf, True, False)
                sprites[state][Direction.LEFT].append(flipped)
        
        return sprites
    
    # Ken的特殊能力
    def heavy_punch(self):
        """Ken的重拳（可能比基类伤害更高）"""
        super().heavy_punch()
        # Ken的重拳伤害更高，但这需要修改父类方法
        # 这里只是示例，实际效果依赖于Character类的实现 