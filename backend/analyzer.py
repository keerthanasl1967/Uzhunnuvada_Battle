from scorer import calculate_vada_iq
import cv2
import numpy as np


def analyze_image(image_bytes):

    # Convert uploaded image bytes into NumPy array
    image_array = np.frombuffer(image_bytes, np.uint8)

    # Decode image
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    # Check if image is valid
    if image is None:
        return {
            "success": False,
            "message": "Could not read image"
        }

    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # -------------------------
    # CIRCULARITY
    # -------------------------

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    edges = cv2.Canny(
        blurred,
        50,
        150
    )

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    circularity = 0

    if contours:

        # Find the largest contour
        largest_contour = max(
            contours,
            key=cv2.contourArea
        )

        area = cv2.contourArea(
            largest_contour
        )

        perimeter = cv2.arcLength(
            largest_contour,
            True
        )

        if perimeter > 0:

            circularity = (
                4 * np.pi * area
            ) / (perimeter * perimeter) * 100

            circularity = max(
                0,
                min(100, circularity)
            )

    # -------------------------
    # SYMMETRY
    # -------------------------

    # Resize image
    resized = cv2.resize(
        gray,
        (200, 200)
    )

    # Split into two halves
    left_half = resized[:, :100]
    right_half = resized[:, 100:]

    # Flip the right half
    right_half_flipped = cv2.flip(
        right_half,
        1
    )

    # Compare both sides
    difference = cv2.absdiff(
        left_half,
        right_half_flipped
    )

    difference_score = np.mean(
        difference
    )

    symmetry = 100 - (
        difference_score / 255 * 100
    )

    symmetry = max(
        0,
        min(100, symmetry)
    )

    # -------------------------
    # HOLE QUALITY
    # -------------------------

    # Detect dark areas
    _, threshold = cv2.threshold(
        gray,
        80,
        255,
        cv2.THRESH_BINARY_INV
    )

    hole_contours, _ = cv2.findContours(
        threshold,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    hole_quality = 0

    if hole_contours:

        # Image center
        center_x = image.shape[1] / 2
        center_y = image.shape[0] / 2

        best_hole = None
        best_distance = float("inf")

        # Find contour closest to the center
        for contour in hole_contours:

            hole_area = cv2.contourArea(
                contour
            )

            # Ignore tiny noise
            if hole_area < 50:
                continue

            moments = cv2.moments(
                contour
            )

            if moments["m00"] == 0:
                continue

            hole_x = (
                moments["m10"] /
                moments["m00"]
            )

            hole_y = (
                moments["m01"] /
                moments["m00"]
            )

            distance = np.sqrt(
                (hole_x - center_x) ** 2 +
                (hole_y - center_y) ** 2
            )

            if distance < best_distance:

                best_distance = distance
                best_hole = contour

        # Calculate hole circularity
        if best_hole is not None:

            hole_area = cv2.contourArea(
                best_hole
            )

            hole_perimeter = cv2.arcLength(
                best_hole,
                True
            )

            if hole_perimeter > 0:

                hole_circularity = (
                    4 * np.pi * hole_area
                ) / (hole_perimeter ** 2) * 100

                hole_quality = max(
                    0,
                    min(100, hole_circularity)
                )

    # -------------------------
    # CRISPINESS
    # -------------------------

    # Detect texture
    laplacian = cv2.Laplacian(
        gray,
        cv2.CV_64F
    )

    texture_score = laplacian.var()

    # Normalize texture score
    texture_score = min(
        100,
        texture_score / 10
    )

    # Measure brightness
    brightness = np.mean(
        gray
    )

    # Darker / browned surface score
    browning_score = 100 - (
        brightness / 255 * 100
    )

    browning_score = max(
        0,
        min(100, browning_score)
    )

    # Combine texture and browning
    crispiness = (
        texture_score * 0.6 +
        browning_score * 0.4
    )

    crispiness = max(
        0,
        min(100, crispiness)
    )

    # -------------------------
    # VADA IQ
    # -------------------------

    stats = {
        "circularity": round(float(circularity), 2),
        "symmetry": round(float(symmetry), 2),
        "holeQuality": round(float(hole_quality), 2),
        "crispiness": round(float(crispiness), 2)
    }

    # Calculate final Vada IQ
    stats["vadaIQ"] = calculate_vada_iq(stats)

    # -------------------------
    # RETURN RESULTS
    # -------------------------

    return {
        "success": True,
        "stats": stats
    }