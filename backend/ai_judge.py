import os
import base64
import json

from dotenv import load_dotenv
from openai import OpenAI

from pathlib import Path

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)


# --------------------------------
# CREATE OPENAI CLIENT
# --------------------------------

api_key = os.getenv("OPENAI_API_KEY")
print("API Key loaded:", api_key is not None)

client = None

if api_key:
    client = OpenAI(
        api_key=api_key
    )
    print("Client:", client)


# --------------------------------
# ANALYZE VADA WITH AI VISION
# --------------------------------

def analyze_vada_with_ai(
    image_bytes,
    opencv_stats
):
    """
    Send the uploaded vada image to AI Vision.

    Returns:
    - visualScore
    - appearance
    - strengths
    - weaknesses
    - roast
    """

    # --------------------------------
    # FALLBACK IF API KEY IS MISSING
    # --------------------------------

    if client is None:
        return {
            "success": False,
            "visualScore": 0,
            "appearance": "AI analysis unavailable.",
            "strengths": [],
            "weaknesses": [],
            "roast": "The AI judge forgot to bring its glasses 🤓",
            "message": "OPENAI_API_KEY is not configured."
        }

    try:

        # --------------------------------
        # CONVERT IMAGE TO BASE64
        # --------------------------------

        base64_image = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        # --------------------------------
        # CREATE PROMPT
        # --------------------------------

        prompt = f"""
You are an AI food judge participating in a fun
"Vada Battle" competition.

Analyze the uploaded image of an uzhunnu vada.

Use the image as the primary source of visual judgment.
The OpenCV measurements below are supporting measurements:

Circularity: {opencv_stats.get("circularity", 0)}
Symmetry: {opencv_stats.get("symmetry", 0)}
Hole Quality: {opencv_stats.get("holeQuality", 0)}
Crispiness Estimate: {opencv_stats.get("crispiness", 0)}
OpenCV Vada IQ: {opencv_stats.get("vadaIQ", 0)}

Judge the visible vada based on:

1. Overall appearance
2. Shape
3. Color and browning
4. Visible crispiness
5. Center hole quality
6. Presentation

Return ONLY valid JSON.

Use exactly this format:

{{
    "visualScore": 0,
    "appearance": "",
    "strengths": [],
    "weaknesses": [],
    "roast": ""
}}

Rules:

- visualScore must be a number from 0 to 100.
- appearance must be a short description.
- strengths must contain 2 or 3 short points.
- weaknesses must contain 1 or 2 short points.
- roast must be funny and playful, not hateful or abusive.
- Do not mention that you are an AI.
- Do not include markdown.
- Do not include text outside the JSON.
"""

        # --------------------------------
        # SEND IMAGE TO OPENAI
        # --------------------------------

        response = client.responses.create(
            model="gpt-4.1",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt
                        },
                        {
                            "type": "input_image",
                            "image_url": (
                                "data:image/jpeg;base64,"
                                + base64_image
                            )
                        }
                    ]
                }
            ]
        )

        # --------------------------------
        # GET AI RESPONSE
        # --------------------------------

        response_text = response.output_text.strip()

        # Remove accidental markdown fences
        response_text = response_text.replace(
            "```json",
            ""
        )

        response_text = response_text.replace(
            "```",
            ""
        )

        response_text = response_text.strip()

        # --------------------------------
        # PARSE JSON
        # --------------------------------

        ai_result = json.loads(
            response_text
        )

        # --------------------------------
        # VALIDATE SCORE
        # --------------------------------

        visual_score = float(
            ai_result.get(
                "visualScore",
                0
            )
        )

        visual_score = max(
            0,
            min(
                100,
                visual_score
            )
        )

        # --------------------------------
        # RETURN CLEAN RESULT
        # --------------------------------

        return {
            "success": True,

            "visualScore": round(
                visual_score,
                2
            ),

            "appearance": ai_result.get(
                "appearance",
                "No appearance analysis available."
            ),

            "strengths": ai_result.get(
                "strengths",
                []
            ),

            "weaknesses": ai_result.get(
                "weaknesses",
                []
            ),

            "roast": ai_result.get(
                "roast",
                "This vada escaped judgment somehow."
            )
        }

    except Exception as error:
        import traceback

        print("\n========== AI ERROR ==========")
        traceback.print_exc()
        print("==============================\n")

        return {
          "success": False,
          "visualScore": 0,
          "appearance": "AI visual analysis could not be completed.",
          "strengths": [],
          "weaknesses": [],
          "roast": "The AI judge dropped its spectacles 🤓",
          "message": str(error)
    }

         