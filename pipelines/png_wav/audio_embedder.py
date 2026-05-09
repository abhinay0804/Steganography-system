import hashlib
import numpy as np
import warnings
from scipy.io import wavfile
from scipy.io.wavfile import WavFileWarning

warnings.filterwarnings("ignore", category=WavFileWarning)
import struct
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.converters import bytes_to_bits, bits_to_bytes
from pipelines.png_wav.embedder import generate_random_path

def embed_audio(audio_path: str, payload_bytes: bytes, password: str, output_path: str):
    """
    Hides payload_bytes within the given WAV audio file losslessly.
    payload_bytes must include a 4-byte prefix length header.
    """
    rate, data = wavfile.read(audio_path)
    original_shape = data.shape
    
    # Flatten array (handles mono/stereo transparently)
    flat_samples = data.reshape(-1)
    
    payload_bits = bytes_to_bits(payload_bytes)
    
    if len(payload_bits) > len(flat_samples):
        raise ValueError(f"Audio file is too small! Need {len(payload_bits)} samples, but audio only has {len(flat_samples)} capacity.")
        
    # Re-use the exact same deterministic PRNG logic
    path = generate_random_path(password, len(flat_samples))
    
    samples_copy = flat_samples.copy()
    
    for i in range(len(payload_bits)):
        idx = path[i]
        bit = payload_bits[i]
        # Replace the LSB of the int16 sample
        samples_copy[idx] = (samples_copy[idx] & -2) | bit
        
    final_data = samples_copy.reshape(original_shape)
    wavfile.write(output_path, rate, final_data.astype(np.int16))
    
    print(f"[*] Successfully embedded {len(payload_bytes)} bytes into {output_path}")

def extract_audio(audio_path: str, password: str) -> bytes:
    """
    Extracts the payload from a stego-WAV using the same password logic.
    Assumes the first 32 bits denote the payload length.
    """
    rate, data = wavfile.read(audio_path)
    flat_samples = data.reshape(-1)
    
    path = generate_random_path(password, len(flat_samples))
    
    # 1. Recover the first 32 bits to determine payload size
    header_bits = []
    for i in range(32):
        idx = path[i]
        header_bits.append(flat_samples[idx] & 1)
        
    header_bytes = bits_to_bytes(header_bits)
    payload_length = struct.unpack(">I", header_bytes)[0]
    
    # 2. Recover the rest of the payload
    total_payload_bits = payload_length * 8
    
    if 32 + total_payload_bits > len(flat_samples):
        raise ValueError("Corrupted data or wrong password: length header exceeds audio capacity.")
        
    payload_bits = []
    for i in range(32, 32 + total_payload_bits):
        idx = path[i]
        payload_bits.append(flat_samples[idx] & 1)
        
    return bits_to_bytes(payload_bits)
