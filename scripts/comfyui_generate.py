#!/usr/bin/env python3
"""
ComfyUI Image Generator Script
用于通过 ComfyUI API 生成图片并返回本地路径

Usage:
    python comfyui_generate.py --prompt "your prompt here"
    python comfyui_generate.py --prompt "your prompt" --seed 12345 --width 512 --height 512
"""

import urllib.request
import urllib.parse
import json
import uuid
import time
import argparse
import random
import os
import sys

# 默认服务器配置
DEFAULT_SERVER = "http://192.168.1.53:8188"
DEFAULT_OUTPUT_DIR = "/opt/data"

# 默认模型配置
DEFAULT_UNET = "moodyPornMix_v11DPOFP8.safetensors"
DEFAULT_CLIP = "qwen3_4B_FP8.safetensors"
DEFAULT_VAE = "ae.safetensors"

# 默认生成参数
DEFAULT_WIDTH = 1024
DEFAULT_HEIGHT = 1024
DEFAULT_STEPS = 30
DEFAULT_CFG = 1.0
DEFAULT_SAMPLER = "euler"
DEFAULT_SCHEDULER = "simple"


def build_workflow(
    prompt: str,
    seed: int = None,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    steps: int = DEFAULT_STEPS,
    cfg: float = DEFAULT_CFG,
    sampler: str = DEFAULT_SAMPLER,
    scheduler: str = DEFAULT_SCHEDULER,
    unet: str = DEFAULT_UNET,
    clip: str = DEFAULT_CLIP,
    vae: str = DEFAULT_VAE,
    filename_prefix: str = "Hermes_Gen"
) -> dict:
    """
    构建 Lumina2 工作流 JSON
    
    Args:
        prompt: 生成提示词
        seed: 随机种子（None则随机生成）
        width: 图片宽度
        height: 图片高度
        steps: 采样步数
        cfg: CFG值
        sampler: 采样器名称
        scheduler: 调度器名称
        unet: UNET模型名称
        clip: CLIP模型名称
        vae: VAE模型名称
        filename_prefix: 输出文件名前缀
    
    Returns:
        ComfyUI 工作流 JSON
    """
    if seed is None:
        seed = random.randint(0, 999999999)
    
    workflow = {
        "1": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": unet,
                "weight_dtype": "default"
            }
        },
        "2": {
            "class_type": "CLIPLoader",
            "inputs": {
                "clip_name": clip,
                "type": "lumina2"
            }
        },
        "3": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": vae
            }
        },
        "4": {
            "class_type": "CLIPTextEncodeLumina2",
            "inputs": {
                "system_prompt": "superior",
                "user_prompt": prompt,
                "clip": ["2", 0]
            }
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": width,
                "height": height,
                "batch_size": 1
            }
        },
        "6": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": sampler,
                "scheduler": scheduler,
                "positive": ["4", 0],
                "negative": ["4", 0],  # Lumina 不用 traditional negative
                "latent_image": ["5", 0],
                "denoise": 1.0
            }
        },
        "7": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["6", 0],
                "vae": ["3", 0]
            }
        },
        "8": {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["7", 0],
                "filename_prefix": filename_prefix
            }
        }
    }
    
    return workflow


def submit_workflow(server: str, workflow: dict, client_id: str = None) -> str:
    """
    提交工作流到 ComfyUI
    
    Args:
        server: ComfyUI 服务器地址
        workflow: 工作流 JSON
        client_id: 客户端 ID
    
    Returns:
        prompt_id
    """
    prompt_id = str(uuid.uuid4())
    if client_id is None:
        client_id = f"hermes_client_{random.randint(1000, 9999)}"
    
    payload = {
        "prompt": workflow,
        "client_id": client_id,
        "prompt_id": prompt_id
    }
    
    req = urllib.request.Request(
        f"{server}/prompt",
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            result = json.loads(r.read())
            if 'error' in result:
                raise Exception(f"Workflow error: {result}")
            return prompt_id
    except Exception as e:
        raise Exception(f"Failed to submit workflow: {e}")


def wait_for_completion(server: str, prompt_id: str, max_wait: int = 120) -> dict:
    """
    等待生成完成
    
    Args:
        server: ComfyUI 服务器地址
        prompt_id: 提示词 ID
        max_wait: 最大等待时间（秒）
    
    Returns:
        执行历史记录
    """
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        # 检查队列状态
        with urllib.request.urlopen(f"{server}/queue") as r:
            queue = json.loads(r.read())
        
        if len(queue['queue_running']) == 0 and len(queue['queue_pending']) == 0:
            # 队列空了，检查历史
            with urllib.request.urlopen(f"{server}/history/{prompt_id}") as r:
                history = json.loads(r.read())
            
            if prompt_id in history:
                return history[prompt_id]
        
        time.sleep(2)
    
    raise Exception(f"Timeout waiting for completion after {max_wait}s")


def download_image(server: str, filename: str, subfolder: str = "", 
                   img_type: str = "output", output_dir: str = DEFAULT_OUTPUT_DIR) -> str:
    """
    下载生成的图片
    
    Args:
        server: ComfyUI 服务器地址
        filename: 图片文件名
        subfolder: 子文件夹
        img_type: 图片类型
        output_dir: 输出目录
    
    Returns:
        本地文件路径
    """
    params = urllib.parse.urlencode({
        "filename": filename,
        "subfolder": subfolder,
        "type": img_type
    })
    
    url = f"{server}/view?{params}"
    save_path = os.path.join(output_dir, f"comfyui_{filename}")
    
    with urllib.request.urlopen(url) as img_resp:
        with open(save_path, 'wb') as f:
            f.write(img_resp.read())
    
    return save_path


def generate_image(
    prompt: str,
    server: str = DEFAULT_SERVER,
    seed: int = None,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    steps: int = DEFAULT_STEPS,
    cfg: float = DEFAULT_CFG,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    filename_prefix: str = "Hermes_Gen",
    verbose: bool = False
) -> str:
    """
    生成图片的完整流程
    
    Args:
        prompt: 生成提示词
        server: ComfyUI 服务器地址
        seed: 随机种子
        width: 图片宽度
        height: 图片高度
        steps: 采样步数
        cfg: CFG值
        output_dir: 输出目录
        filename_prefix: 文件名前缀
        verbose: 是否输出详细日志
    
    Returns:
        本地图片文件路径
    """
    if verbose:
        print(f"[ComfyUI] Building workflow...")
    
    workflow = build_workflow(
        prompt=prompt,
        seed=seed,
        width=width,
        height=height,
        steps=steps,
        cfg=cfg,
        filename_prefix=filename_prefix
    )
    
    if verbose:
        print(f"[ComfyUI] Submitting workflow...")
    
    prompt_id = submit_workflow(server, workflow)
    
    if verbose:
        print(f"[ComfyUI] Prompt ID: {prompt_id}")
        print(f"[ComfyUI] Waiting for completion...")
    
    history = wait_for_completion(server, prompt_id)
    
    status = history.get('status', {}).get('status_str', '')
    
    if status != 'success':
        error_msg = history.get('status', {}).get('messages', [])
        raise Exception(f"Generation failed: {status}, {error_msg}")
    
    if verbose:
        print(f"[ComfyUI] Generation successful!")
    
    # 获取输出图片
    outputs = history.get('outputs', {})
    image_paths = []
    
    for node_id, output in outputs.items():
        if 'images' in output:
            for img in output['images']:
                path = download_image(
                    server=server,
                    filename=img['filename'],
                    subfolder=img['subfolder'] or "",
                    img_type=img['type'],
                    output_dir=output_dir
                )
                image_paths.append(path)
                if verbose:
                    print(f"[ComfyUI] Saved: {path}")
    
    if not image_paths:
        raise Exception("No images generated")
    
    return image_paths[0]


def main():
    parser = argparse.ArgumentParser(description='Generate images via ComfyUI API')
    parser.add_argument('--prompt', '-p', required=True, help='Generation prompt')
    parser.add_argument('--server', '-s', default=DEFAULT_SERVER, help='ComfyUI server URL')
    parser.add_argument('--seed', type=int, default=None, help='Random seed')
    parser.add_argument('--width', '-W', type=int, default=DEFAULT_WIDTH, help='Image width')
    parser.add_argument('--height', '-H', type=int, default=DEFAULT_HEIGHT, help='Image height')
    parser.add_argument('--steps', type=int, default=DEFAULT_STEPS, help='Sampling steps')
    parser.add_argument('--cfg', type=float, default=DEFAULT_CFG, help='CFG value')
    parser.add_argument('--output', '-o', default=DEFAULT_OUTPUT_DIR, help='Output directory')
    parser.add_argument('--prefix', default='Hermes_Gen', help='Filename prefix')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    try:
        path = generate_image(
            prompt=args.prompt,
            server=args.server,
            seed=args.seed,
            width=args.width,
            height=args.height,
            steps=args.steps,
            cfg=args.cfg,
            output_dir=args.output,
            filename_prefix=args.prefix,
            verbose=args.verbose
        )
        print(path)  # 输出路径供其他程序使用
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()