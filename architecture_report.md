# Secure Steganography Suite: Complete Architectural Blueprint

This document serves as the official technical thesis and architectural blueprint of the entire Secure Steganography System. It details the structural integration across all cryptographic layers, upper-level integrations, and algorithmic pipelines optimized for each specific file format.

---

## 1. Overall Upper-Layer Architecture (The Core)

The system is constructed using a decoupled, modular design pattern that separates the cryptographic engine from the physical steganography pipelines. This ensures that every piece of data hidden inside a file is mathematically authenticated before execution, preventing targeted extraction attacks or data corruption.

### 🔐 The Cryptographic Engine (`crypto/encryption.py`)
Before *any* data is hidden inside a host file, the payload passes through an impenetrable cryptographic pipeline built on modern security standards:
1. **Key Derivation (PBKDF2)**: Uses `PBKDF2HMAC` with `SHA-256` running at **100,000 iterations** to convert the user's string password into an astronomically secure 32-byte cryptographic key.
2. **Stream Cryptography (ChaCha20)**: Implements `ChaCha20` (a 256-bit secure stream cipher) to encrypt the payload. It utilizes a securely generated 16-byte cryptographically secure random `Nonce`, making frequency analysis mathematically impossible.
3. **Integrity Validation (Encrypt-then-MAC)**: Appends an `HMAC-SHA256` signature to the absolute end of the payload. **If even a single bit of the file is flipped by compression or tampered with by a hacker, the HMAC strictly prevents decryption with an `Integrity Check Failed` alert locally.** 

### 🖥️ The Interface Layer (GUI & CLI)
The application bridges the backend dynamically:
- **CLI Router (`main.py`)**: A command-line parser that cleanly maps commands (`embed`, `extract`) into format-specific pipelines dynamically based on file extensions.
- **GUI Engine (`ui/gui.py`)**: A native `Tkinter` application that continuously monitors the user's active inputs. For example, if a user uploads a `.mp3` or `.mp4`, the GUI organically responds by rendering unique Protocol Hiding toggles (Metadata vs EOF).

---

## 2. Technical Execution Plan (Pipeline by Pipeline)

Because structural formatting across images, vectors, text, and compressed video is fundamentally different, the system utilizes exclusively tailored algorithmic pipelines. 

> [!TIP]
> **Deterministic PRNG Pathing:** For natively modified formats (Image/Audio), the system avoids sequentially injecting bits across the files. Instead, it securely seeds a NumPy random generator using the `SHA256` hash of the user's password to generate a scrambled, non-linear coordinate matrix.

### 🖼️ Pipeline 1: Lossless Images (`.png`)
**Module:** `pipelines/png_wav/embedder.py`
- **Architecture**: Spatial Domain Least Significant Bit (LSB) embedding.
- **Execution Log**: Converts the payload entirely to raw boolean bit-arrays. Opens the image via memory-blocks natively mapped to Numpy. Uses password-seeded coordinates to inject the payload bit into the absolute lowest structural byte of the pixel (`pixel & ~1 | target_bit`). 
- **Integrity Fixes**: Native algorithms detected whether an image was `RGB` or `RGBA`. The suite isolates the alpha layer to prevent background transparency corruption during LSB sweeps.

### 🎵 Pipeline 2: Lossless Audio (`.wav`)
**Module:** `pipelines/png_wav/audio_embedder.py`
- **Architecture**: PCM Signal Sequence Masking.
- **Execution Log**: Bypasses image spatial rendering using 16-bit integer modifications. Analyzes the flat waveform block and performs a 2's complement mask (`signal & -2 | target_bit`) across securely generated coordinates within the track's uncompressed frequencies.

### 📄 Pipeline 3: Steganographic Text (`.txt`)
**Module:** `pipelines/text/`
- **Architecture**: Invisible Unicode Zero-Width Appending.
- **Execution Log**: Replaces classical visible bit mapping entirely by formatting 0s and 1s into strictly invisible textual gaps: 
  - `Bit 0` == `\u200B` (Zero-width space) 
  - `Bit 1` == `\u200C` (Zero-width non-joiner)
- **Execution Outcome**: Appends a massive array of these invisible characters to the EOF of a plaintext `.txt` document natively formatted inside UTF-8. It leaves the file visually identical while preserving native 100% data transmission.

### 📦 Pipeline 4: Lossy Media Containers (`.mp3` & `.mp4`)
**Module:** `stego/container_embedder.py`
- **Architecture**: Lossless Envelope Bypassing & Atom Injection.
- **Execution Log**: Standard LSB modifications completely fail on compression architectures like `.mp4` and `.mp3`. Instead of writing into the audio/video stream frames (which get destroyed on render), the suite hides the *entire untampered cryptographic packet* outside the vector rendering environment using two protocols:
  1. **Metadata Protocol (ID3/FreeForm Atoms)**: Utilizes `mutagen` to inject invisible dictionaries secretly inside structurally valid iTunes tag locations or GEOB music layers organically natively.
  2. **EOF Appending (Magic Signature)**: Appends the fully encrypted payload block mathematically behind the container's structural terminator block. Since media players stop reading video data precisely at the terminator block, the payload survives indefinitely completely unnoticed.

---

> [!WARNING]  
> **A Note on JPEG Systems**: Future implementations involving `.jpg` environments must be engineered deeply around Quantization Disconnects (QIM) matrices utilizing Forward Error Correction (Reed-Solomon packets) because DCT engines consistently modify base frequencies mathematically during standard disk saves. For now, `.mp4`, `.mp3`, `.txt`, `.png` and `.wav` represent absolute cryptological perfection.
