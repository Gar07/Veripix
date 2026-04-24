import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
from forensics_engine import ForensicsEngine
from report_generator import ForensicReport
import os
import time

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class VeriPixApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("VeriPix Advanced Forensics Suite")
        self.geometry("1200x800") 
        
        self.engine = ForensicsEngine()
        self.current_image_path = None
        self.current_tk_image = None
        self.last_result_pil = None
        self.last_analysis_type = "None"
        self.temp_result_path = "temp_analysis_result.jpg"

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="VeriPix V3", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.pack(pady=(20, 10))

        self.btn_load = ctk.CTkButton(self.sidebar_frame, text="📂 Load Target Image", command=self.load_image, height=40)
        self.btn_load.pack(pady=10, padx=20, fill="x")

        # KATEGORI 1
        ctk.CTkLabel(self.sidebar_frame, text="--- SPATIAL FORENSICS ---", text_color="gray", font=("Arial", 10, "bold")).pack(pady=(15, 5))
        self.ela_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.ela_frame.pack(padx=10, fill="x")
        self.btn_ela = ctk.CTkButton(self.ela_frame, text="🔍 Compression (ELA)", fg_color="#D35B58", hover_color="#C72C41", command=self.run_ela)
        self.btn_ela.pack(pady=2, fill="x")
        self.ela_slider = ctk.CTkSlider(self.ela_frame, from_=50, to=99, number_of_steps=49)
        self.ela_slider.set(90)
        self.ela_slider.pack(pady=2)

        self.btn_sift = ctk.CTkButton(self.sidebar_frame, text="🧬 Cloning (SIFT)", fg_color="#D35B58", hover_color="#C72C41", command=self.run_sift)
        self.btn_sift.pack(pady=5, padx=20, fill="x")

        self.btn_noise = ctk.CTkButton(self.sidebar_frame, text="🌌 Noise Map (Splicing)", fg_color="#D35B58", hover_color="#C72C41", command=self.run_noise)
        self.btn_noise.pack(pady=5, padx=20, fill="x")

        # KATEGORI 2
        ctk.CTkLabel(self.sidebar_frame, text="--- ADVANCED & CYBER ---", text_color="gray", font=("Arial", 10, "bold")).pack(pady=(15, 5))
        self.btn_fft = ctk.CTkButton(self.sidebar_frame, text="🤖 AI Detect (FFT)", fg_color="#8E44AD", hover_color="#732D91", command=self.run_fft)
        self.btn_fft.pack(pady=5, padx=20, fill="x")

        self.btn_lsb = ctk.CTkButton(self.sidebar_frame, text="🕵️ Steganography (LSB)", fg_color="#8E44AD", hover_color="#732D91", command=self.run_lsb)
        self.btn_lsb.pack(pady=5, padx=20, fill="x")

        # KATEGORI 3
        ctk.CTkLabel(self.sidebar_frame, text="--- DATA & OSINT ---", text_color="gray", font=("Arial", 10, "bold")).pack(pady=(15, 5))
        self.btn_ocr = ctk.CTkButton(self.sidebar_frame, text="🔤 Extract Text (OCR)", fg_color="#E67E22", hover_color="#D35400", command=self.run_ocr)
        self.btn_ocr.pack(pady=5, padx=20, fill="x")

        self.btn_map = ctk.CTkButton(self.sidebar_frame, text="🌍 Track Location (GPS)", fg_color="#E67E22", hover_color="#D35400", command=self.run_osint_map)
        self.btn_map.pack(pady=5, padx=20, fill="x")

        self.btn_hist = ctk.CTkButton(self.sidebar_frame, text="📊 Color Profiling", fg_color="#E67E22", hover_color="#D35400", command=self.run_histogram)
        self.btn_hist.pack(pady=5, padx=20, fill="x")

        # KATEGORI 4
        ctk.CTkLabel(self.sidebar_frame, text="--- REPORTING ---", text_color="gray", font=("Arial", 10, "bold")).pack(pady=(15, 5))
        self.btn_meta = ctk.CTkButton(self.sidebar_frame, text="📝 EXIF & Hash", fg_color="#3B8ED0", hover_color="#36719F", command=self.show_metadata)
        self.btn_meta.pack(pady=5, padx=20, fill="x")
        
        self.btn_export = ctk.CTkButton(self.sidebar_frame, text="📄 PDF Investigation Report", fg_color="#F39C12", hover_color="#D68910", command=self.export_report)
        self.btn_export.pack(pady=5, padx=20, fill="x")

        # --- AREA DISPLAY ---
        self.display_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.display_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.image_label = ctk.CTkLabel(self.display_frame, text="Awaiting Image...", font=ctk.CTkFont(size=16))
        self.image_label.pack(expand=True, fill="both")

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg;*.jpeg;*.png;*.tif;*.webp;*.bmp")])
        if file_path:
            self.current_image_path = file_path
            self.last_result_pil = None
            self.last_analysis_type = "Original Image"
            self.show_image_on_gui(Image.open(file_path))

    def show_image_on_gui(self, pil_image):
        try:
            w, h = pil_image.size
            aspect_ratio = w / h
            target_height = 650
            target_width = int(target_height * aspect_ratio)
            
            if target_width > 850:
                target_width = 850
                target_height = int(target_width / aspect_ratio)

            resized_img = pil_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            self.current_tk_image = ctk.CTkImage(light_image=resized_img, dark_image=resized_img, size=(target_width, target_height))
            self.image_label.configure(image=self.current_tk_image, text="")
        except Exception as e:
            messagebox.showerror("Error", f"Display error: {e}")

    def run_wrapper(self, func, process_name, success_msg):
        if not self.current_image_path:
            messagebox.showwarning("Akses Ditolak", "Muat gambar target terlebih dahulu.")
            return

        self.image_label.configure(text=f"Executing {process_name}...")
        self.update()

        result = func()
        
        if result:
            self.show_image_on_gui(result)
            self.last_result_pil = result
            self.last_analysis_type = process_name
            messagebox.showinfo(f"{process_name} Complete", success_msg)
        else:
            messagebox.showerror("Error", f"Gagal mengeksekusi {process_name}. (Cek Console/Terminal untuk detail)")

    def run_ela(self):
        q = int(self.ela_slider.get())
        self.run_wrapper(lambda: self.engine.perform_ela(self.current_image_path, q), 
                         f"ELA (Quality {q})", "Area terang indikasi tempelan/teks modifikasi.")

    def run_sift(self):
        self.run_wrapper(lambda: self.engine.detect_copy_move(self.current_image_path), 
                         "SIFT Copy-Move", "Garis merah menunjukkan pola identik (Kloning).")

    def run_noise(self):
        self.run_wrapper(lambda: self.engine.analyze_noise_map(self.current_image_path), 
                         "Noise Map Residual", "Area dengan tekstur berbeda drastis adalah tempelan (Splicing).")

    def run_fft(self):
        self.run_wrapper(lambda: self.engine.detect_ai_fft(self.current_image_path), 
                         "AI FFT Spectrum", "Spektrum natural berbentuk bintang terpusat. AI sering memiliki pola grid geometris yang aneh di sudut spektrum.")

    def run_lsb(self):
        self.run_wrapper(lambda: self.engine.extract_lsb_steganography(self.current_image_path), 
                         "LSB Steganography", "Pola acak = Aman. Pola solid/teks/barcode samar = Ada data tersembunyi.")
                         
    def run_ocr(self):
        if not self.current_image_path:
            messagebox.showwarning("Warning", "Load gambar dulu!")
            return
            
        self.image_label.configure(text="Reading text via Tesseract OCR...")
        self.update()
        
        text_result = self.engine.extract_text_ocr(self.current_image_path)
        self.image_label.configure(text="") 
        
        top = ctk.CTkToplevel(self)
        top.title("Extracted Text Content")
        top.geometry("600x400")
        top.attributes('-topmost', True) # Agar window tidak tenggelam
        
        textbox = ctk.CTkTextbox(top, width=580, height=380, font=("Consolas", 14))
        textbox.pack(padx=10, pady=10, expand=True, fill="both")
        textbox.insert("0.0", text_result)

    def run_osint_map(self):
        if not self.current_image_path:
            messagebox.showwarning("Warning", "Load gambar dulu!")
            return
            
        self.image_label.configure(text="Scanning EXIF for GPS Signatures...")
        self.update()
        
        success, msg = self.engine.generate_osint_map(self.current_image_path)
        self.image_label.configure(text="")
        
        if success:
            messagebox.showinfo("OSINT Tracking Success", msg)
        else:
            messagebox.showinfo("OSINT Result", msg)

    def run_histogram(self):
        self.run_wrapper(lambda: self.engine.generate_color_histogram(self.current_image_path), 
                         "RGB Histogram Profiling", "Grafik distribusi piksel warna. Perhatikan celah atau anomali lonjakan yang mengindikasikan editan warna.")

    def show_metadata(self):
        if not self.current_image_path: return
        data = self.engine.extract_metadata(self.current_image_path)
        if not data: return
        info = "\n".join([f"{k}: {v}" for k, v in list(data.items())[:25]])
        messagebox.showinfo("Forensic Data", info)

    def export_report(self):
        if not self.current_image_path: return
        if not self.last_result_pil:
            if not messagebox.askyesno("Info", "Belum ada analisis visual. Lanjut export?"): return

        try:
            self.image_label.configure(text="Generating PDF Document...")
            self.update()
            
            temp_res = None
            if self.last_result_pil:
                # FIX ERROR RGBA KE JPG: Paksa konversi ke RGB
                safe_img = self.last_result_pil.convert('RGB')
                safe_img.save(self.temp_result_path)
                temp_res = self.temp_result_path
            
            meta = self.engine.extract_metadata(self.current_image_path)
            out_name = f"VeriPix_Intel_{int(time.time())}.pdf"
            
            success, msg = ForensicReport().generate_pdf(
                self.current_image_path, meta, self.last_analysis_type, temp_res, out_name)
            
            if os.path.exists(self.temp_result_path): os.remove(self.temp_result_path)
            
            self.image_label.configure(text="") # Bersihkan label status
            
            if success:
                messagebox.showinfo("Sukses", f"Laporan Intelijen siap:\n{msg}")
                # FIX PATH WINDOWS: Menambahkan tanda kutip agar nama file aman dibuka
                os.system(f'start "" "{msg}"')
            else:
                messagebox.showerror("Error", msg)
        except Exception as e:
            messagebox.showerror("Critical Error", str(e))

if __name__ == "__main__":
    app = VeriPixApp()
    app.mainloop()