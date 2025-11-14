import os
import base64
import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from PIL import Image

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("WARNING: GEMINI_API_KEY not set. The /predict endpoint will not work.")

@app.get("/")
async def read_root():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.post("/predict")
async def predict_currency(file: UploadFile = File(...)):
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured. Please set your API key in the Secrets tab."
        )
    
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        image.verify()
        image = Image.open(io.BytesIO(contents))
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = """You are an expert in Indian currency authentication. Analyze this image carefully and determine if it shows a REAL or FAKE Indian currency note.

Consider the following security features commonly found in genuine Indian currency:
- Watermark visibility and quality
- Security thread presence and characteristics
- Micro-lettering clarity
- Intaglio printing (raised print feel visible in high-res images)
- Fluorescent ink under UV (if visible)
- See-through register alignment
- Identification mark for visually impaired
- Number panel and denomination
- Portrait and overall print quality
- Color and paper quality

Provide your analysis in the following format:
1. Classification: REAL or FAKE
2. Confidence: A percentage (0-100%)
3. Explanation: A detailed explanation of why you classified it as real or fake, mentioning specific features you observed

Be thorough and precise in your analysis."""

        response = model.generate_content([prompt, image])
        
        analysis_text = response.text
        
        if "REAL" in analysis_text.upper() and "FAKE" not in analysis_text.split('\n')[0].upper():
            label = "REAL"
        elif "FAKE" in analysis_text.upper():
            label = "FAKE"
        else:
            label = "UNCERTAIN"
        
        confidence = 0
        for line in analysis_text.split('\n'):
            if 'confidence' in line.lower() and '%' in line:
                try:
                    import re
                    numbers = re.findall(r'\d+', line)
                    if numbers:
                        confidence = int(numbers[0])
                        break
                except:
                    pass
        
        if confidence == 0:
            if label == "REAL":
                confidence = 75
            elif label == "FAKE":
                confidence = 70
            else:
                confidence = 50
        
        return JSONResponse(content={
            "label": label,
            "confidence": confidence,
            "explanation": analysis_text,
            "success": True
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.get("/health")
async def health_check():
    has_api_key = bool(api_key)
    return {
        "status": "healthy",
        "gemini_configured": has_api_key
    }

app.mount("/static", StaticFiles(directory="static"), name="static")

from fastapi.responses import HTMLResponse

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
