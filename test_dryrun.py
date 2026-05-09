import struct
import os
import sys

# Add path so local imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pipelines.png_wav.embedder import embed, extract

def test_dryrun():
    message = "Evarki Telsu @#!"
    password = "test"
    image_in = "samples/crypto_4.png"
    image_out = "samples/crypto_4_stego.png"

    print(f"[*] Formatting payload...")
    message_bytes = message.encode()
    # Adding a 4-byte prefix length header as expected by the extractor
    payload_bytes = struct.pack(">I", len(message_bytes)) + message_bytes

    print(f"[*] Embedding...")
    embed(image_in, payload_bytes, password, image_out)
    
    print(f"[*] Extracting...")
    extracted_bytes = extract(image_out, password)
    
    print(f"[*] Extracted output: {extracted_bytes.decode('utf-8', errors='ignore')}")
    print(f"[*] Success: {extracted_bytes == message_bytes}")

if __name__ == "__main__":
    test_dryrun()
