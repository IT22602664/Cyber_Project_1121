import { useState, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { Shield, User, Mail, Lock, FileText, Briefcase, Calendar, Mic, Keyboard, Mouse } from 'lucide-react';
import { KeystrokeCapture, MouseCapture, VoiceCapture } from '../utils/biometricCapture';

const Register = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    medicalLicenseNumber: '',
    specialization: '',
    yearsOfExperience: '',
  });

  // Biometric data
  const [voiceBlob, setVoiceBlob] = useState(null);
  const [keystrokeData, setKeystrokeData] = useState([]);
  const [mouseData, setMouseData] = useState([]);
  
  // Capture instances
  const keystrokeCapture = useRef(new KeystrokeCapture());
  const mouseCapture = useRef(new MouseCapture());
  const voiceCapture = useRef(new VoiceCapture());
  
  // Recording states
  const [isRecordingVoice, setIsRecordingVoice] = useState(false);
  const [isCapturingKeystroke, setIsCapturingKeystroke] = useState(false);
  const [isCapturingMouse, setIsCapturingMouse] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleNext = () => {
    // Validate current step
    if (step === 1) {
      if (!formData.firstName || !formData.lastName || !formData.email || 
          !formData.password || !formData.confirmPassword) {
        toast.error('Please fill in all fields');
        return;
      }
      if (formData.password !== formData.confirmPassword) {
        toast.error('Passwords do not match');
        return;
      }
      if (formData.password.length < 6) {
        toast.error('Password must be at least 6 characters');
        return;
      }
    }
    
    if (step === 2) {
      if (!formData.medicalLicenseNumber || !formData.specialization || !formData.yearsOfExperience) {
        toast.error('Please fill in all professional details');
        return;
      }
    }
    
    setStep(step + 1);
  };

  const handleBack = () => {
    setStep(step - 1);
  };

  // Voice Recording
  const startVoiceRecording = async () => {
    const started = await voiceCapture.current.start();
    if (started) {
      setIsRecordingVoice(true);
      toast.success('Recording... Please speak for 5-10 seconds');
    } else {
      toast.error('Failed to access microphone');
    }
  };

  const stopVoiceRecording = async () => {
    const blob = await voiceCapture.current.stop();
    setVoiceBlob(blob);
    setIsRecordingVoice(false);
    toast.success('Voice sample captured!');
  };

  // Keystroke Capture
  const startKeystrokeCapture = () => {
    keystrokeCapture.current.start();
    setIsCapturingKeystroke(true);
    toast.success('Type the following phrase: "The quick brown fox jumps over the lazy dog"');
  };

  const stopKeystrokeCapture = () => {
    const features = keystrokeCapture.current.stop();
    // Collect multiple samples
    setKeystrokeData(prev => [...prev, features]);
    setIsCapturingKeystroke(false);
    toast.success(`Keystroke sample ${keystrokeData.length + 1} captured!`);
  };

  // Mouse Capture
  const startMouseCapture = () => {
    mouseCapture.current.start();
    setIsCapturingMouse(true);
    toast.success('Move your mouse naturally for 10 seconds');
  };

  const stopMouseCapture = () => {
    const events = mouseCapture.current.stop();
    setMouseData(events);
    setIsCapturingMouse(false);
    toast.success('Mouse pattern captured!');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!voiceBlob) {
      toast.error('Please record a voice sample');
      return;
    }
    
    if (keystrokeData.length < 3) {
      toast.error('Please capture at least 3 keystroke samples');
      return;
    }
    
    if (mouseData.length === 0) {
      toast.error('Please capture a mouse movement pattern');
      return;
    }

    setLoading(true);

    try {
      const submitData = new FormData();
      submitData.append('firstName', formData.firstName);
      submitData.append('lastName', formData.lastName);
      submitData.append('email', formData.email);
      submitData.append('password', formData.password);
      submitData.append('medicalLicenseNumber', formData.medicalLicenseNumber);
      submitData.append('specialization', formData.specialization);
      submitData.append('yearsOfExperience', formData.yearsOfExperience);
      submitData.append('voiceSample', voiceBlob, 'voice-sample.wav');
      submitData.append('keystrokePattern', JSON.stringify(keystrokeData));
      submitData.append('mousePattern', JSON.stringify(mouseData));

      await register(submitData);
      toast.success('Registration successful!');
      navigate('/dashboard');
    } catch (error) {
      console.error('Registration error:', error);
      toast.error(error.response?.data?.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-8">
          <div className="flex justify-center">
            <div className="bg-primary-600 p-3 rounded-full">
              <Shield className="h-12 w-12 text-white" />
            </div>
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Doctor Registration
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Step {step} of 3
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-xl p-8">
          <form onSubmit={handleSubmit}>
            {/* Step 1: Personal Information */}
            {step === 1 && (
              <div className="space-y-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Personal Information</h3>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">First Name</label>
                    <input
                      type="text"
                      name="firstName"
                      value={formData.firstName}
                      onChange={handleChange}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Last Name</label>
                    <input
                      type="text"
                      name="lastName"
                      value={formData.lastName}
                      onChange={handleChange}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Email Address</label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Password</label>
                    <input
                      type="password"
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Confirm Password</label>
                    <input
                      type="password"
                      name="confirmPassword"
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                      required
                    />
                  </div>
                </div>

                <button
                  type="button"
                  onClick={handleNext}
                  className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  Next
                </button>
              </div>
            )}

            {/* Step 2: Professional Information */}
            {step === 2 && (
              <div className="space-y-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Professional Information</h3>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Medical License Number</label>
                  <input
                    type="text"
                    name="medicalLicenseNumber"
                    value={formData.medicalLicenseNumber}
                    onChange={handleChange}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Specialization</label>
                  <input
                    type="text"
                    name="specialization"
                    value={formData.specialization}
                    onChange={handleChange}
                    placeholder="e.g., Cardiology, Pediatrics"
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Years of Experience</label>
                  <input
                    type="number"
                    name="yearsOfExperience"
                    value={formData.yearsOfExperience}
                    onChange={handleChange}
                    min="0"
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    required
                  />
                </div>

                <div className="flex gap-4">
                  <button
                    type="button"
                    onClick={handleBack}
                    className="flex-1 py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    Back
                  </button>
                  <button
                    type="button"
                    onClick={handleNext}
                    className="flex-1 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}

            {/* Step 3: Biometric Enrollment */}
            {step === 3 && (
              <div className="space-y-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Biometric Enrollment</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Please provide biometric samples for continuous authentication during consultations.
                </p>

                {/* Voice Sample */}
                <div className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center">
                      <Mic className="h-5 w-5 text-primary-600 mr-2" />
                      <h4 className="font-medium">Voice Sample</h4>
                    </div>
                    {voiceBlob && <span className="text-green-600 text-sm">✓ Captured</span>}
                  </div>
                  <p className="text-sm text-gray-600 mb-3">Record your voice for 5-10 seconds</p>
                  <button
                    type="button"
                    onClick={isRecordingVoice ? stopVoiceRecording : startVoiceRecording}
                    className={`w-full py-2 px-4 rounded-md text-sm font-medium ${
                      isRecordingVoice
                        ? 'bg-red-600 hover:bg-red-700 text-white'
                        : 'bg-primary-600 hover:bg-primary-700 text-white'
                    }`}
                  >
                    {isRecordingVoice ? 'Stop Recording' : 'Start Recording'}
                  </button>
                </div>

                {/* Keystroke Pattern */}
                <div className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center">
                      <Keyboard className="h-5 w-5 text-primary-600 mr-2" />
                      <h4 className="font-medium">Keystroke Pattern</h4>
                    </div>
                    <span className="text-sm text-gray-600">{keystrokeData.length}/3 samples</span>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">Capture 3 typing samples</p>
                  {isCapturingKeystroke && (
                    <textarea
                      className="w-full p-2 border border-gray-300 rounded-md mb-2"
                      rows="3"
                      placeholder="Type here..."
                      onKeyDown={(e) => keystrokeCapture.current.handleKeyDown(e)}
                      onKeyUp={(e) => keystrokeCapture.current.handleKeyUp(e)}
                    />
                  )}
                  <button
                    type="button"
                    onClick={isCapturingKeystroke ? stopKeystrokeCapture : startKeystrokeCapture}
                    disabled={keystrokeData.length >= 3}
                    className="w-full py-2 px-4 rounded-md text-sm font-medium bg-primary-600 hover:bg-primary-700 text-white disabled:opacity-50"
                  >
                    {isCapturingKeystroke ? 'Stop Capture' : 'Start Capture'}
                  </button>
                </div>

                {/* Mouse Pattern */}
                <div className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center">
                      <Mouse className="h-5 w-5 text-primary-600 mr-2" />
                      <h4 className="font-medium">Mouse Movement Pattern</h4>
                    </div>
                    {mouseData.length > 0 && <span className="text-green-600 text-sm">✓ Captured</span>}
                  </div>
                  <p className="text-sm text-gray-600 mb-3">Move your mouse naturally for 10 seconds</p>
                  {isCapturingMouse && (
                    <div
                      className="w-full h-32 bg-gray-100 rounded-md mb-2 cursor-crosshair"
                      onMouseMove={(e) => mouseCapture.current.handleMouseMove(e)}
                      onClick={(e) => mouseCapture.current.handleMouseClick(e)}
                    >
                      <p className="text-center pt-12 text-gray-500">Move your mouse here</p>
                    </div>
                  )}
                  <button
                    type="button"
                    onClick={isCapturingMouse ? stopMouseCapture : startMouseCapture}
                    className="w-full py-2 px-4 rounded-md text-sm font-medium bg-primary-600 hover:bg-primary-700 text-white"
                  >
                    {isCapturingMouse ? 'Stop Capture' : 'Start Capture'}
                  </button>
                </div>

                <div className="flex gap-4">
                  <button
                    type="button"
                    onClick={handleBack}
                    className="flex-1 py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                  >
                    Back
                  </button>
                  <button
                    type="submit"
                    disabled={loading || !voiceBlob || keystrokeData.length < 3 || mouseData.length === 0}
                    className="flex-1 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50"
                  >
                    {loading ? 'Registering...' : 'Complete Registration'}
                  </button>
                </div>
              </div>
            )}
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Already have an account?{' '}
              <Link to="/login" className="font-medium text-primary-600 hover:text-primary-500">
                Sign in here
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;

