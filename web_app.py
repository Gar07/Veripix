import streamlit as st
from PIL import Image
import os
import time
import pandas as pd
from forensics_engine import ForensicsEngine
from report_generator import ForensicReport
import streamlit.components.v1 as components

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="VeriPix OSINT", page_icon="🕵️‍♂️", layout="wide")

@st.cache_resource
def load_engine(): return ForensicsEngine()
engine = load_engine()

# --- CSS CUSTOM ---
st.markdown("""
    <style>
    .main {background-color: #0E1117;}
    h1, h2, h3 {color: #00FF41;}
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/nolan/96/cyber-security.png", width=80)
    st.title("VeriPix")
    st.caption("Advanced Digital Forensics")
    st.markdown("---")
    
    # Mode Operasi Utama
    app_mode = st.radio("Operation Mode", ["Single Investigation", "Mass Batch Processing"])
    st.markdown("---")

# ==========================================
# MODE 1: SINGLE INVESTIGATION (Detail)
# ==========================================
if app_mode == "Single Investigation":
    uploaded_file = st.sidebar.file_uploader("Upload 1 Target Image", type=['jpg', 'jpeg', 'png', 'webp'])
    
    if uploaded_file is not None:
        module = st.sidebar.selectbox("Analysis Module", [
            "Dashboard (Metadata)", 
            "Compression ELA (Splicing)",
            "Explainable AI (Target Bounding Box)",
            "3D Anomaly Topography (Visualizer)",
            "SIFT Copy-Move (Cloning)", 
            "Noise Map Residual", 
            "AI Detect (FFT)", 
            "Steganography (LSB)", 
            "Extract Text (OCR)", 
            "Color Profiling (Histogram)", 
            "Location Tracker (OSINT)",
            "Reverse Image Search (OSINT API)"
        ])
        
        temp_img_path = "temp_web_target.jpg"
        temp_res_path = "temp_web_result.jpg"
        
        with open(temp_img_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        col1, col2 = st.columns([3, 1])
        with col1: st.title(f"🔍 {module}")
        with col2:
            if st.button("📄 Export PDF Report"):
                with st.spinner('Compiling...'):
                    meta = engine.extract_metadata(temp_img_path)
                    res_path = temp_res_path if os.path.exists(temp_res_path) else None
                    out_name = f"Report_{int(time.time())}.pdf"
                    success, msg = ForensicReport().generate_pdf(temp_img_path, meta, module, res_path, out_name)
                    if success:
                        with open(out_name, "rb") as pdf_file:
                            st.download_button("📥 Download PDF", data=pdf_file.read(), file_name=out_name, mime='application/octet-stream')
                            
        st.markdown("---")
        img_col, res_col = st.columns(2)
        with img_col:
            st.subheader("Source Image")
            st.image(temp_img_path, width='stretch')
            
        with res_col:
            st.subheader("Intelligence Result")
            
            if module == "Dashboard (Metadata)":
                st.json(engine.extract_metadata(temp_img_path))
                
            elif module == "Compression ELA (Splicing)":
                with st.spinner("Processing..."):
                    res_img = engine.perform_ela(temp_img_path)
                    st.image(res_img, width='stretch', caption="Heatmap: Terang = Editan")
                    res_img.convert('RGB').save(temp_res_path)

            elif module == "Explainable AI (Target Bounding Box)":
                with st.spinner("Computer Vision is searching for anomalies..."):
                    res_img, found = engine.perform_ela_with_bounding_boxes(temp_img_path)
                    st.image(res_img, width='stretch', caption="Kotak Merah menunjukkan koordinat manipulasi")
                    if found: st.error("🚨 WARNING: Splicing / Text Overlay Detected!")
                    else: st.success("✅ Image structure appears clean/uniform.")
                    res_img.convert('RGB').save(temp_res_path)

            elif module == "SIFT Copy-Move (Cloning)":
                with st.spinner("Processing..."):
                    res_img = engine.detect_copy_move(temp_img_path)
                    if res_img:
                        st.image(res_img, width='stretch')
                        res_img.convert('RGB').save(temp_res_path)
                    else: st.success("No cloning detected.")

            elif module == "Noise Map Residual":
                with st.spinner("Processing..."):
                    res_img = engine.analyze_noise_map(temp_img_path)
                    st.image(res_img, width='stretch')
                    res_img.convert('RGB').save(temp_res_path)

            elif module == "AI Detect (FFT)":
                with st.spinner("Processing..."):
                    res_img = engine.detect_ai_fft(temp_img_path)
                    st.image(res_img, width='stretch')
                    res_img.convert('RGB').save(temp_res_path)

            elif module == "Steganography (LSB)":
                with st.spinner("Processing..."):
                    res_img = engine.extract_lsb_steganography(temp_img_path)
                    st.image(res_img, width='stretch')
                    res_img.convert('RGB').save(temp_res_path)

            elif module == "Color Profiling (Histogram)":
                with st.spinner("Processing..."):
                    res_img = engine.generate_color_histogram(temp_img_path)
                    st.image(res_img, width='stretch')
                    res_img.convert('RGB').save(temp_res_path)

            elif module == "Extract Text (OCR)":
                with st.spinner("Processing..."):
                    st.code(engine.extract_text_ocr(temp_img_path))

            elif module == "Location Tracker (OSINT)":
                with st.spinner("Tracking Satellites..."):
                    success, msg, map_path = engine.generate_osint_map(temp_img_path)
                    if success:
                        st.success(msg)
                        with open(map_path, "r", encoding='utf-8') as f:
                            components.html(f.read(), height=400)
                    else: st.warning(msg)

            elif module == "3D Anomaly Topography (Visualizer)":
                with st.spinner("Rendering 3D Surface..."):
                    fig = engine.generate_3d_anomaly_surface(temp_img_path)
                    if fig:
                        # Tampilkan grafik interaktif Plotly
                        st.plotly_chart(fig, use_container_width=True)
                        st.info("💡 TIP: Anda dapat memutar, zoom, dan melihat grafik 3D di atas. Puncak (gunung) yang sangat tinggi mengindikasikan tingkat kompresi error yang tinggi (potensi tempelan/teks).")
                    else:
                        st.error("Gagal melakukan render 3D.")

            elif module == "Reverse Image Search (OSINT API)":
                st.info("Fitur ini membutuhkan API Key gratis dari api.imgbb.com")
                imgbb_key = st.text_input("Masukkan ImgBB API Key:", type="password")
                st.write("🕵️‍♂️ **Cross-Platform Reverse Image Search**")
                st.caption("VeriPix akan mengunggah gambar sebagai 'umpan' dan mencari rekam jejaknya di seluruh internet.")
                
                # Cek apakah user sudah memasukkan API Key di sidebar
                if 'imgbb_key' in locals() and imgbb_key != "":
                    if st.button("🚀 Mulai Penelusuran Internet"):
                        with st.spinner("Mengunggah umpan dan menganalisis database global..."):
                            success, links, img_url = engine.reverse_image_search_osint(temp_img_path, imgbb_key)
                            
                            if success:
                                st.success("Umpan berhasil diunggah!")
                                st.image(img_url, width=150, caption="Umpan Cloud")
                                st.markdown("### 🌐 OSINT Investigation Links")
                                st.markdown("Klik tautan di bawah ini untuk mencari jejak gambar:")
                                
                                # Buat tombol link bergaya elegan
                                for name, url in links.items():
                                    st.markdown(f"➤ **[{name}]({url})**")
                                    
                                st.info("💡 **Strategi Intelijen:** Gunakan Yandex untuk melacak wajah/CCTV (algoritma wajah mereka terbaik), dan gunakan TinEye untuk melacak gambar berita hoax.")
                            else:
                                st.error(links) # Berisi pesan error
                else:
                    st.warning("⚠️ Masukkan ImgBB API Key untuk menggunakan fitur ini.")
    else:
        st.info("👈 Upload gambar target di sidebar untuk memulai.")

# ==========================================
# MODE 2: MASS BATCH PROCESSING
# ==========================================
elif app_mode == "Mass Batch Processing":
    st.title("📁 Mass Evidence Scanner")
    st.markdown("Unggah puluhan gambar sekaligus. VeriPix akan memindai metadata, GPS, dan potensi editan secara otomatis, lalu merangkumnya ke dalam tabel Data Intelijen.")
    
    batch_files = st.sidebar.file_uploader("Upload Multiple Images", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)
    
    if batch_files:
        if st.button("🚀 Start Mass Scanning"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results = []
            total_files = len(batch_files)
            
            for i, file in enumerate(batch_files):
                status_text.text(f"Scanning file {i+1} of {total_files}: {file.name}...")
                
                # Save temp file
                temp_path = f"temp_batch_{i}.jpg"
                with open(temp_path, "wb") as f:
                    f.write(file.getbuffer())
                
                # Ekstrak Info
                meta = engine.extract_metadata(temp_path)
                has_gps = "GPSInfo" in meta or "GPSLatitude" in meta
                software_edit = meta.get("Software", "None")
                
                # Cek manipulasi cepat via Anomali Bounding Box
                _, anomaly_found = engine.perform_ela_with_bounding_boxes(temp_path)
                
                results.append({
                    "File Name": file.name,
                    "Size": meta.get("File Size", "N/A"),
                    "Modified by Software?": software_edit,
                    "Has GPS Location?": "Yes" if has_gps else "No",
                    "Visual Anomaly (Splicing)": "DETECTED 🚨" if anomaly_found else "Clean",
                    "MD5 Hash": meta.get("MD5 Checksum", "N/A")
                })
                
                os.remove(temp_path) # Cleanup
                progress_bar.progress((i + 1) / total_files)
            
            status_text.text("Scanning Complete!")
            st.success(f"Berhasil memindai {total_files} barang bukti.")
            
            # Tampilkan sebagai Tabel Data (Pandas DataFrame)
            df = pd.DataFrame(results)
            st.dataframe(df, width='stretch')
            
            # Tombol Unduh CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Threat Intelligence Data (CSV)",
                data=csv,
                file_name='VeriPix_Mass_Report.csv',
                mime='text/csv',
            )
    else:
        st.info("👈 Silakan unggah banyak file sekaligus di sidebar.")