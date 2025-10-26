#!/usr/bin/env python3
"""
Test script to verify AI detection improvements
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shadowhunt_working import SimpleDeepfakeDetector
import numpy as np
import cv2

def create_test_images():
    """Create test images for AI detection"""
    # Create a simple test image
    test_img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Add a simple face-like pattern
    cv2.rectangle(test_img, (200, 150), (440, 350), (255, 220, 177), -1)  # Face
    cv2.circle(test_img, (280, 220), 15, (0, 0, 0), -1)  # Left eye
    cv2.circle(test_img, (360, 220), 15, (0, 0, 0), -1)  # Right eye
    cv2.ellipse(test_img, (320, 280), (30, 15), 0, 0, 180, (0, 0, 0), 2)  # Mouth
    
    # Save test image
    cv2.imwrite('test_image.jpg', test_img)
    return 'test_image.jpg'

def test_ai_detection():
    """Test the improved AI detection system"""
    print("Testing Improved AI Detection System")
    print("=" * 50)
    
    # Initialize detector
    detector = SimpleDeepfakeDetector()
    
    # Create test image
    test_image_path = create_test_images()
    
    try:
        # Test the detection
        print("Analyzing test image...")
        result = detector.analyze_image(test_image_path)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return False
        
        print(f"✅ Analysis completed successfully!")
        print(f"   Confidence Real: {result['confidence_real']:.3f} ({result['confidence_real']*100:.1f}%)")
        print(f"   Confidence Fake: {result['confidence_fake']:.3f} ({result['confidence_fake']*100:.1f}%)")
        print(f"   Status: {result['status']}")
        print(f"   Watermark Found: {result['watermark']['found']}")
        
        # Check if percentages are within valid range
        real_percent = result['confidence_real'] * 100
        fake_percent = result['confidence_fake'] * 100
        
        if 0 <= real_percent <= 100 and 0 <= fake_percent <= 100:
            print("✅ Percentage calculation is correct (within 0-100% range)")
        else:
            print(f"❌ Percentage calculation error: Real={real_percent:.1f}%, Fake={fake_percent:.1f}%")
        
        # Check detection scores
        if 'detection_scores' in result['analysis_details']:
            print("\nDetailed Detection Scores:")
            for method, score in result['analysis_details']['detection_scores'].items():
                print(f"   {method}: {score:.3f}")
        
        # Test with different thresholds
        print(f"\nThreshold Analysis:")
        if result['confidence_real'] > 0.7:
            print("   ✅ High confidence in real image")
        elif result['confidence_real'] < 0.3:
            print("   ✅ High confidence in fake image")
        else:
            print("   ⚠️  Uncertain result - requires further analysis")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    finally:
        # Clean up test image
        if os.path.exists(test_image_path):
            os.remove(test_image_path)

if __name__ == "__main__":
    test_ai_detection()

