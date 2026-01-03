import Session from '../models/Session.js';
import { v4 as uuidv4 } from 'uuid';

// @desc    Create a new session
// @route   POST /api/sessions
// @access  Private
export const createSession = async (req, res) => {
  try {
    const { patientId } = req.body;

    const session = await Session.create({
      sessionId: uuidv4(),
      doctorId: req.doctor._id,
      patientId: patientId || 'demo-patient',
      status: 'active'
    });

    res.status(201).json({
      success: true,
      message: 'Session created successfully',
      data: session
    });
  } catch (error) {
    console.error('Create session error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error',
      error: error.message
    });
  }
};

// @desc    Get session by ID
// @route   GET /api/sessions/:sessionId
// @access  Private
export const getSession = async (req, res) => {
  try {
    const session = await Session.findOne({ sessionId: req.params.sessionId })
      .populate('doctorId', 'firstName lastName specialization');

    if (!session) {
      return res.status(404).json({
        success: false,
        message: 'Session not found'
      });
    }

    res.json({
      success: true,
      data: session
    });
  } catch (error) {
    console.error('Get session error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error',
      error: error.message
    });
  }
};

// @desc    Get all sessions for a doctor
// @route   GET /api/sessions/doctor/:doctorId
// @access  Private
export const getDoctorSessions = async (req, res) => {
  try {
    const sessions = await Session.find({ doctorId: req.params.doctorId })
      .sort({ startTime: -1 })
      .limit(50);

    res.json({
      success: true,
      count: sessions.length,
      data: sessions
    });
  } catch (error) {
    console.error('Get doctor sessions error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error',
      error: error.message
    });
  }
};

// @desc    Update session status
// @route   PUT /api/sessions/:sessionId
// @access  Private
export const updateSession = async (req, res) => {
  try {
    const { status, endTime } = req.body;

    const session = await Session.findOne({ sessionId: req.params.sessionId });

    if (!session) {
      return res.status(404).json({
        success: false,
        message: 'Session not found'
      });
    }

    if (status) session.status = status;
    if (endTime) session.endTime = endTime;

    await session.save();

    res.json({
      success: true,
      message: 'Session updated successfully',
      data: session
    });
  } catch (error) {
    console.error('Update session error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error',
      error: error.message
    });
  }
};

// @desc    Add verification log to session
// @route   POST /api/sessions/:sessionId/verification
// @access  Private
export const addVerificationLog = async (req, res) => {
  try {
    const { verificationType, verified, confidence, details } = req.body;

    const session = await Session.findOne({ sessionId: req.params.sessionId });

    if (!session) {
      return res.status(404).json({
        success: false,
        message: 'Session not found'
      });
    }

    session.verificationLogs.push({
      verificationType,
      verified,
      confidence,
      details
    });

    // Update overall trust score
    const recentLogs = session.verificationLogs.slice(-10);
    const avgConfidence = recentLogs.reduce((sum, log) => sum + (log.confidence || 0), 0) / recentLogs.length;
    session.overallTrustScore = Math.round(avgConfidence * 100);

    // Check for suspicious activity
    if (avgConfidence < 0.5) {
      session.status = 'suspicious';
      session.alerts.push({
        type: 'low_trust_score',
        severity: 'high',
        message: 'Overall trust score dropped below 50%',
        details: { avgConfidence, trustScore: session.overallTrustScore }
      });
    }

    await session.save();

    res.json({
      success: true,
      message: 'Verification log added',
      data: session
    });
  } catch (error) {
    console.error('Add verification log error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error',
      error: error.message
    });
  }
};

