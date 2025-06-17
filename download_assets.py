#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
下载游戏资源脚本
"""

import os
import requests
import zipfile
import io
import shutil
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# 创建必要的目录
def create_directories():
    """创建必要的目录结构"""
    dirs = [
        "assets/images/characters/ryu",
        "assets/images/characters/ken",
        "assets/images/characters/chun-li",
        "assets/images/backgrounds",
        "assets/sounds"
    ]
    
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ 创建目录结构完成")

# 下载资源文件
def download_file(url, filename):
    """下载文件
    
    Args:
        url: 文件URL
        filename: 保存的文件名
    
    Returns:
        是否下载成功
    """
    try:
        print(f"⬇️ 正在下载: {filename}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ 下载完成: {filename}")
        return True
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return False

# 创建高级精灵图像
def create_advanced_sprite_sheet(filename, color, secondary_color, frames=4, width=400, height=200):
    """创建高级精灵表
    
    Args:
        filename: 输出文件名
        color: 主要颜色 (R,G,B)
        secondary_color: 次要颜色 (R,G,B)
        frames: 帧数
        width: 宽度
        height: 高度
    """
    # 创建精灵表图像
    sprite_width = width // frames
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 为每一帧添加细节
    for i in range(frames):
        # 计算当前帧的位置
        x0 = i * sprite_width
        x1 = x0 + sprite_width
        cx = (x0 + x1) // 2  # 中心x坐标
        
        # 动画效果计算
        animation_phase = i / frames
        bounce = np.sin(animation_phase * np.pi * 2) * 5
        
        # 根据文件类型选择不同的绘制风格
        if filename.endswith("idle.png"):
            # ==== 站立姿势 ====
            # 头部
            head_size = sprite_width // 3
            head_y = 30 + bounce
            draw.ellipse([cx-head_size//2, head_y-head_size//2, 
                         cx+head_size//2, head_y+head_size//2], fill=color)
            
            # 眼睛和面部特征
            eye_size = head_size // 8
            if "ryu" in filename or "ken" in filename:
                # 男性角色的脸部特征
                draw.ellipse([cx-head_size//4, head_y-head_size//8, 
                             cx-head_size//4+eye_size, head_y-head_size//8+eye_size], fill=(255, 255, 255))
                draw.ellipse([cx+head_size//4-eye_size, head_y-head_size//8, 
                             cx+head_size//4, head_y-head_size//8+eye_size], fill=(255, 255, 255))
                
                # 头带 (Ryu和Ken的特征)
                if "ryu" in filename:
                    draw.rectangle([cx-head_size//2-5, head_y-head_size//3, 
                                   cx+head_size//2+5, head_y-head_size//3+10], fill=secondary_color)
            
            if "chun-li" in filename:
                # 春丽的发髻
                draw.ellipse([cx-head_size//2-8, head_y-head_size//2-5, 
                             cx-head_size//2+8, head_y-head_size//2+15], fill=secondary_color)
                draw.ellipse([cx+head_size//2-8, head_y-head_size//2-5, 
                             cx+head_size//2+8, head_y-head_size//2+15], fill=secondary_color)
            
            # 躯干
            torso_width = head_size * 1.5
            torso_height = head_size * 2
            draw.rectangle([cx-torso_width//2, head_y+head_size//2, 
                           cx+torso_width//2, head_y+head_size//2+torso_height], fill=color)
            
            # 武道服的细节
            belt_height = 8
            belt_y = head_y+head_size//2+torso_height*0.6
            draw.rectangle([cx-torso_width//2-2, belt_y, 
                           cx+torso_width//2+2, belt_y+belt_height], fill=secondary_color)
            
            # 手臂
            arm_width = 12
            shoulder_y = head_y+head_size//2+10
            arm_len = torso_height * 0.8
            # 左臂
            arm_angle = np.sin(animation_phase * np.pi * 2) * 0.2 - 0.2  # 摆动
            arm_x = cx-torso_width//2
            arm_end_x = arm_x - np.sin(arm_angle) * arm_len
            arm_end_y = shoulder_y + np.cos(arm_angle) * arm_len
            draw.line([arm_x, shoulder_y, arm_end_x, arm_end_y], fill=color, width=arm_width)
            # 左手
            draw.ellipse([arm_end_x-8, arm_end_y-8, arm_end_x+8, arm_end_y+8], fill=secondary_color)
            
            # 右臂
            arm_angle = np.sin(animation_phase * np.pi * 2 + np.pi) * 0.2 + 0.2  # 反向摆动
            arm_x = cx+torso_width//2
            arm_end_x = arm_x + np.sin(arm_angle) * arm_len
            arm_end_y = shoulder_y + np.cos(arm_angle) * arm_len
            draw.line([arm_x, shoulder_y, arm_end_x, arm_end_y], fill=color, width=arm_width)
            # 右手
            draw.ellipse([arm_end_x-8, arm_end_y-8, arm_end_x+8, arm_end_y+8], fill=secondary_color)
            
            # 腿部
            leg_width = 15
            hip_y = head_y+head_size//2+torso_height
            leg_len = torso_height * 1.2
            # 左腿
            draw.rectangle([cx-torso_width//3-leg_width//2, hip_y, 
                           cx-torso_width//3+leg_width//2, hip_y+leg_len], fill=color)
            # 左脚
            draw.ellipse([cx-torso_width//3-10, hip_y+leg_len-5, 
                         cx-torso_width//3+10, hip_y+leg_len+10], fill=secondary_color)
            
            # 右腿
            draw.rectangle([cx+torso_width//3-leg_width//2, hip_y, 
                           cx+torso_width//3+leg_width//2, hip_y+leg_len], fill=color)
            # 右脚
            draw.ellipse([cx+torso_width//3-10, hip_y+leg_len-5, 
                         cx+torso_width//3+10, hip_y+leg_len+10], fill=secondary_color)
        
        elif filename.endswith("punch.png"):
            # ==== 拳击姿势 ====
            punch_extend = animation_phase * sprite_width * 0.3  # 出拳距离
            
            # 头部
            head_size = sprite_width // 3
            head_y = 30
            draw.ellipse([cx-head_size//2, head_y-head_size//2, 
                         cx+head_size//2, head_y+head_size//2], fill=color)
            
            # 眼睛和面部特征
            eye_size = head_size // 8
            if "ryu" in filename or "ken" in filename:
                # 男性角色的脸部特征
                draw.ellipse([cx-head_size//4, head_y-head_size//8, 
                             cx-head_size//4+eye_size, head_y-head_size//8+eye_size], fill=(255, 255, 255))
                draw.ellipse([cx+head_size//4-eye_size, head_y-head_size//8, 
                             cx+head_size//4, head_y-head_size//8+eye_size], fill=(255, 255, 255))
                
                # 头带 (Ryu和Ken的特征)
                if "ryu" in filename:
                    draw.rectangle([cx-head_size//2-5, head_y-head_size//3, 
                                   cx+head_size//2+5, head_y-head_size//3+10], fill=secondary_color)
            
            if "chun-li" in filename:
                # 春丽的发髻
                draw.ellipse([cx-head_size//2-8, head_y-head_size//2-5, 
                             cx-head_size//2+8, head_y-head_size//2+15], fill=secondary_color)
                draw.ellipse([cx+head_size//2-8, head_y-head_size//2-5, 
                             cx+head_size//2+8, head_y-head_size//2+15], fill=secondary_color)
            
            # 躯干（略微倾斜）
            torso_width = head_size * 1.5
            torso_height = head_size * 2
            torso_skew = 5  # 向出拳方向倾斜
            points = [
                (cx-torso_width//2+torso_skew, head_y+head_size//2),
                (cx+torso_width//2+torso_skew, head_y+head_size//2),
                (cx+torso_width//2, head_y+head_size//2+torso_height),
                (cx-torso_width//2, head_y+head_size//2+torso_height)
            ]
            draw.polygon(points, fill=color)
            
            # 武道服的细节
            belt_height = 8
            belt_y = head_y+head_size//2+torso_height*0.6
            draw.rectangle([cx-torso_width//2, belt_y, 
                           cx+torso_width//2+torso_skew, belt_y+belt_height], fill=secondary_color)
            
            # 手臂 - 出拳的手臂伸直
            arm_width = 12
            shoulder_y = head_y+head_size//2+10
            
            # 出拳的手臂（右手）
            punch_arm_length = torso_height * 0.8 + punch_extend
            punch_arm_end_x = cx+torso_width//2 + punch_arm_length
            draw.line([cx+torso_width//2, shoulder_y, punch_arm_end_x, shoulder_y], 
                     fill=color, width=arm_width)
            
            # 拳头（右手）
            fist_size = 12
            draw.ellipse([punch_arm_end_x-fist_size, shoulder_y-fist_size, 
                         punch_arm_end_x+fist_size, shoulder_y+fist_size], fill=secondary_color)
            
            # 另一只手臂（左手）弯曲作防御姿势
            arm_len = torso_height * 0.6
            arm_x = cx-torso_width//2
            arm_mid_x = arm_x - arm_len * 0.4
            arm_mid_y = shoulder_y + arm_len * 0.4
            draw.line([arm_x, shoulder_y, arm_mid_x, arm_mid_y], fill=color, width=arm_width)
            draw.line([arm_mid_x, arm_mid_y, arm_mid_x, arm_mid_y+arm_len*0.5], 
                     fill=color, width=arm_width)
            
            # 左手
            draw.ellipse([arm_mid_x-8, arm_mid_y+arm_len*0.5-8, 
                         arm_mid_x+8, arm_mid_y+arm_len*0.5+8], fill=secondary_color)
            
            # 腿部 - 略微分开以保持平衡
            leg_width = 15
            hip_y = head_y+head_size//2+torso_height
            leg_len = torso_height * 1.2
            
            # 左腿
            leg_offset = 10  # 分开的距离
            draw.rectangle([cx-torso_width//3-leg_width//2-leg_offset, hip_y, 
                           cx-torso_width//3+leg_width//2-leg_offset, hip_y+leg_len], fill=color)
            # 左脚
            draw.ellipse([cx-torso_width//3-10-leg_offset, hip_y+leg_len-5, 
                         cx-torso_width//3+10-leg_offset, hip_y+leg_len+10], fill=secondary_color)
            
            # 右腿
            draw.rectangle([cx+torso_width//3-leg_width//2+leg_offset, hip_y, 
                           cx+torso_width//3+leg_width//2+leg_offset, hip_y+leg_len], fill=color)
            # 右脚
            draw.ellipse([cx+torso_width//3-10+leg_offset, hip_y+leg_len-5, 
                         cx+torso_width//3+10+leg_offset, hip_y+leg_len+10], fill=secondary_color)
            
            # 出拳时的动作线（速度感）
            if i > 0:  # 只在动作进行中的帧上添加
                for j in range(3):
                    line_x = punch_arm_end_x - j*15 - 5
                    draw.line([line_x, shoulder_y-10, line_x-10, shoulder_y], 
                             fill=(255,255,255,150), width=2)
            
        elif filename.endswith("kick.png"):
            # ==== 踢腿姿势 ====
            kick_phase = animation_phase
            
            # 头部
            head_size = sprite_width // 3
            head_y = 30
            draw.ellipse([cx-head_size//2, head_y-head_size//2, 
                         cx+head_size//2, head_y+head_size//2], fill=color)
            
            # 眼睛和面部特征
            eye_size = head_size // 8
            if "ryu" in filename or "ken" in filename:
                # 男性角色的脸部特征
                draw.ellipse([cx-head_size//4, head_y-head_size//8, 
                             cx-head_size//4+eye_size, head_y-head_size//8+eye_size], fill=(255, 255, 255))
                draw.ellipse([cx+head_size//4-eye_size, head_y-head_size//8, 
                             cx+head_size//4, head_y-head_size//8+eye_size], fill=(255, 255, 255))
                
                # 头带 (Ryu和Ken的特征)
                if "ryu" in filename:
                    draw.rectangle([cx-head_size//2-5, head_y-head_size//3, 
                                   cx+head_size//2+5, head_y-head_size//3+10], fill=secondary_color)
            
            if "chun-li" in filename:
                # 春丽的发髻
                draw.ellipse([cx-head_size//2-8, head_y-head_size//2-5, 
                             cx-head_size//2+8, head_y-head_size//2+15], fill=secondary_color)
                draw.ellipse([cx+head_size//2-8, head_y-head_size//2-5, 
                             cx+head_size//2+8, head_y-head_size//2+15], fill=secondary_color)
            
            # 躯干（略微后倾）
            torso_width = head_size * 1.5
            torso_height = head_size * 2
            torso_skew = -10 * kick_phase  # 向后倾斜
            points = [
                (cx-torso_width//2+torso_skew, head_y+head_size//2),
                (cx+torso_width//2+torso_skew, head_y+head_size//2),
                (cx+torso_width//2, head_y+head_size//2+torso_height),
                (cx-torso_width//2, head_y+head_size//2+torso_height)
            ]
            draw.polygon(points, fill=color)
            
            # 武道服的细节
            belt_height = 8
            belt_y = head_y+head_size//2+torso_height*0.6
            draw.rectangle([cx-torso_width//2, belt_y, 
                           cx+torso_width//2+torso_skew, belt_y+belt_height], fill=secondary_color)
            
            # 手臂 - 保持平衡
            arm_width = 12
            shoulder_y = head_y+head_size//2+10
            
            # 右手臂抬起以保持平衡
            arm_angle = 0.3  # 向上抬
            arm_len = torso_height * 0.8
            arm_x = cx+torso_width//2+torso_skew
            arm_end_x = arm_x + np.sin(arm_angle) * arm_len
            arm_end_y = shoulder_y - np.cos(arm_angle) * arm_len
            draw.line([arm_x, shoulder_y, arm_end_x, arm_end_y], fill=color, width=arm_width)
            
            # 右手
            draw.ellipse([arm_end_x-8, arm_end_y-8, arm_end_x+8, arm_end_y+8], fill=secondary_color)
            
            # 左手臂向前伸展
            arm_angle = -0.2  # 向前伸
            arm_x = cx-torso_width//2+torso_skew
            arm_end_x = arm_x + np.sin(arm_angle) * arm_len
            arm_end_y = shoulder_y + np.cos(arm_angle) * arm_len
            draw.line([arm_x, shoulder_y, arm_end_x, arm_end_y], fill=color, width=arm_width)
            
            # 左手
            draw.ellipse([arm_end_x-8, arm_end_y-8, arm_end_x+8, arm_end_y+8], fill=secondary_color)
            
            # 腿部 - 一腿抬起踢出
            leg_width = 15
            hip_y = head_y+head_size//2+torso_height
            leg_len = torso_height * 1.2
            
            # 支撑腿 (左腿)
            draw.rectangle([cx-torso_width//3-leg_width//2, hip_y, 
                           cx-torso_width//3+leg_width//2, hip_y+leg_len], fill=color)
            # 左脚
            draw.ellipse([cx-torso_width//3-10, hip_y+leg_len-5, 
                         cx-torso_width//3+10, hip_y+leg_len+10], fill=secondary_color)
            
            # 踢腿 (右腿) - 向前踢出
            kick_angle = -0.7 - kick_phase * 0.5  # 随动画逐渐踢高
            leg_x = cx+torso_width//3
            knee_x = leg_x + np.sin(kick_angle) * leg_len * 0.5
            knee_y = hip_y + np.cos(kick_angle) * leg_len * 0.5
            
            # 大腿
            draw.line([leg_x, hip_y, knee_x, knee_y], fill=color, width=leg_width)
            
            # 小腿
            kick_extend = kick_phase * 0.7  # 踢腿伸直程度
            foot_angle = kick_angle - kick_extend
            foot_x = knee_x + np.sin(foot_angle) * leg_len * 0.6
            foot_y = knee_y + np.cos(foot_angle) * leg_len * 0.6
            draw.line([knee_x, knee_y, foot_x, foot_y], fill=color, width=leg_width)
            
            # 脚
            draw.ellipse([foot_x-12, foot_y-8, foot_x+12, foot_y+8], fill=secondary_color)
            
            # 踢腿时的动作线（速度感）
            if i > 0:  # 只在动作进行中的帧上添加
                for j in range(3):
                    line_x = foot_x - j*15
                    line_y = foot_y - j*10
                    draw.line([line_x, line_y, line_x-10, line_y-5], 
                             fill=(255,255,255,150), width=2)
        # 跳跃动画
        elif filename.endswith("jump.png"):
            # 跳跃高度基于帧序号
            jump_height = animation_phase * 40
            
            # ==== 跳跃姿势 ====
            # 头部
            head_size = sprite_width // 3
            head_y = 30 - jump_height  # 头部位置随跳跃高度上升
            draw.ellipse([cx-head_size//2, head_y-head_size//2, 
                         cx+head_size//2, head_y+head_size//2], fill=color)
            
            # 眼睛和面部特征
            eye_size = head_size // 8
            if "ryu" in filename or "ken" in filename:
                # 男性角色的脸部特征
                draw.ellipse([cx-head_size//4, head_y-head_size//8, 
                             cx-head_size//4+eye_size, head_y-head_size//8+eye_size], fill=(255, 255, 255))
                draw.ellipse([cx+head_size//4-eye_size, head_y-head_size//8, 
                             cx+head_size//4, head_y-head_size//8+eye_size], fill=(255, 255, 255))
                
                # 头带 (Ryu和Ken的特征)
                if "ryu" in filename:
                    draw.rectangle([cx-head_size//2-5, head_y-head_size//3, 
                                   cx+head_size//2+5, head_y-head_size//3+10], fill=secondary_color)
            
            # 躯干 - 跳跃姿势下躯干略微前倾
            torso_width = head_size * 1.5
            torso_height = head_size * 1.8
            torso_skew = head_size * 0.3  # 前倾程度
            
            # 绘制前倾的躯干
            points = [
                (cx-torso_width//2, head_y+head_size//2),
                (cx+torso_width//2, head_y+head_size//2),
                (cx+torso_width//2-torso_skew, head_y+head_size//2+torso_height),
                (cx-torso_width//2-torso_skew, head_y+head_size//2+torso_height)
            ]
            draw.polygon(points, fill=color)
            
            # 武道服的细节
            belt_height = 8
            belt_y = head_y+head_size//2+torso_height*0.6
            draw.rectangle([cx-torso_width//2-torso_skew*0.6, belt_y, 
                           cx+torso_width//2-torso_skew*0.6, belt_y+belt_height], fill=secondary_color)
            
            # 手臂 - 跳跃姿势下双臂上举
            arm_width = 12
            shoulder_y = head_y+head_size//2+10
            
            # 右手臂上举
            arm_angle = -0.5 - animation_phase * 0.3  # 根据帧序号调整角度
            arm_len = torso_height * 0.7
            arm_x = cx+torso_width//4
            arm_end_x = arm_x + np.sin(arm_angle) * arm_len
            arm_end_y = shoulder_y + np.cos(arm_angle) * arm_len
            draw.line([arm_x, shoulder_y, arm_end_x, arm_end_y], fill=color, width=arm_width)
            
            # 右手
            draw.ellipse([arm_end_x-8, arm_end_y-8, arm_end_x+8, arm_end_y+8], fill=secondary_color)
            
            # 左手臂也上举
            arm_angle = -0.8 - animation_phase * 0.3
            arm_x = cx-torso_width//4
            arm_end_x = arm_x + np.sin(arm_angle) * arm_len
            arm_end_y = shoulder_y + np.cos(arm_angle) * arm_len
            draw.line([arm_x, shoulder_y, arm_end_x, arm_end_y], fill=color, width=arm_width)
            
            # 左手
            draw.ellipse([arm_end_x-8, arm_end_y-8, arm_end_x+8, arm_end_y+8], fill=secondary_color)
            
            # 腿部 - 跳跃姿势下双腿弯曲
            leg_width = 15
            hip_y = head_y+head_size//2+torso_height
            leg_len = torso_height * 1.1
            
            # 左腿弯曲
            knee_angle = 0.7 + animation_phase * 0.4
            knee_x = cx-torso_width//3 + np.sin(knee_angle) * leg_len * 0.5
            knee_y = hip_y + np.cos(knee_angle) * leg_len * 0.5
            draw.line([cx-torso_width//3, hip_y, knee_x, knee_y], fill=color, width=leg_width)
            
            # 小腿
            ankle_angle = knee_angle + 0.8
            ankle_x = knee_x + np.sin(ankle_angle) * leg_len * 0.5
            ankle_y = knee_y + np.cos(ankle_angle) * leg_len * 0.5
            draw.line([knee_x, knee_y, ankle_x, ankle_y], fill=color, width=leg_width)
            
            # 左脚
            draw.ellipse([ankle_x-10, ankle_y-5, ankle_x+10, ankle_y+10], fill=secondary_color)
            
            # 右腿弯曲 - 与左腿对称
            knee_angle = -0.7 - animation_phase * 0.4
            knee_x = cx+torso_width//3 + np.sin(knee_angle) * leg_len * 0.5
            knee_y = hip_y + np.cos(knee_angle) * leg_len * 0.5
            draw.line([cx+torso_width//3, hip_y, knee_x, knee_y], fill=color, width=leg_width)
            
            # 小腿
            ankle_angle = knee_angle - 0.8
            ankle_x = knee_x + np.sin(ankle_angle) * leg_len * 0.5
            ankle_y = knee_y + np.cos(ankle_angle) * leg_len * 0.5
            draw.line([knee_x, knee_y, ankle_x, ankle_y], fill=color, width=leg_width)
            
            # 右脚
            draw.ellipse([ankle_x-10, ankle_y-5, ankle_x+10, ankle_y+10], fill=secondary_color)
        
        # 受击动画
        elif filename.endswith("hit.png"):
            # 受击反应 - 头部后仰
            recoil = animation_phase * 15
            
            # ==== 受击姿势 ====
            # 头部 - 受到攻击时后仰
            head_size = sprite_width // 3
            head_y = 30 + bounce
            head_x = cx + recoil  # 头部位置向后移动
            draw.ellipse([head_x-head_size//2, head_y-head_size//2, 
                         head_x+head_size//2, head_y+head_size//2], fill=color)
            
            # 眼睛和面部特征 - 受击时表情
            eye_size = head_size // 8
            if "ryu" in filename or "ken" in filename:
                # 受击表情 - X形眼睛
                draw.line([head_x-head_size//4-5, head_y-head_size//8-5, 
                          head_x-head_size//4+5, head_y-head_size//8+5], fill=(255, 255, 255), width=2)
                draw.line([head_x-head_size//4+5, head_y-head_size//8-5, 
                          head_x-head_size//4-5, head_y-head_size//8+5], fill=(255, 255, 255), width=2)
                
                draw.line([head_x+head_size//4-5, head_y-head_size//8-5, 
                          head_x+head_size//4+5, head_y-head_size//8+5], fill=(255, 255, 255), width=2)
                draw.line([head_x+head_size//4+5, head_y-head_size//8-5, 
                          head_x+head_size//4-5, head_y-head_size//8+5], fill=(255, 255, 255), width=2)
                
                # 头带 (Ryu和Ken的特征)
                if "ryu" in filename:
                    draw.rectangle([head_x-head_size//2-5, head_y-head_size//3, 
                                   head_x+head_size//2+5, head_y-head_size//3+10], fill=secondary_color)
            
            # 躯干 - 受击时身体后倾
            torso_width = head_size * 1.5
            torso_height = head_size * 2
            torso_skew = head_size * 0.3 + recoil  # 后倾程度
            
            # 绘制后倾的躯干
            points = [
                (head_x-torso_width//2, head_y+head_size//2),
                (head_x+torso_width//2, head_y+head_size//2),
                (head_x+torso_width//2+torso_skew, head_y+head_size//2+torso_height),
                (head_x-torso_width//2+torso_skew, head_y+head_size//2+torso_height)
            ]
            draw.polygon(points, fill=color)
            
            # 受击效果 - 闪烁
            if i % 2 == 0:
                flash_color = (255, 255, 255, 100)
                draw.polygon(points, fill=flash_color)
            
            # 武道服的细节
            belt_height = 8
            belt_y = head_y+head_size//2+torso_height*0.6
            draw.rectangle([head_x-torso_width//2+torso_skew*0.5, belt_y, 
                           head_x+torso_width//2+torso_skew*0.5, belt_y+belt_height], fill=secondary_color)
            
            # 手臂 - 受击时双臂张开
            arm_width = 12
            shoulder_y = head_y+head_size//2+10
            
            # 右手臂向外张开
            arm_angle = 0.3 + animation_phase * 0.5
            arm_len = torso_height * 0.7
            arm_x = head_x+torso_width//4
            arm_end_x = arm_x + np.sin(arm_angle) * arm_len
            arm_end_y = shoulder_y + np.cos(arm_angle) * arm_len
            draw.line([arm_x, shoulder_y, arm_end_x, arm_end_y], fill=color, width=arm_width)
            
            # 右手
            draw.ellipse([arm_end_x-8, arm_end_y-8, arm_end_x+8, arm_end_y+8], fill=secondary_color)
            
            # 左手臂向外张开
            arm_angle = -0.8 - animation_phase * 0.4
            arm_x = head_x-torso_width//4
            arm_end_x = arm_x + np.sin(arm_angle) * arm_len
            arm_end_y = shoulder_y + np.cos(arm_angle) * arm_len
            draw.line([arm_x, shoulder_y, arm_end_x, arm_end_y], fill=color, width=arm_width)
            
            # 左手
            draw.ellipse([arm_end_x-8, arm_end_y-8, arm_end_x+8, arm_end_y+8], fill=secondary_color)
            
            # 腿部 - 受击时重心不稳
            leg_width = 15
            hip_y = head_y+head_size//2+torso_height
            leg_len = torso_height * 1.1
            
            # 左腿弯曲
            knee_angle = 0.2 + animation_phase * 0.2
            knee_x = head_x-torso_width//3 + np.sin(knee_angle) * leg_len * 0.5
            knee_y = hip_y + np.cos(knee_angle) * leg_len * 0.5
            draw.line([head_x-torso_width//3+torso_skew*0.5, hip_y, knee_x, knee_y], fill=color, width=leg_width)
            
            # 小腿
            ankle_angle = knee_angle + 0.2
            ankle_x = knee_x + np.sin(ankle_angle) * leg_len * 0.5
            ankle_y = knee_y + np.cos(ankle_angle) * leg_len * 0.5
            draw.line([knee_x, knee_y, ankle_x, ankle_y], fill=color, width=leg_width)
            
            # 左脚
            draw.ellipse([ankle_x-10, ankle_y-5, ankle_x+10, ankle_y+10], fill=secondary_color)
            
            # 右腿弯曲
            knee_angle = -0.2 - animation_phase * 0.2
            knee_x = head_x+torso_width//3 + np.sin(knee_angle) * leg_len * 0.5
            knee_y = hip_y + np.cos(knee_angle) * leg_len * 0.5
            draw.line([head_x+torso_width//3+torso_skew*0.5, hip_y, knee_x, knee_y], fill=color, width=leg_width)
            
            # 小腿
            ankle_angle = knee_angle - 0.2
            ankle_x = knee_x + np.sin(ankle_angle) * leg_len * 0.5
            ankle_y = knee_y + np.cos(ankle_angle) * leg_len * 0.5
            draw.line([knee_x, knee_y, ankle_x, ankle_y], fill=color, width=leg_width)
            
            # 右脚
            draw.ellipse([ankle_x-10, ankle_y-5, ankle_x+10, ankle_y+10], fill=secondary_color)
            
            # 受击效果 - 冲击星
            impact_x = head_x - torso_width//2 - 20
            impact_y = shoulder_y
            for angle in range(0, 360, 45):
                rad = angle * np.pi / 180
                end_x = impact_x + np.cos(rad) * 15
                end_y = impact_y + np.sin(rad) * 15
                draw.line([impact_x, impact_y, end_x, end_y], fill=(255, 255, 0), width=3)
    
    # 保存图像
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    img.save(filename)
    print(f"✅ 创建精灵表: {filename}")

# 创建角色精灵表
def create_character_sprites():
    """创建角色精灵表"""
    
    # Ryu (蓝色)
    create_advanced_sprite_sheet("assets/images/characters/ryu/idle.png", (0, 0, 255), (255, 255, 255), 4)
    create_advanced_sprite_sheet("assets/images/characters/ryu/punch.png", (0, 0, 255), (255, 255, 255), 3)
    create_advanced_sprite_sheet("assets/images/characters/ryu/kick.png", (0, 0, 255), (255, 255, 255), 3)
    create_advanced_sprite_sheet("assets/images/characters/ryu/jump.png", (0, 0, 255), (255, 255, 255), 3)
    create_advanced_sprite_sheet("assets/images/characters/ryu/hit.png", (0, 0, 255), (255, 255, 255), 2)
    
    # Ken (红色)
    create_advanced_sprite_sheet("assets/images/characters/ken/idle.png", (255, 0, 0), (255, 255, 0), 4)
    create_advanced_sprite_sheet("assets/images/characters/ken/punch.png", (255, 0, 0), (255, 255, 0), 3)
    create_advanced_sprite_sheet("assets/images/characters/ken/kick.png", (255, 0, 0), (255, 255, 0), 3)
    create_advanced_sprite_sheet("assets/images/characters/ken/jump.png", (255, 0, 0), (255, 255, 0), 3)
    create_advanced_sprite_sheet("assets/images/characters/ken/hit.png", (255, 0, 0), (255, 255, 0), 2)
    
    # Chun-Li (绿色)
    create_advanced_sprite_sheet("assets/images/characters/chun-li/idle.png", (0, 180, 0), (0, 0, 255), 4)
    create_advanced_sprite_sheet("assets/images/characters/chun-li/punch.png", (0, 180, 0), (0, 0, 255), 3)
    create_advanced_sprite_sheet("assets/images/characters/chun-li/kick.png", (0, 180, 0), (0, 0, 255), 3)
    create_advanced_sprite_sheet("assets/images/characters/chun-li/jump.png", (0, 180, 0), (0, 0, 255), 3)
    create_advanced_sprite_sheet("assets/images/characters/chun-li/hit.png", (0, 180, 0), (0, 0, 255), 2)
    
    print("✅ 角色精灵创建完成")

# 创建背景图像
def create_background():
    """创建背景图像"""
    
    # 创建简单的背景图像
    width, height = 800, 600
    img = Image.new('RGB', (width, height), (80, 130, 200))  # 天空蓝色
    draw = ImageDraw.Draw(img)
    
    # 添加太阳
    sun_x, sun_y = width * 0.8, height * 0.2
    sun_radius = 60
    # 光晕效果
    for r in range(sun_radius, 0, -5):
        alpha = int(255 * (r / sun_radius))
        color = (255, 255, 200, alpha)
        draw.ellipse([sun_x-r, sun_y-r, sun_x+r, sun_y+r], fill=color)
    
    # 云朵
    for i in range(7):
        cloud_x = (i * 150 + 30) % width
        cloud_y = 100 + i * 30
        cloud_width = 120 + i * 10
        cloud_height = 50
        
        # 绘制蓬松的云
        for j in range(5):
            puff_x = cloud_x + j * cloud_width//6
            puff_y = cloud_y
            puff_size = cloud_height * (0.7 + 0.3 * np.sin(j))
            draw.ellipse([puff_x-puff_size//2, puff_y-puff_size//2, 
                         puff_x+puff_size//2, puff_y+puff_size//2], 
                        fill=(255, 255, 255, 200))
    
    # 远山
    for i in range(5):
        mountain_x = i * 200 - 50
        mountain_height = 100 + i * 20
        
        # 远山是灰蓝色
        draw.polygon([mountain_x, 400, 
                     mountain_x+250, 400, 
                     mountain_x+125, 400-mountain_height], 
                    fill=(100, 120, 150))
    
    # 近山
    for i in range(3):
        mountain_x = i * 300
        mountain_height = 150
        
        # 近山是深绿色
        draw.polygon([mountain_x, 400, 
                     mountain_x+350, 400, 
                     mountain_x+175, 400-mountain_height], 
                    fill=(40, 100, 40))
    
    # 地面（平台）
    ground_color = (150, 100, 50)
    draw.rectangle([0, 400, width, height], fill=ground_color)
    
    # 地板纹理
    platform_top_color = (180, 120, 60)
    draw.rectangle([0, 400, width, 420], fill=platform_top_color)
    
    # 纹理细节
    for i in range(40):
        x = i * 20
        line_color = (160, 110, 55) if i % 2 == 0 else (170, 115, 58)
        draw.line([x, 400, x+10, 400], fill=line_color, width=3)
    
    # 场地装饰
    # 左侧树
    tree_trunk_color = (100, 60, 20)
    draw.rectangle([50, 300, 70, 400], fill=tree_trunk_color)
    
    # 树叶
    leaf_color = (60, 160, 60)
    draw.ellipse([20, 220, 100, 310], fill=leaf_color)
    draw.ellipse([30, 180, 90, 250], fill=leaf_color)
    
    # 右侧石头
    rock_color = (150, 150, 150)
    draw.ellipse([650, 350, 750, 420], fill=rock_color)
    
    # 保存背景图像
    os.makedirs("assets/images/backgrounds", exist_ok=True)
    img.save("assets/images/backgrounds/stage1.jpg")
    
    print("✅ 背景图像创建完成")

# 主函数
def main():
    """主函数"""
    print("🎮 开始创建格斗游戏资源...")
    
    # 创建目录
    create_directories()
    
    # 创建角色精灵
    create_character_sprites()
    
    # 创建背景
    create_background()
    
    print("🎉 所有资源创建完成！游戏现在可以使用图形资源了。")

if __name__ == "__main__":
    main() 