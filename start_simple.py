#!/usr/bin/env python3
"""
Super simple startup script for Mac users
Automatically finds available port and opens browser
"""

import os
import sys
import socket
import webbrowser
import time
from pathlib import Path

def find_free_port():
    """Find an available port starting from 8000"""
    for port in range(8000, 8010):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return 8000

def main():
    print("🚀 Starting Email Domain Validator (Mac Version)...")
    
    # Set environment variables for SQLite setup
    os.environ["DATABASE_URL"] = "sqlite:///./edv_database.db"
    os.environ["REDIS_URL"] = "redis://localhost:6379"
    
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Find available port
    port = find_free_port()
    
    try:
        import uvicorn
        from app.main import app
        from app.models.database import engine, Base
        
        print("📋 Setting up database...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database setup complete!")
        
        print(f"\n{'='*60}")
        print("🎯 EMAIL DOMAIN VALIDATOR")
        print("="*60)
        print(f"🌐 Web Interface: http://localhost:{port}")
        print(f"📚 API Docs: http://localhost:{port}/docs")
        print(f"🛠️ Admin Panel: http://localhost:{port}/admin")
        print("="*60)
        print("💡 Press Ctrl+C to stop the server")
        print("="*60)
        
        # Open browser automatically
        print("🌐 Opening browser...")
        webbrowser.open(f"http://localhost:{port}")
        
        # Start the server
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=port,
            reload=False,
            log_level="warning"
        )
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\n🔧 Installing dependencies...")
        os.system("pip install -r requirements.txt")
        print("✅ Dependencies installed! Please run this script again.")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down Email Domain Validator...")
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"\n🔍 Try accessing manually: http://localhost:{port}")
        sys.exit(1)

if __name__ == "__main__":
    main()