# 格斗之王 (Fighting King)

一个类似拳皇的2D格斗游戏，支持玩家对战、玩家对AI和AI对AI战斗模式。

## 最新功能

- **AI对战AI模式**：观看两个AI角色互相对战
- **个性化AI行为**：不同AI角色有不同的战斗风格和偏好
- **攻击冷却系统**：更加平衡的战斗体验
- **视觉特效系统**：攻击、受击和伤害显示的视觉反馈
- **多语言支持**：支持中文显示

## 项目结构

```
.
├── assets/              # 游戏资源(图像、音效等)
├── src/                 # 源代码
│   ├── characters/      # 角色类
│   ├── engine/          # 游戏引擎
│   ├── ai/              # AI对战系统
│   └── ui/              # 用户界面
├── environment.yml      # Conda环境配置
└── main.py              # 游戏入口
```

## 安装与运行

### 使用Conda环境

1. 创建并激活环境:
```bash
conda env create -f environment.yml
conda activate fighting-game
```

2. 运行游戏:
```bash
python main.py
```

### 直接安装依赖

```bash
pip install pygame requests
python main.py
```

## 游戏控制

### 玩家1:
- W: 跳跃
- A: 左移
- D: 右移
- S: 蹲下
- J: 轻拳
- K: 重拳
- L: 轻腿
- ;: 重腿
- 空格: 格挡

### 玩家2:
- ↑: 跳跃
- ←: 左移
- →: 右移
- ↓: 蹲下
- 1: 轻拳
- 2: 重拳
- 3: 轻腿
- 4: 重腿
- 0: 格挡

## 游戏模式

- **玩家对战模式**：两个玩家互相对战
- **VS AI模式**：与AI对战，支持不同难度级别
- **AI对战AI模式**：观看两个AI角色互相对战

## 战斗系统特点

- **攻击冷却系统**：每次攻击后有冷却时间
- **命中判定**：基于距离和时间窗口的命中判定
- **角色碰撞**：角色之间有碰撞检测，防止重叠
- **格挡系统**：可以格挡对手的攻击

## AI系统

游戏包含多种AI行为模式：

- **进攻型AI**：更喜欢接近对手并进行攻击
- **防守型AI**：更喜欢保持距离并反击
- **平衡型AI**：攻守平衡的AI行为

AI角色会根据战场情况做出决策，包括移动、攻击、防御和躲避等行为。

## 自定义AI

游戏支持自定义AI，您可以在`src/ai/custom_ai.py`中创建自己的AI逻辑。详细说明请参考该文件中的注释。 