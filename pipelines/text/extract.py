import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from pipelines.text.text_utils import zwc_to_bits
from utils.converters import bits_to_bytes

def extract_text(file_path: str, password: str) -> bytes:
    """
    Filters entirely for ZWC within a text file and reconstructs the payload bytes.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    extracted_bits = zwc_to_bits(content)
    
    if len(extracted_bits) == 0:
        raise ValueError("No zero-width steganographic characters found in file.")
        
    # Strip the 4-byte padding header to perfectly align with ChaCha20
    return bits_to_bytes(extracted_bits)[4:]
