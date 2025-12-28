# 🔧 Troubleshooting Guide - Zero Trust Telehealth Platform

## 🎯 Quick Diagnostics

### Check All Services Status
```bash
python test_all_services.py
```

### Check Which Ports Are Listening
```bash
netstat -ano | findstr "8001 8002 8003 5000 5173"
```

---

## 🚨 Common Issues & Solutions

### 1. Voice API (Port 8001) Not Starting

#### Symptoms
- Port 8001 not listening
- Cannot access http://localhost:8001/health
- Voice API terminal window shows errors

#### Possible Causes & Solutions

**A. Model Loading Timeout**
- **Cause:** ECAPA-TDNN model (83.3 MB) takes time to load
- **Solution:** Wait 30-60 seconds for the model to fully load
- **Check:** Look for "✓ Anti-spoofing model loaded" message in terminal

**B. Missing Dependencies**
```bash
cd "Voiceprint Analysis"
pip install -r requirements.txt
```

**C. TorchAudio Library Issue**
```bash
pip uninstall torchaudio -y
pip install torchaudio
```

**D. Port Already in Use**
```bash
# Find process using port 8001
netstat -ano | findstr "8001"

# Kill the process (replace <PID> with actual PID)
taskkill /PID <PID> /F
```

**E. Manual Start with Debug Output**
```bash
cd "Voiceprint Analysis"
python main.py api
```
Watch for error messages in the output.

---

### 2. Mouse API (Port 8003) Not Starting

#### Symptoms
- Port 8003 not listening
- Cannot access http://localhost:8003/health
- Mouse API terminal window shows errors

#### Possible Causes & Solutions

**A. PyTorch Model Loading Issue**
- **Cause:** PyTorch 2.6+ changed default `weights_only` parameter
- **Solution:** Already fixed in `test.py`, but may need fix in `main.py`

**B. Missing Dependencies**
```bash
cd "Mouse Movement Analysis"
pip install -r requirements.txt
```

**C. Scikit-learn Version Mismatch**
```bash
pip install --upgrade scikit-learn
```

**D. Manual Start with Debug Output**
```bash
cd "Mouse Movement Analysis"
python main.py api
```

---

### 3. Keystroke API Issues

#### If Keystroke API Stops Working

**A. Restart the Service**
```bash
cd "Keystroke Dynamics"
python main.py api
```

**B. Check Model File**
```bash
# Verify model exists
dir "Keystroke Dynamics\models\checkpoints\best_model.pth"
```

---

### 4. Backend Server Issues

#### Port 5000 Already in Use
```bash
# Find process
netstat -ano | findstr "5000"

# Kill process
taskkill /PID <PID> /F

# Restart backend
cd Backend
npm run dev
```

#### Missing Node Modules
```bash
cd Backend
npm install
npm run dev
```

---

### 5. Frontend Issues

#### Port 5173 Already in Use
```bash
# Kill process on port 5173
netstat -ano | findstr "5173"
taskkill /PID <PID> /F

# Restart frontend
cd Client
npm run dev
```

#### Build Errors
```bash
cd Client
npm install
npm run dev
```

---

## 🔍 Advanced Debugging

### Check Python Version
```bash
python --version
# Should be Python 3.8+
```

### Check Node Version
```bash
node --version
# Should be Node 16+
```

### Check Installed Python Packages
```bash
pip list
```

### View API Logs

**Voice API:**
```bash
cd "Voiceprint Analysis"
type logs\*.log
```

**Keystroke API:**
```bash
cd "Keystroke Dynamics"
type logs\*.log
```

**Mouse API:**
```bash
cd "Mouse Movement Analysis"
type logs\*.log
```

---

## 🚀 Complete System Restart

If all else fails, restart everything:

### 1. Kill All Services
```bash
# Kill all Python processes
taskkill /F /IM python.exe

# Kill all Node processes
taskkill /F /IM node.exe
```

### 2. Restart All Services
```bash
.\start-all-services.bat
```

### 3. Wait and Test
```bash
# Wait 60 seconds for all services to start
timeout /t 60

# Test all services
python test_all_services.py
```

---

## 📊 Expected Startup Times

| Service | Expected Startup Time |
|---------|----------------------|
| Keystroke API | 5-10 seconds |
| Mouse API | 10-20 seconds |
| Voice API | 30-60 seconds (large model) |
| Backend | 5-10 seconds |
| Frontend | 10-15 seconds |

---

## 🆘 Still Having Issues?

### Check System Requirements
- **Python:** 3.8 or higher
- **Node.js:** 16 or higher
- **RAM:** At least 8 GB (16 GB recommended)
- **Disk Space:** At least 2 GB free

### Verify Model Files Exist
```bash
# Voice model
dir "Voiceprint Analysis\models\pretrained\ecapa_tdnn\embedding_model.ckpt"

# Keystroke model
dir "Keystroke Dynamics\models\checkpoints\best_model.pth"

# Mouse model
dir "Mouse Movement Analysis\models\checkpoints\best_model.pth"
```

### Check Firewall Settings
Make sure Windows Firewall allows Python and Node.js to listen on ports 8001-8003, 5000, and 5173.

---

## 📝 Reporting Issues

If you encounter persistent issues, collect the following information:

1. Output of `python test_all_services.py`
2. Output of `netstat -ano | findstr "8001 8002 8003 5000 5173"`
3. Error messages from terminal windows
4. Python version: `python --version`
5. Node version: `node --version`
6. Operating System version

---

**Last Updated:** December 28, 2025

