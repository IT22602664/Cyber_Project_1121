import mongoose from 'mongoose';

const verificationLogSchema = new mongoose.Schema({
  timestamp: {
    type: Date,
    default: Date.now
  },
  verificationType: {
    type: String,
    enum: ['voice', 'keystroke', 'mouse', 'combined'],
    required: true
  },
  verified: {
    type: Boolean,
    required: true
  },
  confidence: {
    type: Number,
    min: 0,
    max: 1
  },
  details: {
    type: mongoose.Schema.Types.Mixed
  }
});

const sessionSchema = new mongoose.Schema({
  sessionId: {
    type: String,
    required: true,
    unique: true
  },
  doctorId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Doctor',
    required: true
  },
  patientId: {
    type: String,
    default: 'demo-patient' // For demo purposes
  },
  startTime: {
    type: Date,
    default: Date.now
  },
  endTime: {
    type: Date,
    default: null
  },
  status: {
    type: String,
    enum: ['active', 'completed', 'terminated', 'suspicious'],
    default: 'active'
  },
  verificationLogs: [verificationLogSchema],
  alerts: [{
    timestamp: Date,
    type: String,
    severity: {
      type: String,
      enum: ['low', 'medium', 'high', 'critical']
    },
    message: String,
    details: mongoose.Schema.Types.Mixed
  }],
  overallTrustScore: {
    type: Number,
    min: 0,
    max: 100,
    default: 100
  },
  metadata: {
    type: mongoose.Schema.Types.Mixed,
    default: {}
  }
});

// Index for faster queries
sessionSchema.index({ doctorId: 1, startTime: -1 });
sessionSchema.index({ sessionId: 1 });

const Session = mongoose.model('Session', sessionSchema);

export default Session;

