from scorer import calculate_vada_iq

import cv2
import numpy as np


def contour_circularity(contour):
    """
    Calculate how circular a contour is.
    Returns a value between 0 and 1.
    """

    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)

    if area <= 0 or perimeter <= 0:
        return 0

    return (4 * np.pi * area) / (perimeter * perimeter)


def find_best_vada_contour(contours, image_shape):
    """
    Choose the contour most likely to be a vada.

    The score considers:
    - contour size
    - circularity
    - distance from image center
    """

    image_height, image_width = image_shape[:2]
    image_area = image_height * image_width

    image_center_x = image_width / 2
    image_center_y = image_height / 2

    best_contour = None
    best_score = -1

    for contour in contours:

        area = cv2.contourArea(contour)

        # Ignore very small contours/noise
        if area < image_area * 0.005:
            continue

        # Ignore contours that are almost the entire image
        if area > image_area * 0.90:
            continue

        perimeter = cv2.arcLength(contour, True)

        if perimeter <= 0:
            continue

        # Circularity: 1 = perfect circle
        circularity = (
            4 * np.pi * area
        ) / (perimeter * perimeter)

        circularity = max(
            0,
            min(1, circularity)
        )

        # Get contour center
        moments = cv2.moments(contour)

        if moments["m00"] == 0:
            continue

        contour_x = moments["m10"] / moments["m00"]
        contour_y = moments["m01"] / moments["m00"]

        # Distance from image center
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

        # Area score
        area_ratio = area / image_area

        area_score = min(
            1,
            area_ratio * 5
        )

        # Final "vada likelihood" score
        vada_score = (
            circularity * 0.50 +
            center_score * 0.30 +
            area_score * 0.20
        )

        if vada_score > best_score:
            best_score = vada_score
            best_contour = contour

    return best_contour


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

    # Improve local contrast slightly
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

    # Close small gaps in edges
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
    # FIND ALL CONTOURS
    # --------------------------------

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return {
            "success": False,
            "message": "Could not detect any object in the image"
        }

    # --------------------------------
    # FIND THE MOST LIKELY VADA
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

    area = cv2.contourArea(
        vada_contour
    )

    perimeter = cv2.arcLength(
        vada_contour,
        True
    )

    circularity = 0

    if perimeter > 0:

        circularity = (
            4 * np.pi * area
        ) / (
            perimeter * perimeter
        ) * 100

        circularity = max(
            0,
            min(100, circularity)
        )

    # --------------------------------
    # CROP DETECTED VADA
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
    # HOLE DETECTION
    # --------------------------------

    _, threshold = cv2.threshold(
        vada_gray,
        80,
        255,
        cv2.THRESH_BINARY_INV
    )

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

            # Ignore noise
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

    masked_vada = cv2.bitwise_and(
        vada_gray,
        vada_gray,
        mask=vada_mask
    )

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

    texture_score = min(
        100,
        texture_score / 15
    )

    brightness_pixels = vada_gray[
        vada_mask > 0
    ]

    if len(brightness_pixels) > 0:

        brightness = np.mean(
            brightness_pixels
        )

    else:
        brightness = 255

    browning_score = 100 - (
        brightness / 255 * 100
    )

    browning_score = max(
        0,
        min(100, browning_score)
    )

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