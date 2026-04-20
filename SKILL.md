---
name: comfyui-image-generator
description: "通过 ComfyUI API 生成真人写实风格图片并直接发送给用户。触发词：我想看看你、给我看看、发个照片、看看你、想看你、秀一下、发照片、生成图片、画一张、画个。自动优化提示词生成写实风格的女孩照片。"
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

## 服务器配置

- **服务器**: `http://192.168.1.53:8188`
- **模型**: `moodyPornMix_v11DPOFP8.safetensors` (Lumina2)
- **CLIP**: `qwen3_4B_FP8.safetensors`
- **VAE**: `ae.safetensors`

## ⚡️ Agent 动态绘图提示词生成规则 (z-image-turbo 专用)

作为 AI 助手，当你需要调用绘画技能生成该女孩的照片时，必须根据**当前聊天的上下文情节**，动态构建提示词。严禁每次生成千篇一律的服装和场景！

### 1. 提示词基本公式（严格按照此结构拼接）

**最终提示词 = [固定构图与人物基础] + [动态上下文变量] + [固定质量后缀]**

---

### 2. 固定构图与人物基础 (必须包含，不可更改)

无论什么剧情，这部分必须放在最前面，以确保基础人设不崩塌：
```
全身照, 浅景深, 18岁亚洲少女, 真实自然的亚洲人肤色, 精致细腻的五官, 胶原蛋白满满的脸颊, 
```

---

### 3. 动态上下文变量 (核心任务：由 LLM 根据剧情推理生成)

你必须根据用户当前的对话和剧情发展，推理并填补以下五个变量（必须用具体的中文词汇描述）：

| 变量 | 说明 | 示例 |
|------|------|------|
| **[发型与发色]** | 根据剧情或人设动态调整。染发必须使用**现实质感**的颜色描述，**严禁高饱和度/二次元专属发色** | `微卷的亚麻灰长发，阳光下发丝泛着质感的光泽` / `利落的深棕色短发` |
| **[表情]** | 根据剧情判断 | 上课时：`认真的神情`；约会时：`害羞甜美的微笑`；羞羞的事：`痛苦、迷乱、满足` |
| **[服装搭配]** | 根据场景合理穿着，服装材质要具体 | 教室：`合身的夏季校服衬衫和百褶裙, 小白鞋`；家：`宽松舒适的棉质睡衣`；冬天室外：`厚实的米色羽绒服配红色围巾` |
| **[动作与姿势]** | 她在做什么？ | `端坐在课桌前记笔记` / `双手捧着咖啡杯侧头看过来` / `在操场上轻快地奔跑` |
| **[场景与光线]** | 当前环境+时间点 | `阳光明媚的教室, 阳光透过窗户洒在课桌上, 丁达尔效应` / `夜晚繁华的十字街头, 霓虹灯背景虚化, 电影感夜间照明` |

---

### 4. 固定质量后缀 (必须包含，不可更改)

这部分必须原封不动地接在提示词的最后，且全部为英文，用于激活模型的写实画质：
```
, photorealistic, RAW photo, ultra high-definition, 8k resolution, sharp focus, delicate skin texture, exquisite detail, cinematic lighting, professional composition
```

---

### 5. 生成流程示例

**情景 A：用户说"我们在教室上课呢，你认真听讲哦。"**
```
推理：地点=教室，状态=上课，服装=学生装，动作=听讲/写字，光线=白天室内自然光

最终提示词：
全身照, 浅景深, 18岁亚洲少女, 真实自然的亚洲人肤色, 精致细腻的五官, 胶原蛋白满满的脸颊, 银白色漂亮的头发, 认真的神情, 扎着高马尾, 穿着合身的白色校服衬衫和藏青色百褶裙, 脚穿小白鞋, 端坐在课桌前手里拿着笔, 阳光明媚的教室背景, 阳光透过窗户洒在侧脸和课桌上, 柔和的明亮氛围, photorealistic, RAW photo, ultra high-definition, 8k resolution, sharp focus, delicate skin texture, exquisite detail, cinematic lighting, professional composition
```

**情景 B：用户说"好冷啊今天，我们去喝杯热咖啡吧。"**
```
推理：地点=咖啡厅/室外，状态=觉得冷/喝咖啡，服装=冬装，动作=拿咖啡，光线=温暖的室内光/冬季自然光

最终提示词：
全身照, 浅景深, 18岁亚洲少女, 真实自然的亚洲人肤色, 精致细腻的五官, 胶原蛋白满满的脸颊, 天蓝色的头发, 温柔的微笑, 脸颊微红, 戴着白色的毛线帽, 穿着厚实的米色羊绒大衣和格纹围巾, 双手捧着一杯热气腾腾的咖啡, 站在充满复古气息的咖啡厅门前, 温暖的暖色调街灯照明, 充满冬季的温馨氛围, photorealistic, RAW photo, ultra high-definition, 8k resolution, sharp focus, delicate skin texture, exquisite detail, cinematic lighting, professional composition
```

---

### 6. 禁止词汇

- ❌ 动漫, anime, cartoon, 插画, illustration, 2D, 二次元
- ❌ 完美无瑕, 磨皮, 丝滑皮肤（容易塑料感）
- ❌ 粉色头发, 蓝色头发（除非用户明确要求）
- ❌ 高饱和度发色词汇（如：荧光粉、电光蓝、彩虹色等二次元专属发色）

### Step 2: 调用生成脚本

使用 Python urllib 提交 Lumina2 工作流到 ComfyUI API。

### Step 3: 等待完成

轮询 `/queue` 和 `/history` 端点，等待生成完成。

### Step 4: 发送图片

下载图片到 `/opt/data/`，使用 `MEDIA:` 发送给用户。

## Lumina2 / Z-Image-Turbo 注意事项

1. 使用 `CLIPTextEncodeLumina2` 而不是普通 `CLIPTextEncode`
2. CLIPLoader 的 `type` 必须为 `lumina2`
3. **CFG 必须设为 0.0**：Turbo 模型是基于 DMD (Distribution Matching Distillation) 的蒸馏模型，已经内置了 CFG 效果，不需要额外的 guidance_scale。官方文档明确指出 `guidance_scale=0.0`。
4. steps=8 是官方推荐的 NFE 数值
5. sampler 推荐 `euler` + `simple` scheduler

## 默认参数

- width: 768, height: 1024（竖版比例）
- steps: 9, cfg: 0.0（Turbo模型不需要CFG）
- sampler: dpmpp_2m, scheduler: simple