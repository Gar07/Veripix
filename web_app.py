import streamlit as st
from PIL import Image
import os
import time
import pandas as pd
from forensics_engine import ForensicsEngine
from report_generator import ForensicReport
import streamlit.components.v1 as components

# ==========================================
# KONFIGURASI HALAMAN & ENGINE INIT
# ==========================================
st.set_page_config(page_title="VeriPix OSINT Suite", page_icon="🕵️‍♂️", layout="wide")

@st.cache_resource
def load_engine(): 
    return ForensicsEngine()
engine = load_engine()

st.markdown("""
    <style>
    .main {background-color: #0E1117;}
    h1, h2, h3 {color: #00FF41;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/nolan/96/cyber-security.png", width=80)
    st.title("VeriPix V4")
    st.caption("Advanced Digital Forensics & OSINT")
    st.markdown("---")
    
    app_mode = st.radio("System Operation Mode", ["🔍 Single Investigation", "📁 Mass Batch Processing"])
    st.markdown("---")

# ==========================================
# MODE 1: SINGLE INVESTIGATION
# ==========================================
if app_mode == "🔍 Single Investigation":
    uploaded_file = st.sidebar.file_uploader("Upload Target Evidence", type=['jpg', 'jpeg', 'png', 'webp'])
    
    if uploaded_file is not None:
        # Klasifikasi Modul agar rapi
        module = st.sidebar.selectbox("Select Investigation Tool", [
            "-- OVERVIEW --",
            "Dashboard (Metadata)", 
            "-- SPATIAL FORENSICS --",
            "Compression ELA (Splicing)",
            "Explainable AI (Target Bounding Box)",
            "3D Anomaly Topography (Visualizer)",
            "SIFT Copy-Move (Cloning)", 
            "Noise Map Residual", 
            "-- CYBER & SPECTRAL --",
            "AI Detect (FFT Spectrum)", 
            "Steganography (LSB)", 
            "Color Profiling (Histogram)", 
            "-- OSINT & TRACKING --",
            "Extract Text (OCR)", 
            "Location Tracker (GPS to Map)",
            "Reverse Image Search (API)"
        ])
        
        # Penanganan file sementara (I/O)
        temp_img_path = "temp_web_target.jpg"
        temp_res_path = "temp_web_result.jpg"
        
        with open(temp_img_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Header UI & Ekspor Laporan PDF
        col1, col2 = st.columns([3, 1])
        with col1: 
            clean_module_name = module if "--" not in module else module.replace("--", "").strip()
            st.title(f"🔍 {clean_module_name}")
            
        with col2:
            if "--" not in module and module != "Dashboard (Metadata)":
                if st.button("📄 Generate Intelligence PDF"):
                    with st.spinner('Compiling Dossier...'):
                        meta = engine.extract_metadata(temp_img_path)
                        res_path = temp_res_path if os.path.exists(temp_res_path) else None
                        out_name = f"VeriPix_Dossier_{int(time.time())}.pdf"
                        
                        success, msg = ForensicReport().generate_pdf(temp_img_path, meta, module, res_path, out_name)
                        
                        if success:
                            with open(out_name, "rb") as pdf_file:
                                st.download_button("📥 Download Official Report", data=pdf_file.read(), file_name=out_name, mime='application/pdf')
                            st.success("Dossier Prepared.")
                        else:
                            st.error(msg)
                            
        st.markdown("---")
        
        # Cegah eksekusi jika user memilih kategori pembatas ("-- OVERVIEW --")
        if "--" in module:
            st.info("👈 Please select a specific module under this category from the dropdown menu.")
        else:
            img_col, res_col = st.columns(2)
            with img_col:
                st.subheader("Source Evidence")
                st.image(temp_img_path, width='stretch')
                
            with res_col:
                st.subheader("Analysis & Extraction")
                
                if module == "Dashboard (Metadata)":
                    st.json(engine.extract_metadata(temp_img_path))
                    
                elif module == "Compression ELA (Splicing)":
                    with st.spinner("Processing Matrix..."):
                        res_img = engine.perform_ela(temp_img_path)
                        st.image(res_img, width='stretch', caption="Heatmap: Bright = Modified")
                        res_img.convert('RGB').save(temp_res_path)

                elif module == "Explainable AI (Target Bounding Box)":
                    with st.spinner("Computer Vision searching for structural anomalies..."):
                        res_img, found = engine.perform_ela_with_bounding_boxes(temp_img_path)
                        st.image(res_img, width='stretch', caption="Red box indicates manipulation coordinates")
                        if found: st.error("🚨 WARNING: Splicing / Text Overlay Detected!")
                        else: st.success("✅ Image structure appears clean/uniform.")
                        res_img.convert('RGB').save(temp_res_path)

                elif module == "SIFT Copy-Move (Cloning)":
                    with st.spinner("Hunting duplicate feature vectors..."):
                        res_img = engine.detect_copy_move(temp_img_path)
                        if res_img:
                            st.image(res_img, width='stretch')
                            res_img.convert('RGB').save(temp_res_path)
                        else: st.success("No cloned regions detected.")

                elif module == "Noise Map Residual":
                    with st.spinner("Isolating Sensor Pattern Noise..."):
                        res_img = engine.analyze_noise_map(temp_img_path)
                        st.image(res_img, width='stretch')
                        res_img.convert('RGB').save(temp_res_path)

                elif module == "AI Detect (FFT Spectrum)":
                    with st.spinner("Transforming to Frequency Domain..."):
                        res_img = engine.detect_ai_fft(temp_img_path)
                        st.image(res_img, width='stretch')
                        res_img.convert('RGB').save(temp_res_path)

                elif module == "Steganography (LSB)":
                    with st.spinner("Slicing Bit-Planes..."):
                        res_img = engine.extract_lsb_steganography(temp_img_path)
                        st.image(res_img, width='stretch')
                        res_img.convert('RGB').save(temp_res_path)

                elif module == "Color Profiling (Histogram)":
                    with st.spinner("Generating Distribution Graph..."):
                        res_img = engine.generate_color_histogram(temp_img_path)
                        st.image(res_img, width='stretch')
                        res_img.convert('RGB').save(temp_res_path)

                elif module == "Extract Text (OCR)":
                    with st.spinner("Optical Character Recognition engaged..."):
                        st.code(engine.extract_text_ocr(temp_img_path))

                elif module == "Location Tracker (GPS to Map)":
                    with st.spinner("Triangulating Satellite Coordinates..."):
                        success, msg, map_path = engine.generate_osint_map(temp_img_path)
                        if success:
                            st.success(msg)
                            with open(map_path, "r", encoding='utf-8') as f:
                                components.html(f.read(), height=400)
                        else: st.warning(msg)

                elif module == "3D Anomaly Topography (Visualizer)":
                    with st.spinner("Rendering 3D Surface Engine..."):
                        fig = engine.generate_3d_anomaly_surface(temp_img_path)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                        else: st.error("Failed to render 3D topography.")

                elif module == "Reverse Image Search (API)":
                    imgbb_key = st.text_input("Enter ImgBB API Key (Required):", type="password")
                    st.caption("VeriPix will upload a temporary decoy to trace the image's footprint across the global internet.")
                    
                    if imgbb_key:
                        if st.button("🚀 Execute Global Trace"):
                            with st.spinner("Uplinking to databases..."):
                                success, links, img_url = engine.reverse_image_search_osint(temp_img_path, imgbb_key)
                                if success:
                                    st.success("Decoy Deployed Successfully!")
                                    st.image(img_url, width=150)
                                    st.markdown("### 🌐 OSINT Gateways")
                                    for name, url in links.items():
                                        st.markdown(f"➤ **[{name}]({url})**")
                                else: st.error(links)
                    else: st.warning("⚠️ API Key is required to unlock this module.")
    else:
        st.markdown("<h2 style='text-align: center; color: gray; margin-top: 100px;'>SYSTEM STANDBY</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Awaiting Target Upload in the Sidebar.</p>", unsafe_allow_html=True)

# ==========================================
# MODE 2: MASS BATCH PROCESSING
# ==========================================
elif app_mode == "📁 Mass Batch Processing":
    st.title("📁 Mass Evidence Scanner")
    st.markdown("Automated batch processing module. Upload an archive of images, and VeriPix will simultaneously scan for metadata, geolocations, and structural splicing anomalies, compiling a definitive Threat Intelligence database.")
    
    batch_files = st.sidebar.file_uploader("Upload Evidence Batch", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)
    
    if batch_files:
        if st.button("🚀 INITIALIZE MASS SCAN"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results = []
            total_files = len(batch_files)
            
            for i, file in enumerate(batch_files):
                status_text.text(f"Scanning target {i+1}/{total_files}: {file.name}...")
                
                temp_path = f"temp_batch_{i}.jpg"
                with open(temp_path, "wb") as f:
                    f.write(file.getbuffer())
                
                meta = engine.extract_metadata(temp_path)
                has_gps = "GPSInfo" in meta or "GPSLatitude" in meta
                software_edit = meta.get("Software", "None")
                
                _, anomaly_found = engine.perform_ela_with_bounding_boxes(temp_path)
                
                results.append({
                    "File Name": file.name,
                    "Size": meta.get("File Size", "N/A"),
                    "Software Signature": software_edit,
                    "GPS Tag": "Yes" if has_gps else "No",
                    "Visual Anomaly (Splicing)": "DETECTED 🚨" if anomaly_found else "Clean",
                    "Integrity Hash (MD5)": meta.get("MD5 Checksum", "N/A")
                })
                
                os.remove(temp_path) 
                progress_bar.progress((i + 1) / total_files)
            
            status_text.text("Scan Concluded.")
            st.success(f"Successfully processed {total_files} evidence files.")
            
            df = pd.DataFrame(results)
            st.dataframe(df, width='stretch')
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Threat Intelligence Data (CSV)",
                data=csv,
                file_name='VeriPix_Batch_Report.csv',
                mime='text/csv',
            )
    else:
        st.info("👈 Initialize the batch process by uploading multiple files on the sidebar.")