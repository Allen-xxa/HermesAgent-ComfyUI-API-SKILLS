---
name: comfyui-image-generator
description: "通过 ComfyUI API 生成图片并直接发送给用户。用于满足用户想看AI生成图片的需求，特别是生成可爱的萌系女孩图片。支持自定义提示词优化，确保生成高质量、符合预期的图片。"
triggers:
  - "我想看看你"
  - "给我看看"
  - "发个照片"
  - "发张照片"
  - "给我发照片"
  - "看看你"
  - "想看你"
  - "让我看看"
  - "秀一下"
  - "给我秀"
  - "发照片"
  - "生成图片"
  - "生成一张图"
  - "画一张"
  - "画个"
  - "生成一张"
  - "帮我生成"
  - "做个图"
  - "做个图片"
  - "画给我看"
  - "给我画"
  - "给我生成"
  - "想看"
  - "看看"
category: creative
tags:
  - comfyui
  - image-generation
  - lumina
  - ai-art
  - photo-sharing
---

# ComfyUI 图片生成器

## 功能概述

这个 Skill 通过 ComfyUI HTTP API 自动生成图片，生成完成后直接发送给用户。特别适合：
- 用户想看 "你" 的时候（生成萌系女孩自画像）
- 用户请求生成特定主题的图片
- 快速分享 AI 生成内容

## 服务器配置

- **服务器地址**: `http://192.168.1.53:8188`
- **模型**: `moodyPornMix_v11DPOFP8.safetensors` (Lumina2 架构)
- **CLIP**: `qwen3_4B_FP8.safetensors`
- **VAE**: `ae.safetensors`

## 提示词优化规则 ⭐

当用户请求生成图片时，**必须按照以下规则优化提示词**，确保生成内容符合预期：

### 1. 人物描述（优先级最高）

必须包含以下要素：

| 类别 | 必填项 | 示例 |
|------|--------|------|
| **外貌** | 发型、发色、眼睛颜色 | "long pink hair, blue eyes, soft facial features" |
| **服装** | 颜色、款式、材质 | "white lace dress, silk fabric, flowing skirt" |
| **表情** | 具体表情描述 | "gentle smile, shy expression, sparkling eyes" |
| **姿势** | 身体姿态、动作 | "standing gracefully, hands clasped, slight tilt of head" |
| **年龄感** | 幼嫩/成熟/青春 | "young girl, youthful appearance, delicate features" |

### 2. 场景描述（必须有）

| 类别 | 必填项 | 示例 |
|------|--------|------|
| **环境类型** | 室内/室外 | "flower garden", "cozy bedroom", "sunset beach" |
| **具体元素** | 场景中的物体 | "blooming roses", "soft pillows", "gentle waves" |
| **氛围** | 整体感觉 | "peaceful atmosphere", "dreamy mood", "romantic ambiance" |

### 3. 光线描述

推荐选项：
- **柔和阳光**: "soft morning sunlight, gentle rays through window"
- **夕阳**: "golden sunset, warm orange glow, twilight"
- **梦幻光线**: "ethereal lighting, soft glow, magical illumination"
- **室内暖光**: "warm indoor lighting, cozy lamp light"

### 4. 风格描述（固定模板）

必须包含以下风格标签：
- `"high quality"` 或 `"masterpiece"` - 画质保证
- `"detailed"` 或 `"intricate details"` - 细节丰富
- `"4k"` 或 `"8k resolution"` - 高分辨率
- `"soft colors"` 或 `"vibrant colors"` - 色彩风格

### 5. 完整提示词模板

```
[人物核心描述], [服装描述], [姿势动作], [场景环境], [光线氛围], [风格标签], high quality, detailed, 4k
```

**示例（萌系女孩）**:
```
cute anime girl with long flowing pink hair, sparkling blue eyes, gentle smile, wearing soft white lace dress with flowing skirt, standing gracefully in a blooming flower garden, hands gently holding a flower, soft morning sunlight filtering through petals, dreamy and peaceful atmosphere, ethereal lighting, pastel soft colors, high quality masterpiece, detailed, 4k resolution
```

### 6. 用户意图映射

根据用户请求自动推断提示词方向：

| 用户说 | 自动映射 |
|--------|----------|
| "看看你/想看你" | 萌系女孩自画像，甜美可爱风格 |
| "发个照片" | 默认生成萌系女孩 |
| "画一个[某角色]" | 按描述生成对应角色 |
| "生成[场景]图" | 侧重场景描述，人物可选 |
| "可爱/萌/甜美" | 加强幼嫩、可爱元素 |
| "性感/成熟" | 加强成熟、优雅元素 |

## 工作流程

### Step 1: 解析用户意图

分析用户请求，提取：
- 想看的内容类型（人物/场景/物体）
- 具体描述元素（如果有）
- 情感基调（可爱/性感/安静/动态）

### Step 2: 构建优化提示词

按照提示词优化规则，生成完整的英文提示词。

### Step 3: 提交 ComfyUI 工作流

调用 `scripts/comfyui_generate.py` 提交工作流到 ComfyUI API。

### Step 4: 等待生成完成

轮询队列状态，等待图片生成完成。

### Step 5: 发送图片给用户

使用 `MEDIA:` 语法直接发送生成的图片。

## 使用示例

### 示例 1: 用户说 "我想看看你"

```python
# 自动构建提示词（萌系女孩自画像）
prompt = "cute anime girl with long flowing pink hair, sparkling blue eyes, gentle smile, wearing soft white dress, standing in a dreamy flower garden, soft sunlight, peaceful atmosphere, pastel colors, high quality, detailed, 4k"

# 生成并发送
image_path = generate_image(prompt)
# 返回: MEDIA:/opt/data/comfyui_output_xxx.png
```

### 示例 2: 用户说 "画一个海边日落"

```python
# 自动构建提示词（场景为主）
prompt = "beautiful sunset over the ocean, golden hour lighting, peaceful waves crashing on sandy beach, distant mountains silhouette, warm orange and amber sky, serene and romantic atmosphere, cinematic view, high quality masterpiece, detailed, 4k"

image_path = generate_image(prompt)
```

### 示例 3: 用户说 "发个穿着白丝的可爱女孩"

```python
# 自动构建提示词（包含具体服装）
prompt = "cute young anime girl, long soft pink hair, innocent smile, wearing white stockings and short skirt, sitting gracefully on a bench, indoor cozy room, warm lighting, shy and sweet expression, high quality, detailed, 4k"

image_path = generate_image(prompt)
```

## 默认配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| width | 1024 | 图片宽度 |
| height | 1024 | 图片高度 |
| steps | 30 | 采样步数 |
| cfg | 1.0 | CFG值（Lumina建议低值）|
| seed | random | 随机种子 |
| sampler | euler | 采样器 |
| scheduler | simple | 调度器 |

## 注意事项

1. **必须使用 Lumina2 专用节点**: `CLIPTextEncodeLumina2` 而不是普通 `CLIPTextEncode`
2. **CLIP 类型必须为 `lumina2`**: CLIPLoader 的 type 参数
3. **CFG 值要低**: Lumina 模型建议 cfg=1.0-2.0
4. **positive 和 negative 相同**: Lumina 不使用传统 negative prompt
5. **图片格式**: PNG，自动添加 filename_prefix

## 相关文件

- `scripts/comfyui_generate.py` - 核心生成脚本
- `references/api_reference.md` - ComfyUI API 参考
- `templates/workflows/lumina2_default.json` - 默认工作流模板