#!/usr/bin/env python3
"""
Simple test script to verify camera functionality fixes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from camera_detector import CameraDetector
import time

def test_camera_simple():
    """Simple camera test to verify functionality"""
    print("🎥 Simple Camera Test")
    print("=" * 40)
    
    # Initialize detector
    detector = CameraDetector()
    
    if not detector.available_cameras:
        print("❌ No cameras found!")
        print("Please check:")
        print("1. Camera is connected")
        print("2. No other apps are using camera")
        print("3. Camera permissions are enabled")
        return False
    
    print(f"✅ Found {len(detector.available_cameras)} camera(s)")
    
    # Test the first camera
    camera = detector.available_cameras[0]
    print(f"\n🎯 Testing: {camera['name']}")
    print(f"   Type: {camera.get('type', 'Unknown')}")
    print(f"   Index: {camera['index']}")
    
    # Test camera selection
    print(f"\n🔄 Selecting camera...")
    if detector.select_camera(camera['index']):
        print("✅ Camera selected successfully")
    else:
        print("❌ Failed to select camera")
        return False
    
    # Test camera access
    print(f"\n🔍 Testing camera access...")
    if detector.test_camera_access(camera['index']):
        print("✅ Camera access test passed")
    else:
        print("❌ Camera access test failed")
        return False
    
    # Test streaming
    print(f"\n🎬 Starting camera stream...")
    if detector.start_stream():
        print("✅ Camera stream started")
        
        # Wait for frames
        print("⏳ Waiting for frames...")
        time.sleep(2)
        
        # Test frame capture
        frame = detector.get_latest_frame()
        if frame is not None:
            print(f"✅ Frame captured successfully!")
            print(f"   Frame size: {frame.shape}")
            print(f"   Frame type: {frame.dtype}")
        else:
            print("❌ No frame captured")
            return False
        
        # Stop stream
        detector.stop_stream()
        print("🛑 Camera stream stopped")
        
    else:
        print("❌ Failed to start camera stream")
        return False
    
    detector.cleanup()
    
    print(f"\n🎉 Camera test completed successfully!")
    print("Your camera is working properly!")
    return True

if __name__ == "__main__":
    success = test_camera_simple()
    if not success:
        print("\n⚠️ Camera test failed.")
        print("Please check the troubleshooting steps above.")

