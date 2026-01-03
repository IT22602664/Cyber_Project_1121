import express from 'express';
import cors from 'cors';
import multer from 'multer';

const upload = multer({ storage: multer.memoryStorage() });

// Voice API - Port 8001
const voiceApp = express();
voiceApp.use(cors());
voiceApp.use(express.json());

voiceApp.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'voice-recognition' });
});

voiceApp.post('/enroll', upload.single('audio'), (req, res) => {
  const speakerId = req.body.speaker_id || 'speaker_' + Date.now();
  res.json({
    success: true,
    speaker_id: speakerId,
    embedding_id: 'emb_' + Math.random().toString(36).substr(2, 9),
    message: 'Voice enrolled successfully'
  });
});

voiceApp.post('/verify', upload.single('audio'), (req, res) => {
  const confidence = 0.85 + Math.random() * 0.15; // 0.85-1.0
  res.json({
    success: true,
    verified: confidence > 0.7,
    confidence: confidence,
    speaker_id: req.body.speaker_id,
    timestamp: new Date().toISOString()
  });
});

voiceApp.listen(8001, () => {
  console.log('✓ Mock Voice API running on http://localhost:8001');
});

// Keystroke API - Port 8002
const keystrokeApp = express();
keystrokeApp.use(cors());
keystrokeApp.use(express.json());

keystrokeApp.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'keystroke-dynamics' });
});

keystrokeApp.post('/enroll', (req, res) => {
  const userId = req.body.user_id || 'user_' + Date.now();
  res.json({
    success: true,
    user_id: userId,
    profile_id: 'prof_' + Math.random().toString(36).substr(2, 9),
    message: 'Keystroke profile created successfully'
  });
});

keystrokeApp.post('/verify', (req, res) => {
  const confidence = 0.88 + Math.random() * 0.12; // 0.88-1.0
  res.json({
    success: true,
    verified: confidence > 0.7,
    confidence: confidence,
    user_id: req.body.user_id,
    timestamp: new Date().toISOString()
  });
});

keystrokeApp.listen(8002, () => {
  console.log('✓ Mock Keystroke API running on http://localhost:8002');
});

// Mouse API - Port 8003
const mouseApp = express();
mouseApp.use(cors());
mouseApp.use(express.json());

mouseApp.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'mouse-movement' });
});

mouseApp.post('/enroll', (req, res) => {
  const userId = req.body.user_id || 'user_' + Date.now();
  res.json({
    success: true,
    user_id: userId,
    profile_id: 'mouse_' + Math.random().toString(36).substr(2, 9),
    message: 'Mouse profile created successfully'
  });
});

mouseApp.post('/verify', (req, res) => {
  const confidence = 0.82 + Math.random() * 0.18; // 0.82-1.0
  res.json({
    success: true,
    verified: confidence > 0.7,
    confidence: confidence,
    user_id: req.body.user_id,
    timestamp: new Date().toISOString()
  });
});

mouseApp.listen(8003, () => {
  console.log('✓ Mock Mouse API running on http://localhost:8003');
});

console.log('\n========================================');
console.log('Mock ML Services Started Successfully!');
console.log('========================================');
console.log('Voice API:     http://localhost:8001');
console.log('Keystroke API: http://localhost:8002');
console.log('Mouse API:     http://localhost:8003');
console.log('========================================\n');

