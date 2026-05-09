import hashlib
import numpy as np
from PIL import Image
import sys
import os

# Add parent directory to path so we can import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.converters import bytes_to_bits, bits_to_bytes

def generate_random_path(seed_password: str, maximum_length: int) -> np.ndarray:
    """
    Generates a deterministic sequence of unique indices (a path) covering the entire image.
    Relies on numpy's default_rng which is deterministic given the same seed.
    """
    seed_int = int.from_bytes(hashlib.sha256(seed_password.encode()).digest(), "big")
    # To avoid ValueError from large seeds in numpy, restrict it to 32-bit or use PCG64 directly
    # Numpy's default_rng can take arbitrarily large integers since version 1.17
    rng = np.random.default_rng(seed_int)
    
    # We do a permutation of all the available indices (very fast in numpy)
    path = rng.permutation(maximum_length)
    return path

def embed(image_path: str, payload_bytes: bytes, password: str, output_path: str):
    """
    Hides payload_bytes within the given image losslessly.
    payload_bytes must include a 4-byte prefix length header.
    """
    img = Image.open(image_path)
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGBA')
    
    img_arr = np.array(img)
    original_shape = img_arr.shape
    flat_img = img_arr.flatten()
    
    payload_bits = bytes_to_bits(payload_bytes)
    
    if len(payload_bits) > len(flat_img):
        raise ValueError(f"Image is too small to embed payload! Need {len(payload_bits)} bits, but image has {len(flat_img)} capacity.")

    # Generate shuffle sequence
    path = generate_random_path(password, len(flat_img))
    
    # Embed bits into the LSB of chosen indices
    for i in range(len(payload_bits)):
        idx = path[i]
        bit = payload_bits[i] & 1
        # Clear the LSB and set it to the target bit
        flat_img[idx] = (flat_img[idx] & 254) | bit
        
    # Reconstruct image
    stego_img_arr = flat_img.reshape(original_shape)
    stego_img = Image.fromarray(stego_img_arr, mode=img.mode)
    stego_img.save(output_path, "PNG") # Must save out as PNG for losslessness!
    print(f"[*] Successfully embedded {len(payload_bytes)} bytes into {output_path}")

def extract(image_path: str, password: str) -> bytes:
    """
    Extracts the payload from a stego-image using the same password logic.
    Assumes the first 32 bits denote the payload length.
    """
    img = Image.open(image_path)
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGBA')
        
    flat_img = np.array(img).flatten()
    path = generate_random_path(password, len(flat_img))
    
    # 1. Recover the first 32 bits to determine payload size
    header_bits = []
    for i in range(32):
        idx = path[i]
        header_bits.append(flat_img[idx] & 1)
        
    header_bytes = bits_to_bytes(header_bits)
    # Convert those 4 bytes back to an integer
    import struct
    payload_length = struct.unpack(">I", header_bytes)[0]
    
    # 2. Recover the rest of the payload
    # Total bits to recover = payload_length * 8
    total_payload_bits = payload_length * 8
    
    if 32 + total_payload_bits > len(flat_img):
        raise ValueError("Corrupted data or wrong password: length header exceeds image capacity.")
        
    payload_bits = []
    for i in range(32, 32 + total_payload_bits):
        idx = path[i]
        payload_bits.append(flat_img[idx] & 1)
        
    return bits_to_bytes(payload_bits)
