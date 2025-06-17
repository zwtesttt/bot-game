# 格斗之王 (Fighting King)

一个类似拳皇的2D格斗游戏，支持AI对战系统。

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

### 玩家2:
- ↑: 跳跃
- ←: 左移
- →: 右移
- ↓: 蹲下
- 1: 轻拳
- 2: 重拳
- 3: 轻腿
- 4: 重腿

## AI模式

在主菜单中选择"VS AI"模式，可以与AI对战。AI模式支持不同难度级别。

## 自定义AI

游戏支持自定义AI，您可以在`src/ai/custom_ai.py`中创建自己的AI逻辑。详细说明请参考该文件中的注释。 