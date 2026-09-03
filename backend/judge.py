def get_battle_analysis(vada1_score, vada2_score):
    """
    Compare two final Vada scores and decide:
    - Winner
    - Battle type
    - Score difference
    - Battle message
    """

    # Convert scores to float
    score1 = float(vada1_score)
    score2 = float(vada2_score)

    # Calculate difference
    difference = round(
        abs(score1 - score2),
        2
    )

    # --------------------------------
    # TIE
    # --------------------------------

    if difference < 1:

        return {
            "winner": "tie",
            "battleType": "tie",
            "difference": difference,
            "message": (
                "🤝 It's a perfect tie! "
                "Both vadas came out equally crispy and dangerous."
            )
        }

    # --------------------------------
    # CLOSE BATTLE
    # --------------------------------

    if difference < 5:

        winner = (
            "vada1"
            if score1 > score2
            else "vada2"
        )

        winner_name = (
            "Vada 1"
            if winner == "vada1"
            else "Vada 2"
        )

        return {
            "winner": winner,
            "battleType": "close_battle",
            "difference": difference,
            "message": (
                f"🔥 What a close battle! "
                f"{winner_name} wins by only "
                f"{difference} points!"
            )
        }

    # --------------------------------
    # CLEAR WINNER
    # --------------------------------

    winner = (
        "vada1"
        if score1 > score2
        else "vada2"
    )

    winner_name = (
        "Vada 1"
        if winner == "vada1"
        else "Vada 2"
    )

    return {
        "winner": winner,
        "battleType": "clear_winner",
        "difference": difference,
        "message": (
            f"🏆 {winner_name} takes the crown! "
            f"It wins with a {difference}-point advantage."
        )
    }