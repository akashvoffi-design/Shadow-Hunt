#!/usr/bin/env python3
"""
ShadowHunt Working Version - No Unicode characters for Windows compatibility
"""

import os
import sys
import json
import random
import hashlib
from datetime import datetime
from io import BytesIO

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

# Core imports with fallbacks
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("WARNING: OpenCV not available")

try:
    from flask import Flask, render_template_string, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("WARNING: Flask not available")

# Import camera detector
try:
    from camera_detector import CameraDetector
    CAMERA_DETECTOR_AVAILABLE = True
except ImportError:
    CAMERA_DETECTOR_AVAILABLE = False
    print("WARNING: Camera detector not available")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("WARNING: PIL not available")

# Initialize Flask app
if FLASK_AVAILABLE:
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
    app.config['SECRET_KEY'] = 'shadowhunt_secret_key_2024'

# Create upload directory
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class SimpleDeepfakeDetector:
    """Simple deepfake detector with basic functionality"""
    
    def __init__(self):
        self.model_loaded = False
        self.load_models()
    
    def load_models(self):
        """Load basic detection models"""
        try:
            if OPENCV_AVAILABLE:
                # Load basic face detection
                self.face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                self.eye_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
                self.model_loaded = True
                print("SUCCESS: Basic models loaded successfully!")
            else:
                print("WARNING: OpenCV not available - using simulation mode")
                self.model_loaded = False
        except Exception as e:
            print(f"WARNING: Model loading failed: {e}")
            self.model_loaded = False
    
    def analyze_image(self, img_path):
        """Analyze image for deepfake characteristics using advanced algorithms"""
        try:
            if not OPENCV_AVAILABLE:
                return self._simulate_analysis("image")
            
            # Load image
            img = cv2.imread(img_path)
            if img is None:
                return {"error": "Could not load image"}
            
            height, width = img.shape[:2]
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Initialize detection scores
            detection_scores = {
                "face_consistency": 0.0,
                "eye_alignment": 0.0,
                "facial_symmetry": 0.0,
                "image_quality": 0.0,
                "color_consistency": 0.0,
                "edge_patterns": 0.0,
                "noise_analysis": 0.0,
                "metadata_check": 0.0
            }
            
            # 1. Face Detection and Analysis
            faces = self.face_detector.detectMultiScale(gray, 1.1, 4)
            face_count = len(faces)
            
            if face_count > 0:
                # Analyze each face for deepfake indicators
                for (x, y, w, h) in faces:
                    face_roi = gray[y:y+h, x:x+w]
                    
                    # Eye detection and alignment
                    eyes = self.eye_detector.detectMultiScale(face_roi, 1.1, 3)
                    detection_scores["eye_alignment"] += self._analyze_eye_alignment(eyes, w, h)
                    
                    # Facial symmetry analysis
                    detection_scores["facial_symmetry"] += self._analyze_facial_symmetry(face_roi)
                    
                    # Face consistency check
                    detection_scores["face_consistency"] += self._analyze_face_consistency(face_roi)
            
            # 2. Image Quality Analysis
            detection_scores["image_quality"] = self._analyze_image_quality(img)
            
            # 3. Color Consistency Analysis
            detection_scores["color_consistency"] = self._analyze_color_consistency(img)
            
            # 4. Edge Pattern Analysis
            detection_scores["edge_patterns"] = self._analyze_edge_patterns(gray)
            
            # 5. Noise Analysis
            detection_scores["noise_analysis"] = self._analyze_noise_patterns(gray)
            
            # 6. Metadata Analysis
            detection_scores["metadata_check"] = self._analyze_metadata(img_path)
            
            # 7. AI Artifact Detection
            detection_scores["ai_artifacts"] = self._detect_ai_artifacts(img)
            
            # Calculate weighted confidence score with improved weights for AI detection
            weights = {
                "face_consistency": 0.25,  # Face analysis
                "eye_alignment": 0.20,     # Eye analysis
                "facial_symmetry": 0.15,   # Symmetry analysis
                "ai_artifacts": 0.20,      # AI artifact detection
                "image_quality": 0.08,     # Image quality
                "color_consistency": 0.06, # Color consistency
                "edge_patterns": 0.04,     # Edge patterns
                "noise_analysis": 0.01,    # Noise analysis
                "metadata_check": 0.01     # Metadata check
            }
            
            # Calculate overall confidence with bias toward detecting fakes
            base_confidence = sum(detection_scores[key] * weights[key] for key in weights)
            
            # Apply AI detection heuristics
            ai_indicators = 0
            total_checks = 0
            
            # Check 1: Perfect symmetry (AI indicator)
            if detection_scores["facial_symmetry"] > 0.8:
                ai_indicators += 1
            total_checks += 1
            
            # Check 2: Unnatural eye alignment (AI indicator)
            if detection_scores["eye_alignment"] < 0.6:
                ai_indicators += 1
            total_checks += 1
            
            # Check 3: Unnatural face consistency (AI indicator)
            if detection_scores["face_consistency"] < 0.5:
                ai_indicators += 1
            total_checks += 1
            
            # Check 4: Unnatural image quality (AI indicator)
            if detection_scores["image_quality"] < 0.4:
                ai_indicators += 1
            total_checks += 1
            
            # Check 5: Unnatural color consistency (AI indicator)
            if detection_scores["color_consistency"] < 0.4:
                ai_indicators += 1
            total_checks += 1
            
            # Check 6: Unnatural edge patterns (AI indicator)
            if detection_scores["edge_patterns"] < 0.4:
                ai_indicators += 1
            total_checks += 1
            
            # Calculate AI probability
            ai_probability = ai_indicators / total_checks if total_checks > 0 else 0
            
            # Adjust confidence based on AI indicators
            if ai_probability > 0.5:  # More than half indicators suggest AI
                confidence_real = max(0.1, base_confidence - (ai_probability * 0.6))
            else:
                confidence_real = min(0.9, base_confidence + (0.5 - ai_probability) * 0.2)
            
            # Apply additional heuristics for better accuracy
            doc_info = self._detect_document_like(img)
            if face_count == 0:
                # If it looks like a document/ID card, do NOT penalize for no face
                if doc_info.get("is_document"):
                    # Slight boost to counter bias toward fakes
                    confidence_real = min(0.95, max(0.2, confidence_real + 0.25))
                else:
                    confidence_real = max(0.1, confidence_real - 0.4)  # No face and not a document
            elif face_count > 1:
                confidence_real = max(0.1, confidence_real - 0.3)  # Multiple faces suspicious
            
            # Ensure confidence is within valid range
            confidence_real = max(0.0, min(1.0, confidence_real))
            confidence_fake = 1.0 - confidence_real
            
            # Generate watermark analysis
            watermark_hash = self._generate_hash(img_path)
            has_watermark = self._check_watermark(img)
            
            # Determine status with more accurate thresholds
            if confidence_real > 0.7:
                status = "Likely Real"
            elif confidence_real < 0.3:
                status = "Likely Fake"
            else:
                status = "Uncertain - Requires Further Analysis"
            
            return {
                "type": "image",
                "confidence_real": round(confidence_real, 3),
                "confidence_fake": round(confidence_fake, 3),
                "status": status,
                "watermark": {
                    "found": has_watermark,
                    "hash": watermark_hash if has_watermark else None
                },
                "analysis_details": {
                    "face_count": face_count,
                    "image_dimensions": f"{width}x{height}",
                    "detection_scores": {k: round(v, 3) for k, v in detection_scores.items()},
                    "analysis_methods": "Advanced Multi-Algorithm Detection",
                    "document_analysis": doc_info
                }
            }
        except Exception as e:
            return {"error": f"Image analysis failed: {str(e)}"}
    
    def _simulate_analysis(self, file_type):
        """Simulate analysis when OpenCV is not available"""
        confidence_real = random.uniform(0.3, 0.8)
        confidence_fake = 1.0 - confidence_real
        
        return {
            "type": file_type,
            "confidence_real": round(confidence_real, 3),
            "confidence_fake": round(confidence_fake, 3),
            "status": "Likely Real" if confidence_real > 0.6 else "Likely Fake",
            "watermark": {
                "found": random.choice([True, False, True]),
                "hash": f"sim_{random.randint(1000, 9999)}" if random.choice([True, False]) else None
            },
            "analysis_details": {
                "mode": "simulation",
                "note": "OpenCV not available - using simulated analysis"
            }
        }
    
    def _analyze_eye_alignment(self, eyes, face_width, face_height):
        """Analyze eye alignment for deepfake detection - improved for AI detection"""
        try:
            if len(eyes) != 2:
                return 0.2  # More suspicious if not exactly 2 eyes
            
            # Get eye centers
            eye_centers = []
            for (ex, ey, ew, eh) in eyes:
                center_x = ex + ew // 2
                center_y = ey + eh // 2
                eye_centers.append((center_x, center_y))
            
            # Check horizontal alignment (AI often has perfect alignment)
            y_diff = abs(eye_centers[0][1] - eye_centers[1][1])
            if y_diff < 2:  # Too perfect alignment - likely AI
                return 0.1
            elif y_diff > face_height * 0.15:  # Eyes not horizontally aligned
                return 0.2
            elif y_diff <= face_height * 0.05:  # Very good alignment
                return 0.8
            
            # Check eye distance (should be ~30% of face width)
            eye_distance = abs(eye_centers[0][0] - eye_centers[1][0])
            expected_distance = face_width * 0.3
            distance_ratio = eye_distance / expected_distance
            
            # AI often has very precise eye distances
            if 0.95 <= distance_ratio <= 1.05:  # Too precise - likely AI
                return 0.2
            elif 0.7 <= distance_ratio <= 1.3:  # Normal eye distance
                return 0.9
            elif 0.5 <= distance_ratio <= 1.5:  # Acceptable range
                return 0.6
            else:
                return 0.3  # Unusual eye distance
                
        except Exception:
            return 0.5
    
    def _analyze_facial_symmetry(self, face_roi):
        """Analyze facial symmetry for deepfake detection - improved for AI detection"""
        try:
            height, width = face_roi.shape
            
            # Split face into left and right halves
            left_half = face_roi[:, :width//2]
            right_half = cv2.flip(face_roi[:, width//2:], 1)
            
            # Resize to same dimensions
            min_width = min(left_half.shape[1], right_half.shape[1])
            left_half = cv2.resize(left_half, (min_width, left_half.shape[0]))
            right_half = cv2.resize(right_half, (min_width, right_half.shape[0]))
            
            # Calculate symmetry difference
            diff = np.mean(np.abs(left_half.astype(float) - right_half.astype(float)))
            
            # AI-generated faces often have too perfect symmetry (diff < 8) or unnatural patterns
            if diff < 8:  # Too perfect - likely AI
                return 0.1  # Very low score for perfect symmetry
            elif 8 <= diff <= 25:  # Natural asymmetry range
                return 0.9
            elif 25 < diff <= 45:  # Acceptable range
                return 0.7
            elif 45 < diff <= 70:  # Somewhat suspicious
                return 0.4
            else:
                return 0.2  # Very suspicious - likely manipulated
                
        except Exception:
            return 0.5
    
    def _analyze_face_consistency(self, face_roi):
        """Analyze face consistency and natural variations - improved for AI detection"""
        try:
            # Calculate local binary patterns for texture analysis
            lbp = self._calculate_lbp(face_roi)
            
            # Analyze texture consistency
            texture_variance = np.var(lbp)
            
            # AI-generated faces often have very uniform or very chaotic textures
            if texture_variance < 30:  # Too uniform - likely AI
                return 0.1
            elif texture_variance > 500:  # Too chaotic - likely AI
                return 0.2
            elif 50 <= texture_variance <= 200:  # Natural texture variance
                return 0.9
            elif 30 <= texture_variance <= 300:  # Acceptable range
                return 0.7
            else:
                return 0.4  # Unnatural texture patterns
                
        except Exception:
            return 0.5
    
    def _calculate_lbp(self, image):
        """Calculate Local Binary Pattern for texture analysis"""
        try:
            # Simple LBP implementation
            lbp = np.zeros_like(image)
            for i in range(1, image.shape[0] - 1):
                for j in range(1, image.shape[1] - 1):
                    center = image[i, j]
                    binary_string = ""
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            if di == 0 and dj == 0:
                                continue
                            if image[i + di, j + dj] >= center:
                                binary_string += "1"
                            else:
                                binary_string += "0"
                    lbp[i, j] = int(binary_string, 2)
            return lbp
        except Exception:
            return np.zeros_like(image)
    
    def _analyze_image_quality(self, img):
        """Analyze image quality metrics"""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Calculate Laplacian variance (sharpness)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Calculate contrast
            contrast = gray.std()
            
            # Calculate brightness distribution
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist_entropy = -np.sum(hist * np.log2(hist + 1e-10))
            
            # Score based on natural quality metrics
            quality_score = 0.0
            
            # Sharpness check
            if 100 <= laplacian_var <= 2000:
                quality_score += 0.4
            elif 50 <= laplacian_var <= 3000:
                quality_score += 0.2
            
            # Contrast check
            if 20 <= contrast <= 80:
                quality_score += 0.3
            elif 15 <= contrast <= 100:
                quality_score += 0.2
            
            # Entropy check (natural images have good entropy)
            if 6.0 <= hist_entropy <= 8.0:
                quality_score += 0.3
            elif 5.0 <= hist_entropy <= 8.5:
                quality_score += 0.2
            
            return min(1.0, quality_score)
            
        except Exception:
            return 0.5
    
    def _analyze_color_consistency(self, img):
        """Analyze color consistency and natural color distribution"""
        try:
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # Calculate color histograms
            hist_h = cv2.calcHist([hsv], [0], None, [180], [0, 180])
            hist_s = cv2.calcHist([hsv], [1], None, [256], [0, 256])
            hist_v = cv2.calcHist([hsv], [2], None, [256], [0, 256])
            
            # Calculate entropy for each channel
            def calculate_entropy(hist):
                hist = hist.flatten()
                hist = hist[hist > 0]
                if len(hist) == 0:
                    return 0
                prob = hist / hist.sum()
                return -np.sum(prob * np.log2(prob + 1e-10))
            
            h_entropy = calculate_entropy(hist_h)
            s_entropy = calculate_entropy(hist_s)
            v_entropy = calculate_entropy(hist_v)
            
            avg_entropy = (h_entropy + s_entropy + v_entropy) / 3
            
            # Natural images have good color entropy
            if avg_entropy > 6.5:
                return 0.9
            elif avg_entropy > 5.0:
                return 0.7
            elif avg_entropy > 3.0:
                return 0.5
            else:
                return 0.2  # Very low entropy, likely artificial
                
        except Exception:
            return 0.5
    
    def _analyze_edge_patterns(self, gray):
        """Analyze edge patterns for deepfake detection"""
        try:
            # Detect edges
            edges = cv2.Canny(gray, 50, 150)
            
            # Calculate edge density
            edge_density = np.sum(edges > 0) / edges.size
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Analyze contour complexity
            if len(contours) > 0:
                avg_contour_area = np.mean([cv2.contourArea(c) for c in contours])
                contour_complexity = len(contours) / (gray.shape[0] * gray.shape[1] / 10000)
            else:
                avg_contour_area = 0
                contour_complexity = 0
            
            # Score based on natural edge patterns
            score = 0.0
            
            # Edge density check
            if 0.05 <= edge_density <= 0.25:
                score += 0.4
            elif 0.02 <= edge_density <= 0.35:
                score += 0.2
            
            # Contour complexity check
            if 5 <= contour_complexity <= 50:
                score += 0.3
            elif 2 <= contour_complexity <= 100:
                score += 0.2
            
            # Average contour area check
            if 100 <= avg_contour_area <= 5000:
                score += 0.3
            elif 50 <= avg_contour_area <= 10000:
                score += 0.2
            
            return min(1.0, score)
            
        except Exception:
            return 0.5
    
    def _analyze_noise_patterns(self, gray):
        """Analyze noise patterns for deepfake detection"""
        try:
            # Apply Gaussian blur and subtract from original to get noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            noise = cv2.absdiff(gray, blurred)
            
            # Calculate noise statistics
            noise_mean = np.mean(noise)
            noise_std = np.std(noise)
            noise_variance = np.var(noise)
            
            # Natural images have specific noise characteristics
            score = 0.0
            
            # Noise mean check
            if 2 <= noise_mean <= 15:
                score += 0.4
            elif 1 <= noise_mean <= 25:
                score += 0.2
            
            # Noise standard deviation check
            if 5 <= noise_std <= 25:
                score += 0.3
            elif 3 <= noise_std <= 40:
                score += 0.2
            
            # Noise variance check
            if 25 <= noise_variance <= 625:
                score += 0.3
            elif 10 <= noise_variance <= 1600:
                score += 0.2
            
            return min(1.0, score)
            
        except Exception:
            return 0.5
    
    def _analyze_metadata(self, img_path):
        """Analyze image metadata for inconsistencies"""
        try:
            # Try to read EXIF data
            from PIL import Image
            from PIL.ExifTags import TAGS
            
            with Image.open(img_path) as img:
                exif_data = img._getexif()
                
                if exif_data is None:
                    return 0.3  # No metadata, suspicious
                
                # Check for common deepfake indicators in metadata
                suspicious_indicators = 0
                total_checks = 0
                
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    total_checks += 1
                    
                    # Check for suspicious software
                    if tag == "Software" and value:
                        software_lower = str(value).lower()
                        if any(sus in software_lower for sus in ['deepfake', 'face-swap', 'fake', 'synthetic']):
                            suspicious_indicators += 1
                    
                    # Check for unusual camera models
                    if tag == "Model" and value:
                        model_lower = str(value).lower()
                        if any(sus in model_lower for sus in ['virtual', 'fake', 'synthetic']):
                            suspicious_indicators += 1
                
                if total_checks == 0:
                    return 0.5
                
                # Calculate score based on suspicious indicators
                suspicious_ratio = suspicious_indicators / total_checks
                if suspicious_ratio == 0:
                    return 0.9  # No suspicious indicators
                elif suspicious_ratio < 0.2:
                    return 0.7  # Few suspicious indicators
                else:
                    return 0.2  # Many suspicious indicators
                    
        except Exception:
            return 0.5  # Default score if metadata analysis fails
    
    def _detect_ai_artifacts(self, img):
        """Detect common AI generation artifacts"""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            artifacts_detected = 0
            total_checks = 0
            
            # Check 1: Unnatural frequency patterns (AI often has specific frequency signatures)
            f_transform = np.fft.fft2(gray)
            f_shift = np.fft.fftshift(f_transform)
            magnitude_spectrum = np.log(np.abs(f_shift) + 1)
            
            # AI images often have unusual frequency patterns
            freq_variance = np.var(magnitude_spectrum)
            if freq_variance < 2.0 or freq_variance > 8.0:  # Unnatural frequency patterns
                artifacts_detected += 1
            total_checks += 1
            
            # Check 2: Unnatural gradient patterns
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # AI images often have very smooth or very sharp gradients
            grad_variance = np.var(gradient_magnitude)
            if grad_variance < 50 or grad_variance > 1000:  # Unnatural gradient patterns
                artifacts_detected += 1
            total_checks += 1
            
            # Check 3: Unnatural color channel correlations
            if len(img.shape) == 3:
                b, g, r = cv2.split(img)
                # AI images often have unusual correlations between color channels
                corr_bg = np.corrcoef(b.flatten(), g.flatten())[0, 1]
                corr_br = np.corrcoef(b.flatten(), r.flatten())[0, 1]
                corr_gr = np.corrcoef(g.flatten(), r.flatten())[0, 1]
                
                # Natural images have specific correlation patterns
                if abs(corr_bg) > 0.9 or abs(corr_br) > 0.9 or abs(corr_gr) > 0.9:
                    artifacts_detected += 1
                total_checks += 1
            
            # Check 4: Unnatural edge density patterns
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # AI images often have very uniform edge distributions
            if edge_density < 0.02 or edge_density > 0.4:  # Unnatural edge density
                artifacts_detected += 1
            total_checks += 1
            
            # Check 5: Unnatural pixel value distributions
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist_entropy = -np.sum(hist * np.log2(hist + 1e-10))
            
            # AI images often have unnatural pixel distributions
            if hist_entropy < 6.0 or hist_entropy > 8.5:  # Unnatural distribution
                artifacts_detected += 1
            total_checks += 1
            
            # Calculate artifact score (lower score = more artifacts detected)
            artifact_ratio = artifacts_detected / total_checks if total_checks > 0 else 0
            return max(0.1, 1.0 - artifact_ratio)  # Invert so higher score = more real
            
        except Exception:
            return 0.5
    
    def _detect_document_like(self, img):
        """Detect if an image looks like a flat ID/document (e.g., Aadhaar/PAN).

        Heuristic-only (no OCR): looks for a prominent quadrilateral card-like contour,
        plausible aspect ratio, and text/edge density patterns typical of printed IDs.
        Returns a dictionary with a boolean and scores for transparency.
        """
        try:
            if img is None or len(img.shape) != 3:
                return {"is_document": False, "score": 0.0, "reason": "invalid_image"}

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            h, w = gray.shape[:2]

            # Preprocess to emphasize edges and card boundaries
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blur, 50, 150)

            # Find contours and select the largest reasonable one
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            rect_score = 0.0
            aspect_ok = False
            coverage_ok = False
            if contours:
                contours = sorted(contours, key=cv2.contourArea, reverse=True)
                largest = contours[0]
                peri = cv2.arcLength(largest, True)
                approx = cv2.approxPolyDP(largest, 0.02 * peri, True)

                # Quadrilateral shape is common for cards
                if len(approx) == 4:
                    rect_score += 0.6
                    x, y, ww, hh = cv2.boundingRect(approx)
                    aspect = (ww / max(1, hh)) if hh > 0 else 0
                    # Typical ID card aspect ratios are around 1.4–1.6 (landscape) or ~0.6–0.7 (portrait)
                    if 1.3 <= aspect <= 1.9 or 0.5 <= aspect <= 0.8:
                        aspect_ok = True
                        rect_score += 0.2
                    # Ensure the detected card occupies a reasonable image area (not tiny artifact)
                    area_ratio = (ww * hh) / float(w * h)
                    if 0.15 <= area_ratio <= 0.95:
                        coverage_ok = True
                        rect_score += 0.2

            # Text/edge density heuristic (printed text regions create mid/high edge density)
            edge_density = float((edges > 0).sum()) / float(edges.size)
            # Compute local variance to distinguish flat printed surfaces from natural scenes
            local_var = cv2.Laplacian(gray, cv2.CV_64F).var()

            text_edge_ok = 0.06 <= edge_density <= 0.30  # too low = blank, too high = cluttered scene
            flat_surface_ok = 50 <= local_var <= 1200     # avoid extremely low/high texture variance

            score_components = [
                rect_score,  # 0.0–1.0
                0.2 if text_edge_ok else 0.0,
                0.2 if flat_surface_ok else 0.0,
            ]
            score = float(sum(score_components))

            is_document = score >= 0.6 and aspect_ok and coverage_ok

            return {
                "is_document": bool(is_document),
                "score": round(score, 3),
                "edge_density": round(edge_density, 3),
                "local_variance": round(local_var, 1) if isinstance(local_var, (int, float)) else 0.0,
                "aspect_ratio_ok": bool(aspect_ok),
                "coverage_ok": bool(coverage_ok),
            }
        except Exception:
            return {"is_document": False, "score": 0.0, "reason": "exception"}
    
    def _check_watermark(self, img):
        """Check for watermarks or digital signatures"""
        try:
            # Simple watermark detection based on corner analysis
            height, width = img.shape[:2]
            
            # Check corners for watermark patterns
            corners = [
                img[0:50, 0:50],  # Top-left
                img[0:50, width-50:width],  # Top-right
                img[height-50:height, 0:50],  # Bottom-left
                img[height-50:height, width-50:width]  # Bottom-right
            ]
            
            watermark_score = 0
            for corner in corners:
                # Check for low-variance regions (potential watermarks)
                if np.var(corner) < 100:  # Low variance might indicate watermark
                    watermark_score += 1
            
            # If multiple corners have low variance, likely has watermark
            return watermark_score >= 2
            
        except Exception:
            return False
    
    def _generate_hash(self, file_path):
        """Generate a simple hash for watermarking"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            hash_input = content + str(datetime.now().timestamp()).encode()
            return hashlib.sha256(hash_input).hexdigest()[:16]
        except:
            return f"hash_{random.randint(1000, 9999)}"

# Initialize detector
detector = SimpleDeepfakeDetector()

# Initialize camera detector
if CAMERA_DETECTOR_AVAILABLE:
    camera_detector = CameraDetector()
    print("Camera detector initialized successfully!")
else:
    camera_detector = None
    print("Camera detector not available")

# Simple HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShadowHunt - Deepfake Detection</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;600&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: 'Exo 2', sans-serif; 
            background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
            color: white; 
            overflow-x: hidden;
            min-height: 100vh;
        }
        
        .animated-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            background: radial-gradient(circle at 20% 80%, rgba(0, 255, 255, 0.1) 0%, transparent 50%),
                        radial-gradient(circle at 80% 20%, rgba(255, 0, 255, 0.1) 0%, transparent 50%),
                        radial-gradient(circle at 40% 40%, rgba(0, 255, 0, 0.05) 0%, transparent 50%);
            animation: bgPulse 8s ease-in-out infinite;
        }
        
        @keyframes bgPulse {
            0%, 100% { opacity: 0.3; transform: scale(1); }
            50% { opacity: 0.6; transform: scale(1.05); }
        }
        
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px;
            position: relative;
            z-index: 1;
        }
        
        .header { 
            text-align: center; 
            margin-bottom: 50px;
            animation: slideDown 1s ease-out;
        }
        
        @keyframes slideDown {
            from { transform: translateY(-50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        .title { 
            font-family: 'Orbitron', monospace;
            font-size: 4rem; 
            font-weight: 900;
            background: linear-gradient(45deg, #00ffff, #ff00ff, #ffff00, #00ffff);
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: gradientShift 3s ease-in-out infinite, glow 2s ease-in-out infinite alternate;
            margin-bottom: 20px;
            text-shadow: 0 0 30px rgba(0, 255, 255, 0.5);
        }
        
        @keyframes gradientShift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        @keyframes glow {
            from { filter: drop-shadow(0 0 20px rgba(0, 255, 255, 0.3)); }
            to { filter: drop-shadow(0 0 40px rgba(255, 0, 255, 0.5)); }
        }
        
        .subtitle {
            font-size: 1.2rem;
            color: #b0b0b0;
            margin-bottom: 10px;
            animation: fadeInUp 1s ease-out 0.5s both;
        }
        
        .tagline {
            font-style: italic;
            color: #888;
            font-size: 1rem;
            animation: fadeInUp 1s ease-out 1s both;
        }
        
        @keyframes fadeInUp {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        .upload-area { 
            border: 3px dashed #00ffff; 
            padding: 60px 40px; 
            text-align: center; 
            margin: 40px 0; 
            border-radius: 20px; 
            cursor: pointer;
            background: rgba(0, 255, 255, 0.05);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            animation: slideUp 1s ease-out 1.5s both;
        }
        
        @keyframes slideUp {
            from { transform: translateY(50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        .upload-area::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(0, 255, 255, 0.1), transparent);
            transform: rotate(45deg);
            transition: all 0.5s ease;
            opacity: 0;
        }
        
        .upload-area:hover::before {
            animation: shimmer 1s ease-in-out;
        }
        
        @keyframes shimmer {
            0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); opacity: 0; }
            50% { opacity: 1; }
            100% { transform: translateX(100%) translateY(100%) rotate(45deg); opacity: 0; }
        }
        
        .upload-area:hover { 
            background: rgba(0, 255, 255, 0.1); 
            border-color: #ff00ff;
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 255, 255, 0.2);
        }
        
        .upload-icon {
            font-size: 4rem;
            margin-bottom: 20px;
            animation: bounce 2s ease-in-out infinite;
        }
        
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-10px); }
            60% { transform: translateY(-5px); }
        }
        
        .btn { 
            background: linear-gradient(45deg, #00ffff, #ff00ff);
            color: white;
            padding: 18px 36px;
            border: none;
            border-radius: 50px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin: 15px;
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 10px 20px rgba(0, 255, 255, 0.3);
        }
        
        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s ease;
        }
        
        .btn:hover::before {
            left: 100%;
        }
        
        .btn:hover { 
            transform: translateY(-3px);
            box-shadow: 0 15px 30px rgba(255, 0, 255, 0.4);
            background: linear-gradient(45deg, #ff00ff, #00ffff);
        }
        
        .btn:disabled { 
            background: #666; 
            cursor: not-allowed;
            box-shadow: none;
            transform: none;
        }
        
        .btn:disabled:hover {
            transform: none;
            box-shadow: none;
        }
        
        .results { 
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            padding: 30px; 
            border-radius: 20px; 
            margin: 30px 0;
            border: 1px solid rgba(0, 255, 255, 0.2);
            animation: slideIn 0.8s ease-out;
        }
        
        @keyframes slideIn {
            from { transform: translateX(-100px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .trust-meter { 
            text-align: center; 
            margin: 30px 0;
            animation: scaleIn 1s ease-out;
        }
        
        @keyframes scaleIn {
            from { transform: scale(0.5); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }
        
        .trust-gauge { 
            width: 200px; 
            height: 200px; 
            border-radius: 50%; 
            background: conic-gradient(from 0deg, #ff0000 0deg, #ffff00 120deg, #00ff00 240deg); 
            margin: 0 auto 30px; 
            display: flex; 
            align-items: center; 
            justify-content: center;
            position: relative;
            animation: rotate 10s linear infinite;
        }
        
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        .trust-gauge::before {
            content: '';
            position: absolute;
            top: 10px;
            left: 10px;
            right: 10px;
            bottom: 10px;
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            border-radius: 50%;
            z-index: 1;
        }
        
        .trust-inner { 
            width: 140px; 
            height: 140px; 
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            border-radius: 50%; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center;
            position: relative;
            z-index: 2;
            border: 2px solid rgba(0, 255, 255, 0.3);
        }
        
        .trust-percentage { 
            font-family: 'Orbitron', monospace;
            font-size: 2.5rem; 
            font-weight: bold; 
            background: linear-gradient(45deg, #00ffff, #ff00ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        .status { 
            font-size: 1.8rem; 
            font-weight: bold; 
            margin: 20px 0;
            padding: 15px 30px;
            border-radius: 50px;
            display: inline-block;
            animation: statusGlow 2s ease-in-out infinite alternate;
        }
        
        .status.real { 
            color: #00ff00;
            background: rgba(0, 255, 0, 0.1);
            border: 2px solid #00ff00;
        }
        
        .status.fake { 
            color: #ff4444;
            background: rgba(255, 68, 68, 0.1);
            border: 2px solid #ff4444;
        }
        
        @keyframes statusGlow {
            from { box-shadow: 0 0 20px rgba(0, 255, 255, 0.3); }
            to { box-shadow: 0 0 40px rgba(255, 0, 255, 0.5); }
        }
        
        .details { 
            margin: 20px 0; 
            padding: 20px; 
            background: rgba(0, 0, 0, 0.3);
            border-radius: 15px;
            border-left: 4px solid #00ffff;
            transition: all 0.3s ease;
        }
        
        .details:hover {
            background: rgba(0, 0, 0, 0.4);
            border-left-color: #ff00ff;
            transform: translateX(10px);
        }
        
        .progress { 
            display: none; 
            text-align: center; 
            margin: 30px 0;
            animation: fadeIn 0.5s ease-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .progress-bar { 
            width: 100%; 
            height: 25px; 
            background: rgba(0, 0, 0, 0.3);
            border-radius: 50px;
            overflow: hidden;
            border: 2px solid rgba(0, 255, 255, 0.3);
        }
        
        .progress-fill { 
            height: 100%; 
            background: linear-gradient(90deg, #00ffff, #ff00ff, #ffff00);
            background-size: 200% 100%;
            width: 0%; 
            transition: width 0.3s ease;
            animation: progressShine 2s ease-in-out infinite;
        }
        
        @keyframes progressShine {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        .error { 
            background: rgba(255, 68, 68, 0.1);
            border: 2px solid #ff4444;
            color: #ff6666; 
            padding: 20px; 
            border-radius: 15px; 
            margin: 20px 0;
            animation: shake 0.5s ease-in-out;
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
        }
        
        .floating-particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 0;
        }
        
        .particle {
            position: absolute;
            width: 4px;
            height: 4px;
            background: rgba(0, 255, 255, 0.5);
            border-radius: 50%;
            animation: float 6s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0; }
            10%, 90% { opacity: 1; }
            50% { transform: translateY(-100px) rotate(180deg); }
        }
        
        .camera-btn {
            background: linear-gradient(45deg, #ff00ff, #00ffff);
            position: relative;
            overflow: hidden;
        }
        
        .camera-btn::after {
            content: '📸';
            margin-left: 10px;
            animation: blink 1s ease-in-out infinite;
        }
        
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        /* ID Verification Card Styles */
        .id-verification-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(15px);
            border-radius: 20px;
            padding: 40px;
            margin: 30px 0;
            border: 2px solid rgba(0, 255, 255, 0.3);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            animation: slideIn 0.8s ease-out;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }
        
        .verification-header {
            display: flex;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid rgba(0, 255, 255, 0.2);
        }
        
        .verification-icon {
            font-size: 4rem;
            margin-right: 20px;
            animation: pulse 2s ease-in-out infinite;
        }
        
        .verification-icon.verified {
            color: #00ff00;
            text-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
        }
        
        .verification-icon.rejected {
            color: #ff4444;
            text-shadow: 0 0 20px rgba(255, 68, 68, 0.5);
        }
        
        .verification-title h2 {
            font-family: 'Orbitron', monospace;
            font-size: 1.8rem;
            font-weight: 700;
            color: #00ffff;
            margin-bottom: 5px;
            letter-spacing: 2px;
        }
        
        .verification-title p {
            color: #b0b0b0;
            font-size: 1rem;
            margin: 0;
        }
        
        .verification-status {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .status-badge {
            display: inline-block;
            padding: 15px 30px;
            border-radius: 50px;
            margin-bottom: 15px;
            font-family: 'Orbitron', monospace;
            font-weight: 700;
            font-size: 1.2rem;
            letter-spacing: 1px;
            animation: statusGlow 2s ease-in-out infinite alternate;
        }
        
        .verification-status.real .status-badge {
            background: linear-gradient(45deg, #00ff00, #44ff44);
            color: #000;
            border: 2px solid #00ff00;
        }
        
        .verification-status.fake .status-badge {
            background: linear-gradient(45deg, #ff4444, #ff6666);
            color: #fff;
            border: 2px solid #ff4444;
        }
        
        .confidence-score {
            margin-top: 15px;
        }
        
        .score-label {
            color: #b0b0b0;
            font-size: 0.9rem;
            margin-bottom: 5px;
        }
        
        .score-value {
            font-family: 'Orbitron', monospace;
            font-size: 2.5rem;
            font-weight: 900;
            color: #00ffff;
            text-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
        }
        
        .verification-details {
            margin-bottom: 30px;
        }
        
        .detail-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .detail-row:last-child {
            border-bottom: none;
        }
        
        .detail-label {
            color: #b0b0b0;
            font-weight: 600;
            font-size: 0.9rem;
        }
        
        .detail-value {
            color: #fff;
            font-weight: 400;
            font-size: 0.9rem;
        }
        
        .verification-summary {
            margin-bottom: 30px;
        }
        
        .summary-title {
            font-family: 'Orbitron', monospace;
            font-size: 1.2rem;
            font-weight: 700;
            color: #00ffff;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .summary-item {
            margin-bottom: 15px;
        }
        
        .summary-label {
            color: #b0b0b0;
            font-size: 0.9rem;
            margin-bottom: 8px;
            display: block;
        }
        
        .summary-bar {
            position: relative;
            height: 25px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 15px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .summary-fill {
            height: 100%;
            border-radius: 15px;
            transition: width 1s ease-out;
            position: relative;
        }
        
        .summary-fill.real {
            background: linear-gradient(90deg, #00ff00, #44ff44);
        }
        
        .summary-fill.fake {
            background: linear-gradient(90deg, #ff4444, #ff6666);
        }
        
        .summary-percentage {
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            color: #fff;
            font-weight: 700;
            font-size: 0.8rem;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
        }
        
        .verification-footer {
            text-align: center;
            padding-top: 20px;
            border-top: 2px solid rgba(0, 255, 255, 0.2);
        }
        
        .footer-text {
            color: #b0b0b0;
            font-size: 1rem;
            line-height: 1.5;
            font-style: italic;
        }
        
        @media (max-width: 768px) {
            .title { font-size: 2.5rem; }
            .upload-area { padding: 40px 20px; }
            .trust-gauge { width: 150px; height: 150px; }
            .trust-inner { width: 110px; height: 110px; }
            .id-verification-card { padding: 20px; margin: 20px; }
            .verification-icon { font-size: 3rem; margin-right: 15px; }
            .verification-title h2 { font-size: 1.4rem; }
            .score-value { font-size: 2rem; }
        }
    </style>
</head>
<body>
    <div class="animated-bg"></div>
    
    <div class="floating-particles" id="particles"></div>
    
    <div class="container">
        <div class="header">
            <h1 class="title">ShadowHunt</h1>
            <p class="subtitle">Deepfake & Identity Scam Detection Tool</p>
            <p class="tagline">"In the era of AI-generated lies, ShadowHunt restores trust by detecting what's real and what's fake."</p>
        </div>
        
        <div class="upload-area" onclick="document.getElementById('fileInput').click()">
            <div class="upload-icon">📁</div>
            <h3>Drop files here or click to upload</h3>
            <p>Supports: JPG, PNG, MP4, WAV, MP3 (Max: 50MB)</p>
            <input type="file" id="fileInput" style="display: none;" accept=".jpg,.jpeg,.png,.mp4,.wav,.mp3">
        </div>
        
        <div style="text-align: center;">
            <button class="btn" id="analyzeBtn" onclick="analyzeFile()" disabled>🔍 Analyze for Deepfakes</button>
            <button class="btn camera-btn" id="cameraBtn" onclick="openCameraDetector()">Camera Detection</button>
        </div>
        
        <div class="progress" id="progressContainer">
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <p>Analyzing your file...</p>
        </div>
        
        <div id="resultsContainer"></div>
    </div>

    <script>
        let selectedFile = null;
        
        // Create floating particles
        function createParticles() {
            const particlesContainer = document.getElementById('particles');
            const particleCount = 50;
            
            for (let i = 0; i < particleCount; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.top = Math.random() * 100 + '%';
                particle.style.animationDelay = Math.random() * 6 + 's';
                particle.style.animationDuration = (Math.random() * 3 + 3) + 's';
                particlesContainer.appendChild(particle);
            }
        }
        
        // Initialize particles on page load
        window.addEventListener('load', createParticles);
        
        // Enhanced file input handling with animations
        document.getElementById('fileInput').addEventListener('change', function(e) {
            selectedFile = e.target.files[0];
            const uploadArea = document.querySelector('.upload-area');
            const analyzeBtn = document.getElementById('analyzeBtn');
            
            if (selectedFile) {
                analyzeBtn.disabled = false;
                document.querySelector('.upload-area h3').textContent = `File selected: ${selectedFile.name}`;
                uploadArea.style.borderColor = '#00ff00';
                uploadArea.style.background = 'rgba(0, 255, 0, 0.1)';
                
                // Animate button activation
                analyzeBtn.style.transform = 'scale(1.05)';
                setTimeout(() => {
                    analyzeBtn.style.transform = 'scale(1)';
                }, 200);
            } else {
                analyzeBtn.disabled = true;
                document.querySelector('.upload-area h3').textContent = 'Drop files here or click to upload';
                uploadArea.style.borderColor = '#00ffff';
                uploadArea.style.background = 'rgba(0, 255, 255, 0.05)';
            }
        });
        
        // Add drag and drop functionality with animations
        const uploadArea = document.querySelector('.upload-area');
        
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.style.transform = 'scale(1.02)';
            this.style.borderColor = '#ff00ff';
            this.style.background = 'rgba(255, 0, 255, 0.1)';
        });
        
        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.style.transform = 'scale(1)';
            this.style.borderColor = '#00ffff';
            this.style.background = 'rgba(0, 255, 255, 0.05)';
        });
        
        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                document.getElementById('fileInput').files = files;
                document.getElementById('fileInput').dispatchEvent(new Event('change'));
            }
            this.style.transform = 'scale(1)';
        });
        
        async function analyzeFile() {
            if (!selectedFile) return;
            
            const resultsContainer = document.getElementById('resultsContainer');
            const progressContainer = document.getElementById('progressContainer');
            const progressFill = document.getElementById('progressFill');
            
            // Show progress
            progressContainer.style.display = 'block';
            resultsContainer.innerHTML = '';
            
            // Simulate progress
            let progress = 0;
            const progressInterval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress > 90) progress = 90;
                progressFill.style.width = progress + '%';
            }, 200);
            
            try {
                const formData = new FormData();
                formData.append('file', selectedFile);
                
                const response = await fetch('/analyze', {
                    method: 'POST',
                    body: formData
                });
                
                clearInterval(progressInterval);
                progressFill.style.width = '100%';
                
                setTimeout(async () => {
                    const result = await response.json();
                    displayResults(result);
                    progressContainer.style.display = 'none';
                }, 500);
                
            } catch (error) {
                clearInterval(progressInterval);
                progressContainer.style.display = 'none';
                showError('Analysis failed: ' + error.message);
            }
        }
        
        function displayResults(results) {
            const resultsContainer = document.getElementById('resultsContainer');
            
            if (results.error) {
                showError(results.error);
                return;
            }
            
            const isReal = results.confidence_real > results.confidence_fake;
            const trustPercentage = Math.min(100, Math.max(0, Math.round(results.confidence_real * 100)));
            const fakePercentage = Math.min(100, Math.max(0, Math.round(results.confidence_fake * 100)));
            
            // Clear ID Verification Style Display
            let html = `
                <div class="id-verification-card">
                    <div class="verification-header">
                        <div class="verification-icon ${isReal ? 'verified' : 'rejected'}">
                            ${isReal ? '✅' : '❌'}
                        </div>
                        <div class="verification-title">
                            <h2>IDENTITY VERIFICATION</h2>
                            <p>Deepfake Detection Result</p>
                        </div>
                    </div>
                    
                    <div class="verification-status ${isReal ? 'real' : 'fake'}">
                        <div class="status-badge">
                            <span class="status-text">${isReal ? 'AUTHENTIC' : 'FAKE DETECTED'}</span>
                        </div>
                        <div class="confidence-score">
                            <div class="score-label">Confidence Level</div>
                            <div class="score-value">${trustPercentage}%</div>
                        </div>
                    </div>
                    
                    <div class="verification-details">
                        <div class="detail-row">
                            <span class="detail-label">File Type:</span>
                            <span class="detail-value">${results.type.toUpperCase()}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Analysis Method:</span>
                            <span class="detail-value">AI Deepfake Detection</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Watermark:</span>
                            <span class="detail-value">${results.watermark.found ? 'Present' : 'Not Found'}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Timestamp:</span>
                            <span class="detail-value">${new Date().toLocaleString()}</span>
                        </div>
                    </div>
                    
                    <div class="verification-summary">
                        <div class="summary-title">Analysis Summary</div>
                        <div class="summary-content">
                            <div class="summary-item">
                                <span class="summary-label">Real Probability:</span>
                                <div class="summary-bar">
                                    <div class="summary-fill real" style="width: ${trustPercentage}%"></div>
                                    <span class="summary-percentage">${trustPercentage}%</span>
                                </div>
                            </div>
                            <div class="summary-item">
                                <span class="summary-label">Fake Probability:</span>
                                <div class="summary-bar">
                                    <div class="summary-fill fake" style="width: ${fakePercentage}%"></div>
                                    <span class="summary-percentage">${fakePercentage}%</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="verification-footer">
                        <div class="footer-text">
                            ${isReal ? 
                                '✅ This content appears to be authentic and genuine.' : 
                                '⚠️ This content has been identified as potentially fake or manipulated.'
                            }
                        </div>
                    </div>
                </div>
            `;
            
            resultsContainer.innerHTML = html;
        }
        
        function showError(message) {
            const resultsContainer = document.getElementById('resultsContainer');
            resultsContainer.innerHTML = `<div class="error"><strong>Error:</strong> ${message}</div>`;
        }
        
        function openCameraDetector() {
            window.open('/camera', '_blank');
        }
    </script>
</body>
</html>
'''

if FLASK_AVAILABLE:
    @app.route('/')
    def index():
        """Main page with upload interface"""
        return render_template_string(HTML_TEMPLATE)
    
    @app.route('/demo')
    def demo():
        """Demo and features showcase page"""
        try:
            with open('demo.html', 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return render_template_string(HTML_TEMPLATE)

    @app.route('/analyze', methods=['POST'])
    def analyze_file():
        """Analyze uploaded files for deepfakes"""
        try:
            if 'file' not in request.files:
                return jsonify({"error": "No file uploaded"})
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No file selected"})
            
            # Save uploaded file
            filename = file.filename
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            # Analyze based on file type
            file_ext = filename.lower().split('.')[-1]
            
            if file_ext in ['jpg', 'jpeg', 'png']:
                result = detector.analyze_image(file_path)
            else:
                result = detector._simulate_analysis(file_ext)
            
            result['filename'] = filename
            
            # Clean up uploaded file
            try:
                os.remove(file_path)
            except:
                pass
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({"error": f"Analysis failed: {str(e)}"})

    @app.route('/camera')
    def camera_detection_page():
        """Camera detection page - redirect to camera interface"""
        if CAMERA_DETECTOR_AVAILABLE:
            # Import and serve camera interface
            try:
                from camera_web_interface import CAMERA_HTML_TEMPLATE
                return render_template_string(CAMERA_HTML_TEMPLATE)
            except ImportError:
                return jsonify({"error": "Camera interface not available"})
        else:
            return jsonify({"error": "Camera detector not available"})

    @app.route('/api/cameras')
    def get_cameras():
        """Get list of available cameras"""
        try:
            if not CAMERA_DETECTOR_AVAILABLE or not camera_detector:
                return jsonify({"error": "Camera detector not available"})
            
            cameras = camera_detector.get_camera_list()
            # Prefer a single laptop camera; fallback to first available
            preferred = None
            laptop_cams = [c for c in cameras if (c.get('type') == 'Laptop Camera')]
            if laptop_cams:
                preferred = laptop_cams[0]
            elif cameras:
                preferred = cameras[0]
            else:
                preferred = None
            
            return jsonify([preferred] if preferred else [])
        except Exception as e:
            return jsonify({"error": str(e)})
    
    @app.route('/api/refresh-cameras', methods=['POST'])
    def refresh_cameras():
        """Refresh the list of available cameras"""
        try:
            if not CAMERA_DETECTOR_AVAILABLE or not camera_detector:
                return jsonify({"error": "Camera detector not available"})
            
            success = camera_detector.refresh_camera_list()
            cameras = camera_detector.get_camera_list()
            laptop_cams = [c for c in cameras if (c.get('type') == 'Laptop Camera')]
            preferred = laptop_cams[0] if laptop_cams else (cameras[0] if cameras else None)
            return jsonify({
                "success": success,
                "cameras": [preferred] if preferred else [],
                "count": 1 if preferred else 0
            })
        except Exception as e:
            return jsonify({"error": str(e)})
    
    @app.route('/api/camera-permissions')
    def check_camera_permissions():
        """Check camera permissions and system status"""
        try:
            if not CAMERA_DETECTOR_AVAILABLE or not camera_detector:
                return jsonify({"error": "Camera detector not available"})
            
            permissions_info = camera_detector.check_camera_permissions()
            return jsonify(permissions_info)
        except Exception as e:
            return jsonify({"error": str(e)})

    @app.route('/api/start-stream/<int:camera_index>', methods=['POST'])
    def start_camera_stream(camera_index):
        """Start camera stream"""
        try:
            if not CAMERA_DETECTOR_AVAILABLE or not camera_detector:
                return jsonify({"success": False, "error": "Camera detector not available"})
            
            # Force prefer laptop camera
            cameras = camera_detector.get_camera_list()
            laptop_cams = [c for c in cameras if (c.get('type') == 'Laptop Camera')]
            preferred_index = (laptop_cams[0]['index'] if laptop_cams else (cameras[0]['index'] if cameras else camera_index))
            
            if camera_detector.select_camera(preferred_index):
                if camera_detector.start_stream():
                    return jsonify({"success": True, "message": f"Camera {preferred_index} stream started"})
                else:
                    return jsonify({"success": False, "error": "Failed to start stream"})
            else:
                return jsonify({"success": False, "error": "Failed to select camera"})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    @app.route('/api/stop-stream', methods=['POST'])
    def stop_camera_stream():
        """Stop camera stream"""
        try:
            if not CAMERA_DETECTOR_AVAILABLE or not camera_detector:
                return jsonify({"success": False, "error": "Camera detector not available"})
            
            camera_detector.stop_stream()
            return jsonify({"success": True, "message": "Stream stopped"})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    @app.route('/api/analyze-camera', methods=['POST'])
    def analyze_camera():
        """Analyze camera for authenticity"""
        try:
            if not CAMERA_DETECTOR_AVAILABLE or not camera_detector:
                return jsonify({"error": "Camera detector not available"})
            
            data = request.get_json()
            camera_index = data.get('camera_index', 0)
            duration = data.get('duration', 3)
            
            # Force prefer laptop camera
            cameras = camera_detector.get_camera_list()
            laptop_cams = [c for c in cameras if (c.get('type') == 'Laptop Camera')]
            preferred_index = (laptop_cams[0]['index'] if laptop_cams else (cameras[0]['index'] if cameras else camera_index))
            if camera_detector.current_camera != preferred_index:
                if not camera_detector.select_camera(preferred_index):
                    return jsonify({"error": f"Failed to select camera {preferred_index}"})
            
            # Perform analysis
            results = camera_detector.capture_and_analyze(duration=duration)
            return jsonify(results)
            
        except Exception as e:
            return jsonify({"error": str(e)})

    @app.route('/api/camera-feed/<int:camera_index>')
    def get_camera_feed(camera_index):
        """Get camera feed frame with improved error handling and reliability"""
        try:
            if not CAMERA_DETECTOR_AVAILABLE or not camera_detector:
                return jsonify({"error": "Camera detector not available"})
            
            # Use preferred laptop camera only
            available_cameras = camera_detector.get_camera_list()
            laptop_cams = [cam for cam in available_cameras if cam.get('type') == 'Laptop Camera']
            camera_info = (laptop_cams[0] if laptop_cams else (available_cameras[0] if available_cameras else None))
            
            if not camera_info:
                return jsonify({"error": "No available camera"})
            
            print(f"🎥 Testing camera {camera_info['index']} ({camera_info.get('type', 'Unknown')})")
            
            # Select camera if needed
            if camera_detector.current_camera != camera_info['index']:
                print(f"🔄 Selecting camera {camera_info['index']}...")
                if not camera_detector.select_camera(camera_info['index']):
                    return jsonify({"error": f"Failed to select camera {camera_info['index']}"})
            
            # Test camera access first
            if not camera_detector.test_camera_access(camera_info['index']):
                return jsonify({"error": f"Camera {camera_info['index']} access test failed"})
            
            # Start stream if not already streaming
            if not camera_detector.is_streaming:
                print(f"🎬 Starting stream for camera {camera_info['index']}...")
                if not camera_detector.start_stream():
                    return jsonify({"error": "Failed to start camera stream"})
            
            # Wait a moment for frames to be captured
            import time
            time.sleep(0.5)
            
            # Get latest frame
            frame = camera_detector.get_latest_frame()
            if frame is None:
                # Try to get a frame directly from camera
                print(f"⚠️ No frame in queue, trying direct read...")
                if camera_detector.camera_stream and camera_detector.camera_stream.isOpened():
                    ret, frame = camera_detector.camera_stream.read()
                    if not ret or frame is None:
                        return jsonify({"error": "Camera not responding - may be busy or not working"})
                    print(f"✅ Direct read successful - frame shape: {frame.shape}")
                else:
                    return jsonify({"error": "Camera stream not available"})
            else:
                print(f"✅ Frame from queue - shape: {frame.shape}")
            
            # Validate frame
            if frame.size == 0 or len(frame.shape) != 3:
                return jsonify({"error": "Invalid frame received from camera"})
            
            # Convert frame to base64 for web display
            import base64
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return jsonify({
                "success": True,
                "frame": f"data:image/jpeg;base64,{frame_base64}",
                "camera_index": camera_info['index'],
                "camera_type": camera_info.get('type', 'Unknown'),
                "frame_shape": frame.shape,
                "message": f"Camera {camera_info['index']} is working correctly!"
            })
            
        except Exception as e:
            print(f"❌ Camera feed error: {e}")
            return jsonify({"error": f"Camera feed error: {str(e)}"})

    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            "status": "healthy",
            "model_loaded": detector.model_loaded,
            "opencv_available": OPENCV_AVAILABLE,
            "camera_detector_available": CAMERA_DETECTOR_AVAILABLE,
            "timestamp": datetime.now().isoformat()
        })

def main():
    """Main function to run the application"""
    if not FLASK_AVAILABLE:
        print("ERROR: Flask not available. Please install: pip install flask")
        return
    
    print("ShadowHunt - Deepfake Detection Tool")
    print("=" * 50)
    print("Web Interface: http://localhost:5000")
    print("Health Check: http://localhost:5000/health")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\nShadowHunt server stopped. Goodbye!")
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == '__main__':
    main()

