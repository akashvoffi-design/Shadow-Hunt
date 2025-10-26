#!/usr/bin/env python3
"""
ShadowHunt Camera Detector - Laptop Camera Access and Fake Detection
"""

import os
import sys
import json
import time
import cv2
import numpy as np
import hashlib
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import threading
import queue

class CameraDetector:
    """Advanced camera detector for laptop cameras with fake detection capabilities"""
    
    def __init__(self):
        self.available_cameras = []
        self.current_camera = None
        self.camera_stream = None
        self.is_streaming = False
        self.frame_queue = queue.Queue(maxsize=10)
        self.detection_results = {}
        self.face_database = {}  # Store known face encodings
        self.suspicious_patterns = []  # Track suspicious behavior patterns
        
        # Initialize camera detection
        self._detect_available_cameras()
        
        # Load face detection models
        self._load_face_models()
        
    def _set_prop_safely(self, cap, prop_name, value):
        """Set a VideoCapture property only if supported by current OpenCV build."""
        try:
            prop = getattr(cv2, prop_name, None)
            if prop is not None:
                try:
                    cap.set(prop, value)
                except Exception:
                    pass
        except Exception:
            pass

    def _detect_available_cameras(self):
        """Detect all available cameras on the system with improved laptop camera support"""
        self.available_cameras = []
        
        print("Scanning for available cameras...")
        print("Checking laptop cameras and external cameras...")
        
        # Test camera indices from 0 to 10 (increased range for laptop cameras)
        for i in range(11):
            camera_found = False
            
            # Try multiple backends for better laptop camera compatibility
            backends_to_try = [
                (cv2.CAP_ANY, "Auto-detect"),
                (cv2.CAP_DSHOW, "DirectShow"),
                (cv2.CAP_MSMF, "Media Foundation"),
                (cv2.CAP_V4L2, "Video4Linux2")
            ]
            
            for backend, backend_name in backends_to_try:
                try:
                    cap = cv2.VideoCapture(i, backend)
                    if cap.isOpened():
                        # Try to read multiple frames to confirm camera works reliably
                        frame_count = 0
                        successful_frames = 0
                        
                        for attempt in range(3):  # Try 3 times
                            ret, frame = cap.read()
                            frame_count += 1
                            if ret and frame is not None and frame.size > 0:
                                successful_frames += 1
                            time.sleep(0.1)  # Small delay between attempts
                        
                        # Camera is reliable if it can capture frames consistently
                        if successful_frames >= 2:  # At least 2 out of 3 attempts successful
                            # Get camera properties
                            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            fps = cap.get(cv2.CAP_PROP_FPS)
                            
                            # Validate camera properties
                            if width > 0 and height > 0:
                                # Determine camera type based on properties
                                camera_type = self._determine_camera_type(width, height, fps, i)
                                
                                camera_info = {
                                    'index': i,
                                    'width': width,
                                    'height': height,
                                    'fps': fps if fps > 0 else 30.0,
                                    'backend': cap.getBackendName(),
                                    'backend_type': backend_name,
                                    'name': f"{camera_type} {i}",
                                    'type': camera_type,
                                    'reliability': successful_frames / frame_count
                                }
                                
                                self.available_cameras.append(camera_info)
                                print(f"Found {camera_type} {i}: {width}x{height} @ {fps}fps ({cap.getBackendName()}) - Reliability: {camera_info['reliability']:.2f}")
                                camera_found = True
                                break
                    
                    cap.release()
                    time.sleep(0.2)  # Longer delay to prevent conflicts
                    
                except Exception as e:
                    print(f"Error testing camera {i} with {backend_name}: {e}")
                    if 'cap' in locals():
                        cap.release()
                    continue
            
            if not camera_found:
                # Try one more time with default backend and longer timeout
                try:
                    cap = cv2.VideoCapture(i)
                    if cap.isOpened():
                        # Set a longer timeout for laptop cameras (if supported)
                        self._set_prop_safely(cap, 'CAP_PROP_TIMEOUT', 5000)
                        
                        ret, frame = cap.read()
                        if ret and frame is not None and frame.size > 0:
                            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            fps = cap.get(cv2.CAP_PROP_FPS)
                            
                            if width > 0 and height > 0:
                                camera_type = self._determine_camera_type(width, height, fps, i)
                                
                                camera_info = {
                                    'index': i,
                                    'width': width,
                                    'height': height,
                                    'fps': fps if fps > 0 else 30.0,
                                    'backend': cap.getBackendName(),
                                    'backend_type': "Default",
                                    'name': f"{camera_type} {i} (Default)",
                                    'type': camera_type,
                                    'reliability': 0.8  # Assume good reliability
                                }
                                
                                self.available_cameras.append(camera_info)
                                print(f"Found {camera_type} {i}: {width}x{height} @ {fps}fps (Default Backend)")
                    
                    cap.release()
                    time.sleep(0.3)
                    
                except Exception as e:
                    print(f"Error testing camera {i} with default backend: {e}")
                    if 'cap' in locals():
                        cap.release()
        
        if not self.available_cameras:
            print("❌ No cameras found on this system")
            print("\n🔧 Troubleshooting steps:")
            print("1. Check if your laptop camera is enabled in Device Manager")
            print("2. Make sure no other applications are using the camera")
            print("3. Check camera permissions in Windows Settings > Privacy > Camera")
            print("4. Try running the application as administrator")
            print("5. Restart your computer to reset camera drivers")
            print("6. Update your camera drivers from the manufacturer's website")
        else:
            print(f"✅ Total cameras found: {len(self.available_cameras)}")
            laptop_cameras = [cam for cam in self.available_cameras if cam['type'] == 'Laptop Camera']
            external_cameras = [cam for cam in self.available_cameras if cam['type'] == 'External Camera']
            
            if laptop_cameras:
                print(f"   📱 Laptop cameras: {len(laptop_cameras)}")
            if external_cameras:
                print(f"   📷 External cameras: {len(external_cameras)}")
    
    def _determine_camera_type(self, width, height, fps, index):
        """Determine if camera is laptop camera or external camera"""
        # Laptop cameras typically have specific characteristics
        if index == 0:  # Index 0 is usually laptop camera
            return "Laptop Camera"
        elif width <= 1280 and height <= 720:  # Lower resolution often indicates laptop camera
            return "Laptop Camera"
        elif fps <= 30:  # Laptop cameras often have lower FPS
            return "Laptop Camera"
        else:
            return "External Camera"
    
    def _load_face_models(self):
        """Load face detection and recognition models"""
        try:
            # Load OpenCV face detection models
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            self.profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
            
            print("Face detection models loaded successfully")
        except Exception as e:
            print(f"Warning: Could not load face models: {e}")
            self.face_cascade = None
            self.eye_cascade = None
            self.profile_cascade = None
    
    def get_camera_list(self) -> List[Dict]:
        """Get list of available cameras"""
        # Prefer returning a single laptop camera if available, else first camera
        if not self.available_cameras:
            return []
        laptop_cams = [c for c in self.available_cameras if c.get('type') == 'Laptop Camera']
        if laptop_cams:
            return [laptop_cams[0]]
        return [self.available_cameras[0]]
    
    def refresh_camera_list(self) -> bool:
        """Refresh the list of available cameras"""
        try:
            print("Refreshing camera list...")
            
            # Stop any current stream to avoid conflicts
            if self.is_streaming:
                self.stop_stream()
            
            # Release current camera
            if self.camera_stream:
                self.camera_stream.release()
                self.camera_stream = None
                time.sleep(0.5)  # Wait for camera to be fully released
            
            self._detect_available_cameras()
            return len(self.available_cameras) > 0
        except Exception as e:
            print(f"Error refreshing camera list: {e}")
            return False
    
    def select_camera(self, camera_index: int) -> bool:
        """Select a specific camera for detection with improved laptop camera support"""
        try:
            # Only allow preferred (laptop) camera selection for simplicity
            preferred_list = self.get_camera_list()
            valid_cameras = [cam['index'] for cam in preferred_list]
            if camera_index not in valid_cameras:
                print(f"⚠️ Non-preferred camera requested ({camera_index}). Falling back to preferred laptop camera.")
                if not preferred_list:
                    return False
                camera_index = preferred_list[0]['index']
            
            # Get camera info
            camera_info = next((cam for cam in self.available_cameras if cam['index'] == camera_index), None)
            if not camera_info:
                print(f"❌ Camera {camera_index} information not found")
                return False
            
            print(f"🔍 Selecting {camera_info['type']} {camera_index}...")
            
            # Release current camera if open
            if self.camera_stream:
                self.camera_stream.release()
                self.camera_stream = None
                time.sleep(0.5)  # Longer wait for laptop cameras
            
            # Try to open camera with the backend that worked during detection
            backend_used = None
            success = False
            
            # Try the backend that was successful during detection
            if camera_info.get('backend_type') == 'DirectShow':
                backend_used = cv2.CAP_DSHOW
            elif camera_info.get('backend_type') == 'Media Foundation':
                backend_used = cv2.CAP_MSMF
            elif camera_info.get('backend_type') == 'Video4Linux2':
                backend_used = cv2.CAP_V4L2
            else:
                backend_used = cv2.CAP_ANY
            
            try:
                self.camera_stream = cv2.VideoCapture(camera_index, backend_used)
                if self.camera_stream.isOpened():
                    # Set timeout for laptop cameras (if supported)
                    self._set_prop_safely(self.camera_stream, 'CAP_PROP_TIMEOUT', 3000)
                    
                    # Test if we can read frames consistently
                    successful_reads = 0
                    for attempt in range(3):
                        ret, test_frame = self.camera_stream.read()
                        if ret and test_frame is not None and test_frame.size > 0:
                            successful_reads += 1
                        time.sleep(0.1)
                    
                    if successful_reads >= 2:  # At least 2 successful reads
                        print(f"✅ Successfully opened {camera_info['type']} {camera_index} with {camera_info.get('backend_type', 'Default')} backend")
                        success = True
                    else:
                        print(f"❌ {camera_info['type']} {camera_index} opened but cannot read frames consistently")
                        self.camera_stream.release()
                        self.camera_stream = None
                else:
                    print(f"❌ Failed to open {camera_info['type']} {camera_index}")
                    
            except Exception as e:
                print(f"❌ Error opening {camera_info['type']} {camera_index}: {e}")
                if self.camera_stream:
                    self.camera_stream.release()
                    self.camera_stream = None
            
            # If the preferred backend failed, try default backend
            if not success:
                try:
                    print(f"🔄 Trying default backend for {camera_info['type']} {camera_index}...")
                    self.camera_stream = cv2.VideoCapture(camera_index)
                    if self.camera_stream.isOpened():
                        self.camera_stream.set(cv2.CAP_PROP_TIMEOUT, 5000)  # 5 second timeout
                        
                        ret, test_frame = self.camera_stream.read()
                        if ret and test_frame is not None and test_frame.size > 0:
                            print(f"✅ Successfully opened {camera_info['type']} {camera_index} with default backend")
                            success = True
                        else:
                            print(f"❌ {camera_info['type']} {camera_index} opened with default backend but cannot read frames")
                            self.camera_stream.release()
                            self.camera_stream = None
                    else:
                        print(f"❌ Failed to open {camera_info['type']} {camera_index} with default backend")
                        
                except Exception as e:
                    print(f"❌ Error opening {camera_info['type']} {camera_index} with default backend: {e}")
                    if self.camera_stream:
                        self.camera_stream.release()
                        self.camera_stream = None
            
            if not success:
                return False
            
            # Set camera properties optimized for laptop cameras
            try:
                # Get current properties
                current_width = int(self.camera_stream.get(cv2.CAP_PROP_FRAME_WIDTH))
                current_height = int(self.camera_stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
                current_fps = self.camera_stream.get(cv2.CAP_PROP_FPS)
                
                print(f"📊 Camera properties: {current_width}x{current_height} @ {current_fps}fps")
                
                # Set optimized properties for laptop cameras
                if camera_info['type'] == 'Laptop Camera':
                    # Laptop cameras work better with their native resolution
                    self.camera_stream.set(cv2.CAP_PROP_FRAME_WIDTH, min(640, current_width))
                    self.camera_stream.set(cv2.CAP_PROP_FRAME_HEIGHT, min(480, current_height))
                    self.camera_stream.set(cv2.CAP_PROP_FPS, min(30, current_fps if current_fps > 0 else 30))
                else:
                    # External cameras can handle higher settings
                    self.camera_stream.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    self.camera_stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    self.camera_stream.set(cv2.CAP_PROP_FPS, 30)
                
                # Set buffer size to reduce latency
                self.camera_stream.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
                # Set auto exposure for laptop cameras
                if camera_info['type'] == 'Laptop Camera':
                    self.camera_stream.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)  # Auto exposure
                
                print(f"✅ {camera_info['type']} {camera_index} properties optimized successfully")
                
            except Exception as e:
                print(f"⚠️ Warning: Could not set all camera properties: {e}")
            
            self.current_camera = camera_index
            print(f"🎯 {camera_info['type']} {camera_index} selected and ready!")
            return True
            
        except Exception as e:
            print(f"❌ Error selecting camera {camera_index}: {e}")
            return False
    
    def start_stream(self) -> bool:
        """Start camera streaming for real-time detection with improved reliability"""
        if not self.camera_stream or not self.camera_stream.isOpened():
            print("❌ No camera selected or camera not opened")
            return False
        
        # Test camera before starting stream
        ret, test_frame = self.camera_stream.read()
        if not ret or test_frame is None:
            print("❌ Camera test failed - cannot read frames")
            return False
        
        print(f"✅ Camera test passed - frame size: {test_frame.shape}")
        
        self.is_streaming = True
        self.frame_queue.queue.clear()
        
        # Start frame capture thread
        self.capture_thread = threading.Thread(target=self._capture_frames, daemon=True)
        self.capture_thread.start()
        
        # Wait a moment to ensure thread started
        time.sleep(0.5)
        
        print("🎥 Camera stream started successfully")
        return True
    
    def stop_stream(self):
        """Stop camera streaming"""
        self.is_streaming = False
        
        if hasattr(self, 'capture_thread'):
            self.capture_thread.join(timeout=2)
        
        if self.camera_stream:
            self.camera_stream.release()
        
        print("Camera stream stopped")
    
    def _capture_frames(self):
        """Capture frames in separate thread with improved error handling and reliability"""
        consecutive_failures = 0
        max_failures = 5  # Reduced for faster failure detection
        frame_count = 0
        
        print("🎬 Frame capture thread started")
        
        while self.is_streaming and self.camera_stream:
            try:
                # Check if camera is still opened
                if not self.camera_stream.isOpened():
                    print("⚠️ Camera stream lost, attempting to reconnect...")
                    consecutive_failures += 1
                    
                    if self.current_camera is not None and consecutive_failures < 3:
                        time.sleep(1)  # Wait before reconnecting
                        if self.select_camera(self.current_camera):
                            print("✅ Camera reconnected successfully")
                            consecutive_failures = 0
                            continue
                        else:
                            print("❌ Failed to reconnect camera")
                            break
                    else:
                        print("❌ Too many reconnection attempts, stopping stream")
                        break
                
                # Read frame from camera
                ret, frame = self.camera_stream.read()
                
                if ret and frame is not None and frame.size > 0:
                    # Validate frame quality
                    if frame.shape[0] > 0 and frame.shape[1] > 0:
                        try:
                            # Put frame in queue (non-blocking)
                            self.frame_queue.put_nowait(frame.copy())
                            consecutive_failures = 0
                            frame_count += 1
                            
                            # Log progress every 30 frames
                            if frame_count % 30 == 0:
                                print(f"📹 Captured {frame_count} frames successfully")
                        except queue.Full:
                            # Remove oldest frame if queue is full
                            try:
                                self.frame_queue.get_nowait()
                                self.frame_queue.put_nowait(frame.copy())
                                consecutive_failures = 0
                                frame_count += 1
                            except queue.Empty:
                                pass
                    else:
                        consecutive_failures += 1
                        print(f"⚠️ Invalid frame dimensions: {frame.shape}")
                else:
                    consecutive_failures += 1
                    print(f"⚠️ Failed to read frame (attempt {consecutive_failures})")
                
                # Stop if too many failures
                if consecutive_failures >= max_failures:
                    print(f"❌ Too many consecutive failures ({consecutive_failures}), stopping stream")
                    break
                
                # Control frame rate (30 FPS)
                time.sleep(0.033)  # ~30 FPS
                    
            except Exception as e:
                consecutive_failures += 1
                print(f"❌ Error capturing frame: {e}")
                if consecutive_failures >= max_failures:
                    print(f"❌ Too many consecutive errors, stopping capture")
                    break
                time.sleep(0.1)
        
        print(f"🛑 Frame capture thread stopped (captured {frame_count} frames)")
        self.is_streaming = False
    
    def get_latest_frame(self) -> Optional[np.ndarray]:
        """Get the latest frame from camera with improved reliability"""
        try:
            if not self.is_streaming or self.frame_queue.empty():
                return None
            
            frame = self.frame_queue.get_nowait()
            
            # Validate frame
            if frame is not None and frame.size > 0 and len(frame.shape) == 3:
                return frame
            else:
                print("⚠️ Invalid frame received")
                return None
                
        except queue.Empty:
            return None
        except Exception as e:
            print(f"❌ Error getting frame: {e}")
            return None
    
    def analyze_camera_authenticity(self, frame: np.ndarray) -> Dict:
        """Analyze camera frame for authenticity indicators"""
        if frame is None:
            return {"error": "No frame available"}
        
        analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "frame_shape": frame.shape,
            "authenticity_score": 0.0,
            "is_fake": False,
            "confidence": 0.0,
            "detection_methods": {}
        }
        
        try:
            # Document-like heuristic: treat flat ID documents as valid real content source
            try:
                from shadowhunt_working import SimpleDeepfakeDetector
                temp_detector = SimpleDeepfakeDetector()
                doc_info = temp_detector._detect_document_like(frame)
                # AI artifact score (acts like a CNN feature check proxy)
                ai_artifact_score = temp_detector._detect_ai_artifacts(frame)
            except Exception:
                doc_info = {"is_document": False}
                ai_artifact_score = 0.5
            
            # Method 1: Frame Consistency Analysis
            consistency_score = self._analyze_frame_consistency(frame)
            analysis_results["detection_methods"]["frame_consistency"] = consistency_score
            
            # Method 2: Hardware Fingerprint Analysis
            hardware_score = self._analyze_hardware_fingerprint(frame)
            analysis_results["detection_methods"]["hardware_fingerprint"] = hardware_score
            
            # Method 3: Temporal Analysis (if multiple frames available)
            temporal_score = self._analyze_temporal_patterns(frame)
            analysis_results["detection_methods"]["temporal_analysis"] = temporal_score
            
            # Method 4: Image Quality Analysis
            quality_score = self._analyze_image_quality(frame)
            analysis_results["detection_methods"]["image_quality"] = quality_score
            
            # Method 5: Fake Camera Detection
            fake_detection_score = self._detect_fake_camera_signs(frame)
            analysis_results["detection_methods"]["fake_camera_detection"] = fake_detection_score
            
            # Method 6: Identity Verification
            identity_score = self._verify_identity_authenticity(frame)
            analysis_results["detection_methods"]["identity_verification"] = identity_score
            
            # Method 7: Duplicate Detection
            duplicate_score = self._detect_duplicate_identity(frame)
            analysis_results["detection_methods"]["duplicate_detection"] = duplicate_score

            # Method 8: AI Artifact Analysis (CNN-like proxy)
            analysis_results["detection_methods"]["ai_artifacts"] = {"score": ai_artifact_score}
            
            # Calculate overall authenticity score
            scores = [
                consistency_score["score"],
                hardware_score["score"],
                temporal_score["score"],
                quality_score["score"],
                fake_detection_score["score"],
                identity_score["score"],
                duplicate_score["score"],
                ai_artifact_score  # higher means more likely real
            ]
            
            authenticity_score = float(np.mean(scores))
            # If document-like, give a small positive bias
            if doc_info.get("is_document"):
                authenticity_score = min(1.0, authenticity_score + 0.15)
            analysis_results["authenticity_score"] = round(authenticity_score, 3)
            analysis_results["is_fake"] = authenticity_score < 0.5
            analysis_results["confidence"] = float(abs(authenticity_score - 0.5) * 2)
            
            # Determine status
            if authenticity_score > 0.7:
                analysis_results["status"] = "Likely Real Camera"
            elif authenticity_score < 0.3:
                analysis_results["status"] = "Likely Fake/Virtual Camera"
            else:
                analysis_results["status"] = "Uncertain - Requires More Analysis"
                
        except Exception as e:
            analysis_results["error"] = f"Analysis failed: {str(e)}"
        
        return analysis_results
    
    def _analyze_frame_consistency(self, frame: np.ndarray) -> Dict:
        """Analyze frame consistency for real camera indicators"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate frame statistics
            mean_intensity = np.mean(gray)
            std_intensity = np.std(gray)
            variance = np.var(gray)
            
            # Real cameras typically have natural variance
            # Virtual cameras often have too consistent or too random patterns
            if 20 < std_intensity < 80:
                consistency_score = 0.8
            elif 10 < std_intensity < 100:
                consistency_score = 0.6
            else:
                consistency_score = 0.3
            
            return {
                "score": consistency_score,
                "mean_intensity": round(mean_intensity, 2),
                "std_intensity": round(std_intensity, 2),
                "variance": round(variance, 2),
                "reasoning": "Natural variance indicates real camera"
            }
            
        except Exception as e:
            return {"score": 0.0, "error": str(e)}
    
    def _analyze_hardware_fingerprint(self, frame: np.ndarray) -> Dict:
        """Analyze hardware fingerprint patterns"""
        try:
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Analyze color distribution
            hist_h = cv2.calcHist([hsv], [0], None, [180], [0, 180])
            hist_s = cv2.calcHist([hsv], [1], None, [256], [0, 256])
            hist_v = cv2.calcHist([hsv], [2], None, [256], [0, 256])
            
            # Calculate entropy (measure of randomness)
            def calculate_entropy(hist):
                hist = hist.flatten()
                hist = hist[hist > 0]  # Remove zeros
                prob = hist / hist.sum()
                return -np.sum(prob * np.log2(prob))
            
            h_entropy = calculate_entropy(hist_h)
            s_entropy = calculate_entropy(hist_s)
            v_entropy = calculate_entropy(hist_v)
            
            # Real cameras have natural color distributions
            avg_entropy = (h_entropy + s_entropy + v_entropy) / 3
            
            if avg_entropy > 6.0:
                hardware_score = 0.9
            elif avg_entropy > 4.0:
                hardware_score = 0.7
            else:
                hardware_score = 0.3
            
            return {
                "score": hardware_score,
                "h_entropy": round(h_entropy, 2),
                "s_entropy": round(s_entropy, 2),
                "v_entropy": round(v_entropy, 2),
                "avg_entropy": round(avg_entropy, 2),
                "reasoning": "High entropy indicates natural color distribution"
            }
            
        except Exception as e:
            return {"score": 0.0, "error": str(e)}
    
    def _analyze_temporal_patterns(self, frame: np.ndarray) -> Dict:
        """Analyze temporal patterns (placeholder for multi-frame analysis)"""
        # This would ideally analyze multiple consecutive frames
        # For now, we'll use frame motion detection
        
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate edge density (real cameras have natural edges)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Real cameras have natural edge patterns
            if 0.05 < edge_density < 0.25:
                temporal_score = 0.8
            elif 0.02 < edge_density < 0.35:
                temporal_score = 0.6
            else:
                temporal_score = 0.4
            
            return {
                "score": temporal_score,
                "edge_density": round(edge_density, 4),
                "reasoning": "Natural edge patterns indicate real camera"
            }
            
        except Exception as e:
            return {"score": 0.0, "error": str(e)}
    
    def _analyze_image_quality(self, frame: np.ndarray) -> Dict:
        """Analyze image quality metrics"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate Laplacian variance (sharpness measure)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Calculate contrast
            contrast = gray.std()
            
            # Real cameras have natural quality variations
            if 100 < laplacian_var < 2000 and 20 < contrast < 80:
                quality_score = 0.9
            elif 50 < laplacian_var < 3000 and 15 < contrast < 100:
                quality_score = 0.7
            else:
                quality_score = 0.4
            
            return {
                "score": quality_score,
                "laplacian_variance": round(laplacian_var, 2),
                "contrast": round(contrast, 2),
                "reasoning": "Natural quality metrics indicate real camera"
            }
            
        except Exception as e:
            return {"score": 0.0, "error": str(e)}
    
    def _detect_fake_camera_signs(self, frame: np.ndarray) -> Dict:
        """Detect specific signs of fake/virtual cameras"""
        try:
            fake_indicators = 0
            total_checks = 5
            
            # Check 1: Perfect rectangular regions (common in virtual cameras)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            perfect_rectangles = 0
            for contour in contours:
                approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
                if len(approx) == 4:  # Rectangle
                    perfect_rectangles += 1
            
            if perfect_rectangles > 10:  # Too many perfect shapes
                fake_indicators += 1
            
            # Check 2: Uniform color regions (virtual cameras often have solid backgrounds)
            unique_colors = len(np.unique(gray.reshape(-1)))
            if unique_colors < 100:  # Too few colors
                fake_indicators += 1
            
            # Check 3: Edge patterns
            edges = cv2.Canny(gray, 50, 150)
            edge_clusters = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
            
            if len(edge_clusters) < 5:  # Too few edge clusters
                fake_indicators += 1
            
            # Check 4: Noise patterns
            noise = cv2.Laplacian(gray, cv2.CV_64F)
            noise_std = noise.std()
            
            if noise_std < 5 or noise_std > 50:  # Unnatural noise levels
                fake_indicators += 1
            
            # Check 5: Brightness distribution
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist_peaks = len(cv2.findContours(hist, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0])
            
            if hist_peaks < 3 or hist_peaks > 20:  # Unnatural brightness distribution
                fake_indicators += 1
            
            fake_score = 1.0 - (fake_indicators / total_checks)
            
            return {
                "score": fake_score,
                "fake_indicators": fake_indicators,
                "total_checks": total_checks,
                "perfect_rectangles": perfect_rectangles,
                "unique_colors": unique_colors,
                "edge_clusters": len(edge_clusters),
                "noise_std": round(noise_std, 2),
                "hist_peaks": hist_peaks,
                "reasoning": f"Found {fake_indicators}/{total_checks} fake camera indicators"
            }
            
        except Exception as e:
            return {"score": 0.0, "error": str(e)}
    
    def _verify_identity_authenticity(self, frame: np.ndarray) -> Dict:
        """Verify identity authenticity and detect fake identities"""
        try:
            if self.face_cascade is None:
                return {"score": 0.5, "error": "Face detection not available"}
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            identity_score = 0.0
            fake_indicators = 0
            
            for (x, y, w, h) in faces:
                # Extract face region
                face_roi = gray[y:y+h, x:x+w]
                
                # Check for multiple faces (potential duplicate)
                if len(faces) > 1:
                    fake_indicators += 1
                
                # Analyze facial features consistency
                eyes = self.eye_cascade.detectMultiScale(face_roi, 1.1, 3)
                if len(eyes) != 2:  # Should have exactly 2 eyes
                    fake_indicators += 1
                
                # Check for unnatural symmetry (deepfake indicator)
                left_half = face_roi[:, :w//2]
                right_half = cv2.flip(face_roi[:, w//2:], 1)
                
                # Resize to same dimensions for comparison
                min_width = min(left_half.shape[1], right_half.shape[1])
                left_half = cv2.resize(left_half, (min_width, left_half.shape[0]))
                right_half = cv2.resize(right_half, (min_width, right_half.shape[0]))
                
                # Calculate symmetry difference
                symmetry_diff = np.mean(np.abs(left_half.astype(float) - right_half.astype(float)))
                
                # Too perfect symmetry or too asymmetric indicates fake
                if symmetry_diff < 5 or symmetry_diff > 50:
                    fake_indicators += 1
                
                # Check for unnatural eye movements
                eye_centers = []
                for (ex, ey, ew, eh) in eyes:
                    eye_center = (ex + ew//2, ey + eh//2)
                    eye_centers.append(eye_center)
                
                if len(eye_centers) == 2:
                    eye_distance = np.sqrt((eye_centers[0][0] - eye_centers[1][0])**2 + 
                                         (eye_centers[0][1] - eye_centers[1][1])**2)
                    
                    # Unnatural eye distance indicates fake
                    expected_distance = w * 0.3  # Eyes should be ~30% of face width apart
                    if abs(eye_distance - expected_distance) > expected_distance * 0.5:
                        fake_indicators += 1
            
            # Calculate identity authenticity score
            if len(faces) == 0:
                identity_score = 0.3  # No face detected
            else:
                identity_score = max(0.1, 1.0 - (fake_indicators / max(1, len(faces) * 3)))
            
            return {
                "score": identity_score,
                "faces_detected": len(faces),
                "fake_indicators": fake_indicators,
                "eyes_detected": sum(len(self.eye_cascade.detectMultiScale(gray[y:y+h, x:x+w], 1.1, 3)) for (x, y, w, h) in faces),
                "reasoning": f"Found {fake_indicators} fake identity indicators in {len(faces)} face(s)"
            }
            
        except Exception as e:
            return {"score": 0.0, "error": str(e)}
    
    def _detect_duplicate_identity(self, frame: np.ndarray) -> Dict:
        """Detect duplicate identities and suspicious patterns"""
        try:
            if self.face_cascade is None:
                return {"score": 0.5, "error": "Face detection not available"}
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            duplicate_score = 0.8  # Default: likely not duplicate
            duplicate_indicators = 0
            
            # Check for multiple identical faces (duplicate detection)
            if len(faces) > 1:
                face_features = []
                for (x, y, w, h) in faces:
                    face_roi = gray[y:y+h, x:x+w]
                    # Simple feature extraction (histogram)
                    hist = cv2.calcHist([face_roi], [0], None, [64], [0, 256])
                    face_features.append(hist.flatten())
                
                # Compare all face pairs for similarity
                for i in range(len(face_features)):
                    for j in range(i+1, len(face_features)):
                        # Calculate correlation between face features
                        correlation = np.corrcoef(face_features[i], face_features[j])[0, 1]
                        
                        # High correlation indicates potential duplicate
                        if correlation > 0.9:
                            duplicate_indicators += 1
                            duplicate_score = 0.2  # High duplicate probability
            
            # Check for known suspicious patterns
            current_time = time.time()
            
            # Add current frame info to suspicious patterns
            frame_info = {
                "timestamp": current_time,
                "face_count": len(faces),
                "frame_hash": hashlib.md5(frame.tobytes()).hexdigest()[:8]
            }
            
            self.suspicious_patterns.append(frame_info)
            
            # Keep only recent patterns (last 30 seconds)
            self.suspicious_patterns = [p for p in self.suspicious_patterns 
                                      if current_time - p["timestamp"] < 30]
            
            # Check for suspicious patterns
            if len(self.suspicious_patterns) > 10:  # Too many frames in short time
                duplicate_indicators += 1
            
            # Check for repeated identical frames (potential video loop)
            frame_hashes = [p["frame_hash"] for p in self.suspicious_patterns]
            if len(frame_hashes) != len(set(frame_hashes)):  # Duplicate hashes found
                duplicate_indicators += 2
                duplicate_score = 0.1  # Very high duplicate probability
            
            return {
                "score": duplicate_score,
                "faces_detected": len(faces),
                "duplicate_indicators": duplicate_indicators,
                "pattern_analysis": {
                    "recent_frames": len(self.suspicious_patterns),
                    "unique_frames": len(set(frame_hashes)),
                    "duplicate_frames": len(frame_hashes) - len(set(frame_hashes))
                },
                "reasoning": f"Found {duplicate_indicators} duplicate indicators"
            }
            
        except Exception as e:
            return {"score": 0.0, "error": str(e)}
    
    def capture_and_analyze(self, duration: int = 5) -> Dict:
        """Capture frames for specified duration and analyze"""
        if not self.is_streaming:
            if not self.start_stream():
                return {"error": "Failed to start camera stream"}
        
        print(f"Capturing frames for {duration} seconds...")
        
        frames_analyzed = 0
        results = []
        
        start_time = time.time()
        while time.time() - start_time < duration:
            frame = self.get_latest_frame()
            if frame is not None:
                analysis = self.analyze_camera_authenticity(frame)
                if "error" not in analysis:
                    # Convert numpy types to Python types for JSON serialization
                    analysis = self._convert_numpy_types(analysis)
                    results.append(analysis)
                    frames_analyzed += 1
                    print(f"Analyzed frame {frames_analyzed}")
            
            time.sleep(0.1)  # 10 FPS analysis
        
        if not results:
            return {"error": "No frames captured for analysis"}
        
        # Aggregate results - convert numpy types to Python types
        avg_authenticity = float(np.mean([r["authenticity_score"] for r in results]))
        avg_confidence = float(np.mean([r["confidence"] for r in results]))
        
        # Determine overall status
        fake_count = sum(1 for r in results if r["is_fake"])
        fake_percentage = float((fake_count / len(results)) * 100)
        
        if fake_percentage > 70:
            overall_status = "FAKE/VIRTUAL CAMERA DETECTED"
        elif fake_percentage < 30:
            overall_status = "REAL CAMERA CONFIRMED"
        else:
            overall_status = "UNCERTAIN - MIXED RESULTS"
        
        return {
            "analysis_summary": {
                "total_frames": frames_analyzed,
                "duration_seconds": duration,
                "avg_authenticity_score": round(avg_authenticity, 3),
                "avg_confidence": round(avg_confidence, 3),
                "fake_percentage": round(fake_percentage, 1),
                "overall_status": overall_status,
                "is_fake_camera": fake_percentage > 50
            },
            "detailed_results": results,
            "recommendation": self._generate_recommendation(avg_authenticity, fake_percentage)
        }
    
    def _convert_numpy_types(self, obj):
        """Convert numpy types to Python native types for JSON serialization"""
        import numpy as np
        
        if isinstance(obj, dict):
            return {key: self._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj
    
    def _generate_recommendation(self, authenticity_score: float, fake_percentage: float) -> str:
        """Generate recommendation based on analysis"""
        if fake_percentage > 70:
            return "HIGH RISK: This appears to be a fake/virtual camera. Avoid using for sensitive applications."
        elif fake_percentage < 30:
            return "SAFE: This appears to be a genuine camera. Safe for most applications."
        else:
            return "CAUTION: Results are inconclusive. Additional verification recommended."
    
    def test_camera_access(self, camera_index: int) -> bool:
        """Test if a camera can be accessed without conflicts"""
        try:
            # Create a temporary camera instance to test access
            test_cap = cv2.VideoCapture(camera_index)
            if test_cap.isOpened():
                # Set timeout for laptop cameras (if supported)
                self._set_prop_safely(test_cap, 'CAP_PROP_TIMEOUT', 3000)
                
                # Try to read multiple frames to test reliability
                successful_reads = 0
                for attempt in range(3):
                    ret, frame = test_cap.read()
                    if ret and frame is not None and frame.size > 0:
                        successful_reads += 1
                    time.sleep(0.1)
                
                test_cap.release()
                return successful_reads >= 2  # At least 2 successful reads
            else:
                test_cap.release()
                return False
        except Exception as e:
            print(f"Error testing camera {camera_index} access: {e}")
            return False
    
    def check_camera_permissions(self) -> dict:
        """Check camera permissions and system status"""
        try:
            import platform
            system_info = {
                'os': platform.system(),
                'os_version': platform.version(),
                'python_version': platform.python_version(),
                'opencv_version': cv2.__version__
            }
            
            # Test basic camera access
            test_cap = cv2.VideoCapture(0)
            basic_access = test_cap.isOpened()
            test_cap.release()
            
            return {
                'system_info': system_info,
                'basic_camera_access': basic_access,
                'available_cameras': len(self.available_cameras),
                'laptop_cameras': len([cam for cam in self.available_cameras if cam.get('type') == 'Laptop Camera']),
                'external_cameras': len([cam for cam in self.available_cameras if cam.get('type') == 'External Camera'])
            }
        except Exception as e:
            return {'error': str(e)}
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_stream()
        if self.camera_stream:
            self.camera_stream.release()

def main():
    """Main function for testing camera detector"""
    print("ShadowHunt Camera Detector")
    print("=" * 50)
    
    detector = CameraDetector()
    
    if not detector.available_cameras:
        print("No cameras found. Please check your camera connection.")
        return
    
    # Show available cameras
    print("\nAvailable Cameras:")
    for i, camera in enumerate(detector.available_cameras):
        print(f"  {i}: {camera['name']} ({camera['width']}x{camera['height']})")
    
    # Select first available camera
    camera_index = detector.available_cameras[0]['index']
    print(f"\nSelecting camera {camera_index}...")
    
    if detector.select_camera(camera_index):
        print("\nStarting camera analysis...")
        results = detector.capture_and_analyze(duration=3)
        
        if "error" in results:
            print(f"Analysis failed: {results['error']}")
        else:
            summary = results["analysis_summary"]
            print(f"\nANALYSIS RESULTS:")
            print(f"  Status: {summary['overall_status']}")
            print(f"  Authenticity Score: {summary['avg_authenticity_score']}")
            print(f"  Confidence: {summary['avg_confidence']}")
            print(f"  Fake Percentage: {summary['fake_percentage']}%")
            print(f"  Recommendation: {results['recommendation']}")
    
    detector.cleanup()
    print("\nCamera analysis complete!")

if __name__ == "__main__":
    main()


