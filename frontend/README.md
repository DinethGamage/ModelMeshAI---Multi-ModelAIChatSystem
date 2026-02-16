# Multi-Model AI Chat - React Frontend

Beautiful and responsive React UI for the Multi-Model AI Chat System.

## Features

- 💬 Real-time chat interface
- 🎨 Modern, gradient design
- 📄 PDF upload with drag-and-drop
- 🎯 Routing metadata display
- 🔄 Session management
- 📱 Responsive design
- ⚡ Fast and lightweight

## Setup

### Install Dependencies

```bash
cd frontend
npm install
```

### Run Development Server

```bash
npm run dev
```

The UI will be available at: http://localhost:3000

### Build for Production

```bash
npm run build
```

## Configuration

The frontend connects to the backend at `http://localhost:8000` by default.

To change this, edit `src/services/api.js`:

```javascript
const API_BASE_URL = 'your-backend-url';
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatInterface.jsx    # Main chat component
│   │   ├── Message.jsx           # Message display
│   │   ├── PDFUpload.jsx         # PDF upload
│   │   └── *.css                 # Component styles
│   ├── services/
│   │   └── api.js                # Backend API integration
│   ├── App.jsx                   # Root component
│   ├── main.jsx                  # Entry point
│   └── index.css                 # Global styles
├── index.html
├── package.json
└── vite.config.js
```

## Usage

1. **Start a Conversation**: Type a message and press Enter or click Send
2. **Upload PDF**: Click "Upload PDF" button, select file, and upload
3. **Query Documents**: After uploading, ask questions about the document
4. **View Routing**: See which model was used for each response
5. **New Session**: Click "New Session" to start fresh

## Requirements

- Node.js 18+
- npm or yarn
- Backend running at http://localhost:8000

## Tech Stack

- React 18
- Vite (build tool)
- Axios (HTTP client)
- CSS3 (styling)
