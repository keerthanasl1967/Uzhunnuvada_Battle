from scorer import calculate_vada_iq

import cv2
import numpy as np


# --------------------------------
# HELPER: CONTOUR CIRCULARITY
# --------------------------------

def contour_circularity(contour):
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)

    if area <= 0 or perimeter <= 0:
        return 0.0

    circularity = (
        4 * np.pi * area
    ) / (
        perimeter * perimeter
    )

    return max(0.0, min(1.0, circularity))


# --------------------------------
# FIND BEST VADA CONTOUR
# --------------------------------

def find_best_vada_contour(contours, image_shape):
    """
    Choose the contour most likely to be the vada.
    """

    image_height, image_width = image_shape[:2]
    image_area = image_height * image_width

    image_center_x = image_width / 2
    image_center_y = image_height / 2

    best_contour = None
    best_score = -1

    for contour in contours:

        area = cv2.contourArea(contour)

        # Ignore tiny noise
        if area < image_area * 0.005:
            continue

        # Ignore contour covering almost the entire image
        if area > image_area * 0.90:
            continue

        circularity = contour_circularity(contour)

        moments = cv2.moments(contour)

        if moments["m00"] == 0:
            continue

        contour_x = moments["m10"] / moments["m00"]
        contour_y = moments["m01"] / moments["m00"]

        # Check how close the contour is to image center
        distance = np.sqrt(
            (contour_x - image_center_x) ** 2 +
            (contour_y - image_center_y) ** 2
        )

        max_distance = np.sqrt(
            image_center_x ** 2 +
            image_center_y ** 2
        )

        center_score = 1 - (
            distance / max_distance
        )

        center_score = max(
            0,
            min(1, center_score)
        )

        # Larger reasonable contours get a better score
        area_ratio = area / image_area

        area_score = min(
            1,
            area_ratio * 5
        )

        # Final likelihood score
        vada_score = (
            circularity * 0.50 +
            center_score * 0.30 +
            area_score * 0.20
        )

        if vada_score > best_score:
            best_score = vada_score
            best_contour = contour

    return best_contour


# --------------------------------
# FIND BEST VADA HOLE
# --------------------------------

def find_best_hole(gray, vada_mask):
    """
    Find the most likely center hole of the vada.
    """

    blurred = cv2.GaussianBlur(
        gray,
        (5, 5),
        0
    )

    # Adaptive threshold handles different lighting
    threshold = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        31,
        5
    )

    # Only look inside the vada
    threshold = cv2.bitwise_and(
        threshold,
        vada_mask
    )

    # Remove small noise
    kernel = np.ones(
        (3, 3),
        np.uint8
    )

    threshold = cv2.morphologyEx(
        threshold,
        cv2.MORPH_OPEN,
        kernel,
        iterations=1
    )

    contours, _ = cv2.findContours(
        threshold,
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_SIMPLE
    )

    height, width = gray.shape[:2]

    center_x = width / 2
    center_y = height / 2

    vada_area = cv2.countNonZero(vada_mask)

    best_hole = None
    best_score = -1

    for contour in contours:

        area = cv2.contourArea(contour)

        # Ignore tiny regions
        if area < 30:
            continue

        area_ratio = area / max(vada_area, 1)

        # Hole should not occupy too much of the vada
        if area_ratio > 0.25:
            continue

        perimeter = cv2.arcLength(
            contour,
            True
        )

        if perimeter <= 0:
            continue

        circularity = (
            4 * np.pi * area
        ) / (
            perimeter * perimeter
        )

        circularity = max(
            0,
            min(1, circularity)
        )

        moments = cv2.moments(contour)

        if moments["m00"] == 0:
            continue

        hole_x = moments["m10"] / moments["m00"]
        hole_y = moments["m01"] / moments["m00"]

        # Distance from center
        distance = np.sqrt(
            (hole_x - center_x) ** 2 +
            (hole_y - center_y) ** 2
        )

        max_distance = np.sqrt(
            center_x ** 2 +
            center_y ** 2
        )

        center_score = 1 - (
            distance / max_distance
        )

        center_score = max(
            0,
            min(1, center_score)
        )

        # Ideal hole size is roughly 6% of vada area
        ideal_ratio = 0.06

        size_difference = abs(
            area_ratio - ideal_ratio
        )

        size_score = 1 - min(
            1,
            size_difference / ideal_ratio
        )

        # Final hole likelihood
        hole_score = (
            circularity * 0.45 +
            center_score * 0.35 +
            size_score * 0.20
        )

        if hole_score > best_score:
            best_score = hole_score
            best_hole = contour

    return best_hole, best_score


# --------------------------------
# MAIN IMAGE ANALYSIS
# --------------------------------

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

    # --------------------------------
    # RESIZE LARGE IMAGE
    # --------------------------------

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
    # PREPROCESSING
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

    # Improve contrast
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(
        blurred
    )

    # --------------------------------
    # EDGE DETECTION
    # --------------------------------

    edges = cv2.Canny(
        enhanced,
        40,
        130
    )

    # Close small gaps
    kernel = np.ones(
        (5, 5),
        np.uint8
    )

    edges = cv2.morphologyEx(
        edges,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=2
    )

    # --------------------------------
    # FIND CONTOURS
    # --------------------------------

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return {
            "success": False,
            "message": "Could not detect any object"
        }

    # --------------------------------
    # SELECT BEST VADA
    # --------------------------------

    vada_contour = find_best_vada_contour(
        contours,
        image.shape
    )

    if vada_contour is None:
        return {
            "success": False,
            "message": "Could not confidently detect a vada"
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
        [vada_contour],
        -1,
        255,
        thickness=cv2.FILLED
    )

    # --------------------------------
    # CIRCULARITY
    # --------------------------------

    circularity = (
        contour_circularity(vada_contour)
        * 100
    )

    circularity = max(
        0,
        min(100, circularity)
    )

    # --------------------------------
    # CROP THE VADA
    # --------------------------------

    x, y, w, h = cv2.boundingRect(
        vada_contour
    )

    vada_gray = gray[
        y:y + h,
        x:x + w
    ]

    vada_mask = mask[
        y:y + h,
        x:x + w
    ]

    # --------------------------------
    # SYMMETRY
    # --------------------------------

    vada_resized = cv2.resize(
        vada_gray,
        (200, 200)
    )

    mask_resized = cv2.resize(
        vada_mask,
        (200, 200)
    )

    left_half = vada_resized[:, :100]
    right_half = vada_resized[:, 100:]

    left_mask = mask_resized[:, :100]
    right_mask = mask_resized[:, 100:]

    right_half_flipped = cv2.flip(
        right_half,
        1
    )

    right_mask_flipped = cv2.flip(
        right_mask,
        1
    )

    difference = cv2.absdiff(
        left_half,
        right_half_flipped
    )

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
    # IMPROVED HOLE DETECTION
    # --------------------------------

    best_hole, hole_score = find_best_hole(
        vada_gray,
        vada_mask
    )

    hole_quality = 0

    if best_hole is not None:

        hole_area = cv2.contourArea(
            best_hole
        )

        hole_perimeter = cv2.arcLength(
            best_hole,
            True
        )

        hole_circularity = 0

        if hole_perimeter > 0:

            hole_circularity = (
                4 * np.pi * hole_area
            ) / (
                hole_perimeter * hole_perimeter
            )

            hole_circularity = max(
                0,
                min(1, hole_circularity)
            )

        moments = cv2.moments(
            best_hole
        )

        position_score = 0

        if moments["m00"] > 0:

            hole_x = moments["m10"] / moments["m00"]
            hole_y = moments["m01"] / moments["m00"]

            center_x = w / 2
            center_y = h / 2

            distance = np.sqrt(
                (hole_x - center_x) ** 2 +
                (hole_y - center_y) ** 2
            )

            max_distance = np.sqrt(
                center_x ** 2 +
                center_y ** 2
            )

            position_score = 1 - (
                distance / max_distance
            )

            position_score = max(
                0,
                min(1, position_score)
            )

        # Hole size score
        vada_area = cv2.countNonZero(
            vada_mask
        )

        area_ratio = hole_area / max(
            vada_area,
            1
        )

        ideal_ratio = 0.06

        size_score = 1 - min(
            1,
            abs(
                area_ratio - ideal_ratio
            ) / ideal_ratio
        )

        # Final hole quality
        hole_quality = (
            hole_circularity * 0.45 +
            position_score * 0.35 +
            size_score * 0.20
        ) * 100

    hole_quality = max(
        0,
        min(100, hole_quality)
    )

    # --------------------------------
    # IMPROVED CRISPINESS DETECTION
    # --------------------------------

    # Normalize lighting
    clahe_crisp = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    normalized_vada = clahe_crisp.apply(
        vada_gray
    )

    vada_pixels = normalized_vada[
        vada_mask > 0
    ]

    if len(vada_pixels) > 0:

        # Texture analysis
        laplacian = cv2.Laplacian(
            normalized_vada,
            cv2.CV_64F
        )

        texture_pixels = laplacian[
            vada_mask > 0
        ]

        texture_variance = np.var(
            texture_pixels
        )

        texture_score = min(
            100,
            texture_variance / 20
        )

        # Browning analysis
        mean_brightness = np.mean(
            vada_pixels
        )

        # Medium golden-brown target
        ideal_brightness = 120

        brightness_difference = abs(
            mean_brightness - ideal_brightness
        )

        browning_score = 100 - min(
            100,
            (brightness_difference / 120) * 100
        )

        browning_score = max(
            0,
            min(100, browning_score)
        )

    else:

        texture_score = 0
        browning_score = 0

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
    # CREATE FINAL STATS
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