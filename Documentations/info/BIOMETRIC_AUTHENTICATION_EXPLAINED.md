# 🔐 3-Mode Biometric Authentication System - Complete Guide

**Zero Trust Telehealth Platform**  
**Date:** 2025-12-28

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Mode 1: Voiceprint Analysis](#mode-1-voiceprint-analysis)
3. [Mode 2: Keystroke Dynamics](#mode-2-keystroke-dynamics)
4. [Mode 3: Mouse Movement Analysis](#mode-3-mouse-movement-analysis)
5. [Database Storage Format](#database-storage-format)
6. [Complete Flow Diagrams](#complete-flow-diagrams)

---

## 🎯 System Overview

Your Zero Trust Telehealth Platform uses **3 independent biometric authentication modes** that work together to continuously verify doctor identity during medical consultations.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MERN BACKEND (Node.js)                   │
│                  MongoDB Database Storage                    │
└────────────┬────────────┬────────────┬─────────────────────┘
             │            │            │
    ┌────────▼───┐  ┌────▼─────┐  ┌──▼──────────┐
    │ Voice API  │  │Keystroke │  │  Mouse API  │
    │ Port: 8001 │  │   API    │  │ Port: 8003  │
    │  (Python)  │  │Port: 8002│  │  (Python)   │
    │            │  │ (Python) │  │             │
    └────────────┘  └──────────┘  └─────────────┘
```

### Key Features
- ✅ **Continuous Authentication** - Not just at login, but throughout the entire meeting
- ✅ **Multi-Modal** - 3 independent biometric systems
- ✅ **Real-time Verification** - Every 10-30 seconds during consultation
- ✅ **Adaptive Learning** - Templates update over time to prevent false rejections
- ✅ **Privacy-First** - Only embeddings stored, never raw biometric data

---

## 🎤 Mode 1: Voiceprint Analysis

### What It Does
Analyzes the doctor's voice to create a unique "voiceprint" (like a fingerprint, but for voice).

### Technology
- **Model:** ECAPA-TDNN (192-dimensional embeddings)
- **Anti-Spoofing:** CNN-based fake audio detection
- **API Port:** 8001

---

### 📝 REGISTRATION FLOW (When Doctor Signs Up)

#### Step 1: Doctor Registration Page
```
Doctor fills form:
├── First Name
├── Last Name
├── Email
├── Password
├── Medical License Number
├── Specialization
└── Years of Experience
```

#### Step 2: Voice Enrollment (After Registration)

**Frontend (React) captures voice:**
```javascript
// User clicks "Record Voice Sample"
// System records 3-5 audio samples (3-5 seconds each)

const enrollVoice = async () => {
  // 1. Record audio from microphone
  const audioBlob = await recordAudio(5000); // 5 seconds

  // 2. Send to backend
  const formData = new FormData();
  formData.append('audio_file', audioBlob);
  formData.append('doctor_id', doctorId);

  const response = await fetch('/api/verification/voice/enroll', {
    method: 'POST',
    body: formData
  });
}
```

**Backend (Node.js) processes:**
```javascript
// backend/services/mlService.js
async enrollVoice(userId, audioFilePath) {
  // Forward to Python Voice API
  const response = await axios.post(
    'http://localhost:8001/api/v1/enroll',
    {
      speaker_id: userId,
      audio_files: [audioFilePath1, audioFilePath2, audioFilePath3]
    }
  );

  // Returns: { voiceprint_template, enrollment_quality }
  return response.data;
}
```

**Python Voice API (Port 8001) processes:**
```python
# Voiceprint Analysis/src/speaker_verification.py

def enroll_speaker(speaker_id, audio_samples):
    # 1. Preprocess audio (noise reduction, VAD)
    segments = preprocess_audio(audio_samples)

    # 2. Extract embeddings using ECAPA-TDNN
    embeddings = []
    for segment in segments:
        embedding = ecapa_model.extract_embedding(segment)
        # embedding shape: (192,) - 192-dimensional vector
        embeddings.append(embedding)

    # 3. Create voiceprint template (average of all embeddings)
    voiceprint_template = np.mean(embeddings, axis=0)
    # voiceprint_template shape: (192,)

    # 4. Calculate enrollment quality
    enrollment_quality = calculate_quality(embeddings)

    # 5. Return template (will be saved to MongoDB)
    return {
        'speaker_id': speaker_id,
        'voiceprint_template': voiceprint_template.tolist(),  # Convert to list
        'enrollment_quality': enrollment_quality,
        'num_samples': len(audio_samples),
        'embedding_dim': 192
    }
```

**Backend saves to MongoDB:**
```javascript
// Update Doctor document
await Doctor.findByIdAndUpdate(doctorId, {
  'biometricData.voiceEnrolled': true,
  'biometricData.voiceEmbedding': JSON.stringify(voiceprint_template)
});
```

---

### 🔍 VERIFICATION FLOW (During Meeting - Continuous)

#### How It Works During Consultation

**Every 10-30 seconds during the meeting:**

```
1. Frontend captures audio chunk (2.5 seconds)
   ↓
2. Sends to Backend
   ↓
3. Backend forwards to Voice API (Port 8001)
   ↓
4. Voice API:
   - Extracts embedding from audio chunk
   - Compares with stored voiceprint template
   - Returns: verified (true/false) + confidence score
   ↓
5. Backend logs verification result
   ↓
6. Frontend updates trust score in real-time
```

**Detailed Verification Code:**

**Frontend (React):**
```javascript
// Continuous voice verification during meeting
const verifyVoiceContinuously = () => {
  setInterval(async () => {
    // Capture 2.5 second audio chunk
    const audioChunk = await captureAudioChunk(2500);

    // Send for verification
    const result = await fetch('/api/verification/voice', {
      method: 'POST',
      body: JSON.stringify({
        doctorId: currentDoctor.id,
        sessionId: currentSession.id,
        audioData: audioChunk
      })
    });

    const { verified, confidence } = await result.json();

    // Update UI
    updateTrustScore(verified, confidence);

  }, 10000); // Every 10 seconds
};
```

**Python Voice API Verification:**
```python
def verify_speaker(speaker_id, audio_path):
    # 1. Load stored voiceprint template from database
    stored_template = load_template(speaker_id)  # Shape: (192,)

    # 2. Extract embedding from new audio
    new_embedding = ecapa_model.extract_embedding(audio_path)  # Shape: (192,)

    # 3. Calculate similarity (cosine similarity)
    similarity = cosine_similarity(stored_template, new_embedding)
    # similarity range: 0.0 to 1.0

    # 4. Anti-spoofing check
    is_genuine = anti_spoofing_model.detect(audio_path)

    # 5. Make decision
    threshold = 0.65  # Configurable
    verified = (similarity >= threshold) and is_genuine

    return {
        'verified': verified,
        'confidence_score': similarity,
        'is_genuine': is_genuine,
        'latency_ms': processing_time
    }
```

---

## ⌨️ Mode 2: Keystroke Dynamics

### What It Does
Analyzes how the doctor types (timing between keystrokes, hold times, rhythm).

### Technology
- **Model:** Deep Neural Network (128-dimensional embeddings)
- **Features:** Hold times, DD times, UD times, typing rhythm
- **API Port:** 8002

---

### 📝 REGISTRATION FLOW

#### Step 1: Keystroke Enrollment (During/After Registration)

**Frontend captures typing patterns:**
```javascript
// Capture keystroke events while doctor types
const keystrokeBuffer = [];

document.addEventListener('keydown', (e) => {
  keystrokeBuffer.push({
    key: e.key,
    timestamp: Date.now(),
    type: 'keydown'
  });
});

document.addEventListener('keyup', (e) => {
  keystrokeBuffer.push({
    key: e.key,
    timestamp: Date.now(),
    type: 'keyup'
  });
});

// After collecting enough samples (e.g., typing password 5 times)
const enrollKeystroke = async () => {
  // Extract features from raw events
  const features = extractKeystrokeFeatures(keystrokeBuffer);

  await fetch('/api/verification/keystroke/enroll', {
    method: 'POST',
    body: JSON.stringify({
      doctorId: doctorId,
      keystroke_samples: features  // Array of feature vectors
    })
  });
};
```

**Feature Extraction (Frontend):**
```javascript
function extractKeystrokeFeatures(events) {
  const features = [];

  for (let i = 0; i < events.length - 1; i++) {
    if (events[i].type === 'keydown' && events[i+1].type === 'keyup') {
      // Hold time: time between keydown and keyup
      const holdTime = events[i+1].timestamp - events[i].timestamp;
      features.push(holdTime);
    }

    if (events[i].type === 'keydown' && events[i+1].type === 'keydown') {
      // DD time: time between two keydowns
      const ddTime = events[i+1].timestamp - events[i].timestamp;
      features.push(ddTime);
    }

    if (events[i].type === 'keyup' && events[i+1].type === 'keydown') {
      // UD time: time between keyup and next keydown
      const udTime = events[i+1].timestamp - events[i].timestamp;
      features.push(udTime);
    }
  }

  return features;  // Example: [120, 85, 95, 110, 78, ...]
}
```

**Python Keystroke API (Port 8002) processes:**
```python
# Keystroke Dynamics/src/keystroke_verification.py

def enroll_user(user_id, keystroke_samples):
    # keystroke_samples: List of feature vectors
    # Example: [[120, 85, 95, ...], [115, 88, 92, ...], ...]

    # 1. Convert to tensor
    samples_tensor = torch.FloatTensor(keystroke_samples)
    # Shape: (num_samples, num_features)

    # 2. Extract embeddings using DNN
    embeddings = []
    for sample in samples_tensor:
        embedding = keystroke_model(sample)
        # embedding shape: (128,) - 128-dimensional vector
        embeddings.append(embedding)

    # 3. Create template (mean embedding)
    keystroke_template = torch.mean(embeddings, dim=0)
    # keystroke_template shape: (128,)

    # 4. Store template
    return {
        'user_id': user_id,
        'keystroke_template': keystroke_template.tolist(),
        'num_samples': len(keystroke_samples),
        'embedding_dim': 128
    }
```

**Backend saves to MongoDB:**
```javascript
await Doctor.findByIdAndUpdate(doctorId, {
  'biometricData.keystrokeEnrolled': true,
  'biometricData.keystrokeProfile': JSON.stringify(keystroke_template)
});
```

---

### 🔍 VERIFICATION FLOW (During Meeting - Continuous)

**Every time doctor types during consultation:**

**Frontend:**
```javascript
// Continuous keystroke monitoring
let recentKeystrokes = [];

document.addEventListener('keydown', (e) => {
  recentKeystrokes.push({ key: e.key, timestamp: Date.now(), type: 'keydown' });

  // When we have enough keystrokes (e.g., 20 keys)
  if (recentKeystrokes.length >= 40) {  // 20 keydown + 20 keyup
    verifyKeystroke();
    recentKeystrokes = [];  // Reset
  }
});

const verifyKeystroke = async () => {
  const features = extractKeystrokeFeatures(recentKeystrokes);

  const result = await fetch('/api/verification/keystroke', {
    method: 'POST',
    body: JSON.stringify({
      doctorId: currentDoctor.id,
      sessionId: currentSession.id,
      keystroke_sample: features
    })
  });

  const { verified, confidence } = await result.json();
  updateTrustScore(verified, confidence);
};
```

**Python Keystroke API Verification:**
```python
def verify_user(user_id, keystroke_sample):
    # 1. Load stored template
    stored_template = load_template(user_id)  # Shape: (128,)

    # 2. Extract embedding from new sample
    sample_tensor = torch.FloatTensor(keystroke_sample)
    new_embedding = keystroke_model(sample_tensor)  # Shape: (128,)

    # 3. Calculate similarity
    similarity = cosine_similarity(stored_template, new_embedding)

    # 4. Make decision
    threshold = 0.70
    verified = similarity >= threshold

    # 5. Determine confidence level
    if similarity >= 0.85:
        confidence_level = "high"
    elif similarity >= 0.70:
        confidence_level = "medium"
    else:
        confidence_level = "low"

    return {
        'verified': verified,
        'confidence': similarity,
        'confidence_level': confidence_level,
        'alert': similarity < 0.65,
        'critical': similarity < 0.50
    }
```

---

## 🖱️ Mode 3: Mouse Movement Analysis

### What It Does
Analyzes how the doctor moves the mouse (speed, acceleration, curvature, click patterns).

### Technology
- **Model:** Siamese Neural Network (128-dimensional embeddings)
- **Features:** Velocity, acceleration, curvature, jerk, click dynamics
- **API Port:** 8003

---

### 📝 REGISTRATION FLOW

#### Step 1: Mouse Movement Enrollment

**Frontend captures mouse events:**
```javascript
// Capture mouse movements during registration/onboarding
const mouseEvents = [];

document.addEventListener('mousemove', (e) => {
  mouseEvents.push({
    timestamp: Date.now(),
    x: e.clientX,
    y: e.clientY,
    button: 'NoButton',
    state: 'Move'
  });
});

document.addEventListener('mousedown', (e) => {
  mouseEvents.push({
    timestamp: Date.now(),
    x: e.clientX,
    y: e.clientY,
    button: e.button === 0 ? 'Left' : 'Right',
    state: 'Pressed'
  });
});

document.addEventListener('mouseup', (e) => {
  mouseEvents.push({
    timestamp: Date.now(),
    x: e.clientX,
    y: e.clientY,
    button: e.button === 0 ? 'Left' : 'Right',
    state: 'Released'
  });
});

// After collecting enough events (e.g., 100-200 events)
const enrollMouse = async () => {
  await fetch('/api/verification/mouse/enroll', {
    method: 'POST',
    body: JSON.stringify({
      doctorId: doctorId,
      events: mouseEvents  // Array of mouse events
    })
  });
};
```

**Python Mouse API (Port 8003) processes:**
```python
# Mouse Movement Analysis/src/mouse_verification.py

def enroll_user(user_id, mouse_events):
    # mouse_events: List of {timestamp, x, y, button, state}

    # 1. Extract features from events
    features = extract_mouse_features(mouse_events)
    # Features include:
    # - Velocity (speed in x and y directions)
    # - Acceleration (rate of change of velocity)
    # - Curvature (how curved the mouse path is)
    # - Jerk (rate of change of acceleration)
    # - Click dynamics (time between clicks)
    # - Trajectory features (straightness, efficiency)

    # 2. Convert to tensor
    features_tensor = torch.FloatTensor(features)
    # Shape: (num_samples, num_features)

    # 3. Extract embeddings using Siamese Network
    embeddings = []
    for feature_vector in features_tensor:
        embedding = mouse_model(feature_vector)
        # embedding shape: (128,) - 128-dimensional vector
        embeddings.append(embedding)

    # 4. Create template (mean embedding)
    mouse_template = torch.mean(embeddings, dim=0)
    # mouse_template shape: (128,)

    # 5. Store template
    return {
        'user_id': user_id,
        'mouse_template': mouse_template.tolist(),
        'num_samples': len(features_tensor),
        'embedding_dim': 128
    }
```

**Backend saves to MongoDB:**
```javascript
await Doctor.findByIdAndUpdate(doctorId, {
  'biometricData.mouseEnrolled': true,
  'biometricData.mouseProfile': JSON.stringify(mouse_template)
});
```

---

### 🔍 VERIFICATION FLOW (During Meeting - Continuous)

**Continuous mouse monitoring (every 30 seconds):**

**Frontend:**
```javascript
// Continuous mouse movement monitoring
let recentMouseEvents = [];

document.addEventListener('mousemove', (e) => {
  recentMouseEvents.push({
    timestamp: Date.now(),
    x: e.clientX,
    y: e.clientY,
    button: 'NoButton',
    state: 'Move'
  });

  // When we have enough events (e.g., 50-100 events)
  if (recentMouseEvents.length >= 100) {
    verifyMouse();
    recentMouseEvents = [];  // Reset
  }
});

const verifyMouse = async () => {
  const result = await fetch('/api/verification/mouse', {
    method: 'POST',
    body: JSON.stringify({
      doctorId: currentDoctor.id,
      sessionId: currentSession.id,
      events: recentMouseEvents
    })
  });

  const { verified, confidence } = await result.json();
  updateTrustScore(verified, confidence);
};
```

**Python Mouse API Verification:**
```python
def verify_user(user_id, mouse_events):
    # 1. Load stored template
    stored_template = load_template(user_id)  # Shape: (128,)

    # 2. Extract features from new events
    features = extract_mouse_features(mouse_events)
    features_tensor = torch.FloatTensor(features)

    # 3. Extract embedding from new sample
    new_embedding = mouse_model(features_tensor)  # Shape: (128,)

    # 4. Calculate similarity
    similarity = cosine_similarity(stored_template, new_embedding)

    # 5. Make decision
    threshold = 0.85
    verified = similarity >= threshold

    # 6. Determine confidence level
    if similarity >= 0.85:
        confidence_level = "high"
    elif similarity >= 0.70:
        confidence_level = "medium"
    else:
        confidence_level = "low"

    return {
        'verified': verified,
        'confidence': similarity,
        'confidence_level': confidence_level,
        'alert': similarity < 0.65,
        'critical': similarity < 0.50
    }
```

---

## 💾 Database Storage Format

### MongoDB Collections

#### 1. **doctors** Collection (Main User Data)

**Document Structure:**
```json
{
  "_id": "ObjectId('507f1f77bcf86cd799439011')",
  "firstName": "John",
  "lastName": "Smith",
  "email": "john.smith@hospital.com",
  "password": "$2a$10$hashed_password_here",
  "medicalLicenseNumber": "MD123456",
  "specialization": "Cardiology",
  "yearsOfExperience": 10,

  "biometricData": {
    "voiceEnrolled": true,
    "voiceEmbedding": "[0.123, -0.456, 0.789, ..., 0.234]",  // 192 numbers (JSON string)

    "keystrokeEnrolled": true,
    "keystrokeProfile": "[0.567, 0.234, -0.123, ..., 0.890]",  // 128 numbers (JSON string)

    "mouseEnrolled": true,
    "mouseProfile": "[0.345, -0.678, 0.123, ..., 0.456]"  // 128 numbers (JSON string)
  },

  "isActive": true,
  "createdAt": "2025-12-28T10:30:00.000Z",
  "lastLogin": "2025-12-28T14:45:00.000Z"
}
```

**Storage Format Details:**

| Field | Type | Format | Size | Description |
|-------|------|--------|------|-------------|
| `voiceEmbedding` | String | JSON array | 192 floats | ECAPA-TDNN embedding |
| `keystrokeProfile` | String | JSON array | 128 floats | Keystroke DNN embedding |
| `mouseProfile` | String | JSON array | 128 floats | Mouse Siamese embedding |

**Important Notes:**
- ✅ **Only embeddings are stored** - Never raw audio, keystrokes, or mouse data
- ✅ **Encrypted** - Embeddings can be encrypted at rest
- ✅ **Privacy-compliant** - GDPR/HIPAA compliant (no PII in biometric data)
- ✅ **Compact** - Total biometric data: ~1.7 KB per doctor

---

#### 2. **sessions** Collection (Consultation Sessions)

**Document Structure:**
```json
{
  "_id": "ObjectId('507f1f77bcf86cd799439012')",
  "sessionId": "session_1735392000_abc123",
  "doctorId": "ObjectId('507f1f77bcf86cd799439011')",
  "patientId": "patient_12345",
  "startTime": "2025-12-28T15:00:00.000Z",
  "endTime": "2025-12-28T15:30:00.000Z",
  "status": "completed",

  "verificationLogs": [
    {
      "timestamp": "2025-12-28T15:00:10.000Z",
      "verificationType": "voice",
      "verified": true,
      "confidence": 0.87,
      "details": {
        "similarity": 0.87,
        "is_genuine": true,
        "latency_ms": 245
      }
    },
    {
      "timestamp": "2025-12-28T15:00:15.000Z",
      "verificationType": "keystroke",
      "verified": true,
      "confidence": 0.92,
      "details": {
        "similarity": 0.92,
        "confidence_level": "high"
      }
    },
    {
      "timestamp": "2025-12-28T15:00:20.000Z",
      "verificationType": "mouse",
      "verified": true,
      "confidence": 0.88,
      "details": {
        "similarity": 0.88,
        "confidence_level": "high"
      }
    }
  ],

  "alerts": [
    {
      "timestamp": "2025-12-28T15:15:30.000Z",
      "type": "low_confidence",
      "severity": "medium",
      "message": "Voice verification confidence dropped below 0.70",
      "details": {
        "verificationType": "voice",
        "confidence": 0.62
      }
    }
  ],

  "overallTrustScore": 85,

  "metadata": {
    "totalVerifications": 180,
    "voiceVerifications": 60,
    "keystrokeVerifications": 60,
    "mouseVerifications": 60,
    "averageConfidence": 0.85
  }
}
```

---

## 🔄 Complete Flow Diagrams

### Registration Flow (Complete)

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOCTOR REGISTRATION                          │
└─────────────────────────────────────────────────────────────────┘

Step 1: Basic Registration
┌──────────┐
│ Frontend │ Doctor fills form (name, email, password, etc.)
│ (React)  │ ──────────────────────────────────────────┐
└──────────┘                                            │
                                                        ▼
                                              ┌──────────────────┐
                                              │ Backend (Node.js)│
                                              │ Creates Doctor   │
                                              │ in MongoDB       │
                                              └──────────────────┘

Step 2: Voice Enrollment
┌──────────┐
│ Frontend │ Records 3-5 audio samples (3-5 sec each)
│ (React)  │ ──────────────────────────────────────────┐
└──────────┘                                            │
                                                        ▼
                                              ┌──────────────────┐
                                              │ Backend (Node.js)│
                                              │ Saves audio file │
                                              └────────┬─────────┘
                                                       │
                                                       ▼
                                              ┌──────────────────┐
                                              │ Voice API (8001) │
                                              │ - Preprocess     │
                                              │ - Extract 192-dim│
                                              │   embedding      │
                                              │ - Return template│
                                              └────────┬─────────┘
                                                       │
                                                       ▼
                                              ┌──────────────────┐
                                              │ Backend (Node.js)│
                                              │ Updates Doctor:  │
                                              │ voiceEmbedding   │
                                              └──────────────────┘

Step 3: Keystroke Enrollment
┌──────────┐
│ Frontend │ Captures typing patterns (password typed 5x)
│ (React)  │ ──────────────────────────────────────────┐
└──────────┘                                            │
                                                        ▼
                                              ┌──────────────────┐
                                              │ Backend (Node.js)│
                                              └────────┬─────────┘
                                                       │
                                                       ▼
                                              ┌──────────────────┐
                                              │Keystroke API     │
                                              │(8002)            │
                                              │ - Extract 128-dim│
                                              │   embedding      │
                                              │ - Return template│
                                              └────────┬─────────┘
                                                       │
                                                       ▼
                                              ┌──────────────────┐
                                              │ Backend (Node.js)│
                                              │ Updates Doctor:  │
                                              │keystrokeProfile  │
                                              └──────────────────┘

Step 4: Mouse Enrollment
┌──────────┐
│ Frontend │ Captures mouse movements (100-200 events)
│ (React)  │ ──────────────────────────────────────────┐
└──────────┘                                            │
                                                        ▼
                                              ┌──────────────────┐
                                              │ Backend (Node.js)│
                                              └────────┬─────────┘
                                                       │
                                                       ▼
                                              ┌──────────────────┐
                                              │ Mouse API (8003) │
                                              │ - Extract 128-dim│
                                              │   embedding      │
                                              │ - Return template│
                                              └────────┬─────────┘
                                                       │
                                                       ▼
                                              ┌──────────────────┐
                                              │ Backend (Node.js)│
                                              │ Updates Doctor:  │
                                              │ mouseProfile     │
                                              └──────────────────┘

✅ REGISTRATION COMPLETE - Doctor can now start consultations
```

---

### Continuous Verification Flow (During Meeting)

```
┌─────────────────────────────────────────────────────────────────┐
│              CONTINUOUS VERIFICATION DURING MEETING             │
└─────────────────────────────────────────────────────────────────┘

Doctor starts consultation → Session created in MongoDB

┌──────────────────────────────────────────────────────────────┐
│                    PARALLEL VERIFICATION                      │
│              (All 3 modes run simultaneously)                 │
└──────────────────────────────────────────────────────────────┘

Every 10-30 seconds:

┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   VOICE     │     │  KEYSTROKE  │     │    MOUSE    │
│ (when speak)│     │ (when type) │     │ (continuous)│
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       │ 2.5s audio        │ 20 keystrokes     │ 100 events
       │                   │                   │
       ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Voice API    │    │Keystroke API │    │  Mouse API   │
│ (Port 8001)  │    │ (Port 8002)  │    │ (Port 8003)  │
│              │    │              │    │              │
│ Extract      │    │ Extract      │    │ Extract      │
│ embedding    │    │ embedding    │    │ embedding    │
│              │    │              │    │              │
│ Compare with │    │ Compare with │    │ Compare with │
│ stored       │    │ stored       │    │ stored       │
│ template     │    │ template     │    │ template     │
│              │    │              │    │              │
│ Return:      │    │ Return:      │    │ Return:      │
│ verified=true│    │ verified=true│    │ verified=true│
│ confidence   │    │ confidence   │    │ confidence   │
│ =0.87        │    │ =0.92        │    │ =0.88        │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────────────┴───────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Backend (Node.js)│
                  │                  │
                  │ 1. Log to Session│
                  │    verificationLogs
                  │                  │
                  │ 2. Calculate     │
                  │    Trust Score   │
                  │    (0-100)       │
                  │                  │
                  │ 3. Check alerts  │
                  │    (if conf<0.70)│
                  └────────┬─────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Frontend (React) │
                  │                  │
                  │ Update UI:       │
                  │ - Trust Score    │
                  │ - Status Badges  │
                  │ - Alerts         │
                  └──────────────────┘

If confidence drops below threshold:
┌──────────────────────────────────────────────────────────┐
│                    ALERT SYSTEM                          │
└──────────────────────────────────────────────────────────┘

Confidence < 0.70 → ⚠️  Warning (Yellow badge)
Confidence < 0.60 → 🚨 Alert (Orange badge)
Confidence < 0.50 → 🔴 Critical (Red badge + session terminated)

Alert logged to session.alerts[]
Admin/Security team notified
```

---

## 📊 Summary Table

### Quick Reference

| Mode | Data Collected | Embedding Size | API Port | Verification Frequency | Threshold |
|------|---------------|----------------|----------|----------------------|-----------|
| **Voice** | Audio samples (3-5 sec) | 192 dimensions | 8001 | Every 10-30 sec (when speaking) | 0.65 |
| **Keystroke** | Typing patterns (hold/DD/UD times) | 128 dimensions | 8002 | Every 20 keystrokes | 0.70 |
| **Mouse** | Movement events (x, y, timestamp) | 128 dimensions | 8003 | Every 100 events (~30 sec) | 0.85 |

---

### Data Storage Summary

**Per Doctor in MongoDB:**
```
Basic Info: ~500 bytes
├── Name, email, license, etc.

Biometric Data: ~1.7 KB
├── Voice Embedding: 192 floats × 4 bytes = 768 bytes
├── Keystroke Profile: 128 floats × 4 bytes = 512 bytes
└── Mouse Profile: 128 floats × 4 bytes = 512 bytes

Total per doctor: ~2.2 KB
```

**Per Session in MongoDB:**
```
Session Info: ~200 bytes
├── Session ID, doctor ID, timestamps, status

Verification Logs: ~100 bytes per verification
├── Timestamp, type, verified, confidence, details
├── Average: 180 verifications per 30-min session
└── Total: ~18 KB per session

Alerts: ~50 bytes per alert
└── Variable (0-10 alerts per session)

Total per session: ~20 KB
```

---

## 🎯 Key Takeaways

### Registration (One-Time Setup)
1. **Voice:** Record 3-5 audio samples → Extract 192-dim embedding → Store in MongoDB
2. **Keystroke:** Type password 5 times → Extract 128-dim embedding → Store in MongoDB
3. **Mouse:** Move mouse naturally for 1-2 minutes → Extract 128-dim embedding → Store in MongoDB

### Verification (Continuous During Meeting)
1. **Voice:** Every 10-30 seconds when doctor speaks → Compare with stored template → Log result
2. **Keystroke:** Every 20 keystrokes → Compare with stored template → Log result
3. **Mouse:** Every 100 mouse events (~30 sec) → Compare with stored template → Log result

### Storage Format
- **Only embeddings stored** (never raw biometric data)
- **Compact:** ~2 KB per doctor
- **Privacy-compliant:** GDPR/HIPAA compliant
- **Encrypted:** Can be encrypted at rest

### Security Features
- ✅ **Continuous authentication** throughout entire session
- ✅ **Multi-modal** (3 independent verification systems)
- ✅ **Real-time alerts** when confidence drops
- ✅ **Adaptive templates** (prevent false rejections over time)
- ✅ **Anti-spoofing** (voice replay/synthetic detection)
- ✅ **Audit trail** (complete forensic log of all verifications)

---

## 📞 Need More Details?

For implementation details, see:
- **Voice:** `Voiceprint Analysis/README.md`
- **Keystroke:** `Keystroke Dynamics/README.md`
- **Mouse:** `Mouse Movement Analysis/README.md`
- **Backend:** `backend/services/mlService.js`
- **Database:** `backend/models/Doctor.js` and `backend/models/Session.js`

---

**Document Created:** 2025-12-28
**Zero Trust Telehealth Platform**
**Version:** 1.0

