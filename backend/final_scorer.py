def calculate_final_score(opencv_iq, ai_visual_score):

    final_score = (
        float(opencv_iq) * 0.70
        +
        float(ai_visual_score) * 0.30
    )

    return round(
        max(0, min(100, final_score)),
        2
    )