import express from 'express';
import { 
  getMe, 
  getAllDoctors, 
  getDoctorById, 
  updateDoctor 
} from '../controllers/doctorController.js';
import { protect } from '../middleware/auth.js';

const router = express.Router();

router.get('/me', protect, getMe);
router.get('/', protect, getAllDoctors);
router.get('/:id', protect, getDoctorById);
router.put('/:id', protect, updateDoctor);

export default router;

