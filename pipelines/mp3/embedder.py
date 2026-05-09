import numpy as np
import hashlib
import struct
import sys
import os
from pydub import AudioSegment

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.converters import bytes_to_bits, bits_to_bytes

def generate_random_path(seed_password: str, maximum_length: int) -> np.ndarray:
    seed_int = int.from_bytes(hashlib.sha256(seed_password.encode()).digest(), "big")
    rng = np.random.default_rng(seed_int)
    return rng.permutation(maximum_length)

def embed_mp3(audio_path: str, payload_bytes: bytes, password: str, output_path: str):
    audio = AudioSegment.from_file(audio_path, format="mp3")
    
    # 16-bit signed PCM
    samples = np.array(audio.get_array_of_samples(), dtype=np.int16)
    
    payload_bits = bytes_to_bits(payload_bytes)
    
    if len(payload_bits) > len(samples):
        raise ValueError(f"Payload too large. Need {len(payload_bits)} bits but audio has {len(samples)} samples.")
        
    path = generate_random_path(password, len(samples))
    
    for i in range(len(payload_bits)):
        idx = path[i]
        bit = payload_bits[i] & 1
        
        # We use uint16 equivalent mask or simply -2 to safely clear the LSB of int16
        samples[idx] = (samples[idx] & ~1) | bit
        
    # Reconstruct audio segment
    new_audio = audio._spawn(samples.tobytes())
    
    # Export with extremely high bitrate to minimize recompression damage (Still Experimental!)
    new_audio.export(output_path, format="mp3", bitrate="320k")
    print(f"[*] Successfully embedded {len(payload_bytes)} bytes into {output_path} (MP3 PCM)")

def extract_mp3(audio_path: str, password: str) -> bytes:
    audio = AudioSegment.from_file(audio_path, format="mp3")
    samples = np.array(audio.get_array_of_samples(), dtype=np.int16)
    
    path = generate_random_path(password, len(samples))
    
    header_bits = []
    for i in range(32):
        idx = path[i]
        header_bits.append(samples[idx] & 1)
        
    header_bytes = bits_to_bytes(header_bits)
    payload_length = struct.unpack(">I", header_bytes)[0]
    total_payload_bits = payload_length * 8
    
    if 32 + total_payload_bits > len(samples):
        raise ValueError(f"Corrupted data or wrong password: length exceeds audio capacity (Length header = {payload_length} bytes)")

    payload_bits = []
    for i in range(32, 32 + total_payload_bits):
        idx = path[i]
        payload_bits.append(samples[idx] & 1)

    return bits_to_bytes(payload_bits)
