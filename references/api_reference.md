# ComfyUI API Reference

基于 ComfyUI v0.19.3 的 HTTP API 文档，适用于 `http://192.168.1.53:8188`

## 核心端点

### 1. 工作流提交

#### POST `/prompt`

提交工作流执行请求。

**请求体**:
```json
{
  "prompt": { <workflow_json> },
  "client_id": "optional_client_uuid",
  "prompt_id": "optional_prompt_uuid"
}
```

**响应**:
```json
{
  "prompt_id": "uuid-string",
  "number": 1,
  "node_errors": {}
}
```

#### GET `/prompt`

获取当前队列信息。

**响应**:
```json
{
  "queue_running": [...],
  "queue_pending": [...]
}
```

---

### 2. 队列管理

#### GET `/queue`

获取队列状态。

**响应**:
```json
{
  "queue_running": [],
  "queue_pending": []
}
```

#### POST `/queue`

操作队列。

**请求体**:
```json
{
  "clear": true,           // 清空整个队列
  "delete": ["prompt_id"]  // 删除特定任务
}
```

---

### 3. 执行历史

#### GET `/history`

获取所有执行历史。

#### GET `/history/{prompt_id}`

获取特定任务的执行历史。

**响应**:
```json
{
  "prompt_id": {
    "prompt": [...],
    "outputs": {
      "node_id": {
        "images": [
          {
            "filename": "output.png",
            "subfolder": "",
            "type": "output"
          }
        ]
      }
    },
    "status": {
      "status_str": "success",  // 或 "error"
      "completed": true,
      "messages": [...]
    }
  }
}
```

---

### 4. 图片获取

#### GET `/view`

下载生成的图片。

**参数**:
- `filename`: 文件名
- `subfolder`: 子文件夹（可选）
- `type`: 图片类型（默认 `output`）

**示例**:
```
GET /view?filename=output.png&subfolder=&type=output
```

---

### 5. 模型信息

#### GET `/object_info`

获取所有可用节点类型。

#### GET `/object_info/{node_class}`

获取特定节点的详细信息。

**示例响应**:
```json
{
  "KSampler": {
    "input": {
      "required": {
        "model": ["MODEL"],
        "seed": ["INT", {"default": 0}],
        "steps": ["INT", {"default": 20}],
        ...
      }
    },
    "output": ["LATENT"]
  }
}
```

---

### 6. 模型列表

#### GET `/models`

获取所有模型文件夹列表。

#### GET `/models/{folder}`

获取特定文件夹中的模型列表。

**示例**:
```
GET /models/checkpoints
GET /models/loras
GET /models/vae
```

---

### 7. 系统状态

#### GET `/system_stats`

获取系统信息。

**响应**:
```json
{
  "system": {
    "comfyui_version": "0.19.3",
    "python_version": "3.12.10",
    "pytorch_version": "2.9.0+cu130"
  },
  "devices": [
    {
      "name": "NVIDIA GeForce RTX 5070 Ti",
      "vram_total": 12820480000,
      "vram_free": 11578376192
    }
  ]
}
```

---

### 8. 图片上传

#### POST `/upload/image`

上传输入图片。

**请求**: multipart/form-data
- `image`: 图片文件
- `overwrite`: 是否覆盖（可选）

---

### 9. 执行控制

#### POST `/interrupt`

中断当前执行。

#### POST `/free`

释放内存。

**请求体**:
```json
{
  "unload_models": true,
  "free_memory": true
}
```

---

## Lumina2 专用节点

### CLIPTextEncodeLumina2

Lumina2 专用的文本编码节点，与传统 CLIPTextEncode 不同。

**输入**:
- `system_prompt`: `"superior"` 或 `"alignment"`
  - `superior`: 生成高质量、图像文本对齐度高的图片
  - `alignment`: 最高程度的图像文本对齐
- `user_prompt`: 用户提示词
- `clip`: CLIP 模型连接

**示例**:
```json
{
  "class_type": "CLIPTextEncodeLumina2",
  "inputs": {
    "system_prompt": "superior",
    "user_prompt": "a beautiful sunset...",
    "clip": ["2", 0]
  }
}
```

---

## 工作流节点参考

### UNETLoader

加载 Diffusion 模型。

```json
{
  "class_type": "UNETLoader",
  "inputs": {
    "unet_name": "model.safetensors",
    "weight_dtype": "default"
  }
}
```

### CLIPLoader

加载 CLIP 模型。

```json
{
  "class_type": "CLIPLoader",
  "inputs": {
    "clip_name": "clip.safetensors",
    "type": "lumina2"  // 重要：必须匹配模型类型
  }
}
```

### VAELoader

加载 VAE 模型。

```json
{
  "class_type": "VAELoader",
  "inputs": {
    "vae_name": "vae.safetensors"
  }
}
```

### KSampler

核心采样器。

```json
{
  "class_type": "KSampler",
  "inputs": {
    "model": ["1", 0],
    "seed": 12345,
    "steps": 30,
    "cfg": 1.0,
    "sampler_name": "euler",
    "scheduler": "simple",
    "positive": ["4", 0],
    "negative": ["4", 0],
    "latent_image": ["5", 0],
    "denoise": 1.0
  }
}
```

**注意**: Lumina 模型建议 `cfg` 值为 1.0-2.0，positive 和 negative 使用相同值。

---

## 完整 API 调用流程

```python
import urllib.request
import json
import uuid

server = "http://192.168.1.53:8188"

# 1. 构建工作流
workflow = { ... }

# 2. 提交工作流
prompt_id = str(uuid.uuid4())
payload = {"prompt": workflow, "prompt_id": prompt_id}
req = urllib.request.Request(f"{server}/prompt", data=json.dumps(payload).encode())
result = json.loads(urllib.request.urlopen(req).read())

# 3. 等待完成
while True:
    with urllib.request.urlopen(f"{server}/queue") as r:
        queue = json.loads(r.read())
    if not queue["queue_running"]: break
    time.sleep(2)

# 4. 获取结果
with urllib.request.urlopen(f"{server}/history/{prompt_id}") as r:
    history = json.loads(r.read())

# 5. 下载图片
for output in history[prompt_id]["outputs"]:
    for img in output.get("images", []):
        params = f"filename={img['filename']}&type=output"
        with urllib.request.urlopen(f"{server}/view?{params}") as r:
            image_data = r.read()
```

---

## 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| `normalized_shape mismatch` | CLIP 类型不匹配 | 使用正确的 `type` 参数 |
| `CUDA out of memory` | 显存不足 | 降低分辨率或 batch_size |
| `node not found` | 节点类型错误 | 检查节点名称拼写 |
| `model not found` | 模型文件不存在 | 检查 `/models/{folder}` |

---

## 参考链接

- [ComfyUI GitHub](https://github.com/comfyanonymous/ComfyUI)
- [ComfyUI Script Examples](https://github.com/comfyanonymous/ComfyUI/tree/master/script_examples)
- [ComfyUI API Examples](https://github.com/comfyanonymous/ComfyUI_examples)