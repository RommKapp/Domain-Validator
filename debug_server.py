#!/usr/bin/env python3
"""
Debug version to show exact server URL and test connectivity
"""

import os
import sys
import socket
from pathlib import Path

def find_free_port():
    """Find an available port starting from 9000"""
    for port in range(9000, 9020):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            print(f"Port {port} is in use")
            continue
    return 9000

def main():
    print("🐛 DEBUG MODE - Email Domain Validator")
    print("=" * 50)
    
    # Set environment variables for SQLite setup
    os.environ["DATABASE_URL"] = "sqlite:///./edv_database.db"
    os.environ["REDIS_URL"] = "redis://localhost:6379"
    
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Find available port
    port = find_free_port()
    print(f"🔍 Selected port: {port}")
    
    try:
        import uvicorn
        from app.main import app
        from app.models.database import engine, Base
        
        print("📋 Setting up database...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database setup complete!")
        
        print(f"\n{'='*60}")
        print("🎯 EMAIL DOMAIN VALIDATOR - DEBUG MODE")
        print("="*60)
        print(f"🌐 Web Interface: http://localhost:{port}")
        print(f"📚 API Docs: http://localhost:{port}/docs")
        print(f"🛠️ Admin Panel: http://localhost:{port}/admin")
        print(f"💊 Health Check: http://localhost:{port}/health")
        print("="*60)
        print("🔧 DEBUG INFO:")
        print(f"   - Server will bind to 127.0.0.1:{port}")
        print(f"   - API Base URL: http://localhost:{port}/api/v1/domain")
        print("   - Test with: curl http://localhost:{}/health".format(port))
        print("="*60)
        print("💡 Press Ctrl+C to stop the server")
        print("="*60)
        
        # Don't open browser automatically in debug mode
        print("🌐 NOT opening browser automatically in debug mode")
        print("📱 Manually open: http://localhost:{}".format(port))
        
        # Start the server with debug logging
        print(f"\n🚀 Starting server on port {port}...")
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=port,
            reload=False,
            log_level="info"
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