/**
 * CAMPUSAID - REACT FRONTEND EXAMPLE
 * ===================================
 * 
 * This is a React version of the frontend.
 * Use this if you want a more modern, component-based UI.
 * 
 * SETUP:
 * 1. Create React app: npx create-react-app campusaid-frontend
 * 2. Replace src/App.js with this file
 * 3. Install axios: npm install axios
 * 4. Run: npm start
 */

import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

// Backend API URL
const API_URL = 'http://localhost:8000';

function App() {
  // State for text complaint form
  const [textComplaint, setTextComplaint] = useState('');
  const [studentId, setStudentId] = useState('');
  const [textResult, setTextResult] = useState(null);
  const [textLoading, setTextLoading] = useState(false);

  // State for voice complaint form
  const [audioFile, setAudioFile] = useState(null);
  const [studentIdVoice, setStudentIdVoice] = useState('');
  const [voiceResult, setVoiceResult] = useState(null);
  const [voiceLoading, setVoiceLoading] = useState(false);

  /**
   * SUBMIT TEXT COMPLAINT
   * =====================
   * Sends text complaint to backend API
   */
  const handleTextSubmit = async (e) => {
    e.preventDefault();
    
    if (!textComplaint.trim()) {
      setTextResult({
        type: 'error',
        message: 'Please enter a complaint'
      });
      return;
    }

    setTextLoading(true);
    setTextResult(null);

    try {
      // Call backend API
      // This is where frontend talks to backend!
      const response = await axios.post(`${API_URL}/complaints`, {
        complaint_text: textComplaint,
        student_id: studentId || null
      });

      // Success!
      setTextResult({
        type: response.data.needs_manual_review ? 'warning' : 'success',
        data: response.data
      });

      // Clear form
      setTextComplaint('');
    } catch (error) {
      // Error
      setTextResult({
        type: 'error',
        message: error.response?.data?.detail || 'Connection error. Make sure backend is running.'
      });
    } finally {
      setTextLoading(false);
    }
  };

  /**
   * SUBMIT VOICE COMPLAINT
   * ======================
   * Sends audio file to backend API
   */
  const handleVoiceSubmit = async (e) => {
    e.preventDefault();

    if (!audioFile) {
      setVoiceResult({
        type: 'error',
        message: 'Please select an audio file'
      });
      return;
    }

    setVoiceLoading(true);
    setVoiceResult(null);

    try {
      // Prepare form data
      const formData = new FormData();
      formData.append('audio_file', audioFile);
      if (studentIdVoice) {
        formData.append('student_id', studentIdVoice);
      }

      // Call backend API
      const response = await axios.post(`${API_URL}/complaints/voice`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      // Success!
      setVoiceResult({
        type: response.data.needs_manual_review ? 'warning' : 'success',
        data: response.data
      });

      // Clear form
      setAudioFile(null);
      document.getElementById('audioFileInput').value = '';
    } catch (error) {
      // Error
      setVoiceResult({
        type: 'error',
        message: error.response?.data?.detail || 'Connection error. Make sure backend is running.'
      });
    } finally {
      setVoiceLoading(false);
    }
  };

  return (
    <div className="App">
      <div className="container">
        <h1>🎓 CampusAid</h1>
        <h1 className="text-5xl text-red-600">
  TEST UI CHANGE
</h1>
        <p className="subtitle">Multilingual Complaint Management System</p>

        <div className="info-box">
          <p><strong>Supported Languages:</strong> Hindi, English, Hinglish</p>
          <p><strong>Categories:</strong> Hostel, Academic, IT, Infrastructure, Harassment, Administration</p>
        </div>

        {/* TEXT COMPLAINT FORM */}
        <div className="form-section">
          <h2>📝 Submit Text Complaint</h2>
          <form onSubmit={handleTextSubmit}>
            <label>Student ID (Optional)</label>
            <input
              type="text"
              value={studentId}
              onChange={(e) => setStudentId(e.target.value)}
              placeholder="e.g., 2021CS001"
            />

            <label>Complaint *</label>
            <textarea
              value={textComplaint}
              onChange={(e) => setTextComplaint(e.target.value)}
              placeholder="Describe your complaint in Hindi, English, or Hinglish...&#10;Example: Hot water nahi aa raha hostel mein"
              required
            />

            <button type="submit" disabled={textLoading}>
              {textLoading ? 'Processing...' : 'Submit Complaint'}
            </button>
          </form>

          {/* Result Display */}
          {textResult && (
            <div className={`result ${textResult.type}`}>
              {textResult.data ? (
                <>
                  <h3>Complaint Submitted Successfully</h3>
                  <div className="result-details">
                    <strong>Category:</strong> {textResult.data.predicted_category}<br />
                    <strong>Confidence:</strong> {(textResult.data.confidence_score * 100).toFixed(1)}%<br />
                    <strong>Status:</strong> {textResult.data.needs_manual_review
                      ? '⚠️ Marked for manual review (low confidence)'
                      : '✅ Automatically classified'}
                  </div>
                </>
              ) : (
                <h3>{textResult.message}</h3>
              )}
            </div>
          )}
        </div>

        {/* VOICE COMPLAINT FORM */}
        <div className="form-section">
          <h2>🎤 Submit Voice Complaint</h2>
          <form onSubmit={handleVoiceSubmit}>
            <label>Student ID (Optional)</label>
            <input
              type="text"
              value={studentIdVoice}
              onChange={(e) => setStudentIdVoice(e.target.value)}
              placeholder="e.g., 2021CS001"
            />

            <label>Upload Audio File *</label>
            <input
              id="audioFileInput"
              type="file"
              accept="audio/*"
              onChange={(e) => setAudioFile(e.target.files[0])}
              required
            />
            <p style={{ fontSize: '12px', color: '#666', marginTop: '-10px' }}>
              Supported formats: MP3, WAV, M4A, etc.
            </p>

            <button type="submit" disabled={voiceLoading}>
              {voiceLoading ? 'Processing Audio...' : 'Submit Voice Complaint'}
            </button>
          </form>

          {/* Result Display */}
          {voiceResult && (
            <div className={`result ${voiceResult.type}`}>
              {voiceResult.data ? (
                <>
                  <h3>Voice Complaint Processed</h3>
                  <div className="result-details">
                    <strong>Transcribed Text:</strong> "{voiceResult.data.complaint_text}"<br />
                    <strong>Category:</strong> {voiceResult.data.predicted_category}<br />
                    <strong>Confidence:</strong> {(voiceResult.data.confidence_score * 100).toFixed(1)}%<br />
                    <strong>Status:</strong> {voiceResult.data.needs_manual_review
                      ? '⚠️ Marked for manual review'
                      : '✅ Automatically classified'}
                  </div>
                </>
              ) : (
                <h3>{voiceResult.message}</h3>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
