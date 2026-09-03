def get_battle_analysis(stats1, stats2):
    """
    Compare two vadas using their OpenCV analysis scores.
    """

    iq1 = stats1["vadaIQ"]
    iq2 = stats2["vadaIQ"]

    difference = abs(iq1 - iq2)

    # -----------------------------
    # DECIDE WINNER
    # -----------------------------

    if iq1 > iq2:
        winner = "vada1"

    elif iq2 > iq1:
        winner = "vada2"

    else:
        winner = "draw"

    # -----------------------------
    # BATTLE TYPE
    # -----------------------------

    if winner == "draw":

        battle_type = "draw"

        message = (
            "🤝 The AI judge is completely confused. "
            "Both vadas have achieved equal levels of greatness!"
        )

    elif difference < 3:

        battle_type = "photo_finish"

        message = (
            "😱 PHOTO FINISH! The difference is microscopic. "
            "The frying pan nearly needed VAR technology!"
        )

    elif difference < 10:

        battle_type = "close_battle"

        message = (
            f"⚔️ What a battle! {winner.upper()} wins, "
            "but the loser fought bravely until the last crumb!"
        )

    elif difference < 20:

        battle_type = "clear_winner"

        message = (
            f"🏆 The AI has spoken! {winner.upper()} takes "
            "the crown with a strong frying performance!"
        )

    else:

        battle_type = "absolute_destruction"

        message = (
            f"🔥 {winner.upper()} absolutely destroyed the competition! "
            "Someone call the vada rescue team!"
        )

    # -----------------------------
    # COMPARE INDIVIDUAL FEATURES
    # -----------------------------

    comparisons = {
        "circularityWinner": compare_stat(
            stats1["circularity"],
            stats2["circularity"]
        ),

        "symmetryWinner": compare_stat(
            stats1["symmetry"],
            stats2["symmetry"]
        ),

        "holeWinner": compare_stat(
            stats1["holeQuality"],
            stats2["holeQuality"]
        ),

        "crispinessWinner": compare_stat(
            stats1["crispiness"],
            stats2["crispiness"]
        )
    }

    return {
        "winner": winner,
        "battleType": battle_type,
        "difference": round(difference, 2),
        "message": message,
        "comparisons": comparisons
    }


def compare_stat(score1, score2):
    """
    Compare one feature between two vadas.
    """

    difference = abs(score1 - score2)

    # Almost equal
    if difference < 2:
        return "draw"

    if score1 > score2:
        return "vada1"

    return "vada2"