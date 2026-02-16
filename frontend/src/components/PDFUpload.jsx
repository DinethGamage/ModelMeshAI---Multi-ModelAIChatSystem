import React, { useState } from 'react';
import { chatAPI } from '../services/api';
import './PDFUpload.css';

const PDFUpload = ({ sessionId, onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setError(null);
    } else {
      setFile(null);
      setError('Please select a PDF file');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await chatAPI.uploadPDF(file, sessionId);
      setSuccess(`✅ Uploaded: ${result.filename} (${result.chunks_stored} chunks)`);
      setFile(null);
      if (onUploadSuccess) {
        onUploadSuccess(result);
      }
      // Clear success message after 5 seconds
      setTimeout(() => setSuccess(null), 5000);
    } catch (err) {
      setError(`Upload failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="pdf-upload-container">
      <div className="upload-header">
        <h3>📄 Upload PDF Document</h3>
      </div>
      <div className="upload-body">
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          disabled={uploading}
          className="file-input"
        />
        {file && <div className="file-name">Selected: {file.name}</div>}
        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="upload-button"
        >
          {uploading ? '⏳ Uploading...' : '📤 Upload PDF'}
        </button>
        {error && <div className="upload-error">{error}</div>}
        {success && <div className="upload-success">{success}</div>}
      </div>
    </div>
  );
};

export default PDFUpload;
