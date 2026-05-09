import shutil
import struct
import os
from mutagen.id3 import ID3, GEOB
from mutagen.mp4 import MP4

MAGIC_SIG = b"STEG"

def embed_eof(file_path: str, payload: bytes, output_path: str):
    """Appends payload to the End-Of-File securely."""
    shutil.copy2(file_path, output_path)
    
    length_bytes = struct.pack(">I", len(payload))
    with open(output_path, "ab") as f:
        f.write(payload)
        f.write(length_bytes)
        f.write(MAGIC_SIG)
        
    print(f"[*] Successfully appended {len(payload)} bytes via EOF to {output_path}")

def extract_eof(file_path: str) -> bytes:
    """Reads exactly backward from EOF to extract signature and payload."""
    with open(file_path, "rb") as f:
        # Check Signature
        f.seek(-len(MAGIC_SIG), 2)
        magic_check = f.read(len(MAGIC_SIG))
        if magic_check != MAGIC_SIG:
            raise ValueError("No EOF stego signature found in file!")
            
        # Extract Length
        f.seek(-(len(MAGIC_SIG) + 4), 2)
        length_bytes = f.read(4)
        payload_length = struct.unpack(">I", length_bytes)[0]
        
        # Extract Payload
        f.seek(-(len(MAGIC_SIG) + 4 + payload_length), 2)
        payload = f.read(payload_length)
        
        # Strip the 4-byte length header to perfectly align with ChaCha20 salt
        return payload[4:]

def embed_metadata(file_path: str, payload: bytes, output_path: str):
    """Injects payload into container metadata dynamically."""
    shutil.copy2(file_path, output_path)
    ext = os.path.splitext(output_path.lower())[1]
    
    if ext == ".mp3":
        try:
            audio = ID3(output_path)
        except Exception:
            audio = ID3()
        # GEOB = General Encapsulated Object
        audio.add(GEOB(encoding=0, mime='application/octet-stream', desc='stego', data=payload))
        audio.save(output_path)
    elif ext == ".mp4":
        video = MP4(output_path)
        # Custom Freeform iTunes metadata atom
        video["----:com.apple.iTunes:stego"] = [payload]
        video.save()
    else:
        raise ValueError("Unsupported format for metadata injection")
        
    print(f"[*] Successfully injected {len(payload)} bytes via Metadata into {output_path}")

def extract_metadata(file_path: str) -> bytes:
    ext = os.path.splitext(file_path.lower())[1]
    
    if ext == ".mp3":
        audio = ID3(file_path)
        for frame in audio.getall("GEOB"):
            if frame.desc == 'stego':
                return frame.data[4:] # Strip 4-byte length header
        raise ValueError("No stego metadata found in MP3.")
        
    elif ext == ".mp4":
        video = MP4(file_path)
        payload = video.get("----:com.apple.iTunes:stego")
        if payload:
            return payload[0][4:] # Strip 4-byte length header
        else:
            raise ValueError("No stego metadata found in MP4.")
