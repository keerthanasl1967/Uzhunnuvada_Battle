from scorer import calculate_vada_iq

import cv2
import numpy as np


def analyze_image(image_bytes):

    # --------------------------------
    # READ IMAGE
    # --------------------------------

    image_array = np.frombuffer(
        image_bytes,
        np.uint8
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    if image is None:
        return {
            "success": False,
            "message": "Could not read image"
        }

    # Resize very large images
    height, width = image.shape[:2]

    max_size = 800

    if max(height, width) > max_size:

        scale = max_size / max(height, width)

        image = cv2.resize(
            image,
            (
                int(width * scale),
                int(height * scale)
            )
        )

    # --------------------------------
    # CONVERT TO GRAYSCALE
    # --------------------------------

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    blurred = cv2.GaussianBlur(
        gray,
        (7, 7),
        0
    )

    # --------------------------------
    # DETECT MAIN VADA CONTOUR
    # --------------------------------

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

    if not contours:
        return {
            "success": False,
            "message": "Could not detect a vada in the image"
        }

    # Find largest contour
    largest_contour = max(
        contours,
        key=cv2.contourArea
    )

    area = cv2.contourArea(
        largest_contour
    )

    # Reject extremely tiny detections
    image_area = image.shape[0] * image.shape[1]

    if area < image_area * 0.01:
        return {
            "success": False,
            "message": "The detected vada is too small"
        }

    # --------------------------------
    # CREATE VADA MASK
    # --------------------------------

    mask = np.zeros(
        gray.shape,
        dtype=np.uint8
    )

    cv2.drawContours(
        mask,
        [largest_contour],
        -1,
        255,
        thickness=cv2.FILLED
    )

    # --------------------------------
    # CIRCULARITY
    # --------------------------------

    perimeter = cv2.arcLength(
        largest_contour,
        True
    )

    circularity = 0

    if perimeter > 0:

        circularity = (
            4 * np.pi * area
        ) / (perimeter * perimeter) * 100

        circularity = max(
            0,
            min(100, circularity)
        )

    # --------------------------------
    # GET BOUNDING BOX OF VADA
    # --------------------------------

    x, y, w, h = cv2.boundingRect(
        largest_contour
    )

    vada_gray = gray[y:y + h, x:x + w]
    vada_mask = mask[y:y + h, x:x + w]

    # --------------------------------
    # SYMMETRY
    # --------------------------------

    # Resize detected vada
    vada_resized = cv2.resize(
        vada_gray,
        (200, 200)
    )

    mask_resized = cv2.resize(
        vada_mask,
        (200, 200)
    )

    # Left and right halves
    left_half = vada_resized[:, :100]
    right_half = vada_resized[:, 100:]

    left_mask = mask_resized[:, :100]
    right_mask = mask_resized[:, 100:]

    # Flip right half
    right_half_flipped = cv2.flip(
        right_half,
        1
    )

    right_mask_flipped = cv2.flip(
        right_mask,
        1
    )

    # Compare the two sides
    difference = cv2.absdiff(
        left_half,
        right_half_flipped
    )

    # Only consider pixels inside the vada
    valid_mask = cv2.bitwise_and(
        left_mask,
        right_mask_flipped
    )

    valid_pixels = difference[
        valid_mask > 0
    ]

    if len(valid_pixels) > 0:

        difference_score = np.mean(
            valid_pixels
        )

        symmetry = 100 - (
            difference_score / 255 * 100
        )

    else:

        symmetry = 0

    symmetry = max(
        0,
        min(100, symmetry)
    )

    # --------------------------------
    # HOLE QUALITY
    # --------------------------------

    # Threshold darker regions
    _, threshold = cv2.threshold(
        vada_gray,
        80,
        255,
        cv2.THRESH_BINARY_INV
    )

    # Only look inside detected vada
    threshold = cv2.bitwise_and(
        threshold,
        vada_mask
    )

    hole_contours, _ = cv2.findContours(
        threshold,
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_SIMPLE
    )

    hole_quality = 0

    if hole_contours:

        center_x = w / 2
        center_y = h / 2

        best_hole = None
        best_distance = float("inf")

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

        # Score the best central hole
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
                ) / (
                    hole_perimeter ** 2
                ) * 100

                # Also reward a reasonably sized hole
                hole_ratio = (
                    hole_area / (w * h)
                ) * 100

                size_score = min(
                    100,
                    hole_ratio * 15
                )

                hole_quality = (
                    hole_circularity * 0.7 +
                    size_score * 0.3
                )

    hole_quality = max(
        0,
        min(100, hole_quality)
    )

    # --------------------------------
    # CRISPINESS
    # --------------------------------

    # Only analyze the detected vada
    masked_vada = cv2.bitwise_and(
        vada_gray,
        vada_gray,
        mask=vada_mask
    )

    # Texture measurement
    laplacian = cv2.Laplacian(
        masked_vada,
        cv2.CV_64F
    )

    texture_pixels = laplacian[
        vada_mask > 0
    ]

    if len(texture_pixels) > 0:

        texture_score = np.var(
            texture_pixels
        )

    else:

        texture_score = 0

    # Normalize texture
    texture_score = min(
        100,
        texture_score / 15
    )

    # Average brightness only inside vada
    brightness_pixels = vada_gray[
        vada_mask > 0
    ]

    if len(brightness_pixels) > 0:

        brightness = np.mean(
            brightness_pixels
        )

    else:

        brightness = 255

    # Moderate browning
    browning_score = 100 - (
        brightness / 255 * 100
    )

    browning_score = max(
        0,
        min(100, browning_score)
    )

    # Final crispiness score
    crispiness = (
        texture_score * 0.65 +
        browning_score * 0.35
    )

    crispiness = max(
        0,
        min(100, crispiness)
    )

    # --------------------------------
    # CREATE STATS
    # --------------------------------

    stats = {
        "circularity": round(
            float(circularity),
            2
        ),

        "symmetry": round(
            float(symmetry),
            2
        ),

        "holeQuality": round(
            float(hole_quality),
            2
        ),

        "crispiness": round(
            float(crispiness),
            2
        )
    }

    # --------------------------------
    # CALCULATE VADA IQ
    # --------------------------------

    stats["vadaIQ"] = calculate_vada_iq(
        stats
    )

    # --------------------------------
    # RETURN RESULT
    # --------------------------------

    return {
        "success": True,
        "stats": stats
    }