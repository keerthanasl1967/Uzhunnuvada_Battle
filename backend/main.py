from commentator import get_vada_comment
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
    comment1 = get_vada_comment(iq1)
    comment2 = get_vada_comment(iq2)

    difference = abs(iq1 - iq2)

if iq1 > iq2:
    winner = "vada1"

    if difference < 5:
        message = "😱 Vada 1 wins by a tiny crumb! What a close battle!"
    elif difference < 15:
        message = "🏆 Vada 1 wins! A solid frying-pan performance!"
    else:
        message = "🔥 Vada 1 absolutely destroyed the competition!"

elif iq2 > iq1:
    winner = "vada2"

    if difference < 5:
        message = "😱 Vada 2 wins by a tiny crumb! What a close battle!"
    elif difference < 15:
        message = "🏆 Vada 2 wins! A solid frying-pan performance!"
    else:
        message = "🔥 Vada 2 absolutely destroyed the competition!"

else:
    winner = "draw"
    message = "🤝 Both vadas are equally chaotic. It's a legendary draw!"
    return {
    "vada1": {
        "stats": result1["stats"],
        "comment": comment1
    },
    "vada2": {
        "stats": result2["stats"],
        "comment": comment2
    },
    "winner": winner,
    "difference": round(difference, 2),
    "message": message
}