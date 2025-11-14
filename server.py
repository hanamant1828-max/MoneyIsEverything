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
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = """You are an expert in Indian currency authentication. Analyze this image and make a DEFINITIVE decision: is it REAL or FAKE? You MUST choose one - no uncertain answers allowed.

CRITICAL RULES:
1. If ALL serial numbers are zeros (000 000000 or similar) → ALWAYS classify as FAKE
2. If the image is unclear or low quality → Make your best judgment based on what you CAN see
3. You MUST give a clear REAL or FAKE classification - never say uncertain

Security features to check:
- Serial numbers (all zeros = FAKE)
- Watermark quality
- Security thread
- Micro-lettering
- Print quality and sharpness
- Color accuracy
- Portrait details
- Denomination markings

RESPONSE FORMAT (strictly follow):
1. Classification: REAL or FAKE (pick one, no other options)
2. Confidence: A percentage (0-100%)
3. Explanation: Brief explanation of your decision

Remember: You must make a definitive choice between REAL or FAKE. No uncertain classifications allowed."""

        response = model.generate_content([prompt, image])
        
        if not response or not response.text:
            raise HTTPException(
                status_code=500,
                detail="Gemini API returned an empty response. Please try again with a clearer image."
            )
        
        analysis_text = response.text
        
        import re
        
        label = "FAKE"
        classification_match = re.search(r'classification:\s*(REAL|FAKE)', analysis_text, re.IGNORECASE)
        if classification_match:
            label = classification_match.group(1).upper()
        
        confidence = None
        for line in analysis_text.split('\n'):
            if 'confidence:' in line.lower():
                numbers = re.findall(r'\d+', line)
                if numbers:
                    confidence = min(100, max(0, int(numbers[0])))
                    break
        
        if confidence is None:
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
