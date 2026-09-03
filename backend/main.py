from judge import get_battle_analysis
from analyzer import analyze_image
from commentator import get_vada_comment

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware


# --------------------------------
# CREATE FASTAPI APPLICATION
# --------------------------------

app = FastAPI(
    title="Vada Battle AI",
    description="AI-powered battle system for judging two vadas 🥯⚔️",
    version="1.0.0"
)


# --------------------------------
# CORS - ALLOW FRONTEND CONNECTION
# --------------------------------

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

    # Validate image
    if (
        not image.content_type
        or not image.content_type.startswith("image/")
    ):
        raise HTTPException(
            status_code=400,
            detail="Please upload a valid vada image 🥯"
        )

    # Read image
    image_bytes = await image.read()

    # Analyze using OpenCV
    result = analyze_image(image_bytes)

    # Check analysis success
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get(
                "message",
                "AI could not analyze this image 😭"
            )
        )

    # Get Vada IQ
    iq = result["stats"]["vadaIQ"]

    # Generate funny comment
    comment = get_vada_comment(iq)

    # Return complete result
    return {
        "status": "success",
        "name": "Vada",
        "filename": image.filename,
        "stats": result["stats"],
        "comment": comment
    }


# --------------------------------
# AI VADA BATTLE
# --------------------------------

@app.post("/compare")
async def compare_vadas(
    vada1: UploadFile = File(...),
    vada2: UploadFile = File(...)
):

    # --------------------------------
    # VALIDATE VADA 1
    # --------------------------------

    if (
        not vada1.content_type
        or not vada1.content_type.startswith("image/")
    ):
        raise HTTPException(
            status_code=400,
            detail="Vada 1 is not an image! Nice try though 😂"
        )

    # --------------------------------
    # VALIDATE VADA 2
    # --------------------------------

    if (
        not vada2.content_type
        or not vada2.content_type.startswith("image/")
    ):
        raise HTTPException(
            status_code=400,
            detail="Vada 2 is not an image! The AI judge only accepts vadas 😂"
        )

    # --------------------------------
    # READ BOTH IMAGES
    # --------------------------------

    vada1_bytes = await vada1.read()
    vada2_bytes = await vada2.read()

    # --------------------------------
    # ANALYZE BOTH VADAS
    # --------------------------------

    result1 = analyze_image(vada1_bytes)
    result2 = analyze_image(vada2_bytes)

    # --------------------------------
    # CHECK ANALYSIS SUCCESS
    # --------------------------------

    if not result1.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result1.get(
                "message",
                "Could not analyze Vada 1 😭"
            )
        )

    if not result2.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result2.get(
                "message",
                "Could not analyze Vada 2 😭"
            )
        )

    # --------------------------------
    # GET AI BATTLE RESULT
    # --------------------------------

    battle = get_battle_analysis(
        result1["stats"],
        result2["stats"]
    )

    # --------------------------------
    # GET FUNNY AI COMMENTS
    # --------------------------------

    comment1 = get_vada_comment(
        result1["stats"]["vadaIQ"]
    )

    comment2 = get_vada_comment(
        result2["stats"]["vadaIQ"]
    )

    # --------------------------------
    # RETURN COMPLETE BATTLE RESULT
    # --------------------------------

    return {
        "status": "success",

        "vada1": {
            "name": "Vada 1",
            "filename": vada1.filename,
            "stats": result1["stats"],
            "comment": comment1
        },

        "vada2": {
            "name": "Vada 2",
            "filename": vada2.filename,
            "stats": result2["stats"],
            "comment": comment2
        },

        "battle": battle
    }