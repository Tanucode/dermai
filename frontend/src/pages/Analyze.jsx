/**
 * pages/Analyze.jsx
 * -------------------
 * The core page — where users upload or capture their face photo.
 * 
 * CONCEPT — React State (useState):
 *   State = data that can change and causes the UI to re-render.
 *   const [image, setImage] = useState(null)
 *   - image = current value
 *   - setImage = function to update it
 *   - useState(null) = initial value is null
 * 
 * CONCEPT — useCallback:
 *   Memoizes a function so it doesn't get recreated on every render.
 *   Used with react-dropzone which expects a stable callback reference.
 * 
 * CONCEPT — useNavigate:
 *   React Router hook to programmatically change pages.
 *   navigate('/results') = go to results page.
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { analyzeSkin } from '../services/api';

function Analyze() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [error, setError] = useState(null);
  const [useCamera, setUseCamera] = useState(false);
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const navigate = useNavigate();

  const analysisSteps = [
    { text: 'Uploading image...', icon: '📤' },
    { text: 'Detecting skin features...', icon: '🔬' },
    { text: 'Analyzing with Gemini AI...', icon: '🧠' },
    { text: 'Searching knowledge base (RAG)...', icon: '📚' },
    { text: 'Generating recommendations...', icon: '✨' },
    { text: 'Building your report...', icon: '📋' },
  ];

  // ── Dropzone handler ──────────────────────────────────────
  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setError(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.jpeg', '.jpg', '.png', '.webp'] },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB max
  });

  // ── Camera functions ──────────────────────────────────────
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } }
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setUseCamera(true);
      setError(null);
    } catch (err) {
      setError('Camera access denied. Please allow camera access or upload a photo instead.');
    }
  };

  const capturePhoto = () => {
    if (!videoRef.current) return;
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(videoRef.current, 0, 0);

    canvas.toBlob((blob) => {
      const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(blob));
      stopCamera();
    }, 'image/jpeg', 0.9);
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setUseCamera(false);
  };

  // Cleanup camera on unmount
  useEffect(() => {
    return () => { stopCamera(); };
  }, []);

  // ── Submit for analysis ───────────────────────────────────
  const handleAnalyze = async () => {
    if (!selectedFile) return;
    setIsAnalyzing(true);
    setCurrentStep(0);
    setError(null);

    // Animate through steps
    const stepInterval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev < analysisSteps.length - 1) return prev + 1;
        return prev;
      });
    }, 3000);

    try {
      const result = await analyzeSkin(selectedFile);
      clearInterval(stepInterval);

      // Store result in sessionStorage for the Results page
      sessionStorage.setItem('dermai_result', JSON.stringify(result));
      navigate('/results');
    } catch (err) {
      clearInterval(stepInterval);
      setIsAnalyzing(false);
      console.error('Analysis error:', err);

      if (err.response?.status === 400) {
        setError(err.response.data.detail || 'Invalid image. Please upload a clear face photo.');
      } else {
        setError('Analysis failed. Please check your internet connection and try again.');
      }
    }
  };

  const removeImage = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setError(null);
  };

  return (
    <>
      <div className="analyze-page">
        <motion.div
          className="analyze-content"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1>
            <span className="gradient-text">Analyze</span> Your Skin
          </h1>
          <p className="analyze-subtitle">
            Upload a clear face photo or use your camera. Our AI will detect skin
            conditions and create a personalized skincare plan.
          </p>

          {/* Error message */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              style={{
                padding: '14px 20px',
                background: 'rgba(244, 63, 94, 0.1)',
                border: '1px solid rgba(244, 63, 94, 0.3)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--accent-light)',
                fontSize: '0.9rem',
                marginBottom: '24px'
              }}
            >
              ⚠️ {error}
            </motion.div>
          )}

          {/* Camera view */}
          {useCamera && !selectedFile && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              style={{ marginBottom: '24px' }}
            >
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                style={{
                  width: '100%',
                  maxWidth: '500px',
                  borderRadius: 'var(--radius-lg)',
                  border: '2px solid var(--border)',
                  transform: 'scaleX(-1)' // Mirror for selfie
                }}
              />
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', marginTop: '16px' }}>
                <button className="btn btn-primary" onClick={capturePhoto}>
                  📸 Capture Photo
                </button>
                <button className="btn btn-secondary" onClick={stopCamera}>
                  ✕ Cancel
                </button>
              </div>
            </motion.div>
          )}

          {/* Upload zone (hidden when camera is active) */}
          {!useCamera && !selectedFile && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <div
                {...getRootProps()}
                className={`upload-zone ${isDragActive ? 'drag-active' : ''}`}
              >
                <input {...getInputProps()} />
                <div className="upload-zone-icon">📷</div>
                <h3>Drop your photo here</h3>
                <p>or click to browse files</p>
                <p className="upload-formats">Supports: JPG, PNG, WebP • Max 10MB</p>
              </div>

              <div style={{ marginTop: '20px' }}>
                <button className="btn btn-secondary" onClick={startCamera}>
                  📹 Use Camera Instead
                </button>
              </div>
            </motion.div>
          )}

          {/* Image preview */}
          {selectedFile && previewUrl && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ type: 'spring', stiffness: 200 }}
            >
              <div className="image-preview">
                <img src={previewUrl} alt="Your face photo" />
                <button className="image-preview-remove" onClick={removeImage}>
                  ✕
                </button>
              </div>

              <div className="analyze-button-container">
                <button
                  className="btn btn-accent"
                  onClick={handleAnalyze}
                  style={{ fontSize: '1.05rem', padding: '16px 48px' }}
                >
                  🔬 Analyze My Skin
                </button>
              </div>
            </motion.div>
          )}

          {/* Tips */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            style={{
              marginTop: '48px',
              padding: '24px',
              background: 'var(--bg-glass)',
              borderRadius: 'var(--radius-lg)',
              border: '1px solid var(--border)',
              textAlign: 'left'
            }}
          >
            <h3 style={{ fontSize: '1rem', marginBottom: '12px' }}>📌 Tips for best results:</h3>
            <ul style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', lineHeight: '1.8', paddingLeft: '20px' }}>
              <li>Use natural daylight — avoid harsh flash</li>
              <li>Remove glasses and move hair away from face</li>
              <li>Face the camera directly with a neutral expression</li>
              <li>No filters or beauty mode — we need the real picture</li>
              <li>Clean face preferred — remove makeup if possible</li>
            </ul>
          </motion.div>
        </motion.div>
      </div>

      {/* ── Analyzing Overlay ──────────────────────────────── */}
      <AnimatePresence>
        {isAnalyzing && (
          <motion.div
            className="analyzing-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className="analyzing-content"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <div className="analyzing-spinner" />
              <h2 style={{ marginBottom: '8px' }}>Analyzing Your Skin</h2>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '24px', fontSize: '0.9rem' }}>
                This takes about 15-30 seconds...
              </p>

              <ul className="analyzing-steps">
                {analysisSteps.map((step, index) => (
                  <li
                    key={index}
                    className={`analyzing-step ${index === currentStep ? 'active' : ''} ${index < currentStep ? 'done' : ''}`}
                  >
                    <span className="analyzing-step-icon">
                      {index < currentStep ? '✅' : step.icon}
                    </span>
                    {step.text}
                  </li>
                ))}
              </ul>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

export default Analyze;
