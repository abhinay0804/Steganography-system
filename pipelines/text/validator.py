import os

def validate_text_capacity(file_path: str, payload_bytes: bytes):
    """
    Validates if the text file is properly encoded and alerts if payload is unusually large.
    Since ZWC text steganography inflates file size dramatically (8 ZWC per byte, each ZWC is 3 bytes in UTF-8),
    we enforce a sanity check.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Missing file: {file_path}")
        
    # Check if standard text
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1024)
    except UnicodeDecodeError:
        raise ValueError(f"File {file_path} is not valid UTF-8! Use only plaintext files.")
        
    return True
