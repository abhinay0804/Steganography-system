import sys
import os
import numpy as np
from scipy.io import wavfile

# Add parent dir to run standalone
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from crypto.encryption import encrypt_message, decrypt_message
from pipelines.png_wav.audio_embedder import embed_audio, extract_audio

def generate_dummy_wav(path, duration=3, sample_rate=44100):
    """Generates a simple sine wave WAV file for testing."""
    t = np.linspace(0, duration, int(sample_rate * duration))
    # 440 Hz A4 note
    audio = np.sin(2 * np.pi * 440 * t)
    # Scale to 16-bit integer range
    audio_int16 = np.int16(audio * 32767)
    wavfile.write(path, sample_rate, audio_int16)
    print(f"[+] Dummy WAV created at {path}")

def run_tests():
    password = "test_password_123"
    message = "HELLO THIS IS A TOP SECRET AUDIO MESSAGE!"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    dummy_path = os.path.join(base_dir, "dummy_test.wav")
    stego_path = os.path.join(base_dir, "stego_output.wav")
    
    # 1. Setup Phase
    print("\n--- Audio Steganography Pipeline Test ---")
    generate_dummy_wav(dummy_path)
    
    # 2. Embed Phase
    try:
        print(f"\n[!] Encrypting message: '{message}'")
        payload = encrypt_message(message.encode('utf-8'), password)
        print("[!] Injecting payload into Audio...")
        embed_audio(dummy_path, payload, password, stego_path)
    except Exception as e:
        print(f"[-] Embed failed: {e}")
        sys.exit(1)
        
    # 3. Process Phase
    try:
        print("\n[!] Extracting payload from Stego Audio...")
        extracted_payload = extract_audio(stego_path, password)
        print("[!] Verifying HMAC and Decrypting...")
        plaintext = decrypt_message(extracted_payload, password)
        
        print(f"\n[=== RESULT ===]")
        print(f"Secret: {plaintext.decode('utf-8')}")
        
        assert plaintext.decode('utf-8') == message, "The output message did not match the input!"
        print("\nSUCCESS! The Audio pipeline is fully lossless and secure!")
    except Exception as e:
        print(f"[-] Extraction/Decryption failed: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        if os.path.exists(dummy_path): os.remove(dummy_path)
        if os.path.exists(stego_path): os.remove(stego_path)

if __name__ == "__main__":
    run_tests()
