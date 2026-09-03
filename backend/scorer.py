def calculate_vada_iq(stats):

    circularity = stats.get("circularity", 0)
    symmetry = stats.get("symmetry", 0)
    hole_quality = stats.get("holeQuality", 0)
    crispiness = stats.get("crispiness", 0)

    vada_iq = (
        circularity * 0.30 +
        symmetry * 0.25 +
        hole_quality * 0.25 +
        crispiness * 0.20
    )

    return round(vada_iq, 2)