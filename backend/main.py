from judge import get_battle_analysis
from analyzer import analyze_image
from ai_judge import analyze_vada_with_ai

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response


# --------------------------------
# CREATE FASTAPI APPLICATION
# --------------------------------

app = FastAPI(
    title="Vada Battle AI",
    description="AI-powered OpenCV + Vision AI vada battle system 🥯⚔️",
    version="2.0.0"
)


# --------------------------------
# CORS
# --------------------------------

app.add_middleware(
    CORSMiddleware,
   allow_origins=[
    "http://localhost:5177",
    "http://127.0.0.1:5177",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------
# CALCULATE HYBRID FINAL SCORE
# --------------------------------

def calculate_final_score(opencv_score, ai_score):
    """
    Final score:
    60% OpenCV
    40% AI Vision
    """

    final_score = (
        float(opencv_score) * 0.60
        +
        float(ai_score) * 0.40
    )

    final_score = max(
        0.0,
        min(100.0, final_score)
    )

    return round(final_score, 2)


# --------------------------------
# HOME ENDPOINT
# --------------------------------

@app.get("/")
def home():

    return {
        "message": "🥯 Vada Battle AI is alive!",
        "status": "ready",
        "system": "OpenCV + AI Vision + Hybrid Scoring"
    }


# --------------------------------
# TEST FRONTEND CONNECTION
# --------------------------------

@app.get("/test")
def test():

    return {
        "message": "Backend and frontend can communicate!",
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

    # Read uploaded image
    image_bytes = await image.read()

    # --------------------------------
    # OPENCV ANALYSIS
    # --------------------------------

    result = analyze_image(image_bytes)

    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get(
                "message",
                "Could not analyze this vada."
            )
        )

    opencv_stats = result["stats"]

    # --------------------------------
    # AI VISION ANALYSIS
    # --------------------------------

    ai_result = analyze_vada_with_ai(
        image_bytes,
        opencv_stats
    )

    # --------------------------------
    # GET SCORES
    # --------------------------------

    opencv_score = opencv_stats["vadaIQ"]

    ai_score = ai_result.get(
        "visualScore",
        0
    )

    # --------------------------------
    # CALCULATE FINAL HYBRID SCORE
    # --------------------------------

    final_score = calculate_final_score(
        opencv_score,
        ai_score
    )

    # --------------------------------
    # RETURN RESULT
    # --------------------------------

    return {
        "status": "success",

        "name": "Vada",

        "filename": image.filename,

        "opencv": {
            "stats": opencv_stats,
            "score": opencv_score
        },

        "aiAnalysis": ai_result,

        "finalScore": final_score
    }


# --------------------------------
# OPENCV DEBUG VISUALIZATION
# --------------------------------

@app.post("/analyze-debug")
async def analyze_debug(
    image: UploadFile = File(...)
):

    # Validate image
    if (
        not image.content_type
        or not image.content_type.startswith("image/")
    ):
        raise HTTPException(
            status_code=400,
            detail="Please upload a valid image."
        )

    # Read image
    image_bytes = await image.read()

    # Run OpenCV analysis
    result = analyze_image(
        image_bytes
    )

    # Check success
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get(
                "message",
                "Could not analyze image."
            )
        )

    # Get debug image
    debug_image = result.get(
        "debug_image"
    )

    if debug_image is None:
        raise HTTPException(
            status_code=500,
            detail="Could not create debug visualization."
        )

    # Return processed image
    return Response(
        content=debug_image,
        media_type="image/jpeg"
    )


# --------------------------------
# COMPARE TWO VADAS
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
            detail="Vada 1 is not a valid image."
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
            detail="Vada 2 is not a valid image."
        )

    # --------------------------------
    # READ BOTH IMAGES
    # --------------------------------

    vada1_bytes = await vada1.read()
    vada2_bytes = await vada2.read()

    # --------------------------------
    # OPENCV ANALYSIS - VADA 1
    # --------------------------------

    result1 = analyze_image(
        vada1_bytes
    )

    if not result1.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result1.get(
                "message",
                "Could not analyze Vada 1."
            )
        )

    # --------------------------------
    # OPENCV ANALYSIS - VADA 2
    # --------------------------------

    result2 = analyze_image(
        vada2_bytes
    )

    if not result2.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result2.get(
                "message",
                "Could not analyze Vada 2."
            )
        )

    # --------------------------------
    # GET OPENCV STATS
    # --------------------------------

    stats1 = result1["stats"]
    stats2 = result2["stats"]

    # --------------------------------
    # AI VISION - VADA 1
    # --------------------------------

    ai_result1 = analyze_vada_with_ai(
        vada1_bytes,
        stats1
    )

    # --------------------------------
    # AI VISION - VADA 2
    # --------------------------------

    ai_result2 = analyze_vada_with_ai(
        vada2_bytes,
        stats2
    )

    # --------------------------------
    # CALCULATE HYBRID SCORES
    # --------------------------------

    final_score1 = calculate_final_score(
        stats1["vadaIQ"],
        ai_result1.get("visualScore", 0)
    )

    final_score2 = calculate_final_score(
        stats2["vadaIQ"],
        ai_result2.get("visualScore", 0)
    )

    # --------------------------------
    # CREATE BATTLE RESULT
    # --------------------------------

    difference = round(
        abs(final_score1 - final_score2),
        2
    )

    if difference < 2:

        winner = "tie"

        battle_type = "tie"

        message = (
            "🤝 It's a delicious tie! "
            "Both vadas fought bravely."
        )

    elif final_score1 > final_score2:

        winner = "vada1"

        battle_type = "clear_winner"

        message = (
            "🏆 VADA 1 takes the crown! "
            "The OpenCV and AI judges agree."
        )

    else:

        winner = "vada2"

        battle_type = "clear_winner"

        message = (
            "🏆 VADA 2 takes the crown! "
            "The OpenCV and AI judges agree."
        )

    # --------------------------------
    # RETURN COMPLETE BATTLE RESULT
    # --------------------------------

    return {
        "status": "success",

        "vada1": {
            "name": "Vada 1",
            "filename": vada1.filename,

            "opencv": {
                "stats": stats1,
                "score": stats1["vadaIQ"]
            },

            "aiAnalysis": ai_result1,

            "finalScore": final_score1
        },

        "vada2": {
            "name": "Vada 2",
            "filename": vada2.filename,

            "opencv": {
                "stats": stats2,
                "score": stats2["vadaIQ"]
            },

            "aiAnalysis": ai_result2,

            "finalScore": final_score2
        },

        "battle": {
            "winner": winner,
            "battleType": battle_type,
            "difference": difference,
            "message": message
        }
    }