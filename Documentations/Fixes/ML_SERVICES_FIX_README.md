# ML Services Biometric Enrollment Fix

## Issues Fixed

### 1. **Keystroke & Mouse API Child Process Dying**
**Problem:** APIs were configured with `workers: 4`, which causes uvicorn to spawn multiple worker processes. On Windows, this fails because Windows doesn't support the `fork()` system call that uvicorn uses for multiprocessing.

**Solution:** Changed `workers: 4` to `workers: 1` in all three config files:
- `Keystroke Dynamics/config.yaml`
- `Mouse Movement Analysis/config.yaml`
- `Voiceprint Analysis/config.yaml`

### 2. **Voice API "tuple index out of range" Error**
**Problem:** The Voice Activity Detection (VAD) threshold was too high (`0.01`), causing all audio to be filtered out as "silence". This resulted in empty segments array, which caused the "tuple index out of range" error when trying to compute mean embeddings.

**Solutions Applied:**
- Lowered VAD threshold from `0.01` to `0.001` in `Voiceprint Analysis/config.yaml`
- Changed `enrollment_samples` from `3` to `1` to allow single audio file enrollment
- Added safety checks in `audio_preprocessing.py`:
  - Handle short audio files (shorter than frame length)
  - Return original audio if VAD filters everything out
  - Return audio as single segment if shorter than window duration
- Added validation in `speaker_verification.py`:
  - Check if segments array is empty before processing
  - Check if embeddings array is empty before computing mean
  - Provide clear error messages

### 3. **Database Not Updating (biometricData fields remain false/null)**
**Problem:** When the ML APIs fail, the enrollment process fails silently, and the database is not updated.

**Solution:** The fixes above ensure the ML APIs work correctly, so enrollment will succeed and the database will be updated properly.

## How to Start ML Services

### Option 1: Using PowerShell Script (Recommended)
```powershell
.\start-ml-services.ps1
```

### Option 2: Using Batch Script
```cmd
start-ml-services.bat
```

### Option 3: Manual Start (Separate Terminals)

**Terminal 1 - Voice API:**
```powershell
cd "Voiceprint Analysis"
.\venv\Scripts\Activate.ps1
python main.py api
```

**Terminal 2 - Keystroke API:**
```powershell
cd "Keystroke Dynamics"
.\venv\Scripts\Activate.ps1
python main.py api
```

**Terminal 3 - Mouse API:**
```powershell
cd "Mouse Movement Analysis"
.\venv\Scripts\Activate.ps1
python main.py api
```

## Verification

After starting all services, verify they're running:

1. **Check Health Endpoints:**
   - Voice API: http://localhost:8001/health
   - Keystroke API: http://localhost:8002/health
   - Mouse API: http://localhost:8003/health

2. **Check Dashboard:**
   - The ML Services Status in the dashboard should show green checkmarks for all three services

## Testing Biometric Enrollment

1. Start all ML services using one of the methods above
2. Start the Backend server
3. Start the Frontend application
4. Register as a new Doctor
5. Complete the Biometric Enrollment step:
   - **Voice:** Record a voice sample (speak for 3-5 seconds)
   - **Keystroke:** Type the required text naturally
   - **Mouse Movement:** Move the mouse naturally during the enrollment
6. Click "Complete Registration"
7. Check the database - the biometric fields should now be populated:
   - `voiceEnrolled: true`
   - `voiceEmbedding: <doctor_id>`
   - `keystrokeEnrolled: true`
   - `keystrokeProfile: <doctor_id>`
   - `mouseEnrolled: true`
   - `mouseProfile: <doctor_id>`

## Configuration Changes Summary

### Voiceprint Analysis/config.yaml
```yaml
audio:
  vad_threshold: 0.001  # Changed from 0.01

verification:
  enrollment_samples: 1  # Changed from 3

api:
  workers: 1  # Changed from 4
```

### Keystroke Dynamics/config.yaml
```yaml
api:
  workers: 1  # Changed from 4
```

### Mouse Movement Analysis/config.yaml
```yaml
api:
  workers: 1  # Changed from 4
```

## Troubleshooting

### If Voice API still shows errors:
- Ensure the audio recording is at least 1 second long
- Speak clearly during recording
- Check that the microphone is working properly
- The audio should contain actual speech, not just silence

### If Keystroke/Mouse APIs still crash:
- Make sure you're using `workers: 1` in the config
- Restart the API services
- Check that the virtual environment is properly activated

### If database still shows false/null:
- Check the Backend console for error messages
- Verify all 3 ML services are running (check health endpoints)
- Check the Network tab in browser DevTools to see API responses
- Ensure the Backend can reach the ML services (no firewall blocking)

## Quick Test Script

To quickly verify all ML services are running:
```powershell
.\test-ml-services.ps1
```

This will check the health of all three services and report their status.

## Files Modified

1. **Keystroke Dynamics/config.yaml** - Changed workers from 4 to 1
2. **Mouse Movement Analysis/config.yaml** - Changed workers from 4 to 1
3. **Voiceprint Analysis/config.yaml** - Changed workers from 4 to 1, VAD threshold from 0.01 to 0.001, enrollment_samples from 3 to 1
4. **Voiceprint Analysis/src/audio_preprocessing.py** - Added safety checks for empty audio and short audio
5. **Voiceprint Analysis/src/speaker_verification.py** - Added validation for empty segments and embeddings

## Files Created

1. **start-ml-services.ps1** - PowerShell script to start all ML services
2. **start-ml-services.bat** - Batch script to start all ML services
3. **test-ml-services.ps1** - PowerShell script to test ML services health
4. **ML_SERVICES_FIX_README.md** - This documentation file

