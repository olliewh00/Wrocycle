"""
WroCycle — FastAPI Web Application
Serves the static HTML frontend and provides the AI waste classification API.

Run with:  python main.py
Or:        uvicorn main:app --reload --port 8000
"""

import os
import io
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from dotenv import load_dotenv

from classifier_service import classify_waste

# Load environment variables
load_dotenv()

# App setup
app = FastAPI(
    title="WroCycle API",
    description="AI-powered waste classification for Wrocław dormitories",
    version="1.0.0",
)

# CORS — allow the frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = Path(__file__).resolve().parent
SCREENS_DIR = BASE_DIR / "stitch_screens"

# Mount static files (CSS, JS, images if any)
app.mount("/static", StaticFiles(directory=str(SCREENS_DIR)), name="static")


# ──────────────────────────────────────────────
# Page Routes
# ──────────────────────────────────────────────

@app.get("/")
async def home():
    """Serve the home page."""
    return FileResponse(SCREENS_DIR / "wrocycle_home.html")


@app.get("/game")
async def game():
    """Serve the game page."""
    return FileResponse(SCREENS_DIR / "wrocycle_game.html")


@app.get("/blog")
async def blog():
    """Serve the blog page."""
    return FileResponse(SCREENS_DIR / "wrocycle_blog.html")


# ──────────────────────────────────────────────
# AI Classification API
# ──────────────────────────────────────────────

@app.post("/api/classify")
async def api_classify(image: UploadFile = File(...)):
    """
    Accept an image upload, run AI waste classification,
    and return structured JSON with the sorting decision.
    """
    # Validate file type
    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{image.content_type}'. Allowed: {', '.join(allowed_types)}"
        )

    # Read and validate image
    try:
        contents = await image.read()
        if len(contents) > 10 * 1024 * 1024:  # 10 MB limit
            raise HTTPException(status_code=400, detail="Image too large. Max 10 MB.")

        pil_image = Image.open(io.BytesIO(contents))

        # Convert to RGB if needed (e.g. RGBA PNGs)
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read image: {str(e)}")

    # Run classification
    try:
        result = classify_waste(pil_image)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

    return JSONResponse(content=result)


# ──────────────────────────────────────────────
# Health check
# ──────────────────────────────────────────────

@app.get("/api/health")
async def health():
    """Health check endpoint."""
    has_gemini = bool(os.getenv("GEMINI_API_KEY"))
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    return {
        "status": "ok",
        "gemini_configured": has_gemini,
        "openai_configured": has_openai,
        "model": os.getenv("GEMINI_MODEL", os.getenv("OPENAI_MODEL", "not set")),
    }


# ──────────────────────────────────────────────
# Run with: python main.py
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"\n♻️  WroCycle is running at http://localhost:{port}\n")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
