# 🚀 Complete Setup Guide

This guide walks you through setting up and running the Multi-Model AI Chat System with React UI.

## Prerequisites

Before you begin, ensure you have:

- ✅ Python 3.11 or higher
- ✅ Node.js 18 or higher
- ✅ Google Gemini API key (free tier supported)
- ✅ Git (optional, for cloning)

## Step 1: Get Your Google Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key (keep it safe!)

## Step 2: Setup the Backend

### Windows

1. Open PowerShell or Command Prompt
2. Navigate to the project directory:
   ```bash
   cd path\to\Assignment-Arctiq-Solutions
   ```

3. Create and activate virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create `.env` file:
   ```bash
   copy .env.example .env
   ```

6. Edit `.env` file and add your API key:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

7. Run the backend:
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Linux/Mac

1. Open Terminal
2. Navigate to the project directory:
   ```bash
   cd path/to/Assignment-Arctiq-Solutions
   ```

3. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create `.env` file:
   ```bash
   cp .env.example .env
   ```

6. Edit `.env` file and add your API key:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

7. Run the backend:
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Step 3: Setup the React Frontend

**Open a NEW terminal/PowerShell window** (keep the backend running in the first one)

### Windows

1. Navigate to the project directory:
   ```bash
   cd path\to\Assignment-Arctiq-Solutions
   ```

2. Navigate to frontend folder:
   ```bash
   cd frontend
   ```

3. Install dependencies:
   ```bash
   npm install
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

### Linux/Mac

1. Navigate to the project directory:
   ```bash
   cd path/to/Assignment-Arctiq-Solutions
   ```

2. Navigate to frontend folder:
   ```bash
   cd frontend
   ```

3. Install dependencies:
   ```bash
   npm install
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

## Step 4: Access the Application

After both servers are running:

1. **Open your browser**
2. **Go to**: http://localhost:3000
3. **You should see the chat interface!**

### What You Should See

- Backend running at: http://localhost:8000
- Frontend running at: http://localhost:3000
- Beautiful gradient UI with chat interface

## Testing the System

### 1. Test General Chat
Type: `Hello! How are you?`

### 2. Test Math Query
Type: `What is 456 * 789 + 123?`

You should see:
- Answer with calculation
- Routing metadata showing "math" category
- Calculator tool usage indicator

### 3. Test Coding Query
Type: `Write a Python function to reverse a string`

You should see:
- Python code response
- Routing metadata showing "coding" category

### 4. Test PDF Upload

1. Click "Upload PDF" button
2. Select a PDF file
3. Wait for upload confirmation
4. Ask: `What are the main topics in this document?`

You should see:
- Document-based answer
- Routing metadata showing "document" category
- Number of contexts used

## Troubleshooting

### Backend Issues

**Error: "GOOGLE_API_KEY not found"**
- Solution: Make sure `.env` file exists and contains your API key

**Error: "Module not found"**
- Solution: Activate virtual environment and run `pip install -r requirements.txt`

**Error: "Address already in use"**
- Solution: Port 8000 is occupied. Kill the process or change port in `.env`

### Frontend Issues

**Error: "Cannot connect to backend"**
- Solution: Ensure backend is running at http://localhost:8000

**Error: "npm not found"**
- Solution: Install Node.js from https://nodejs.org/

**Error: "EADDRINUSE: Port 3000 in use"**
- Solution: Kill process on port 3000 or edit `vite.config.js` to use different port

### ChromaDB Issues

**Error: "ChromaDB initialization failed"**
- Solution: Delete `vectorstore/` folder and restart backend

## File Locations

### Backend Files
- Python code: `app/` folder
- Configuration: `app/config.py`
- Environment: `.env` file
- Uploads: `data/` folder
- Vector store: `vectorstore/` folder

### Frontend Files
- React code: `frontend/src/` folder
- Components: `frontend/src/components/`
- API service: `frontend/src/services/api.js`
- Styles: `frontend/src/components/*.css`

## Next Steps

After successful setup:

1. ✅ Try different query types (math, coding, general)
2. ✅ Upload a PDF and ask questions about it
3. ✅ Check routing metadata for each response
4. ✅ Start a new session and continue conversations
5. ✅ Explore API docs at http://localhost:8000/docs

## Production Deployment

### Using Docker

1. Build the image:
   ```bash
   docker-compose up --build
   ```

2. Access at http://localhost:8000

3. For frontend in production, build static files:
   ```bash
   cd frontend
   npm run build
   ```

## Getting Help

- Check [README.md](README.md) for detailed documentation
- View API docs at http://localhost:8000/docs
- Check console/terminal for error messages
- Ensure all prerequisites are installed

## API Key Safety

⚠️ **IMPORTANT**: Never commit your `.env` file to Git!

The `.gitignore` file already includes `.env`, but always verify:
- `.env` should be in your `.gitignore`
- Never share your API key publicly
- Regenerate key if compromised

---

**Enjoy your Multi-Model AI Chat System! 🎉**
