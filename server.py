import os
import base64
import io
import sqlite3
import secrets
from datetime import datetime, timedelta
import bcrypt
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Cookie, Response
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from PIL import Image

app = FastAPI()

DATABASE = "users.db"
SESSIONS = {}

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

def init_database():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                image_data TEXT NOT NULL,
                result TEXT NOT NULL,
                confidence REAL NOT NULL,
                explanation TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            admin_password_hash = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                ("admin", admin_password_hash)
            )
        
        conn.commit()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_user(username: str, password: str) -> bool:
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            (username,)
        )
        result = cursor.fetchone()
        
        if result:
            return bcrypt.checkpw(password.encode(), result[0].encode())
        return False

def create_user(username: str, password: str) -> bool:
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, hash_password(password))
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def create_session(username: str) -> str:
    session_id = secrets.token_urlsafe(32)
    SESSIONS[session_id] = {
        "username": username,
        "created_at": datetime.now()
    }
    return session_id

def get_session_user(session_id: str) -> str:
    if session_id in SESSIONS:
        session = SESSIONS[session_id]
        if datetime.now() - session["created_at"] < timedelta(hours=24):
            return session["username"]
        else:
            del SESSIONS[session_id]
    return None

init_database()

@app.get("/")
async def read_root(session_id: str = Cookie(None)):
    user = get_session_user(session_id) if session_id else None
    if not user:
        return RedirectResponse(url="/login")
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/login")
async def login_page():
    with open("static/login.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/register")
async def register_page():
    with open("static/register.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.post("/api/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if verify_user(username, password):
        session_id = create_session(username)
        response = JSONResponse(content={"success": True, "message": "Login successful"})
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            max_age=86400,
            secure=True,
            samesite="lax"
        )
        return response
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

@app.post("/api/register")
async def register(username: str = Form(...), password: str = Form(...)):
    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    if create_user(username, password):
        session_id = create_session(username)
        response = JSONResponse(content={"success": True, "message": "Registration successful"})
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            max_age=86400,
            secure=True,
            samesite="lax"
        )
        return response
    else:
        raise HTTPException(status_code=400, detail="Username already exists")

@app.post("/api/logout")
async def logout(session_id: str = Cookie(None)):
    if session_id and session_id in SESSIONS:
        del SESSIONS[session_id]
    response = JSONResponse(content={"success": True, "message": "Logged out successfully"})
    response.delete_cookie(key="session_id", secure=True, samesite="lax")
    return response

@app.get("/api/user")
async def get_user(session_id: str = Cookie(None)):
    user = get_session_user(session_id) if session_id else None
    if user:
        return {"username": user}
    raise HTTPException(status_code=401, detail="Not authenticated")

@app.post("/predict")
async def predict_currency(file: UploadFile = File(...), session_id: str = Cookie(None)):
    user = get_session_user(session_id) if session_id else None
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
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
        
        max_size = 1024
        if image.width > max_size or image.height > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        image_base64 = base64.b64encode(contents).decode('utf-8')
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = """Authenticate this Indian currency note. Choose: REAL or FAKE.

CRITICAL: If serial numbers are all zeros (000 000000) → FAKE

Check: serial numbers, watermark, security thread, print quality, colors.

Format:
1. Classification: REAL or FAKE
2. Confidence: percentage
3. Explanation: brief reason

Must choose REAL or FAKE only."""

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
        
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO history (username, image_data, result, confidence, explanation) VALUES (?, ?, ?, ?, ?)",
                (user, image_base64, label, confidence, analysis_text)
            )
            conn.commit()
            history_id = cursor.lastrowid
        
        return JSONResponse(content={
            "label": label,
            "confidence": confidence,
            "explanation": analysis_text,
            "success": True,
            "history_id": history_id
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.get("/dashboard")
async def dashboard_page(session_id: str = Cookie(None)):
    user = get_session_user(session_id) if session_id else None
    if not user:
        return RedirectResponse(url="/login")
    with open("static/dashboard.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/history")
async def history_page(session_id: str = Cookie(None)):
    user = get_session_user(session_id) if session_id else None
    if not user:
        return RedirectResponse(url="/login")
    with open("static/history.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/api/dashboard-stats")
async def get_dashboard_stats(session_id: str = Cookie(None)):
    user = get_session_user(session_id) if session_id else None
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM history WHERE username = ?", (user,))
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM history WHERE username = ? AND result = 'REAL'", (user,))
        real_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM history WHERE username = ? AND result = 'FAKE'", (user,))
        fake_count = cursor.fetchone()[0]
        
        cursor.execute(
            "SELECT id, image_data, result, confidence, timestamp FROM history WHERE username = ? ORDER BY timestamp DESC LIMIT 5",
            (user,)
        )
        recent = []
        for row in cursor.fetchall():
            recent.append({
                "id": row[0],
                "image_data": row[1],
                "result": row[2],
                "confidence": row[3],
                "timestamp": row[4]
            })
    
    return {
        "total": total,
        "real_count": real_count,
        "fake_count": fake_count,
        "recent": recent
    }

@app.get("/api/history")
async def get_history(session_id: str = Cookie(None)):
    user = get_session_user(session_id) if session_id else None
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, image_data, result, confidence, timestamp FROM history WHERE username = ? ORDER BY timestamp DESC",
            (user,)
        )
        history = []
        for row in cursor.fetchall():
            history.append({
                "id": row[0],
                "image_data": row[1],
                "result": row[2],
                "confidence": row[3],
                "timestamp": row[4]
            })
    
    return {"history": history}

@app.get("/api/history/{history_id}")
async def get_history_detail(history_id: int, session_id: str = Cookie(None)):
    user = get_session_user(session_id) if session_id else None
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, image_data, result, confidence, explanation, timestamp FROM history WHERE id = ? AND username = ?",
            (history_id, user)
        )
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="History not found")
        
        return {
            "id": row[0],
            "image_data": row[1],
            "result": row[2],
            "confidence": row[3],
            "explanation": row[4],
            "timestamp": row[5]
        }

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
