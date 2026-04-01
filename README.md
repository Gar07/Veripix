# 🕵️‍♂️ VeriPix OSINT - Digital Image Forensics Suite

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://veripix.streamlit.app/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![OpenCV](https://img.shields.io/badge/opencv-%23white.svg?logo=opencv&logoColor=white)](https://opencv.org/)

VeriPix OSINT is an advanced, web-based digital image forensics tool designed to detect visual manipulation, AI-generated images, and hidden steganographic data using mathematical image processing algorithms without the heavy computational cost of deep learning models.

## 🚀 Live Demo
Access the live web application here: **[VeriPix Web Intelligence](https://veripix.streamlit.app/)**

## 🧩 Core Forensic Modules

* **🔍 Compression Analysis (ELA):** Highlights areas with differing compression levels, indicating splicing or text overlay manipulation.
* **🧬 Cloning Detection (SIFT):** Uses Scale-Invariant Feature Transform to find identical duplicate regions (copy-move forgery).
* **🌌 Noise Map Residuals:** Extracts Sensor Pattern Noise (SPN) to expose inconsistencies from composite images.
* **🤖 AI Detection (FFT Spectrum):** Translates the spatial domain into a frequency domain to spot unnatural, algorithmically generated frequency grids common in AI art.
* **🕵️ Steganography Slicer (LSB):** Isolates the Least Significant Bit to reveal hidden data or messages embedded within pixels.
* **🔤 Optical Character Recognition (OCR):** Extracts text directly from images for rapid fact-checking of fake chat screenshots.
* **🌍 Geolocation Tracker (GPS):** Parses EXIF coordinates and generates an interactive HTML map pinpointing the camera's location.

## 💻 Local Installation

To run this application locally on your machine:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Gar07/Veripix.md](https://github.com/Gar07/Veripix.md)
    cd Veripix
    ```
2.  **Install system dependencies (Tesseract):**
    * For Debian/Ubuntu/Kubuntu users:
        ```bash
        sudo apt update
        sudo apt install tesseract-ocr
        ```
    * For Windows users, download the installer from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki).
3.  **Install Python requirements:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the Streamlit server:**
    ```bash
    streamlit run web_app.py
    ```

## 📄 Automated Reporting
VeriPix automatically generates a comprehensive PDF Intelligence Report including MD5 checksums for evidence integrity, metadata extraction, and side-by-side visual analysis.

---
*Developed by Gar2007*
