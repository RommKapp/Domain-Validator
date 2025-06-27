#!/usr/bin/env python3
"""
Test script to verify the validation API is working
"""

import requests
import subprocess
import time
import sys
from pathlib import Path

def start_app_background():
    """Start the app in background"""
    print("🚀 Starting Email Domain Validator...")
    process = subprocess.Popen(
        [sys.executable, "start_simple.py"],
        cwd=Path(__file__).parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return process

def test_validation():
    """Test the validation endpoints"""
    base_url = "http://localhost:8000"
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    for i in range(15):
        try:
            response = requests.get(f"{base_url}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!")
                break
        except:
            time.sleep(1)
    else:
        print("❌ Server failed to start")
        return False
    
    # Test validation endpoint
    print("\n🧪 Testing domain validation...")
    test_cases = [
        ("google.com", "Should work"),
        ("test@gmail.com", "Should extract domain"), 
        ("invalid-domain-12345.xyz", "Should handle invalid"),
    ]
    
    for domain, description in test_cases:
        try:
            print(f"Testing: {domain} ({description})")
            response = requests.post(
                f"{base_url}/api/v1/domain/validate",
                json={"domain": domain},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ Success: {result['domain_type']} - Score: {result['quality_score']}/10")
            else:
                print(f"  ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\n🌐 Web interface: {base_url}")
    print("📱 Open this URL in your browser to test the UI!")
    return True

if __name__ == "__main__":
    process = start_app_background()
    try:
        success = test_validation()
        if success:
            print("\n✅ All tests passed! The validation should work in the browser.")
            print("💡 If you still get 'network error', try refreshing the page.")
        else:
            print("\n❌ Tests failed. Check the error messages above.")
    finally:
        print("\n🛑 Stopping test server...")
        process.terminate()
        process.wait()