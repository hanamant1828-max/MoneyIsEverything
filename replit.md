# Indian Currency Detection Web App

## Overview
A complete web application that uses Google's Gemini Vision API (gemini-2.0-flash model) to detect whether uploaded images of Indian currency notes are real or fake. The app provides fast AI-powered analysis with confidence scoring and detailed explanations.

## Project Structure
```
.
├── server.py              # FastAPI backend server
├── static/
│   ├── index.html        # Main frontend interface
│   ├── style.css         # Responsive styling
│   └── script.js         # Client-side logic
├── README.md             # User documentation
├── .gitignore           # Git ignore patterns
└── replit.md            # Project documentation
```

## Technology Stack
- **Backend**: Python FastAPI
- **AI Model**: Google Gemini 2.0 Flash Vision (optimized for speed)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Server**: Uvicorn ASGI server
- **Image Processing**: Pillow (PIL)

## Key Features
1. **Image Upload Interface**
   - Drag & drop support
   - File selection button
   - Image preview before analysis

2. **AI-Powered Detection**
   - Uses Gemini Vision API for multi-modal analysis
   - Checks security features: watermarks, security threads, micro-lettering, print quality
   - Returns classification: REAL, FAKE, or UNCERTAIN

3. **Results Display**
   - Clear visual label (color-coded)
   - Confidence percentage with animated progress bar
   - Detailed explanation of the analysis

4. **Responsive Design**
   - Works on desktop and mobile
   - Modern gradient UI
   - Smooth animations and transitions

## API Endpoints
- `GET /` - Serves main HTML page
- `POST /predict` - Accepts image upload, returns detection results
- `GET /health` - Health check with API key status

## Configuration

### Environment Variables
- `GEMINI_API_KEY` - Required for Gemini Vision API access

### Setup Instructions
1. Get API key from Google AI Studio
2. Add to Replit Secrets as `GEMINI_API_KEY`
3. Server will auto-restart and connect to Gemini

## Deployment
- Configured for Replit Autoscale deployment
- Runs on port 5000
- Stateless design suitable for auto-scaling

## Recent Changes
- 2025-11-14: Initial project creation
  - Created FastAPI backend with /predict endpoint
  - Built responsive frontend with drag-drop upload
  - Integrated Gemini 2.5 Flash Vision API
  - Added deployment configuration
  - Set up workflow for port 5000
  - Updated to use gemini-2.0-flash model for faster responses
  - Enhanced AI prompt to prioritize serial number validation (all-zero serial numbers = FAKE)
  - Removed UNCERTAIN classification - only REAL or FAKE results
  - Added image compression (1024px max) for speed optimization
  - Shortened AI prompt for faster processing

## Architecture Decisions
- **FastAPI over Flask**: Chosen for async support and better performance
- **Vanilla JS over React**: Simpler setup, faster load time for single-page app
- **Gemini 2.0 Flash**: Fast model optimized for quick real-time detection
- **Image Optimization**: Automatic resize to 1024px for faster processing
- **Concise Prompts**: Streamlined AI instructions for quicker responses
- **Port 5000**: Required for Replit webview integration
- **StaticFiles mount**: Serves frontend assets efficiently
