import Doctor from '../models/Doctor.js';
import { generateToken } from '../middleware/auth.js';
import mlService from '../services/mlService.js';
import fs from 'fs';

// @desc    Register a new doctor
// @route   POST /api/auth/register
// @access  Public
export const register = async (req, res) => {
  try {
    const {
      firstName,
      lastName,
      email,
      password,
      medicalLicenseNumber,
      specialization,
      yearsOfExperience,
      keystrokePattern,
      mousePattern
    } = req.body;

    // Check if doctor already exists
    const doctorExists = await Doctor.findOne({ 
      $or: [{ email }, { medicalLicenseNumber }] 
    });

    if (doctorExists) {
      return res.status(400).json({
        success: false,
        message: 'Doctor with this email or license number already exists'
      });
    }

    // Create doctor
    const doctor = await Doctor.create({
      firstName,
      lastName,
      email,
      password,
      medicalLicenseNumber,
      specialization,
      yearsOfExperience
    });

    // Enroll biometric data
    const biometricResults = {
      voice: false,
      keystroke: false,
      mouse: false
    };

    // Enroll voice if audio file provided
    if (req.file) {
      try {
        const voiceResult = await mlService.enrollVoice(doctor._id.toString(), req.file.path);
        doctor.biometricData.voiceEnrolled = true;
        doctor.biometricData.voiceEmbedding = doctor._id.toString();
        biometricResults.voice = true;
        
        // Clean up uploaded file
        fs.unlinkSync(req.file.path);
      } catch (error) {
        console.error('Voice enrollment failed:', error.message);
      }
    }

    // Enroll keystroke pattern
    if (keystrokePattern) {
      try {
        const keystrokeData = JSON.parse(keystrokePattern);
        const keystrokeResult = await mlService.enrollKeystroke(
          doctor._id.toString(),
          keystrokeData
        );
        doctor.biometricData.keystrokeEnrolled = true;
        doctor.biometricData.keystrokeProfile = doctor._id.toString();
        biometricResults.keystroke = true;
      } catch (error) {
        console.error('Keystroke enrollment failed:', error.message);
      }
    }

    // Enroll mouse pattern
    if (mousePattern) {
      try {
        const mouseData = JSON.parse(mousePattern);
        const mouseResult = await mlService.enrollMouse(
          doctor._id.toString(),
          mouseData
        );
        doctor.biometricData.mouseEnrolled = true;
        doctor.biometricData.mouseProfile = doctor._id.toString();
        biometricResults.mouse = true;
      } catch (error) {
        console.error('Mouse enrollment failed:', error.message);
      }
    }

    await doctor.save();

    res.status(201).json({
      success: true,
      message: 'Doctor registered successfully',
      data: {
        doctor: {
          id: doctor._id,
          firstName: doctor.firstName,
          lastName: doctor.lastName,
          email: doctor.email,
          medicalLicenseNumber: doctor.medicalLicenseNumber,
          specialization: doctor.specialization,
          yearsOfExperience: doctor.yearsOfExperience,
          biometricData: doctor.biometricData
        },
        biometricResults,
        token: generateToken(doctor._id)
      }
    });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error during registration',
      error: error.message
    });
  }
};

// @desc    Login doctor
// @route   POST /api/auth/login
// @access  Public
export const login = async (req, res) => {
  try {
    const { email, password } = req.body;

    // Validate input
    if (!email || !password) {
      return res.status(400).json({
        success: false,
        message: 'Please provide email and password'
      });
    }

    // Check for doctor (include password for comparison)
    const doctor = await Doctor.findOne({ email }).select('+password');

    if (!doctor) {
      return res.status(401).json({
        success: false,
        message: 'Invalid credentials'
      });
    }

    // Check password
    const isMatch = await doctor.comparePassword(password);

    if (!isMatch) {
      return res.status(401).json({
        success: false,
        message: 'Invalid credentials'
      });
    }

    // Update last login
    doctor.lastLogin = new Date();
    await doctor.save();

    res.json({
      success: true,
      message: 'Login successful',
      data: {
        doctor: {
          id: doctor._id,
          firstName: doctor.firstName,
          lastName: doctor.lastName,
          email: doctor.email,
          medicalLicenseNumber: doctor.medicalLicenseNumber,
          specialization: doctor.specialization,
          yearsOfExperience: doctor.yearsOfExperience,
          biometricData: doctor.biometricData
        },
        token: generateToken(doctor._id)
      }
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error during login',
      error: error.message
    });
  }
};

