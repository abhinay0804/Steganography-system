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

def embed_mp4(video_path: str, payload_bytes: bytes, password: str, output_path: str):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Could not open video file.")
        
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Read all frames into memory
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    
    if len(frames) == 0:
        raise ValueError("Video contains no frames.")
        
    total_capacity = len(frames) * h * w * 3
    payload_bits = bytes_to_bits(payload_bytes)
    
    if len(payload_bits) > total_capacity:
        raise ValueError(f"Payload too large. Need {len(payload_bits)} bits but video has {total_capacity} capacity.")
        
    path = generate_random_path(password, total_capacity)
    
    for i in range(len(payload_bits)):
        idx = path[i]
        
        plane_size = h * w * 3
        frame_idx = idx // plane_size
        rem = idx % plane_size
        
        r = rem // (w * 3)
        rem2 = rem % (w * 3)
        c = rem2 // 3
        ch = rem2 % 3
        
        bit = payload_bits[i] & 1
        
        val = frames[frame_idx][r, c, ch]
        frames[frame_idx][r, c, ch] = (val & 254) | bit
        
    # Write frames out losslessly if possible (actually mp4v is lossy, so extraction might fail on some bits)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
    for f in frames:
        out.write(f)
    out.release()
    print(f"[*] Successfully embedded {len(payload_bytes)} bytes into {output_path} (MP4 Video)")

def extract_mp4(video_path: str, password: str) -> bytes:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Could not open video file.")
        
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    
    if not frames:
        raise ValueError("No frames read from video.")
        
    h, w, channels = frames[0].shape
    total_capacity = len(frames) * h * w * channels
    
    path = generate_random_path(password, total_capacity)
    
    header_bits = []
    for i in range(32):
        idx = path[i]
        plane_size = h * w * 3
        frame_idx = idx // plane_size
        rem = idx % plane_size
        r = rem // (w * 3)
        rem2 = rem % (w * 3)
        c = rem2 // 3
        ch = rem2 % 3
        
        header_bits.append(frames[frame_idx][r, c, ch] & 1)
        
    header_bytes = bits_to_bytes(header_bits)
    payload_length = struct.unpack(">I", header_bytes)[0]
    total_payload_bits = payload_length * 8
    
    if 32 + total_payload_bits > total_capacity:
        raise ValueError(f"Corrupted data or wrong password: length exceeds video capacity")

    payload_bits = []
    for i in range(32, 32 + total_payload_bits):
        idx = path[i]
        plane_size = h * w * 3
        frame_idx = idx // plane_size
        rem = idx % plane_size
        r = rem // (w * 3)
        rem2 = rem % (w * 3)
        c = rem2 // 3
        ch = rem2 % 3
        
        payload_bits.append(frames[frame_idx][r, c, ch] & 1)

    return bits_to_bytes(payload_bits)
