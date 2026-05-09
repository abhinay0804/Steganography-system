import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
import os

# Ensure backend modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto.encryption import encrypt_message, decrypt_message
from pipelines.png_wav.embedder import embed, extract
from pipelines.png_wav.audio_embedder import embed_audio, extract_audio
from pipelines.text.embed import embed_text
from pipelines.text.extract import extract_text
from stego.container_embedder import embed_eof, extract_eof, embed_metadata, extract_metadata

class StegoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Secure Steganography Suite")
        self.geometry("550x550")
        self.resizable(False, False)
        
        # UI Styling
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except:
            pass 
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, expand=True, fill='both')
        
        self.embed_frame = ttk.Frame(self.notebook, padding=(20, 10))
        self.extract_frame = ttk.Frame(self.notebook, padding=(20, 10))
        
        self.notebook.add(self.embed_frame, text="   🔐 Embed Mode   ")
        self.notebook.add(self.extract_frame, text="   🔓 Extract Mode   ")
        
        self._build_embed_tab()
        self._build_extract_tab()
        
    def _build_embed_tab(self):
        ttk.Label(self.embed_frame, text="Target File (.png, .wav, .mp3, .mp4, .txt):", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(5, 0))
        
        file_frame = ttk.Frame(self.embed_frame)
        file_frame.pack(fill="x", pady=2)
        self.embed_filepath = tk.StringVar()
        self.embed_filepath.trace_add("write", self._on_embed_file_changed) # Dynamic binding
        ttk.Entry(file_frame, textvariable=self.embed_filepath, state="readonly", width=45).pack(side="left", padx=(0,10))
        ttk.Button(file_frame, text="Browse", command=self.browse_embed_source).pack(side="left")
        
        ttk.Label(self.embed_frame, text="Secret Message:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(10, 0))
        self.embed_message = tk.Text(self.embed_frame, height=4, width=50)
        self.embed_message.pack(fill="x", pady=2)
        
        ttk.Label(self.embed_frame, text="Password:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(10, 0))
        self.embed_password = tk.StringVar()
        ttk.Entry(self.embed_frame, textvariable=self.embed_password, show="*", width=30).pack(anchor="w", pady=2)
        
        # Dynamic Section for MP3/MP4
        self.lossy_frame = ttk.LabelFrame(self.embed_frame, text="Lossy Media Options", padding=(10, 5))
        self.hiding_method = tk.StringVar(value="metadata")
        ttk.Radiobutton(self.lossy_frame, text="Metadata Injection (ID3/Atom)", variable=self.hiding_method, value="metadata").pack(side="left", padx=10)
        ttk.Radiobutton(self.lossy_frame, text="EOF Appending", variable=self.hiding_method, value="eof").pack(side="left", padx=10)
        # We start with it hidden until a lossy file is picked
        
        self.txt_hint_frame = ttk.LabelFrame(self.embed_frame, text="Text Payload Format", padding=(10, 5))
        ttk.Label(self.txt_hint_frame, text="ℹ Supports completely invisible embedding using Zero-Width Unicode characters.").pack(anchor="w")
        
        ttk.Label(self.embed_frame, text="Save Stego Output As:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(10, 0))
        out_frame = ttk.Frame(self.embed_frame)
        out_frame.pack(fill="x", pady=2)
        self.embed_outpath = tk.StringVar()
        ttk.Entry(out_frame, textvariable=self.embed_outpath, state="readonly", width=45).pack(side="left", padx=(0,10))
        ttk.Button(out_frame, text="Browse", command=self.browse_embed_target).pack(side="left")
        
        ttk.Button(self.embed_frame, text="🚀 ENCRYPT & EMBED DATA", command=self.run_embed).pack(pady=20, fill="x")
        
    def _build_extract_tab(self):
        ttk.Label(self.extract_frame, text="Stego File (.png, .wav, .mp3, .mp4, .txt):", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(5, 0))
        
        file_frame = ttk.Frame(self.extract_frame)
        file_frame.pack(fill="x", pady=2)
        self.ext_filepath = tk.StringVar()
        self.ext_filepath.trace_add("write", self._on_ext_file_changed)
        ttk.Entry(file_frame, textvariable=self.ext_filepath, state="readonly", width=45).pack(side="left", padx=(0,10))
        ttk.Button(file_frame, text="Browse", command=self.browse_ext_source).pack(side="left")
        
        ttk.Label(self.extract_frame, text="Password:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(10, 0))
        self.ext_password = tk.StringVar()
        ttk.Entry(self.extract_frame, textvariable=self.ext_password, show="*", width=30).pack(anchor="w", pady=2)
        
        self.ext_lossy_frame = ttk.LabelFrame(self.extract_frame, text="Extraction Protocol", padding=(10, 5))
        self.ext_hiding_method = tk.StringVar(value="auto")
        ttk.Radiobutton(self.ext_lossy_frame, text="Auto-Detect", variable=self.ext_hiding_method, value="auto").pack(side="left", padx=5)
        ttk.Radiobutton(self.ext_lossy_frame, text="Metadata", variable=self.ext_hiding_method, value="metadata").pack(side="left", padx=5)
        ttk.Radiobutton(self.ext_lossy_frame, text="EOF", variable=self.ext_hiding_method, value="eof").pack(side="left", padx=5)
        
        self.ext_txt_hint_frame = ttk.LabelFrame(self.extract_frame, text="Text Payload Format", padding=(10, 5))
        ttk.Label(self.ext_txt_hint_frame, text="ℹ Will intelligently extract hidden Zero-Width Unicode strings.").pack(anchor="w")
        
        ttk.Button(self.extract_frame, text="🔍 EXTRACT & DECRYPT SUMMARY", command=self.run_extract).pack(pady=20, fill="x")
        
        ttk.Label(self.extract_frame, text="Decrypted Message:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(10, 0))
        self.ext_result = tk.Text(self.extract_frame, height=5, width=50, state="disabled")
        self.ext_result.pack(fill="x", pady=2)

    def _on_embed_file_changed(self, *args):
        # Dynamic UI toggler
        ext = os.path.splitext(self.embed_filepath.get().lower())[1]
        if ext in [".mp3", ".mp4"]:
            self.txt_hint_frame.pack_forget()
            self.lossy_frame.pack(fill="x", pady=(10, 0), before=self.embed_frame.winfo_children()[-3])
        elif ext == ".txt":
            self.lossy_frame.pack_forget()
            self.txt_hint_frame.pack(fill="x", pady=(10, 0), before=self.embed_frame.winfo_children()[-3])
        else:
            self.lossy_frame.pack_forget()
            self.txt_hint_frame.pack_forget()
            
    def _on_ext_file_changed(self, *args):
        ext = os.path.splitext(self.ext_filepath.get().lower())[1]
        if ext in [".mp3", ".mp4"]:
            self.ext_txt_hint_frame.pack_forget()
            self.ext_lossy_frame.pack(fill="x", pady=(10, 0), before=self.extract_frame.winfo_children()[-3])
        elif ext == ".txt":
            self.ext_lossy_frame.pack_forget()
            self.ext_txt_hint_frame.pack(fill="x", pady=(10, 0), before=self.extract_frame.winfo_children()[-3])
        else:
            self.ext_lossy_frame.pack_forget()
            self.ext_txt_hint_frame.pack_forget()

    def browse_embed_source(self):
        f = filedialog.askopenfilename(filetypes=[("Media Files", "*.png *.wav *.mp3 *.mp4 *.txt")])
        if f: self.embed_filepath.set(f)
            
    def browse_embed_target(self):
        src = self.embed_filepath.get()
        if src:
            ext = os.path.splitext(src.lower())[1]
            if ext:
                ext_title = ext[1:].upper() + " File"
                f = filedialog.asksaveasfilename(defaultextension=ext, filetypes=[(ext_title, f"*{ext}")])
            else:
                f = filedialog.asksaveasfilename()
        else:
            f = filedialog.asksaveasfilename(filetypes=[("Media Files", "*.png *.wav *.mp3 *.mp4 *.jpg *.jpeg *.txt")])
            
        if f: self.embed_outpath.set(f)
            
    def browse_ext_source(self):
        f = filedialog.askopenfilename(filetypes=[("Media Files", "*.png *.wav *.mp3 *.mp4 *.txt")])
        if f: self.ext_filepath.set(f)

    def run_embed(self):
        src = self.embed_filepath.get()
        out = self.embed_outpath.get()
        msg = self.embed_message.get("1.0", "end-1c")
        pwd = self.embed_password.get()
        
        if not src or not out or not msg or not pwd:
            messagebox.showwarning("Incomplete", "Please fill in all fields (File, Message, Password, and Output Path).")
            return
            
        src_ext = os.path.splitext(src.lower())[1]
        out_ext = os.path.splitext(out.lower())[1]
        
        if src_ext != out_ext:
            messagebox.showerror("Format Mismatch", "Output file extension MUST match input file extension! (.png -> .png, etc)")
            return
            
        try:
            payload = encrypt_message(msg.encode("utf-8"), pwd)
            
            if src_ext == ".png":
                embed(src, payload, pwd, out)
            elif src_ext == ".wav":
                embed_audio(src, payload, pwd, out)
            elif src_ext == ".txt":
                embed_text(src, payload, pwd, out)
            elif src_ext in [".mp3", ".mp4"]:
                if self.hiding_method.get() == "metadata":
                    embed_metadata(src, payload, out)
                else:
                    embed_eof(src, payload, out)
            else:
                messagebox.showerror("Error", "Unsupported format")
                return
                
            messagebox.showinfo("Success", f"Process complete! Message securely embedded into:\n{out}")
            
            self.embed_message.delete("1.0", "end")
            self.embed_password.set("")
            self.embed_filepath.set("")
            self.embed_outpath.set("")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to embed data:\n{e}")

    def run_extract(self):
        src = self.ext_filepath.get()
        pwd = self.ext_password.get()
        
        if not src or not pwd:
            messagebox.showwarning("Incomplete", "Please select a file and enter the password.")
            return
            
        src_ext = os.path.splitext(src.lower())[1]
        payload = None
        
        try:
            if src_ext == ".png":
                payload = extract(src, pwd)
            elif src_ext == ".wav":
                payload = extract_audio(src, pwd)
            elif src_ext == ".txt":
                payload = extract_text(src, pwd)
            elif src_ext in [".mp3", ".mp4"]:
                method = self.ext_hiding_method.get()
                if method == "metadata":
                    payload = extract_metadata(src)
                elif method == "eof":
                    payload = extract_eof(src)
                else:
                    # Seamless auto-detection
                    try:
                        payload = extract_metadata(src)
                    except ValueError:
                        try:
                            payload = extract_eof(src)
                        except ValueError:
                            raise ValueError("Could not find payload injected via either Metadata or EOF.")
            else:
                messagebox.showerror("Invalid File", "File must be .png, .wav, .mp3, or .mp4")
                return
                
            decrypted = decrypt_message(payload, pwd)
            self.ext_result.config(state="normal")
            self.ext_result.delete("1.0", "end")
            self.ext_result.insert("1.0", decrypted.decode("utf-8"))
            self.ext_result.config(state="disabled")
            
            messagebox.showinfo("Success", "HMAC Integrity verification successfully passed! Text decrypted.")
        except Exception as e:
            messagebox.showerror("Extraction Failed", f"Invalid password or corrupted data stream!\n\nSystem Details: {e}")

if __name__ == "__main__":
    app = StegoApp()
    app.mainloop()
