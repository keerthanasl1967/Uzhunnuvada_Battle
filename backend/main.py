from judge import get_battle_analysis
from analyzer import analyze_image
from commentator import get_vada_comment

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware


# Create FastAPI application
app = FastAPI(
    title="Vada Battle AI",
    description="AI-powered battle system for judging two vadas 🥯⚔️",
    version="1.0.0"
)


# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------
# HOME ENDPOINT
# --------------------------------

@app.get("/")
def home():
    return {
        "message": "🥯 Vada Battle AI is alive!",
        "status": "ready",
        "judge": "AI Vada Inspector 🤖"
    }


# --------------------------------
# TEST FRONTEND CONNECTION
# --------------------------------

@app.get("/test")
def test():
    return {
        "message": "Backend and frontend can communicate!",
        "vada": "🥯",
        "status": "success"
    }


# --------------------------------
# ANALYZE ONE VADA
# --------------------------------

@app.post("/analyze")
async def analyze_vada(
    image: UploadFile = File(...)
):

    # Check if uploaded file is an image
    if (
        not image.content_type
        or not image.content_type.startswith("image/")
    ):
        raise HTTPException(
            status_code=400,
            detail="Please upload a valid vada image 🥯"
        )

    # Read uploaded image
    image_bytes = await image.read()

    # Analyze image
    result = analyze_image(image_bytes)

    # Check analysis success
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail="AI could not analyze this image 😭"
        )

    # Get Vada IQ
    iq = result["stats"]["vadaIQ"]

    # Generate funny AI comment
    comment = get_vada_comment(iq)

    # Add extra information
    result["filename"] = image.filename
    result["comment"] = comment

    return result


# --------------------------------
# AI VADA BATTLE
# --------------------------------

@app.post("/compare")
async def compare_vadas(
    vada1: UploadFile = File(...),
    vada2: UploadFile = File(...)
):

    # ----------------------------
    # VALIDATE VADA 1
    # ----------------------------

    if (
        not vada1.content_type
        or not vada1.content_type.startswith("image/")
    ):
        raise HTTPException(
            status_code=400,
            detail="Vada 1 is not an image! Nice try though 😂"
        )


    # ----------------------------
    # VALIDATE VADA 2
   