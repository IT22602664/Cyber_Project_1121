import express from 'express';
import {
  createSession,
  getSession,
  getDoctorSessions,
  updateSession,
  addVerificationLog
} from '../controllers/sessionController.js';
import { protect } from '../middleware/auth.js';

const router = express.Router();

router.post('/', protect, createSession);
router.get('/:sessionId', protect, getSession);
router.get('/doctor/:doctorId', protect, getDoctorSessions);
router.put('/:sessionId', protect, updateSession);
router.post('/:sessionId/verification', protect, addVerificationLog);

export default router;

