# Complete Service Startup Guide

## Prerequisites

1. **Python Virtual Environments** - Each ML service should have its own venv:
   - `Voiceprint Analysis/venv`
   - `Keystroke Dynamics/venv`
   - `Mouse Movement Analysis/venv`

2. **Node.js** - For Backend and Frontend

3. **MongoDB** - Running on localhost:27017

## Quick Start (Recommended)

### Step 1: Start ML Services

Open PowerShell in the project root and run:

```powershell
.\start-ml-services.ps1
```

This will open 3 separate terminal windows for each ML service.

**Wait 30-60 seconds** for all services to initialize.

### Step 2: Verify ML Services

In a new PowerShell window:

```powershell
.\test-ml-services.ps1
```

You should see:
```
✓ Voice Recognition API - HEALTHY
✓ Keystroke Dynamics API - HEALTHY
✓ Mouse Movement API - HEALTHY
```

### Step 3: Start Backend

Open a new terminal in the `Backend` folder:

```bash
npm run dev
```

Backend should start on http://localhost:5000

### Step 4: Start Frontend

Open a new terminal in the `Client` folder:

```bash
npm run dev
```

Frontend should start on http://localhost:3000

## Manual Start (Alternative)

If the automated scripts don't work, start each service manually:

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

## Service Health Checks

Once all services are running, verify them:

| Service | URL | Expected Response |
|---------|-----|-------------------|
| Voice API | http://localhost:8001/health | `{"status":"healthy"}` |
| Keystroke API | http://localhost:8002/health | `{"status":"healthy"}` |
| Mouse API | http://localhost:8003/health | `{"status":"healthy"}` |
| Backend | http://localhost:5000/api/health | `{"status":"ok"}` |
| Frontend | http://localhost:3000 | Login page loads |

## Testing Biometric Enrollment

1. Navigate to http://localhost:3000
2. Click "Register" 
3. Fill in doctor information:
   - First Name, Last Name
   - Email, Password
   - Medical License Number
   - Specialization
   - Years of Experience
4. Click "Next" to proceed to Biometric Enrollment
5. Complete all 3 biometric enrollments:
   - **Voice**: Record 3 samples (speak for 5-10 seconds each)
   - **Keystroke**: Type the required phrase 3 times
   - **Mouse**: Move mouse naturally for 30 seconds, 3 times
6. Click "Complete Registration"
7. You should be redirected to the dashboard
8. Check the dashboard - all biometric indicators should show "Enrolled ✓"

## Troubleshooting

### ML Services Won't Start

**Problem**: Child process dying errors
**Solution**: Ensure `workers: 1` in all config.yaml files

**Problem**: Module not found errors
**Solution**: Activate venv and reinstall requirements:
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Voice Enrollment Fails

**Problem**: "tuple index out of range" error
**Solution**: Already fixed - VAD threshold lowered to 0.001

**Problem**: No audio detected
**Solution**: 
- Check microphone permissions
- Speak clearly during recording
- Ensure audio is at least 1 second long

### Keystroke/Mouse Enrollment Fails

**Problem**: API not responding
**Solution**: Check that the API is running (health endpoint)

**Problem**: Insufficient data
**Solution**: Complete all required samples (3 for each)

### Database Not Updating

**Problem**: Biometric fields remain false/null
**Solution**: 
1. Check Backend console for errors
2. Verify all ML services are healthy
3. Check browser Network tab for failed requests
4. Ensure MongoDB is running

## Service Ports

| Service | Port | Protocol |
|---------|------|----------|
| Voice API | 8001 | HTTP |
| Keystroke API | 8002 | HTTP |
| Mouse API | 8003 | HTTP |
| Backend | 5000 | HTTP |
| Frontend | 3000 | HTTP |
| MongoDB | 27017 | TCP |

## Stopping Services

### ML Services
Press `Ctrl+C` in each terminal window

### Backend & Frontend
Press `Ctrl+C` in their respective terminals

### MongoDB
```bash
# If running as service
net stop MongoDB

# If running manually
# Press Ctrl+C in MongoDB terminal
```

## Next Steps

After successful enrollment:
1. Login with your credentials
2. Test continuous authentication during a session
3. Check the ML Services Status on the dashboard
4. All three services should show green checkmarks

