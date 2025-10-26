#!/usr/bin/env python3
"""
Comprehensive test script for laptop camera detection and identification
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from camera_detector import CameraDetector
import time

def test_laptop_camera_detection():
    """Test laptop camera detection and identification"""
    print("🔍 Testing Laptop Camera Detection & Identification")
    print("=" * 60)
    
    # Initialize detector
    detector = CameraDetector()
    
    if not detector.available_cameras:
        print("❌ No cameras found on this system")
        print("\n🔧 Troubleshooting steps:")
        print("1. Check if your laptop camera is enabled in Device Manager")
        print("2. Make sure no other applications are using the camera")
        print("3. Check camera permissions in Windows Settings > Privacy > Camera")
        print("4. Try running the application as administrator")
        print("5. Restart your computer to reset camera drivers")
        return False
    
    print(f"✅ Found {len(detector.available_cameras)} camera(s)")
    
    # Analyze camera types
    laptop_cameras = [cam for cam in detector.available_cameras if cam.get('type') == 'Laptop Camera']
    external_cameras = [cam for cam in detector.available_cameras if cam.get('type') == 'External Camera']
    
    print(f"📱 Laptop cameras: {len(laptop_cameras)}")
    print(f"📷 External cameras: {len(external_cameras)}")
    
    # Test each camera
    for camera in detector.available_cameras:
        print(f"\n🔍 Testing {camera['name']}:")
        print(f"   Type: {camera.get('type', 'Unknown')}")
        print(f"   Index: {camera['index']}")
        print(f"   Resolution: {camera['width']}x{camera['height']}")
        print(f"   FPS: {camera['fps']}")
        print(f"   Backend: {camera.get('backend_type', camera.get('backend', 'Unknown'))}")
        print(f"   Reliability: {camera.get('reliability', 'Unknown')}")
        
        # Test camera access
        if detector.test_camera_access(camera['index']):
            print(f"   ✅ Access test: PASSED")
        else:
            print(f"   ❌ Access test: FAILED")
        
        # Test camera selection
        if detector.select_camera(camera['index']):
            print(f"   ✅ Selection test: PASSED")
            
            # Test streaming
            if detector.start_stream():
                print(f"   ✅ Streaming test: PASSED")
                
                # Test frame capture
                time.sleep(1)  # Wait for frames
                frame = detector.get_latest_frame()
                if frame is not None:
                    print(f"   ✅ Frame capture test: PASSED")
                    print(f"   📊 Frame size: {frame.shape}")
                else:
                    print(f"   ❌ Frame capture test: FAILED")
                
                detector.stop_stream()
            else:
                print(f"   ❌ Streaming test: FAILED")
        else:
            print(f"   ❌ Selection test: FAILED")
    
    # Test camera permissions
    print(f"\n🔐 Testing Camera Permissions:")
    permissions_info = detector.check_camera_permissions()
    
    if 'error' in permissions_info:
        print(f"   ❌ Permissions check failed: {permissions_info['error']}")
    else:
        system_info = permissions_info['system_info']
        print(f"   📊 System Info:")
        print(f"      OS: {system_info['os']} {system_info['os_version']}")
        print(f"      Python: {system_info['python_version']}")
        print(f"      OpenCV: {system_info['opencv_version']}")
        print(f"   🔐 Basic Camera Access: {'✅ Available' if permissions_info['basic_camera_access'] else '❌ Not Available'}")
        print(f"   📱 Laptop Cameras: {permissions_info['laptop_cameras']}")
        print(f"   📷 External Cameras: {permissions_info['external_cameras']}")
    
    detector.cleanup()
    
    print(f"\n" + "=" * 60)
    print("🎯 Laptop Camera Test Summary:")
    
    if laptop_cameras:
        print(f"✅ Laptop cameras detected: {len(laptop_cameras)}")
        for cam in laptop_cameras:
            print(f"   - {cam['name']} (Index {cam['index']})")
    else:
        print("❌ No laptop cameras detected")
        print("   This might indicate:")
        print("   - Camera is disabled in Device Manager")
        print("   - Camera drivers are not installed")
        print("   - Camera is being used by another application")
        print("   - Camera permissions are not granted")
    
    if external_cameras:
        print(f"📷 External cameras detected: {len(external_cameras)}")
        for cam in external_cameras:
            print(f"   - {cam['name']} (Index {cam['index']})")
    
    print(f"\n💡 Recommendations:")
    if not laptop_cameras:
        print("1. Check Windows Camera Privacy Settings")
        print("2. Enable camera in Device Manager")
        print("3. Update camera drivers")
        print("4. Restart the application as administrator")
    else:
        print("1. Laptop camera detection is working properly")
        print("2. You can now use the camera for deepfake detection")
        print("3. Try the camera analysis features")
    
    return len(laptop_cameras) > 0

if __name__ == "__main__":
    success = test_laptop_camera_detection()
    if success:
        print("\n🎉 Laptop camera detection test completed successfully!")
    else:
        print("\n⚠️ Laptop camera detection test completed with issues.")
        print("Please check the troubleshooting steps above.")

