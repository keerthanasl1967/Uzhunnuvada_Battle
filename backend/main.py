from analyzer import analyze_image
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Vada Backend is alive!"
    }


@app.get("/test")
def test():
    return {
        "message": "Backend and frontend can communicate!",
        "vada": "🥯",
        "status": "success"
    }


@app.post("/analyze")
async def analyze_vada(image: UploadFile = File(...)):

    image_bytes = await image.read()

    result = analyze_image(image_bytes)

    result["filename"] = image.filename

    return result


@app.post("/compare")
async def compare_vadas(
    vada1: UploadFile = File(...),
    vada2: UploadFile = File(...)
):

    # Read Vada 1
    vada1_bytes = await vada1.read()

    # Read Vada 2
    vada2_bytes = await vada2.read()

    # Analyze both vadas
    result1 = analyze_image(vada1_bytes)
    result2 = analyze_image(vada2_bytes)

    # Get Vada IQ
    iq1 = result1["stats"]["vadaIQ"]
    iq2 = result2["stats"]["vadaIQ"]

    # Decide the winner
    if iq1 > iq2:
        winner = "vada1"
        message = "🥯 Vada 1 wins the battle!"
    elif iq2 > iq1:
        winner = "vada2"
        message = "🥯 Vada 2 wins the battle!"
    else:
        winner = "draw"
        message = "🤝 It's a legendary vada draw!"

    return {
        "vada1": {
            "stats": result1["stats"]
        },
        "vada2": {
            "stats": result2["stats"]
        },
        "winner": winner,
        "message": message
    }