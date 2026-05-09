import argparse
import sys
import os

from crypto.encryption import encrypt_message, decrypt_message
from pipelines.png_wav.embedder import embed, extract
from pipelines.png_wav.audio_embedder import embed_audio, extract_audio
from pipelines.jpeg.embedder import embed_jpeg, extract_jpeg
from pipelines.mp3.embedder import embed_mp3, extract_mp3
from pipelines.mp4.embedder import embed_mp4, extract_mp4
from pipelines.text.embed import embed_text
from pipelines.text.extract import extract_text

def main():
    parser = argparse.ArgumentParser(description="Secure Steganography Pipeline (Image & Audio) using ChaCha20, PBKDF2, and HMAC")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Embed command
    embed_parser = subparsers.add_parser("embed", help="Embed a secret message into a host file (.png, .wav, .jpg, .mp3, .mp4)")
    embed_parser.add_argument("--file", required=True, help="Path to the host (cover) file")
    embed_parser.add_argument("--message", required=True, help="Message to hide (string)")
    embed_parser.add_argument("--password", required=True, help="Password for encryption and PRNG seeding")
    embed_parser.add_argument("--out", required=True, help="Path to save the stego file (must match host extension)")

    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract and decrypt a secret message from a stego file")
    extract_parser.add_argument("--file", required=True, help="Path to the stego file (.png, .wav, .jpg, .mp3, .mp4)")
    extract_parser.add_argument("--password", required=True, help="Password for PRNG seeding and decryption")

    # UI command
    ui_parser = subparsers.add_parser("ui", help="Launch the Desktop Graphical User Interface")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "ui":
        from ui.gui import StegoApp
        app = StegoApp()
        app.mainloop()
        sys.exit(0)

    if args.command == "embed":
        host_ext = os.path.splitext(args.file.lower())[1]
        out_ext = os.path.splitext(args.out.lower())[1]
        
        if host_ext not in [".png", ".wav", ".jpg", ".jpeg", ".mp3", ".mp4", ".txt"]:
            print("[-] Error: Host file must be a .png, .wav, .jpg, .mp3, .mp4, or .txt.")
            sys.exit(1)
            
        if host_ext != out_ext:
            print("[-] Error: Output file extension must exactly match the host file extension.")
            sys.exit(1)
        
        message_bytes = args.message.encode("utf-8")
        payload = encrypt_message(message_bytes, args.password)
        
        try:
            if host_ext == ".png":
                embed(args.file, payload, args.password, args.out)
            elif host_ext == ".wav":
                embed_audio(args.file, payload, args.password, args.out)
            elif host_ext == ".txt":
                embed_text(args.file, payload, args.password, args.out)
            elif host_ext in [".jpg", ".jpeg"]:
                embed_jpeg(args.file, payload, args.password, args.out)
            elif host_ext in [".mp3", ".mp4"]:
                # By default the CLI uses EOF since it's most robust without extra flags.
                # To support metadata from CLI, we could add a flag, but for now we default to EOF.
                print("[*] Lossy format detected. Using robust EOF Container injection...")
                from stego.container_embedder import embed_eof
                embed_eof(args.file, payload, args.out)
        except Exception as e:
            print(f"[-] Embedding failed: {e}")
            sys.exit(1)

    elif args.command == "extract":
        file_ext = os.path.splitext(args.file.lower())[1]
        
        if file_ext not in [".png", ".wav", ".mp3", ".mp4", ".jpg", ".jpeg", ".txt"]:
            print("[-] Error: Input file must be .png, .wav, .mp3, .mp4, .jpg, or .txt.")
            sys.exit(1)
            
        try:
            if file_ext == ".png":
                payload = extract(args.file, args.password)
            elif file_ext == ".wav":
                payload = extract_audio(args.file, args.password)
            elif file_ext == ".txt":
                payload = extract_text(args.file, args.password)
            elif file_ext in [".jpg", ".jpeg"]:
                payload = extract_jpeg(args.file, args.password)
            elif file_ext in [".mp3", ".mp4"]:
                from stego.container_embedder import extract_eof, extract_metadata
                try:
                    payload = extract_metadata(args.file)
                except ValueError:
                    payload = extract_eof(args.file)
        except Exception as e:
            print(f"[-] Extraction failed: {e}")
            sys.exit(1)
            
        try:
            decrypted_message = decrypt_message(payload, args.password)
            print(f"\n[+] Extracted Secret Message:\n{decrypted_message.decode('utf-8')}")
        except Exception as e:
            print(f"[-] Decryption failed (Wrong password or corrupted data): {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
