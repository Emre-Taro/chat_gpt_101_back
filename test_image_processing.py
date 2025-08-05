#!/usr/bin/env python3
"""
Test script to verify image processing functionality with OpenAI API
"""

import os
import sys
import base64
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.openAPI.openai import (
    generate_openai_response_with_vision, 
    create_vision_message, 
    encode_image_to_base64
)

def test_image_processing():
    """Test the image processing functionality"""
    
    # Check if we have any images in the uploads directory
    uploads_dir = Path("static/uploads")
    if not uploads_dir.exists():
        print("❌ Uploads directory not found")
        return False
    
    # Find the first image file
    image_files = list(uploads_dir.glob("*.png")) + list(uploads_dir.glob("*.jpg")) + list(uploads_dir.glob("*.jpeg"))
    
    if not image_files:
        print("❌ No image files found in static/uploads/")
        return False
    
    test_image_path = str(image_files[0])
    print(f"📸 Testing with image: {test_image_path}")
    
    # Test 1: Encode image to base64
    print("\n1. Testing image encoding...")
    try:
        base64_data = encode_image_to_base64(test_image_path)
        if base64_data:
            print("✅ Image encoding successful")
        else:
            print("❌ Image encoding failed")
            return False
    except Exception as e:
        print(f"❌ Image encoding error: {e}")
        return False
    
    # Test 2: Create vision message
    print("\n2. Testing vision message creation...")
    try:
        vision_message = create_vision_message(
            content="What do you see in this image?",
            image_path=test_image_path
        )
        print("✅ Vision message creation successful")
        print(f"   Message structure: {vision_message.keys()}")
    except Exception as e:
        print(f"❌ Vision message creation error: {e}")
        return False
    
    # Test 3: Generate OpenAI response with vision
    print("\n3. Testing OpenAI API with vision...")
    try:
        response = generate_openai_response_with_vision([vision_message])
        
        if isinstance(response, dict) and "error" in response:
            print(f"❌ OpenAI API error: {response['error']}")
            return False
        else:
            print("✅ OpenAI API response successful")
            print(f"   Response: {response[:100]}...")
            return True
            
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Image Processing Functionality")
    print("=" * 50)
    
    success = test_image_processing()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Image processing is working correctly.")
    else:
        print("❌ Some tests failed. Please check the errors above.") 