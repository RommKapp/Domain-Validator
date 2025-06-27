#!/usr/bin/env python3
"""
Simple startup script for Email Domain Validator
This script uses SQLite for easy setup without requiring PostgreSQL
"""

import os
import sys
from pathlib import Path

# Set environment variables for SQLite setup
os.environ["DATABASE_URL"] = "sqlite:///./edv_database.db"
os.environ["REDIS_URL"] = "redis://localhost:6379"  # Will gracefully fail if Redis not available

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    import uvicorn
    from app.main import app
    from app.models.database import engine, Base
    
    print("🚀 Starting Email Domain Validator...")
    print("📋 Setting up database...")
    
    # Create all database tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database setup complete!")
    
    print("\n" + "="*60)
    print("🎯 EMAIL DOMAIN VALIDATOR")
    print("="*60)
    print("🌐 Web Interface: http://localhost:8002")
    print("📚 API Docs: http://localhost:8002/docs")
    print("🛠️ Admin Panel: http://localhost:8002/admin")
    print("="*60)
    print("💡 Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
    
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("\n🔧 Please install required dependencies:")
    print("pip install -r requirements.txt")
    sys.exit(1)
    
except KeyboardInterrupt:
    print("\n\n👋 Shutting down Email Domain Validator...")
    print("Thank you for using our service!")
    sys.exit(0)
    
except Exception as e:
    print(f"❌ Error starting application: {e}")
    print("\n🔍 Troubleshooting tips:")
    print("1. Make sure port 8002 is not in use")
    print("2. Check your internet connection")
    print("3. Try running: pip install -r requirements.txt")
    sys.exit(1)