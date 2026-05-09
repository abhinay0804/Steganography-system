# SECURE MULTIMEDIA STEGANOGRAPHY SYSTEM

A hybrid multimedia steganography framework that combines cryptography and data hiding techniques to securely embed secret messages inside multiple media formats including images, audio, video, and text.

The system integrates:

* PBKDF2 for secure key derivation
* ChaCha20 for encryption
* HMAC-SHA256 for integrity verification
* Multiple steganographic pipelines based on media type

---

# FEATURES

* Secure password-based encryption
* Multi-format multimedia support
* Randomized embedding positions using deterministic PRNG
* HMAC-based tamper detection
* GUI and CLI support
* Modular architecture for easy extensibility

---

# SUPPORTED FORMATS

| Format   | Technique Used                                             |
| -------- | ---------------------------------------------------------- |
| PNG      | LSB Steganography                                          |
| WAV      | LSB Audio Embedding                                        |
| JPEG/JPG | DCT-Based Experimental Embedding                           |
| TXT      | Zero-Width Unicode Steganography                           |
| MP3      | PCM Modification (Experimental) & Metadata/EOF Append      |
| MP4      | Frame-Level LSB Embedding (Experimental) & Metadata Append |

---

# CRYPTOGRAPHIC WORKFLOW

## 1. PBKDF2 Key Derivation

* SHA-256 hashing
* 100,000 iterations
* Random salt generation
* Generates a 512-bit derived key

### Key Splitting

* First 256 bits → ChaCha20 Encryption Key
* Remaining 256 bits → HMAC-SHA256 Key

---

## 2. ChaCha20 Encryption

The plaintext message is encrypted using:

* 256-bit key
* 128-bit nonce

Output:

* Ciphertext

---

## 3. HMAC Integrity Verification

The encrypted payload is authenticated using HMAC-SHA256 to detect:

* Wrong passwords
* Data corruption
* Tampering attempts

---

# PAYLOAD STRUCTURE

```text
[ Header | Salt | Nonce | Ciphertext | HMAC ]
```

| Component  | Purpose                  |
| ---------- | ------------------------ |
| Header     | Stores payload length    |
| Salt       | Used in PBKDF2           |
| Nonce      | Used in ChaCha20         |
| Ciphertext | Encrypted secret message |
| HMAC       | Integrity verification   |

---

# RANDOMIZED EMBEDDING

The system uses a deterministic pseudo-random embedding mechanism.

## Process

1. Password → SHA-256 hash
2. Hash used as PRNG seed
3. NumPy permutation generates randomized embedding positions

This ensures:

* Random embedding locations
* No repeated positions
* Same positions regenerated during extraction

---

# PROJECT STRUCTURE

```bash
SECURE-MULTIMEDIA-STEGANOGRAPHY/
│
├── crypto/
│   └── encryption.py
│
├── pipelines/
│   ├── jpeg/
│   ├── mp3/
│   ├── mp4/
│   ├── png_wav/
│   └── text/
│
├── stego/
│   └── container_embedder.py
│
├── utils/
│   └── converters.py
│
├── ui/
│   └── gui.py
│
├── test/
│
├── main.py
│
└── README.md
```

---

# INSTALLATION

## Clone Repository

```bash
git clone https://github.com/abhinay0804/secure-multimedia-steganography.git
cd secure-multimedia-steganography
```

---

# INSTALL DEPENDENCIES

```bash
pip install -r requirements.txt
```

Or manually install:

```bash
pip install cryptography pillow numpy opencv-python pydub mutagen scipy audioop-lts
```

---

# RUNNING THE PROJECT

## GUI Mode

```bash
python main.py ui
```

---

## CLI Mode

### Embed Message

```bash
python main.py embed --file input.png --message "Secret Message" --password "mypassword" --out output.png
```

### Extract Message

```bash
python main.py extract --file output.png --password "mypassword"
```

---

# EXAMPLE

## Input

* Carrier File: `image.png`
* Secret Message: `"Top Secret"`
* Password: `"secure123"`

## Output

* `stego_image.png`

Extraction with the correct password retrieves the original message successfully.

---

# SECURITY FEATURES

* PBKDF2-based password hardening
* Salted key derivation
* ChaCha20 stream cipher encryption
* HMAC integrity verification
* Randomized embedding positions
* Multi-layered security model

---

# LIMITATIONS

* Lossy compression may affect embedded data in experimental pipelines (JPEG, MP3, MP4).
* Text steganography may fail if formatting removes zero-width characters.
* MP3 and MP4 pipelines are experimental due to compression-related data loss.

---

# FUTURE ENHANCEMENTS

* Reed-Solomon error correction
* Advanced transform-domain steganography
* Web-based deployment
* Real-time secure communication integration

---

# TECHNOLOGIES USED

* Python
* NumPy
* Pillow
* OpenCV
* PyDub
* Cryptography
* Mutagen
* Tkinter

---

# AUTHOR

* Nama Abhinay

---

# LICENSE

This project is developed for academic and educational purposes.
