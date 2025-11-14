# Indian Currency Detection App

A web application that uses Google's Gemini Vision API to detect whether Indian currency notes are real or fake.

## Features

- 🖼️ **Image Upload**: Drag & drop or select currency images
- 🤖 **AI Analysis**: Uses Gemini 2.5 Flash for vision-based detection
- 📊 **Confidence Scoring**: Shows detection confidence percentage
- 📝 **Detailed Explanation**: Provides reasoning for the classification
- 🎨 **Responsive Design**: Works on desktop and mobile devices

## Setup Instructions

### 1. Get Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 2. Add API Key to Replit

1. Click on the **"Secrets"** tab in the left sidebar (🔒 icon)
2. Click **"New Secret"**
3. Set the key as: `GEMINI_API_KEY`
4. Paste your API key as the value
5. Click **"Add Secret"**

### 3. Run the Application

The application will automatically start when you run the project. You can also manually run:

```bash
python server.py
```

The app will be available at `http://localhost:5000`

## How to Use

1. Open the application in your browser
2. Click the upload area or drag & drop an image of Indian currency
3. Wait for the AI to analyze the image
4. View the results showing:
   - Classification (REAL/FAKE)
   - Confidence percentage
   - Detailed explanation of the analysis

## Technology Stack

- **Backend**: FastAPI (Python)
- **AI Model**: Google Gemini 2.5 Flash Vision
- **Frontend**: HTML, CSS, JavaScript
- **Image Processing**: Pillow (PIL)

## API Endpoints

- `GET /` - Serves the main application
- `POST /predict` - Accepts image upload and returns detection results
- `GET /health` - Health check endpoint

## Deployment

To deploy this application:

1. Make sure your `GEMINI_API_KEY` is set in Secrets
2. Click the **"Deploy"** button in Replit
3. Your app will be published with a public URL you can share

## Security Features Analyzed

The AI checks for various security features in Indian currency:
- Watermark quality
- Security thread
- Micro-lettering
- Intaglio printing
- Fluorescent ink
- See-through register
- Identification marks
- Print quality
- Color and paper quality

## Notes

- The app requires a valid Gemini API key to function
- Best results with clear, well-lit images of currency notes
- Supports all Indian currency denominations

## License

MIT License
