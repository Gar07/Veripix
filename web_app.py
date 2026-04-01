import streamlit as st
from PIL import Image
import os
import time
from forensics_engine import ForensicsEngine
from report_generator import ForensicReport
import streamlit.components.v1 as components

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="VeriPix Web Intelligence",
    page_icon="🕵️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INISIALISASI ENGINE ---
@st.cache_resource
def load_engine():
    return ForensicsEngine()

engine = load_engine()

# --- CSS CUSTOM UNTUK TAMPILAN LEBIH "HACKER/CYBER" ---
st.markdown("""
    <style>
    .main {background-color: #0E1117;}
    h1, h2, h3 {color: #00FF41;}
    .stButton>button {width: 100%; border-radius: 5px; background-color: #1E1E1E; color: white; border: 1px solid #00FF41;}
    .stButton>button:hover {background-color: #00FF41; color: black;}
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: KONTROL & UPLOAD ---
with st.sidebar:
    st.image("https://img.icons8.com/nolan/96/cyber-security.png", width=80)
    st.title("VeriPix OSINT")
    st.caption("Digital Image Forensics Suite v3.0")
    st.markdown("---")
    
    uploaded_file = st.file_uploader("📁 Upload Target Image", type=['jpg', 'jpeg', 'png', 'webp', 'bmp'])
    
    st.markdown("---")
    st.subheader("🛠️ Analysis Modules")
    
    # Pilihan Modul Menggunakan Selectbox agar rapi
    module = st.selectbox("Select Investigation Tool", [
        "Dashboard (Overview)",
        "Compression ELA (Splicing)",
        "SIFT Copy-Move (Cloning)",
        "Noise Map Residual",
        "AI Detect (FFT Spectrum)",
        "Steganography (LSB)",
        "Extract Text (OCR)",
        "Color Profiling (Histogram)",
        "Location Tracker (OSINT)"
    ])

    ela_quality = 90
    if module == "Compression ELA (Splicing)":
        ela_quality = st.slider("ELA Sensitivity Quality", 50, 99, 90)

# --- FUNGSI HELPER UNTUK FILE TEMP ---
temp_img_path = "temp_web_target.jpg"
temp_res_path = "temp_web_result.jpg"

if uploaded_file is not None:
    # Simpan file upload ke disk sementara karena engine kita membaca via path
    with open(temp_img_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # --- HEADER KONTEN ---
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"🔍 {module}")
    with col2:
        # Tombol Download Report (Selalu muncul jika ada gambar)
        if st.button("📄 Generate PDF Report"):
            with st.spinner('Compiling Intelligence Report...'):
                meta = engine.extract_metadata(temp_img_path)
                out_name = f"VeriPix_Report_{int(time.time())}.pdf"
                
                # Cek apakah ada file hasil analisis terakhir di disk
                res_path = temp_res_path if os.path.exists(temp_res_path) else None
                
                success, msg = ForensicReport().generate_pdf(
                    temp_img_path, meta, module, res_path, out_name)
                
                if success:
                    with open(out_name, "rb") as pdf_file:
                        PDFbyte = pdf_file.read()
                    st.download_button(label="📥 Download PDF Now",
                                        data=PDFbyte,
                                        file_name=out_name,
                                        mime='application/octet-stream')
                    st.success("Report Ready!")
                else:
                    st.error(f"Failed to generate report: {msg}")

    st.markdown("---")

    # --- TAMPILAN UTAMA ---
    img_col, res_col = st.columns(2)
    
    with img_col:
        st.subheader("Source Image")
        st.image(temp_img_path, width='stretch')
        
    with res_col:
        st.subheader("Analysis Result")
        
        # LOGIKA EKSEKUSI BERDASARKAN PILIHAN DROPDOWN
        if module == "Dashboard (Overview)":
            st.info("Pilih modul di Sidebar sebelah kiri untuk memulai investigasi visual.")
            st.write("**Extracted Metadata / EXIF:**")
            meta_data = engine.extract_metadata(temp_img_path)
            st.json(meta_data)
            # Hapus temp result lama jika kembali ke dashboard
            if os.path.exists(temp_res_path): os.remove(temp_res_path)

        elif module == "Compression ELA (Splicing)":
            with st.spinner("Processing Error Level Analysis..."):
                res_img = engine.perform_ela(temp_img_path, ela_quality)
                if res_img:
                    st.image(res_img, width='stretch', caption=f"ELA Result (Quality: {ela_quality})")
                    res_img.convert('RGB').save(temp_res_path)

        elif module == "SIFT Copy-Move (Cloning)":
            with st.spinner("Hunting for cloned pixels..."):
                res_img = engine.detect_copy_move(temp_img_path)
                if res_img:
                    st.image(res_img, width='stretch', caption="SIFT Matches (Red Lines = Cloned)")
                    res_img.convert('RGB').save(temp_res_path)
                else:
                    st.success("No significant duplication patterns detected.")

        elif module == "Noise Map Residual":
            with st.spinner("Extracting Sensor Pattern Noise..."):
                res_img = engine.analyze_noise_map(temp_img_path)
                if res_img:
                    st.image(res_img, width='stretch', caption="High-frequency Noise Map")
                    res_img.convert('RGB').save(temp_res_path)

        elif module == "AI Detect (FFT Spectrum)":
            with st.spinner("Transforming to Frequency Domain..."):
                res_img = engine.detect_ai_fft(temp_img_path)
                if res_img:
                    st.image(res_img, width='stretch', caption="Fourier Transform Spectrum")
                    res_img.convert('RGB').save(temp_res_path)

        elif module == "Steganography (LSB)":
            with st.spinner("Slicing Bit-Planes..."):
                res_img = engine.extract_lsb_steganography(temp_img_path)
                if res_img:
                    st.image(res_img, width='stretch', caption="Least Significant Bit Visualization")
                    res_img.convert('RGB').save(temp_res_path)

        elif module == "Color Profiling (Histogram)":
            with st.spinner("Generating RGB Profile..."):
                res_img = engine.generate_color_histogram(temp_img_path)
                if res_img:
                    st.image(res_img, width='stretch', caption="Color Distribution Graph")
                    res_img.convert('RGB').save(temp_res_path)

        elif module == "Extract Text (OCR)":
            with st.spinner("Running Optical Character Recognition..."):
                text = engine.extract_text_ocr(temp_img_path)
                st.text_area("Extracted Text", text, height=300)

        elif module == "Location Tracker (OSINT)":
            with st.spinner("Scanning GPS Signatures..."):
                success, msg = engine.generate_osint_map(temp_img_path)
                if success:
                    st.success(msg.split('\n')[0]) # Tampilkan koordinat
                    # Render HTML Map langsung di dalam Web App!
                    if os.path.exists("osint_map_target.html"):
                        with open("osint_map_target.html", "r", encoding='utf-8') as f:
                            html_data = f.read()
                        components.html(html_data, height=400)
                else:
                    st.warning(msg)

else:
    # Tampilan jika belum ada gambar yang di-upload
    st.markdown("<h2 style='text-align: center; color: gray; margin-top: 100px;'>Awaiting Target Input...</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Gunakan panel di sebelah kiri untuk mengunggah gambar barang bukti.</p>", unsafe_allow_html=True)