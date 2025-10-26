#!/usr/bin/env python3
"""
Test script to verify camera fixes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from camera_detector import CameraDetector
import time

def test_camera_detection():
    """Test camera detection and access"""
    print("Testing Camera Detection Fixes")
    print("=" * 50)
    
    # Initialize detector
    detector = CameraDetector()
    
    if not detector.available_cameras:
        print("❌ No cameras found")
        return False
    
    print(f"✅ Found {len(detector.available_cameras)} camera(s)")
    
    # Test each camera
    for camera in detector.available_cameras:
        print(f"\nTesting Camera {camera['index']}:")
        print(f"  Name: {camera['name']}")
        print(f"  Resolution: {camera['width']}x{camera['height']}")
        print(f"  Backend: {camera['backend']}")
        
        # Test camera access
        if detector.test_camera_access(camera['index']):
            print(f"  ✅ Camera {camera['index']} access test: PASSED")
        else:
            print(f"  ❌ Camera {camera['index']} access test: FAILED")
        
        # Test camera selection
        if detector.select_camera(camera['index']):
            print(f"  ✅ Camera {camera['index']} selection: PASSED")
            
            # Test streaming
            if detector.start_stream():
                print(f"  ✅ Camera {camera['index']} streaming: PASSED")
                
                # Test frame capture
                time.sleep(1)  # Wait for frames
                frame = detector.get_latest_frame()
                if frame is not None:
                    print(f"  ✅ Camera {camera['index']} frame capture: PASSED")
                else:
                    print(f"  ❌ Camera {camera['index']} frame capture: FAILED")
                
                detector.stop_stream()
            else:
                print(f"  ❌ Camera {camera['index']} streaming: FAILED")
        else:
            print(f"  ❌ Camera {camera['index']} selection: FAILED")
    
    detector.cleanup()
    print("\n" + "=" * 50)
    print("Camera test completed!")
    return True

if __name__ == "__main__":
    test_camera_detection()

