# Quick Reference - Biometric Enrollment System

## 🚀 Start All Services (One Command)

```powershell
.\start-ml-services.ps1
```

Wait 30-60 seconds, then start Backend and Frontend.

---

## ✅ Health Check

```powershell
.\test-ml-services.ps1
```

Expected output:
```
✓ Voice Recognition API - HEALTHY
✓ Keystroke Dynamics API - HEALTHY  
✓ Mouse Movement API - HEALTHY
```

---

## 🔧 Manual Start (If Needed)

### Terminal 1 - Voice API
```powershell
cd "Voiceprint Analysis"
.\venv\Scripts\Activate.ps1
python main.py api
```

### Terminal 2 - Keystroke API
```powershell
cd "Keystroke Dynamics"
.\venv\Scripts\Activate.ps1
python main.py api
```

### Terminal 3 - Mouse API
```powershell
cd "Mouse Movement Analysis"
.\venv\Scripts\Activate.ps1
python main.py api
```

### Terminal 4 - Backend
```bash
cd Backend
npm run dev
```

### Terminal 5 - Frontend
```bash
cd Client
npm run dev
```

---

## 🌐 Service URLs

| Service | URL |
|---------|-----|
| Voice API | http://localhost:8001/health |
| Keystroke API | http://localhost:8002/health |
| Mouse API | http://localhost:8003/health |
| Backend | http://localhost:5000 |
| Frontend | http://localhost:3000 |

---

## 🐛 Common Issues & Quick Fixes

### Issue: Child process dying
**Fix:** Already fixed - `workers: 1` in all configs

### Issue: Voice enrollment fails
**Fix:** Already fixed - VAD threshold lowered to 0.001

### Issue: API won't start
**Fix:** 
```powershell
cd "<API folder>"
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Issue: Database not updating
**Fix:** Ensure all ML services are running (check health endpoints)

---

## 📝 Test Biometric Enrollment

1. Go to http://localhost:3000
2. Click "Register"
3. Fill doctor info → Next
4. Complete biometric enrollment:
   - Voice: 3 samples (5-10 sec each)
   - Keystroke: Type phrase 3 times
   - Mouse: Move naturally 3 times (30 sec each)
5. Click "Complete Registration"
6. Check dashboard - should show "Enrolled ✓" for all

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `START_SERVICES_GUIDE.md` | Complete startup instructions |
| `FIXES_APPLIED.md` | Summary of all fixes |
| `ML_SERVICES_FIX_README.md` | Detailed technical documentation |
| `BIOMETRIC_ENROLLMENT_FIX_SUMMARY.md` | Technical summary |
| `QUICK_REFERENCE.md` | This file |

---

## 🔍 What Was Fixed

1. ✅ Keystroke API - Changed workers from 4 to 1
2. ✅ Mouse API - Changed workers from 4 to 1
3. ✅ Voice API - Changed workers from 4 to 1
4. ✅ Voice API - Lowered VAD threshold from 0.01 to 0.001
5. ✅ Voice API - Reduced enrollment samples from 3 to 1
6. ✅ Voice API - Added safety checks for empty audio
7. ✅ Database - Now updates correctly after successful enrollment

---

## 💡 Key Configuration Changes

### All ML Services
```yaml
api:
  workers: 1  # Changed from 4
```

### Voice API Only
```yaml
audio:
  vad_threshold: 0.001  # Changed from 0.01

verification:
  enrollment_samples: 1  # Changed from 3
```

---

## 🎯 Expected Database State After Enrollment

```javascript
{
  biometricData: {
    voiceEnrolled: true,        // ✓ Was false
    voiceEmbedding: "doctor_id", // ✓ Was null
    keystrokeEnrolled: true,     // ✓ Was false
    keystrokeProfile: "doctor_id", // ✓ Was null
    mouseEnrolled: true,         // ✓ Was false
    mouseProfile: "doctor_id"    // ✓ Was null
  }
}
```

---

## 🆘 Need Help?

1. Run health check: `.\test-ml-services.ps1`
2. Check service logs in each terminal
3. Review `START_SERVICES_GUIDE.md` troubleshooting section
4. Verify MongoDB is running
5. Check browser console for frontend errors
6. Check Backend console for API errors

