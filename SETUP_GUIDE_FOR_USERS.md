# 🚀 Email Domain Validator - Setup Guide for Users

## 📋 What You'll Need

Before starting, you'll need to install a few things on your computer. Don't worry - we'll guide you through each step!

### Required Software:
1. **Python** (programming language)
2. **Git** (to download the code)
3. **A web browser** (Chrome, Firefox, Safari, or Edge)

---

## 🔧 Step 1: Install Python

### For Windows:
1. Go to [python.org](https://www.python.org/downloads/)
2. Click the big yellow "Download Python" button
3. Run the downloaded file
4. ⚠️ **IMPORTANT**: Check the box "Add Python to PATH" during installation
5. Click "Install Now"

### For Mac:
1. Go to [python.org](https://www.python.org/downloads/)
2. Click "Download Python" 
3. Open the downloaded `.pkg` file
4. Follow the installation wizard

### For Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install python3 python3-pip git
```

---

## 📥 Step 2: Download the Email Domain Validator

### Option A: Using Git (Recommended)
1. Open **Terminal** (Mac/Linux) or **Command Prompt** (Windows)
2. Copy and paste this command:
```bash
git clone https://github.com/your-username/email-domain-validator.git
cd email-domain-validator
```

### Option B: Download ZIP file
1. Go to the project page on GitHub
2. Click the green "Code" button
3. Click "Download ZIP"
4. Extract the ZIP file to your Desktop
5. Open Terminal/Command Prompt and navigate to the folder:
```bash
cd Desktop/email-domain-validator
```

---

## ⚙️ Step 3: Set Up the Application

### 1. Install Required Components
Copy and paste these commands one by one:

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 2. Set Up the Database (Optional - uses SQLite by default)
```bash
# Create database tables
python -c "from app.models.database import engine, Base; Base.metadata.create_all(engine)"
```

---

## 🚀 Step 4: Start the Application

### Start the Server
Copy and paste this command:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

You should see something like this:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 🎉 Access the Application
Open your web browser and go to:
**http://localhost:8000**

---

## 🖥️ Using the Email Domain Validator

### 🔍 Single Domain Check
1. **Enter a domain or email** in the input field
   - Examples: `google.com` or `user@company.com`
2. **Click "Validate"** or press Enter
3. **View the results** showing:
   - Domain type (Corporate, Public Provider, etc.)
   - Quality score (0-10)
   - Recommendation (Accept/Reject/Review)
   - Technical details (DNS, SSL, etc.)

### 📋 Bulk Domain Check
1. **Switch to "Batch Domain Validation"** section
2. **Enter multiple domains** (one per line):
   ```
   example.com
   user@company.com
   university.edu
   ```
3. **OR Upload a file**: Click "Choose File" and select a .csv or .txt file
4. **Click "Validate Batch"**
5. **View summary statistics** and individual results
6. **Export results** as CSV or JSON for further analysis

### 🛠️ Admin Features
- Click **"Admin Panel"** to manage whitelists and blacklists
- Add trusted domains to whitelist
- Block suspicious domains in blacklist

---

## 📱 What the Interface Looks Like

The interface includes:
- **🎨 Modern Design**: Clean, professional appearance
- **📊 Visual Results**: Color-coded domain types and recommendations
- **⚡ Quick Examples**: One-click testing with sample domains
- **📈 Statistics**: Real-time processing stats and summaries
- **💾 Export Options**: Download results in multiple formats
- **📚 Help Guide**: Built-in explanation of domain categories

---

## ❓ Troubleshooting

### Problem: "Command not found" error
**Solution**: Python is not installed correctly
- Reinstall Python and make sure to check "Add to PATH"
- Restart your Terminal/Command Prompt

### Problem: "Permission denied" error
**Solution**: Try adding `sudo` (Mac/Linux) or run as Administrator (Windows)
```bash
sudo pip install -r requirements.txt
```

### Problem: "Port already in use" error
**Solution**: Another application is using port 8000
- Try a different port:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```
- Then access: **http://localhost:8001**

### Problem: Website shows "This site can't be reached"
**Solutions**:
1. Make sure the server is still running (you should see logs in Terminal)
2. Check the exact URL: **http://localhost:8000** (not https)
3. Try **http://127.0.0.1:8000** instead

### Problem: Slow validation times
**Solutions**:
1. Make sure you have a good internet connection
2. Start Redis for better caching (optional):
   ```bash
   # Install Redis (Mac with Homebrew)
   brew install redis
   redis-server
   ```

---

## 🔄 Stopping the Application

To stop the server:
1. Go back to your Terminal/Command Prompt
2. Press **Ctrl+C** (Windows/Linux) or **Cmd+C** (Mac)
3. You'll see: `Shutting down`

---

## 📞 Getting Help

If you encounter any issues:

1. **Check the Terminal output** for error messages
2. **Restart the application** (Ctrl+C, then run the start command again)
3. **Check your internet connection** (the app needs internet to validate domains)
4. **Try different browsers** (Chrome, Firefox, Safari, Edge)

### Common URLs to bookmark:
- **Main Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:8000/admin

---

## 💡 Tips for Best Results

### For Single Domain Validation:
- ✅ Use: `example.com` or `user@example.com`
- ❌ Avoid: `http://example.com` or `www.example.com`

### For Batch Validation:
- Put one domain/email per line
- Files should be .txt or .csv format
- Remove headers from CSV files
- Maximum recommended: 100 domains per batch

### Understanding Results:
- **🟢 Corporate/Educational/Government**: Usually safe to accept
- **🔵 Public Provider**: Gmail, Yahoo - review individually  
- **🔴 Disposable/Suspicious**: Usually reject
- **⚫ Unreachable**: Domain doesn't exist

---

## 🎯 You're All Set!

The Email Domain Validator is now running on your computer. You can:
- ✅ Validate individual domains
- ✅ Process bulk domain lists
- ✅ Export results for analysis
- ✅ Manage whitelists and blacklists
- ✅ Access detailed API documentation

**Need to use it again later?** Just run the start command:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

And open: **http://localhost:8000**