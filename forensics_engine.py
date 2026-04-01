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

class ForensicsEngine:
    def __init__(self):
        # Deteksi OS cerdas: Jika di Windows (lokal), gunakan path C:\
        # Jika di Linux (Cloud Server), biarkan kosong agar memakai settingan default server
        if os.name == 'nt':  # 'nt' artinya Windows
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
            print(f"Error ELA: {e}")
            return None

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
        except Exception as e:
            print(f"Error SIFT: {e}")
            return None

    def detect_ai_fft(self, image_path):
        try:
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            f = np.fft.fft2(img)
            fshift = np.fft.fftshift(f)
            magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1)
            magnitude_spectrum = cv2.normalize(magnitude_spectrum, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            colored_spectrum = cv2.applyColorMap(magnitude_spectrum, cv2.COLORMAP_JET)
            return Image.fromarray(cv2.cvtColor(colored_spectrum, cv2.COLOR_BGR2RGB))
        except Exception as e:
            print(f"Error FFT: {e}")
            return None

    def analyze_noise_map(self, image_path):
        try:
            img = cv2.imread(image_path)
            denoised = cv2.medianBlur(img, 5)
            noise = cv2.absdiff(img, denoised)
            noise = cv2.normalize(noise, None, 0, 255, cv2.NORM_MINMAX)
            noise_gray = cv2.cvtColor(noise, cv2.COLOR_BGR2GRAY)
            heatmap = cv2.applyColorMap(noise_gray, cv2.COLORMAP_BONE)
            return Image.fromarray(cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB))
        except Exception as e:
            print(f"Error Noise Map: {e}")
            return None

    def extract_lsb_steganography(self, image_path):
        try:
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            lsb = img & 1
            lsb_visual = lsb * 255
            return Image.fromarray(lsb_visual.astype(np.uint8))
        except Exception as e:
            print(f"Error Steganography: {e}")
            return None

    def extract_text_ocr(self, image_path):
        try:
            img = Image.open(image_path)
            extracted_text = pytesseract.image_to_string(img)
            
            if not extracted_text.strip():
                return "Tidak ada teks yang dapat dibaca di dalam gambar ini."
            return extracted_text
        except Exception as e:
            return f"Error OCR: Pastikan path Tesseract benar. Detail: {e}"

    def generate_osint_map(self, image_path):
        try:
            img = Image.open(image_path)
            exif = img._getexif()
            if not exif:
                return False, "Tidak ada data EXIF pada gambar (Bukan dari kamera atau metadata sudah dihapus)."

            gps_info = None
            for tag, value in exif.items():
                decoded = ExifTags.TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    gps_info = value
                    break

            if not gps_info:
                return False, "Tidak ditemukan koordinat GPS pada metadata EXIF."

            def convert_to_degrees(value):
                d, m, s = value
                return float(d) + (float(m) / 60.0) + (float(s) / 3600.0)

            lat = convert_to_degrees(gps_info[2])
            if gps_info[1] != 'N': lat = -lat
            
            lon = convert_to_degrees(gps_info[4])
            if gps_info[3] != 'E': lon = -lon

            map_path = "osint_map_target.html"
            m = folium.Map(location=[lat, lon], zoom_start=15)
            folium.Marker(
                [lat, lon], 
                popup="Target Location Extracted",
                tooltip="Click for details",
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(m)
            
            m.save(map_path)
            webbrowser.open('file://' + os.path.realpath(map_path))
            return True, f"Koordinat ditemukan: {lat}, {lon}\nPeta telah dibuka di browser Anda."

        except Exception as e:
            return False, f"Error OSINT Map: {e}"

    def generate_color_histogram(self, image_path):
        try:
            img = cv2.imread(image_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            plt.figure(figsize=(6, 4), facecolor='#1e1e1e')
            ax = plt.axes()
            ax.set_facecolor('#1e1e1e')
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.title.set_color('white')
            
            colors = ('red', 'green', 'blue')
            for i, col in enumerate(colors):
                hist = cv2.calcHist([img], [i], None, [256], [0, 256])
                plt.plot(hist, color=col, linewidth=2)
                plt.xlim([0, 256])
                
            plt.title('RGB Channel Distribution')
            plt.xlabel('Pixel Intensity')
            plt.ylabel('Frequency')
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            plt.close() 
            
            return Image.open(buf)
        except Exception as e:
            print(f"Error Histogram: {e}")
            return None

    def extract_metadata(self, image_path):
        result = {}
        try:
            file_stats = os.stat(image_path)
            result['File Name'] = os.path.basename(image_path)
            result['File Size'] = f"{file_stats.st_size / 1024:.2f} KB"
            
            with open(image_path, "rb") as f:
                file_hash = hashlib.md5()
                while chunk := f.read(8192):
                    file_hash.update(chunk)
            result['MD5 Checksum'] = file_hash.hexdigest()
            result['Last Modified'] = time.ctime(file_stats.st_mtime)

            img = Image.open(image_path)
            result['Format'] = img.format 
            result['Dimensions'] = f"{img.width} x {img.height}"
            
            exif_raw = img.getexif()
            if exif_raw:
                for tag_id, value in exif_raw.items():
                    tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                    if isinstance(value, bytes):
                        try: value = value.decode(errors='ignore') # FIX: Cegah error decode
                        except: value = "(Binary Data)"
                    result[str(tag_name)] = str(value)

            return result
        except Exception as e:
            return {"Error": str(e)}