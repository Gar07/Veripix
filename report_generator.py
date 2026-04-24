from fpdf import FPDF
import os
from datetime import datetime
from PIL import Image

class ForensicReport(FPDF):
    """
    Modul Generator PDF untuk VeriPix.
    Bertanggung jawab merakit data intelijen, metadata, dan gambar ke dalam
    format laporan formal yang siap digunakan sebagai dokumen pembuktian.
    """
    
    def sanitize_txt(self, txt):
        """Menghapus karakter Unicode yang tidak didukung oleh standar FPDF (Latin-1)."""
        return str(txt).encode('latin-1', 'replace').decode('latin-1')

    def header(self):
        """Desain Header Laporan (Otomatis muncul di setiap halaman)."""
        self.set_font('Arial', 'B', 18)
        self.set_text_color(0, 51, 102) # Warna Biru Gelap
        self.cell(0, 10, 'VERIPIX DIGITAL FORENSICS', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, 'Automated Open Source Intelligence (OSINT) Report', 0, 1, 'C')
        self.set_line_width(0.5)
        self.set_draw_color(0, 51, 102)
        self.line(10, 28, 200, 28)
        self.ln(15)

    def footer(self):
        """Desain Footer Laporan."""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Generated securely by VeriPix Engine - Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, label):
        """Pembuat Judul Sub-Bab dengan latar belakang warna."""
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(230, 240, 255) # Biru Muda
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, self.sanitize_txt(f"  {label}"), 0, 1, 'L', 1)
        self.ln(4)

    def _get_analysis_explanation(self, analysis_type):
        """
        Kamus Pintar (Knowledge Base) Forensik.
        Mengembalikan teks penjelasan teknis berdasarkan modul yang dijalankan pengguna.
        """
        explanations = {
            "Compression ELA (Splicing)": (
                "METHODOLOGY: Error Level Analysis (ELA) identifies areas within an image that are at different compression levels. "
                "With JPEG images, the entire picture should generally be at roughly the same level.\n\n"
                "INTERPRETATION: Look for areas that are significantly brighter or uniquely colored compared to the surrounding background. "
                "These high-contrast regions indicate that the pixels were likely pasted from another source (splicing) or modified recently."
            ),
            "Explainable AI (Target Bounding Box)": (
                "METHODOLOGY: This module combines ELA with Computer Vision contour detection to automatically isolate and highlight anomalous regions.\n\n"
                "INTERPRETATION: A red bounding box drawn on the image indicates an algorithmic lock on a region with statistically abnormal compression signatures. "
                "This heavily suggests a localized digital manipulation, such as text overlay or object insertion."
            ),
            "SIFT Copy-Move (Cloning)": (
                "METHODOLOGY: Scale-Invariant Feature Transform (SIFT) extracts local geometric features and matches them across the same image to detect copy-move forgery.\n\n"
                "INTERPRETATION: Red lines connecting two distinct areas within the image confirm that the feature vectors are mathematically identical. "
                "This is concrete evidence of cloning (copy-pasting an object within the same frame to hide or duplicate elements)."
            ),
            "Noise Map Residual": (
                "METHODOLOGY: High-pass filtering (Median Blur subtraction) isolates the Sensor Pattern Noise (SPN) intrinsic to the camera hardware.\n\n"
                "INTERPRETATION: An authentic image exhibits a uniform noise pattern. If a specific region (like a face or object) shows a drastically "
                "smoother or harsher noise texture compared to its surroundings, it indicates composite forgery (splicing from a different camera)."
            ),
            "AI Detect (FFT)": (
                "METHODOLOGY: Fast Fourier Transform (FFT) converts the spatial image into the frequency domain to expose synthetic generation artifacts.\n\n"
                "INTERPRETATION: Natural photographs display a smooth, star-like frequency dispersion centered in the image. Generative AI models (e.g., Midjourney, DALL-E) "
                "often leave behind unnatural, geometric grid patterns or 'blind spots' in the high-frequency corners of the spectrum."
            ),
            "Steganography (LSB)": (
                "METHODOLOGY: Least Significant Bit (LSB) extraction strips away all visual data to reveal the absolute 0s and 1s of the lowest color bit-plane.\n\n"
                "INTERPRETATION: A normal image will display pure random static (white noise). If you observe structured patterns, faded barcodes, "
                "or solid blocks, it indicates that hidden data or malicious payloads have been steganographically embedded into the pixels."
            ),
            "Color Profiling (Histogram)": (
                "METHODOLOGY: RGB Histogram Profiling charts the exact distribution of red, green, and blue pixel intensities (0-255).\n\n"
                "INTERPRETATION: Natural images have smooth, flowing curves. If the graph displays 'comb effects' (sharp spikes with sudden zero-value gaps), "
                "it proves the image has undergone global digital color manipulation (such as Instagram filters, contrast boosting, or brush edits)."
            )
        }
        
        # Kembalikan penjelasan yang sesuai, atau default jika tidak ada
        for key in explanations:
            if key in analysis_type:
                return explanations[key]
        
        return "METHODOLOGY: Standard visual data extraction.\nINTERPRETATION: Please review the attached metadata and visual evidence manually."

    def generate_pdf(self, image_path, metadata, analysis_type, result_image_path, output_filename="Report.pdf"):
        """Fungsi utama untuk merakit PDF."""
        self.add_page()
        
        # --- 1. DOSSIER INFO ---
        self.set_font('Arial', '', 10)
        self.cell(40, 6, "Report Date", 0, 0); self.cell(0, 6, f": {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
        self.cell(40, 6, "Analysis Module", 0, 0); self.cell(0, 6, self.sanitize_txt(f": {analysis_type}"), 0, 1)
        self.cell(40, 6, "Target File", 0, 0); self.cell(0, 6, self.sanitize_txt(f": {metadata.get('File Name', 'Unknown')}"), 0, 1)
        self.ln(5)

        # --- 2. METADATA & INTEGRITY ---
        self.chapter_title('1. Evidence Integrity & Metadata')
        self.set_font('Arial', '', 9)
        
        keys_priority = ['File Name', 'File Size', 'MD5 Checksum', 'Format', 'Dimensions', 'Make', 'Model', 'Software', 'DateTime']
        
        for key in keys_priority:
            if key in metadata:
                val = str(metadata[key])
                if len(val) > 85: val = val[:82] + "..."
                self.set_fill_color(245, 245, 245)
                self.cell(45, 6, self.sanitize_txt(key), border=1, fill=True)
                self.cell(145, 6, self.sanitize_txt(val), border=1, ln=1)
        self.ln(8)

        # --- 3. FORENSIC EXPLANATION (FITUR BARU) ---
        self.chapter_title('2. Forensic Methodology & Interpretation')
        self.set_font('Arial', '', 10)
        explanation_text = self._get_analysis_explanation(analysis_type)
        self.multi_cell(0, 5, self.sanitize_txt(explanation_text))
        self.ln(8)

        # --- 4. VISUAL EVIDENCE ---
        self.chapter_title('3. Visual Evidence Verification')
        
        y_pos = self.get_y()
        self.set_font('Arial', 'B', 10)
        self.cell(90, 8, "Exhibit A: Original Image", 0, 0, 'C')
        self.cell(10, 8, "", 0, 0)
        self.cell(90, 8, "Exhibit B: Processed Result", 0, 1, 'C')
        
        img_width = 90
        try:
            if os.path.exists(image_path):
                self.image(image_path, x=10, y=y_pos+10, w=img_width)
            
            if result_image_path and os.path.exists(result_image_path):
                self.image(result_image_path, x=110, y=y_pos+10, w=img_width)
            else:
                self.set_xy(110, y_pos+30)
                self.set_font('Arial', 'I', 10)
                self.cell(90, 10, "[No visual processing generated]", 0, 0, 'C')
                
        except Exception as e:
            self.set_xy(10, y_pos+10)
            self.multi_cell(0, 10, self.sanitize_txt(f"[Error rendering visual preview: {str(e)}]"))

        # Mengamankan kursor agar tidak menimpa gambar
        self.set_y(y_pos + 90) 
        self.ln(10)

        # --- 5. DISCLAIMER ---
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 150, 150)
        disclaimer = ("DISCLAIMER: This document was algorithmically generated by VeriPix OSINT Suite. "
                      "Results are based on mathematical pixel/frequency analysis and do not constitute absolute legal truth. "
                      "False positives may occur due to extreme native compression or low-resolution sources. "
                      "Human expert verification is strictly advised.")
        self.multi_cell(0, 4, self.sanitize_txt(disclaimer))

        try:
            self.output(output_filename)
            return True, output_filename
        except Exception as e:
            return False, f"PDF Generation Failed. Error: {str(e)}"