import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from pipelines.text.text_utils import bits_to_zwc, ZERO, ONE
from pipelines.text.validator import validate_text_capacity
from utils.converters import bytes_to_bits

def embed_text(file_path: str, payload_bytes: bytes, password: str, output_path: str):
    """
    Appends the payload losslessly formatted as Zero-Width Characters (ZWC)
    to the end of a UTF-8 text document (Approach A).
    """
    validate_text_capacity(file_path, payload_bytes)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    payload_bits = bytes_to_bits(payload_bytes)
    zwc_string = bits_to_zwc(payload_bits)
    
    final_content = content + zwc_string
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
        
    print(f"[*] Successfully invisibly embedded {len(payload_bytes)} bytes into {output_path} (.txt ZWC)")
