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
    const holdTimes = [];
    const ddTimes = [];
    const udTimes = [];

    // Calculate timing features
    for (let i = 0; i < this.events.length - 1; i++) {
      const current = this.events[i];
      const next = this.events[i + 1];

      if (current.type === 'keydown' && next.type === 'keyup' && current.key === next.key) {
        // Hold time (H) - convert to seconds
        holdTimes.push((next.timestamp - current.timestamp) / 1000);
      }

      if (current.type === 'keydown' && next.type === 'keydown') {
        // Down-Down time (DD) - convert to seconds
        ddTimes.push((next.timestamp - current.timestamp) / 1000);
      }

      if (current.type === 'keyup' && next.type === 'keydown') {
        // Up-Down time (UD) - convert to seconds
        udTimes.push((next.timestamp - current.timestamp) / 1000);
      }
    }

    // Combine timing features into a single vector
    const timingFeatures = [...holdTimes, ...ddTimes, ...udTimes];

    // Pad or truncate to fixed length (31 timing features)
    while (timingFeatures.length < 31) {
      timingFeatures.push(0);
    }
    const paddedTimingFeatures = timingFeatures.slice(0, 31);

    // Calculate statistical features (7 features: mean, std, median, min, max, q25, q75)
    const stats = this.calculateStatistics(paddedTimingFeatures);

    // Combine timing features (31) + statistical features (7) = 38 total
    return [...paddedTimingFeatures, ...stats];
  }

  calculateStatistics(features) {
    if (features.length === 0) {
      return [0, 0, 0, 0, 0, 0, 0];
    }

    const validFeatures = features.filter(f => f > 0);
    if (validFeatures.length === 0) {
      return [0, 0, 0, 0, 0, 0, 0];
    }

    const sorted = [...validFeatures].sort((a, b) => a - b);
    const sum = validFeatures.reduce((a, b) => a + b, 0);
    const mean = sum / validFeatures.length;

    // Standard deviation
    const variance = validFeatures.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / validFeatures.length;
    const std = Math.sqrt(variance);

    // Median
    const mid = Math.floor(sorted.length / 2);
    const median = sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid];

    // Min and Max
    const min = sorted[0];
    const max = sorted[sorted.length - 1];

    // Quartiles
    const q1Index = Math.floor(sorted.length * 0.25);
    const q3Index = Math.floor(sorted.length * 0.75);
    const q25 = sorted[q1Index];
    const q75 = sorted[q3Index];

    return [mean, std, median, min, max, q25, q75];
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

