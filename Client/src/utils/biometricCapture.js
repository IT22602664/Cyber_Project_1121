// Keystroke Dynamics Capture
export class KeystrokeCapture {
  constructor() {
    this.events = [];
    this.isRecording = false;
  }

  start() {
    this.events = [];
    this.isRecording = true;
  }

  stop() {
    this.isRecording = false;
    return this.getFeatures();
  }

  handleKeyDown(event) {
    if (!this.isRecording) return;
    
    this.events.push({
      key: event.key,
      type: 'keydown',
      timestamp: Date.now()
    });
  }

  handleKeyUp(event) {
    if (!this.isRecording) return;
    
    this.events.push({
      key: event.key,
      type: 'keyup',
      timestamp: Date.now()
    });
  }

  getFeatures() {
    const features = [];
    const holdTimes = [];
    const ddTimes = [];
    const udTimes = [];

    // Calculate timing features
    for (let i = 0; i < this.events.length - 1; i++) {
      const current = this.events[i];
      const next = this.events[i + 1];

      if (current.type === 'keydown' && next.type === 'keyup' && current.key === next.key) {
        // Hold time (H)
        holdTimes.push(next.timestamp - current.timestamp);
      }

      if (current.type === 'keydown' && next.type === 'keydown') {
        // Down-Down time (DD)
        ddTimes.push(next.timestamp - current.timestamp);
      }

      if (current.type === 'keyup' && next.type === 'keydown') {
        // Up-Down time (UD)
        udTimes.push(next.timestamp - current.timestamp);
      }
    }

    // Combine all features into a single vector
    features.push(...holdTimes, ...ddTimes, ...udTimes);

    // Pad or truncate to fixed length (31 features as per the ML model)
    while (features.length < 31) {
      features.push(0);
    }

    return features.slice(0, 31);
  }
}

// Mouse Movement Capture
export class MouseCapture {
  constructor() {
    this.events = [];
    this.isRecording = false;
  }

  start() {
    this.events = [];
    this.isRecording = true;
  }

  stop() {
    this.isRecording = false;
    return this.events;
  }

  handleMouseMove(event) {
    if (!this.isRecording) return;
    
    this.events.push({
      timestamp: Date.now() / 1000, // Convert to seconds
      x: event.clientX,
      y: event.clientY,
      button: 'NoButton',
      state: 'Move'
    });
  }

  handleMouseClick(event) {
    if (!this.isRecording) return;
    
    this.events.push({
      timestamp: Date.now() / 1000,
      x: event.clientX,
      y: event.clientY,
      button: event.button === 0 ? 'Left' : event.button === 2 ? 'Right' : 'Middle',
      state: 'Pressed'
    });
  }

  getEvents() {
    return this.events;
  }
}

// Voice Recording
export class VoiceCapture {
  constructor() {
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.stream = null;
  }

  async start() {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.mediaRecorder = new MediaRecorder(this.stream);
      this.audioChunks = [];

      this.mediaRecorder.ondataavailable = (event) => {
        this.audioChunks.push(event.data);
      };

      this.mediaRecorder.start();
      return true;
    } catch (error) {
      console.error('Failed to start voice recording:', error);
      return false;
    }
  }

  stop() {
    return new Promise((resolve) => {
      if (!this.mediaRecorder) {
        resolve(null);
        return;
      }

      this.mediaRecorder.onstop = () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
        
        // Stop all tracks
        if (this.stream) {
          this.stream.getTracks().forEach(track => track.stop());
        }
        
        resolve(audioBlob);
      };

      this.mediaRecorder.stop();
    });
  }
}

