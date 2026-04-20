#!/usr/bin/env python3
"""
ComfyUI Image Generator Script
用于通过 ComfyUI API 生成图片并返回本地路径
"""

import urllib.request
import urllib.parse
import json
import uuid
import time
import random
import os

DEFAULT_SERVER = "http://192.168.1.53:8188"
DEFAULT_OUTPUT_DIR = "/opt/data"
DEFAULT_UNET = "moodyPornMix_v11DPOFP8.safetensors"
DEFAULT_CLIP = "qwen3_4B_FP8.safetensors"
DEFAULT_VAE = "ae.safetensors"
DEFAULT_WIDTH = 768
DEFAULT_HEIGHT = 1024
DEFAULT_STEPS = 9
DEFAULT_CFG = 0.0


def build_workflow(prompt, seed=None, width=1024, height=1024, steps=30, cfg=1.0, filename_prefix="Hermes_Gen"):
    if seed is None:
        seed = random.randint(0, 999999999)
    
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": DEFAULT_UNET, "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": DEFAULT_CLIP, "type": "lumina2"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": DEFAULT_VAE}},
        "4": {"class_type": "CLIPTextEncodeLumina2", "inputs": {"system_prompt": "superior", "user_prompt": prompt, "clip": ["2", 0]}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "6": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "seed": seed, "steps": steps, "cfg": cfg, "sampler_name": "dpmpp_2m", "scheduler": "simple", "positive": ["4", 0], "negative": ["4", 0], "latent_image": ["5", 0], "denoise": 1.0}},
        "7": {"class_type": "VAEDecode", "inputs": {"samples": ["6", 0], "vae": ["3", 0]}},
        "8": {"class_type": "SaveImage", "inputs": {"images": ["7", 0], "filename_prefix": filename_prefix}}
    }


def generate_image(prompt, seed=None, width=768, height=1024, verbose=False):
    """生成图片并返回本地路径"""
    server = DEFAULT_SERVER
    
    workflow = build_workflow(prompt, seed, width, height)
    prompt_id = str(uuid.uuid4())
    payload = {"prompt": workflow, "client_id": "hermes_auto", "prompt_id": prompt_id}
    
    if verbose:
        print(f"[ComfyUI] Submitting workflow...")
    
    req = urllib.request.Request(f"{server}/prompt", data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
    result = json.loads(urllib.request.urlopen(req, timeout=30).read())
    
    if verbose:
        print(f"[ComfyUI] Prompt ID: {prompt_id}")
    
    # 等待完成
    for i in range(60):
        time.sleep(1)
        with urllib.request.urlopen(f"{server}/queue") as r:
            queue = json.loads(r.read())
        if len(queue['queue_running']) == 0:
            break
        if verbose and i % 5 == 0:
            print(f"[ComfyUI] [{i}s] Generating...")
    
    # 获取结果
    with urllib.request.urlopen(f"{server}/history/{prompt_id}") as r:
        history = json.loads(r.read())
    
    if prompt_id not in history:
        raise Exception("Generation failed: no history")
    
    status = history[prompt_id].get('status', {}).get('status_str', '')
    if status != 'success':
        raise Exception(f"Generation failed: {status}")
    
    # 下载图片
    outputs = history[prompt_id].get('outputs', {})
    for node_id, output in outputs.items():
        if 'images' in output:
            for img in output['images']:
                params = urllib.parse.urlencode({"filename": img['filename'], "subfolder": img['subfolder'] or "", "type": img['type']})
                save_path = os.path.join(DEFAULT_OUTPUT_DIR, f"comfyui_{img['filename']}")
                with urllib.request.urlopen(f"{server}/view?{params}") as img_resp:
                    with open(save_path, 'wb') as f:
                        f.write(img_resp.read())
                if verbose:
                    print(f"[ComfyUI] Saved: {save_path}")
                return save_path
    
    raise Exception("No images generated")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
        path = generate_image(prompt, verbose=True)
        print(path)