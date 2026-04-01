import cv2
import numpy as np
from PIL import Image, ImageChops, ExifTags
import io
import os
import hashlib
import time

import folium
import webbrowser
import pytesseract
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt

# Library Baru untuk OSINT & Data
from geopy.geocoders import Nominatim

class ForensicsEngine:
    def __init__(self):
        if os.name == 'nt': 
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    def perform_ela(self, image_path, quality=90):
        try:
            original = Image.open(image_path).convert('RGB')
            buffer = io.BytesIO()
            original.save(buffer, 'JPEG', quality=quality)
            buffer.seek(0)
            resaved = Image.open(buffer)
            ela_image = ImageChops.difference(original, resaved)
            extrema = ela_image.getextrema()
            max_diff = max([ex[1] for ex in extrema])
            if max_diff == 0: max_diff = 1
            scale = 255.0 / max_diff
            return ela_image.point(lambda p: p * scale)
        except Exception as e:
            return None

    def perform_ela_with_bounding_boxes(self, image_path, quality=90):
        """
        FITUR BARU: Menganalisis ELA lalu menggambar kotak merah pada gambar asli
        di area yang terindikasi manipulasi.
        """
        ela_img = self.perform_ela(image_path, quality)
        if not ela_img: return None

        try:
            # Konversi ELA ke format OpenCV Grayscale
            ela_cv = np.array(ela_img.convert('L'))
            
            # Thresholding: Ambil piksel yang sangat terang (indikasi error tinggi/editan)
            _, thresh = cv2.threshold(ela_cv, 200, 255, cv2.THRESH_BINARY)
            
            # Cari kontur (bentuk/area) dari piksel terang tersebut
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Load gambar asli untuk digambar
            orig_cv = cv2.cvtColor(np.array(Image.open(image_path).convert('RGB')), cv2.COLOR_RGB2BGR)
            
            anomaly_found = False
            for c in contours:
                # Filter noise kecil, hanya deteksi area editan yang cukup besar
                if cv2.contourArea(c) > 100: 
                    anomaly_found = True
                    x, y, w, h = cv2.boundingRect(c)
                    # Gambar kotak merah tebal
                    cv2.rectangle(orig_cv, (x, y), (x+w, y+h), (0, 0, 255), 3)
                    # Beri label
                    cv2.putText(orig_cv, "ANOMALY", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            # Jika ada anomali, kembalikan gambar dengan kotak. Jika bersih, kembalikan gambar asli
            return Image.fromarray(cv2.cvtColor(orig_cv, cv2.COLOR_BGR2RGB)), anomaly_found
        except Exception as e:
            print(f"Bounding Box Error: {e}")
            return Image.open(image_path), False

    def detect_copy_move(self, image_path):
        try:
            img = cv2.imread(image_path)
            if img is None: return None
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            sift = cv2.SIFT_create()
            keypoints, descriptors = sift.detectAndCompute(gray, None)
            if descriptors is None or len(descriptors) < 2: return None
            
            flann = cv2.FlannBasedMatcher(dict(algorithm=1, trees=5), dict(checks=50))
            matches = flann.knnMatch(descriptors, descriptors, k=2)
            
            good_matches = []
            for m, n in matches:
                if m.distance < 0.75 * n.distance:
                    pt1, pt2 = keypoints[m.queryIdx].pt, keypoints[m.trainIdx].pt
                    if np.linalg.norm(np.array(pt1) - np.array(pt2)) > 40: 
                        good_matches.append(m)

            img_matches = cv2.drawMatches(img, keypoints, img, keypoints, good_matches, None, flags=2, matchColor=(0, 0, 255))
            return Image.fromarray(cv2.cvtColor(img_matches, cv2.COLOR_BGR2RGB))
        except Exception: return None

    def detect_ai_fft(self, image_path):
        try:
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            f = np.fft.fft2(img)
            fshift = np.fft.fftshift(f)
            magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1)
            magnitude_spectrum = cv2.normalize(magnitude_spectrum, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            colored_spectrum = cv2.applyColorMap(magnitude_spectrum, cv2.COLORMAP_JET)
            return Image.fromarray(cv2.cvtColor(colored_spectrum, cv2.COLOR_BGR2RGB))
        except Exception: return None

    def analyze_noise_map(self, image_path):
        try:
            img = cv2.imread(image_path)
            denoised = cv2.medianBlur(img, 5)
            noise = cv2.absdiff(img, denoised)
            noise = cv2.normalize(noise, None, 0, 255, cv2.NORM_MINMAX)
            noise_gray = cv2.cvtColor(noise, cv2.COLOR_BGR2GRAY)
            heatmap = cv2.applyColorMap(noise_gray, cv2.COLORMAP_BONE)
            return Image.fromarray(cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB))
        except Exception: return None

    def extract_lsb_steganography(self, image_path):
        try:
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            lsb = img & 1
            return Image.fromarray((lsb * 255).astype(np.uint8))
        except Exception: return None

    def extract_text_ocr(self, image_path):
        try:
            img = Image.open(image_path)
            extracted_text = pytesseract.image_to_string(img)
            return extracted_text if extracted_text.strip() else "Tidak ada teks terdeteksi."
        except Exception as e: return f"OCR Error: {e}"

    def generate_osint_map(self, image_path):
        """
        FITUR BARU: Menambahkan Reverse Geocoding untuk mencari Alamat Jalan Fisik.
        """
        try:
            img = Image.open(image_path)
            exif = img._getexif()
            if not exif: return False, "Tidak ada data EXIF GPS.", None

            gps_info = None
            for tag, value in exif.items():
                if ExifTags.TAGS.get(tag, tag) == "GPSInfo":
                    gps_info = value
                    break

            if not gps_info: return False, "Metadata EXIF ada, tapi koordinat GPS nihil.", None

            def convert_to_degrees(value):
                d, m, s = value
                return float(d) + (float(m) / 60.0) + (float(s) / 3600.0)

            lat = convert_to_degrees(gps_info[2])
            if gps_info[1] != 'N': lat = -lat
            lon = convert_to_degrees(gps_info[4])
            if gps_info[3] != 'E': lon = -lon

            # REVERSE GEOCODING (Mencari alamat jalan)
            address = "Alamat fisik tidak ditemukan."
            try:
                geolocator = Nominatim(user_agent="veripix_osint_agent")
                location = geolocator.reverse(f"{lat}, {lon}", timeout=5)
                if location: address = location.address
            except Exception:
                pass # Lanjut saja jika server Geopy sedang sibuk

            # Generate Map
            map_path = "osint_map_target.html"
            m = folium.Map(location=[lat, lon], zoom_start=16)
            folium.Marker(
                [lat, lon], popup="Target Location", tooltip=address,
                icon=folium.Icon(color="red", icon="crosshairs", prefix='fa')
            ).add_to(m)
            m.save(map_path)
            
            msg = f"📍 Koordinat: {lat}, {lon}\n🏠 Alamat: {address}"
            return True, msg, map_path

        except Exception as e: return False, f"Error OSINT Map: {e}", None

    def generate_color_histogram(self, image_path):
        try:
            img = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
            plt.figure(figsize=(6, 4), facecolor='#1e1e1e')
            ax = plt.axes()
            ax.set_facecolor('#1e1e1e')
            ax.tick_params(colors='white')
            
            for i, col in enumerate(('red', 'green', 'blue')):
                hist = cv2.calcHist([img], [i], None, [256], [0, 256])
                plt.plot(hist, color=col, linewidth=2)
                plt.xlim([0, 256])
                
            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
            buf.seek(0)
            plt.close() 
            return Image.open(buf)
        except Exception: return None

    def extract_metadata(self, image_path):
        result = {}
        try:
            file_stats = os.stat(image_path)
            result['File Name'] = os.path.basename(image_path)
            result['File Size'] = f"{file_stats.st_size / 1024:.2f} KB"
            with open(image_path, "rb") as f:
                file_hash = hashlib.md5()
                while chunk := f.read(8192): file_hash.update(chunk)
            result['MD5 Checksum'] = file_hash.hexdigest()
            
            img = Image.open(image_path)
            result['Dimensions'] = f"{img.width} x {img.height}"
            
            exif_raw = img.getexif()
            if exif_raw:
                for tag_id, value in exif_raw.items():
                    tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                    if isinstance(value, bytes):
                        try: value = value.decode(errors='ignore')
                        except: value = "(Binary Data)"
                    result[str(tag_name)] = str(value)
            return result
        except Exception: return {"Error": "Failed to read file"}