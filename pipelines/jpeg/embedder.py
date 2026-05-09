import cv2
import numpy as np
import hashlib
import struct
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.converters import bytes_to_bits, bits_to_bytes

def generate_random_path(seed_password: str, maximum_length: int) -> np.ndarray:
    seed_int = int.from_bytes(hashlib.sha256(seed_password.encode()).digest(), "big")
    rng = np.random.default_rng(seed_int)
    return rng.permutation(maximum_length)

def process_blocks_dct(channel):
    h, w = channel.shape
    dct_blocks = np.zeros((h, w), dtype=np.float32)
    for i in range(0, h, 8):
        for j in range(0, w, 8):
            block = channel[i:i+8, j:j+8].astype(np.float32) - 128.0
            dct_blocks[i:i+8, j:j+8] = cv2.dct(block)
    return dct_blocks

def process_blocks_idct(dct_blocks):
    h, w = dct_blocks.shape
    channel = np.zeros((h, w), dtype=np.float32)
    for i in range(0, h, 8):
        for j in range(0, w, 8):
            block = dct_blocks[i:i+8, j:j+8]
            idct_block = cv2.idct(block) + 128.0
            channel[i:i+8, j:j+8] = idct_block
    return np.clip(np.round(channel), 0, 255).astype(np.uint8)

def embed_jpeg(image_path: str, payload_bytes: bytes, password: str, output_path: str):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Could not read the image.")

    h, w = img.shape[:2]
    # Pad to multiple of 8
    pad_h = (8 - h % 8) % 8
    pad_w = (8 - w % 8) % 8
    if pad_h > 0 or pad_w > 0:
        img = cv2.copyMakeBorder(img, 0, pad_h, 0, pad_w, cv2.BORDER_REPLICATE)

    h, w = img.shape[:2]
    yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    y_channel = yuv[:, :, 0]
    
    dct_blocks = process_blocks_dct(y_channel)
    
    num_blocks_v = h // 8
    num_blocks_h = w // 8
    total_blocks = num_blocks_v * num_blocks_h
    
    payload_bits = bytes_to_bits(payload_bytes)
    
    if len(payload_bits) > total_blocks:
        raise ValueError(f"Payload too large! Need {len(payload_bits)} bits but only have {total_blocks} blocks.")

    path = generate_random_path(password, total_blocks)
    
    # We will choose a mid frequency coefficient, e.g., (4, 4)
    # We scale the coefficient by Q step to make it robust against Q=100 or Q=95 resaving
    step = 16.0 

    for i in range(len(payload_bits)):
        block_idx = path[i]
        r = (block_idx // num_blocks_h) * 8
        c = (block_idx % num_blocks_h) * 8
        
        bit = payload_bits[i] & 1
        coeff = dct_blocks[r+4, c+4]
        
        quantized = round(coeff / step)
        
        # Force quantization index to end in 'bit'
        if int(abs(quantized)) % 2 != bit:
            if quantized >= 0:
                quantized += 1
            else:
                quantized -= 1
                
        dct_blocks[r+4, c+4] = quantized * step
        
    yuv[:, :, 0] = process_blocks_idct(dct_blocks)
    output_img = cv2.cvtColor(yuv, cv2.COLOR_YCrCb2BGR)
    
    # Must save with high quality to preserve modifications
    cv2.imwrite(output_path, output_img, [cv2.IMWRITE_JPEG_QUALITY, 100])
    print(f"[*] Successfully embedded {len(payload_bytes)} bytes into {output_path} (JPEG DCT)")

def extract_jpeg(image_path: str, password: str) -> bytes:
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Could not read the image.")

    h, w = img.shape[:2]
    num_blocks_v = h // 8
    num_blocks_h = w // 8
    total_blocks = num_blocks_v * num_blocks_h
    
    yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    y_channel = yuv[:, :, 0]
    
    dct_blocks = process_blocks_dct(y_channel)
    path = generate_random_path(password, total_blocks)
    
    step = 16.0
    
    # 1. Recover 32-bit header
    header_bits = []
    for i in range(32):
        block_idx = path[i]
        r = (block_idx // num_blocks_h) * 8
        c = (block_idx % num_blocks_h) * 8
        
        coeff = dct_blocks[r+4, c+4]
        quantized = round(coeff / step)
        header_bits.append(int(abs(quantized)) % 2)
        
    header_bytes = bits_to_bytes(header_bits)
    payload_length = struct.unpack(">I", header_bytes)[0]
    total_payload_bits = payload_length * 8
    
    if 32 + total_payload_bits > total_blocks:
        raise ValueError(f"Corrupted data or wrong password: length exceeds image capacity (Length header = {payload_length} bytes)")

    payload_bits = []
    for i in range(32, 32 + total_payload_bits):
        block_idx = path[i]
        r = (block_idx // num_blocks_h) * 8
        c = (block_idx % num_blocks_h) * 8
        
        coeff = dct_blocks[r+4, c+4]
        quantized = round(coeff / step)
        payload_bits.append(int(abs(quantized)) % 2)

    return bits_to_bytes(payload_bits)
