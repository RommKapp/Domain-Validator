# 🍎 Mac Startup Guide - Email Domain Validator

## ⚡ Super Quick Start (2 Steps)

### Step 1: Open Terminal
1. **Press** `Cmd + Space` to open Spotlight
2. **Type** "Terminal" and press Enter

### Step 2: Run the Application
```bash
# Navigate to the folder (drag the folder into Terminal to get the path)
cd /path/to/your/email-domain-validator

# Run the simple startup script
python3 start_simple.py
```

**That's it!** The browser will open automatically to your Email Domain Validator.

---

## 🔧 Alternative Methods

### Method 1: Double-click the shell script
1. **Right-click** on `start_app.sh`
2. **Select** "Open With" → "Terminal"

### Method 2: Use the original startup script
```bash
python3 start_app.py
```

### Method 3: If you get permission errors
```bash
chmod +x start_simple.py
chmod +x start_app.sh
./start_simple.py
```

---

## 🚨 Troubleshooting

### ❓ "Nothing happens" when running the script?
**Try this:**
```bash
# Check if Python is installed
python3 --version

# If not installed, install Python
# Go to python.org and download Python 3.9+

# Run with full path
python3 /full/path/to/start_simple.py
```

### ❓ "Command not found" error?
```bash
# Install Python via Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python3

# Or download from python.org
```

### ❓ Browser doesn't open automatically?
**Manually open:** http://localhost:8000 (or check Terminal output for the actual port)

### ❓ "Port already in use" error?
The `start_simple.py` script automatically finds an available port from 8000-8009.

---

## 🎯 What Should Happen

When you run `python3 start_simple.py`, you should see:

```
🚀 Starting Email Domain Validator (Mac Version)...
📋 Setting up database...
✅ Database setup complete!

============================================================
🎯 EMAIL DOMAIN VALIDATOR
============================================================
🌐 Web Interface: http://localhost:8003
📚 API Docs: http://localhost:8003/docs
🛠️ Admin Panel: http://localhost:8003/admin
============================================================
💡 Press Ctrl+C to stop the server
============================================================
🌐 Opening browser...
```

Then your browser should automatically open to the Email Domain Validator interface.

---

## 💡 Pro Tips for Mac Users

### Quick Access (Create an alias)
```bash
# Add to your ~/.zshrc or ~/.bash_profile
alias edv="cd /path/to/email-domain-validator && python3 start_simple.py"

# Then just type 'edv' anywhere to start the app
```

### Create a Desktop Shortcut
1. **Open** Automator
2. **Choose** "Application"
3. **Add** "Run Shell Script" action
4. **Paste:** `cd /path/to/email-domain-validator && python3 start_simple.py`
5. **Save** as "Email Domain Validator" on Desktop

### Dock Icon
Drag the created Automator app to your Dock for one-click access.

---

## ✅ You're All Set!

The Email Domain Validator should now be running with a beautiful modern interface. Check the Terminal output for the exact URL (usually http://localhost:8000-8009).

**Enjoy validating domains!** 🚀