from fpdf import FPDF
import os
from datetime import datetime
from PIL import Image

class ForensicReport(FPDF):
    """
    Modul Generator PDF untuk VeriPix.
    Membuat Laporan Tunggal atau Laporan Kompilasi Multi-Halaman.
    """
    
    def sanitize_txt(self, txt):
        return str(txt).encode('latin-1', 'replace').decode('latin-1')

    def header(self):
        self.set_font('Arial', 'B', 18)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, 'VERIPIX DIGITAL FORENSICS', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, 'Automated Open Source Intelligence (OSINT) Report', 0, 1, 'C')
        self.set_line_width(0.5)
        self.set_draw_color(0, 51, 102)
        self.line(10, 28, 200, 28)
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Generated securely by VeriPix Engine - Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(230, 240, 255)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, self.sanitize_txt(f"  {label}"), 0, 1, 'L', 1)
        self.ln(4)

    def _get_analysis_explanation(self, analysis_type):
        explanations = {
            "Compression ELA": (
                "METHODOLOGY: Error Level Analysis (ELA) identifies areas within an image that are at different compression levels.\n"
                "INTERPRETATION: Look for areas that are significantly brighter or uniquely colored compared to the surrounding background. "
                "These high-contrast regions indicate that the pixels were likely pasted from another source (splicing) or modified recently."
            ),
            "Explainable AI": (
                "METHODOLOGY: Combines ELA with Computer Vision contour detection to automatically isolate anomalous regions.\n"
                "INTERPRETATION: A red bounding box indicates an algorithmic lock on a region with statistically abnormal compression signatures. "
                "This heavily suggests a localized digital manipulation."
            ),
            "SIFT Copy-Move": (
                "METHODOLOGY: Scale-Invariant Feature Transform (SIFT) extracts local geometric features and matches them across the same image.\n"
                "INTERPRETATION: Red lines connecting two distinct areas within the image confirm that the feature vectors are mathematically identical. "
                "This is concrete evidence of cloning."
            ),
            "Noise Map Residual": (
                "METHODOLOGY: High-pass filtering isolates the Sensor Pattern Noise (SPN) intrinsic to the camera hardware.\n"
                "INTERPRETATION: If a specific region shows a drastically smoother or harsher noise texture compared to its surroundings, "
                "it indicates composite forgery (splicing from a different camera)."
            ),
            "AI Detect (FFT)": (
                "METHODOLOGY: Fast Fourier Transform (FFT) converts the spatial image into the frequency domain.\n"
                "INTERPRETATION: Generative AI models often leave behind unnatural, geometric grid patterns or 'blind spots' in the high-frequency corners of the spectrum."
            ),
            "Steganography (LSB)": (
                "METHODOLOGY: Least Significant Bit (LSB) extraction strips away all visual data to reveal the absolute lowest color bit-plane.\n"
                "INTERPRETATION: If you observe structured patterns, faded barcodes, or solid blocks instead of random static, it indicates hidden data."
            ),
            "Color Profiling": (
                "METHODOLOGY: RGB Histogram Profiling charts the exact distribution of red, green, and blue pixel intensities.\n"
                "INTERPRETATION: If the graph displays 'comb effects' (sharp spikes with sudden zero-value gaps), it proves global color manipulation."
            )
        }
        for key in explanations:
            if key in analysis_type: return explanations[key]
        return "METHODOLOGY: Standard visual data extraction.\nINTERPRETATION: Please review the visual evidence manually."

    def _render_metadata_page(self, metadata):
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

    def _render_disclaimer(self):
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 150, 150)
        disclaimer = ("DISCLAIMER: This document was algorithmically generated by VeriPix OSINT Suite. "
                      "Results are based on mathematical pixel/frequency analysis and do not constitute absolute legal truth. "
                      "Human expert verification is strictly advised.")
        self.multi_cell(0, 4, self.sanitize_txt(disclaimer))

    # ---------------------------------------------------------
    # FUNGSI LAMA (SINGLE REPORT) - Tetap dipertahankan
    # ---------------------------------------------------------
    def generate_pdf(self, image_path, metadata, analysis_type, result_image_path, output_filename="Report.pdf"):
        self.add_page()
        self.set_font('Arial', '', 10)
        self.cell(40, 6, "Report Date", 0, 0); self.cell(0, 6, f": {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
        self.cell(40, 6, "Analysis Module", 0, 0); self.cell(0, 6, self.sanitize_txt(f": {analysis_type}"), 0, 1)
        self.cell(40, 6, "Target File", 0, 0); self.cell(0, 6, self.sanitize_txt(f": {metadata.get('File Name', 'Unknown')}"), 0, 1)
        self.ln(5)

        self._render_metadata_page(metadata)

        self.chapter_title('2. Forensic Methodology & Interpretation')
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, self.sanitize_txt(self._get_analysis_explanation(analysis_type)))
        self.ln(8)

        self.chapter_title('3. Visual Evidence Verification')
        y_pos = self.get_y()
        self.set_font('Arial', 'B', 10)
        self.cell(90, 8, "Exhibit A: Original Image", 0, 0, 'C'); self.cell(10, 8, "", 0, 0)
        self.cell(90, 8, "Exhibit B: Processed Result", 0, 1, 'C')
        
        try:
            if os.path.exists(image_path): self.image(image_path, x=10, y=y_pos+10, w=90)
            if result_image_path and os.path.exists(result_image_path): self.image(result_image_path, x=110, y=y_pos+10, w=90)
        except Exception: pass

        self.set_y(y_pos + 90); self.ln(10)
        self._render_disclaimer()

        try:
            self.output(output_filename); return True, output_filename
        except Exception as e: return False, str(e)

    # ---------------------------------------------------------
    # FUNGSI BARU (FULL COMPILATION DOSSIER)
    # ---------------------------------------------------------
    def generate_compilation_pdf(self, image_path, metadata, analysis_results_dict, output_filename="Full_Dossier.pdf"):
        """
        analysis_results_dict: Dictionary berisi { "Nama Modul": "path_gambar_hasil.jpg" }
        """
        self.add_page()
        
        # Halaman 1: Cover & Metadata
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, "FULL FORENSIC COMPILATION DOSSIER", 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 6, f"Date Compiled: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
        self.ln(10)

        self._render_metadata_page(metadata)
        
        # Tampilkan Gambar Asli di Halaman Pertama sebagai Referensi Utama
        self.chapter_title('Primary Evidence (Original)')
        if os.path.exists(image_path):
            self.image(image_path, x=60, w=90) # Ditengah
        self.ln(10)

        # Halaman Selanjutnya: Looping setiap hasil analisis
        chapter_num = 2
        for module_name, res_path in analysis_results_dict.items():
            self.add_page() # Tiap modul mendapat halaman baru agar rapi
            
            self.chapter_title(f'{chapter_num}. Module: {module_name}')
            chapter_num += 1
            
            # Penjelasan Teori
            self.set_font('Arial', '', 10)
            self.multi_cell(0, 5, self.sanitize_txt(self._get_analysis_explanation(module_name)))
            self.ln(8)
            
            # Visualisasi
            self.set_font('Arial', 'B', 10)
            self.cell(0, 8, "Visual Extraction Result:", 0, 1, 'L')
            
            if res_path and os.path.exists(res_path):
                # Render gambar hasil cukup besar di tengah
                self.image(res_path, x=45, w=120) 
            else:
                self.set_font('Arial', 'I', 10)
                self.cell(0, 10, "[No anomalous regions detected / Clean]", 0, 1, 'C')

        # Halaman Terakhir: Disclaimer
        self.ln(20)
        self._render_disclaimer()

        try:
            self.output(output_filename)
            return True, output_filename
        except Exception as e:
            return False, f"PDF Compilation Failed. Error: {str(e)}"