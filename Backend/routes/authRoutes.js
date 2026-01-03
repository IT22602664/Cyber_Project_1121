import express from 'express';
import { register, login } from '../controllers/authController.js';
import upload from '../middleware/upload.js';

const router = express.Router();

// Accept multiple voice samples (up to 5)
router.post('/register', upload.array('voiceSamples', 5), register);
router.post('/login', login);

export default router;

