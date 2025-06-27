#!/usr/bin/env python3
"""
Quick test script to verify the UI and API work correctly
"""

import requests
import time
import subprocess
import sys
import threading
from pathlib import Path

def start_server():
    """Start the server in background"""
    try:
        subprocess.run([sys.executable, "start_app.py"], 
                      cwd=Path(__file__).parent,
                      check=False,
                      stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Server start error: {e}")

def test_endpoints():
    """Test the main endpoints"""
    base_url = "http://localhost:8000"
    
    tests = [
        ("Web Interface", f"{base_url}/", "text/html"),
        ("API Docs", f"{base_url}/docs", "text/html"),
        ("Admin Panel", f"{base_url}/admin", "text/html"),
        ("Health Check", f"{base_url}/health", "application/json"),
    ]
    
    print("🧪 Testing UI and API endpoints...")
    print("=" * 50)
    
    for name, url, expected_type in tests:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                if expected_type in content_type:
                    print(f"✅ {name}: Working perfectly")
                else:
                    print(f"⚠️  {name}: Accessible but unexpected content type")
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"🔄 {name}: Server not ready yet...")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
    
    # Test domain validation API
    try:
        print("\n🧪 Testing Domain Validation API...")
        response = requests.post(
            f"{base_url}/api/v1/domain/validate",
            json={"domain": "google.com"},
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            if 'domain_type' in result and 'quality_score' in result:
                print(f"✅ API Validation: Working perfectly")
                print(f"   Domain: {result['domain']}")
                print(f"   Type: {result['domain_type']}")
                print(f"   Score: {result['quality_score']}/10")
                print(f"   Recommendation: {result['recommendation']}")
            else:
                print(f"⚠️  API Validation: Unexpected response format")
        else:
            print(f"❌ API Validation: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ API Validation: {e}")

def main():
    print("🚀 Starting Email Domain Validator Test...")
    print()
    
    # Start server in background
    print("🔄 Starting server...")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    print("⏳ Waiting for server to initialize...")
    for i in range(10):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!")
                break
        except:
            time.sleep(1)
            if i == 9:
                print("❌ Server failed to start within 10 seconds")
                return
    
    # Run tests
    test_endpoints()
    
    print("\n" + "=" * 50)
    print("🎯 TEST SUMMARY")
    print("=" * 50)
    print("🌐 Main Interface: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🛠️ Admin Panel: http://localhost:8000/admin")
    print("=" * 50)
    print("✨ Open http://localhost:8000 in your browser!")
    print("💡 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Keep script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Stopping test...")

if __name__ == "__main__":
    main()