# Hermes Agent ComfyUI API Skills

通过 ComfyUI HTTP API 自动生成图片并发送给用户的 Hermes Agent Skill。

## 功能特点

- 🎨 **自动生成图片**: 通过 ComfyUI API 生成高质量 AI 图片
- 📸 **直接发送**: 生成完成后自动发送给用户
- 🌸 **萌系自画像**: 特别优化生成可爱萌系女孩图片
- ✨ **智能提示词**: 自动优化提示词，确保生成内容符合预期

## 快速开始

### 1. 安装 Skill

将本仓库克隆到 Hermes Agent 的 skills 目录：

```bash
cd /opt/data/skills/
git clone https://github.com/Allen-xxa/HermesAgent-ComfyUI-API-SKILLS.git comfyui-api
```

### 2. 配置服务器

确保 ComfyUI 服务器运行在 `http://192.168.1.53:8188`，或修改 `scripts/comfyui_generate.py` 中的 `DEFAULT_SERVER`。

### 3. 使用方法

在 Hermes Agent 中触发：

```
用户: 我想看看你
用户: 发个照片
用户: 生成一张海边日落的图片
```

Hermes Agent 会自动：
1. 解析用户意图
2. 优化提示词
3. 调用 ComfyUI API
4. 发送生成的图片

## 文件结构

```
HermesAgent-ComfyUI-API-SKILLS/
├── SKILL.md                    # Skill 主文档（触发词、提示词规则）
├── README.md                   # 本文件
├── scripts/
│   └── comfyui_generate.py     # 核心生成脚本
├── references/
│   └── api_reference.md        # ComfyUI API 参考
└── templates/
    └── workflows/
        └── lumina2_default.json # 默认工作流模板
```

## 提示词优化规则

Skill 会自动优化用户请求，按照以下规则构建提示词：

### 必须包含的元素

1. **人物描述**: 外貌、发型、眼睛、服装、表情、姿势
2. **场景描述**: 环境、地点、氛围、具体元素
3. **光线描述**: 光线类型、效果、颜色
4. **风格标签**: `high quality`, `detailed`, `4k`

### 示例映射

| 用户说 | 自动提示词方向 |
|--------|---------------|
| "看看你" | 萌系女孩自画像，粉色头发，可爱表情 |
| "海边日落" | 场景为主，夕阳，海浪，山脉剪影 |
| "可爱女孩" | 强调幼嫩、甜美、萌元素 |

## 技术细节

### 服务器配置

- **GPU**: NVIDIA RTX 5070 Ti (12GB)
- **模型**: moodyPornMix (Lumina2 架构)
- **CLIP**: qwen3_4B_FP8
- **VAE**: ae.safetensors

### Lumina2 注意事项

1. 必须使用 `CLIPTextEncodeLumina2` 节点
2. CLIPLoader 的 `type` 必须为 `lumina2`
3. CFG 值建议 1.0-2.0（低值）
4. positive/negative 使用相同值

### 默认生成参数

| 参数 | 值 |
|------|-----|
| 尺寸 | 1024x1024 |
| 步数 | 30 |
| CFG | 1.0 |
| 采样器 | euler |
| 调度器 | simple |

## API 参考

完整 API 文档见 `references/api_reference.md`。

核心端点：
- `POST /prompt` - 提交工作流
- `GET /queue` - 查看队列
- `GET /history/{id}` - 获取执行历史
- `GET /view` - 下载图片

## 直接使用脚本

```bash
python scripts/comfyui_generate.py --prompt "cute anime girl, pink hair" --verbose
```

输出：图片本地路径

## 许可证

MIT License

## 作者

Allen Xin & Hermes Agent (十二月) 🌸