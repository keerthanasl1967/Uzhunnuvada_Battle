def get_battle_analysis(iq1, iq2):
    difference = abs(iq1 - iq2)

    if iq1 == iq2:
        return {
            "winner": "draw",
            "battleType": "legendary_draw",
            "message": "🤝 The AI judge is confused. Both vadas achieved equal frying greatness!"
        }

    winner = "vada1" if iq1 > iq2 else "vada2"

    if difference < 3:
        battle_type = "photo_finish"
        message = (
            f"😱 PHOTO FINISH! {winner.upper()} wins by only "
            f"{round(difference, 2)} IQ points. The AI had to inspect every crumb!"
        )

    elif difference < 10:
        battle_type = "close_battle"
        message = (
            f"⚔️ A fierce battle! {winner.upper()} wins, "
            "but the losing vada can still hold its hole high."
        )

    elif difference < 25:
        battle_type = "clear_winner"
        message = (
            f"🏆 The AI has spoken! {winner.upper()} takes the crown "
            "with a strong frying performance!"
        )

    else:
        battle_type = "absolute_destruction"
        message = (
            f"🔥 TOTAL VADA DOMINATION! {winner.upper()} didn't just win — "
            "it sent the other vada back to the batter bowl!"
        )

    return {
        "winner": winner,
        "battleType": battle_type,
        "difference": round(difference, 2),
        "message": message
    }