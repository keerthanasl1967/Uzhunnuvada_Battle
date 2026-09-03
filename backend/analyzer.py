import cv2
import numpy as np


# --------------------------------
# DECODE IMAGE
# --------------------------------

def decode_image(image_bytes):
    """
    Convert uploaded image bytes
    into an OpenCV BGR image.
    """

    image_array = np.frombuffer(
        image_bytes,
        dtype=np.uint8
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    return image


# --------------------------------
# RESIZE IMAGE
# --------------------------------

def resize_image(image, max_width=800):
    """
    Resize large images while
    maintaining aspect ratio.
    """

    height, width = image.shape[:2]

    if width <= max_width:
        return image

    scale = max_width / width

    new_width = int(width * scale)
    new_height = int(height * scale)

    return cv2.resize(
        image,
        (new_width, new_height),
        interpolation=cv2.INTER_AREA
    )


# --------------------------------
# DETECT VADA CONTOUR
# --------------------------------

def find_vada_contour(image):
    """
    Detect the most likely outer
    contour of the vada.
    """

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    blurred = cv2.GaussianBlur(
        gray,
        (7, 7),
        0
    )

    edges = cv2.Canny(
        blurred,
        30,
        120
    )

    kernel = np.ones(
        (7, 7),
        np.uint8
    )

    edges = cv2.morphologyEx(
        edges,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=2
    )

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return None

    height, width = image.shape[:2]
    image_area = height * width

    best_contour = None
    best_score = -1

    for contour in contours:

        area = cv2.contourArea(contour)

        # Ignore very small objects
        if area < image_area * 0.02:
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

        x, y, w, h = cv2.boundingRect(
            contour
        )

        if max(w, h) == 0:
            continue

        aspect_ratio = min(w, h) / max(w, h)

        contour_score = (
            circularity * 0.7
            +
            aspect_ratio * 0.3
        )

        if contour_score > best_score:
            best_score = contour_score
            best_contour = contour

    return best_contour


# --------------------------------
# CREATE VADA MASK
# --------------------------------

def create_vada_mask(image, contour):
    """
    Create a binary mask for the
    detected vada.
    """

    height, width = image.shape[:2]

    mask = np.zeros(
        (height, width),
        dtype=np.uint8
    )

    cv2.drawContours(
        mask,
        [contour],
        -1,
        255,
        thickness=cv2.FILLED
    )

    return mask


# --------------------------------
# CALCULATE CIRCULARITY
# --------------------------------

def calculate_circularity(contour):

    area = cv2.contourArea(
        contour
    )

    perimeter = cv2.arcLength(
        contour,
        True
    )

    if perimeter <= 0:
        return 0.0

    circularity = (
        4 * np.pi * area
    ) / (
        perimeter * perimeter
    )

    circularity = max(
        0.0,
        min(1.0, circularity)
    )

    return round(
        circularity * 100,
        2
    )


# --------------------------------
# CALCULATE SYMMETRY
# --------------------------------

def calculate_symmetry(mask):
    """
    Compare left and right halves
    of the vada mask.
    """

    height, width = mask.shape

    if width < 2:
        return 0.0

    center = width // 2

    left = mask[:, :center]

    right = mask[:, width - center:]

    right = cv2.flip(
        right,
        1
    )

    min_width = min(
        left.shape[1],
        right.shape[1]
    )

    left = left[:, :min_width]
    right = right[:, :min_width]

    difference = cv2.absdiff(
        left,
        right
    )

    total_pixels = difference.size

    if total_pixels == 0:
        return 0.0

    difference_ratio = (
        np.count_nonzero(difference)
        / total_pixels
    )

    symmetry = (
        1 - difference_ratio
    ) * 100

    symmetry = max(
        0.0,
        min(100.0, symmetry)
    )

    return round(
        symmetry,
        2
    )


# --------------------------------
# FIND BEST CENTER HOLE
# --------------------------------

def find_best_hole(
    gray,
    vada_mask,
    vada_contour
):
    """
    Find the most likely center hole.
    """

    moments = cv2.moments(
        vada_contour
    )

    if moments["m00"] == 0:
        return None, 0.0

    vada_x = (
        moments["m10"]
        / moments["m00"]
    )

    vada_y = (
        moments["m01"]
        / moments["m00"]
    )

    blurred = cv2.GaussianBlur(
        gray,
        (5, 5),
        0
    )

    threshold = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        31,
        5
    )

    threshold = cv2.bitwise_and(
        threshold,
        vada_mask
    )

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

    vada_area = cv2.contourArea(
        vada_contour
    )

    if vada_area <= 0:
        return None, 0.0

    equivalent_radius = np.sqrt(
        vada_area / np.pi
    )

    best_hole = None
    best_score = -1.0

    for contour in contours:

        area = cv2.contourArea(
            contour
        )

        if area < 30:
            continue

        area_ratio = (
            area / vada_area
        )

        # Ignore contours that are
        # unrealistically large
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
            0.0,
            min(1.0, circularity)
        )

        hole_moments = cv2.moments(
            contour
        )

        if hole_moments["m00"] == 0:
            continue

        hole_x = (
            hole_moments["m10"]
            / hole_moments["m00"]
        )

        hole_y = (
            hole_moments["m01"]
            / hole_moments["m00"]
        )

        distance = np.sqrt(
            (hole_x - vada_x) ** 2
            +
            (hole_y - vada_y) ** 2
        )

        center_score = (
            1 -
            min(
                1.0,
                distance / max(
                    equivalent_radius,
                    1
                )
            )
        )

        # Ideal hole is approximately
        # 6% of total vada area
        ideal_ratio = 0.06

        size_difference = abs(
            area_ratio - ideal_ratio
        )

        size_score = (
            1 -
            min(
                1.0,
                size_difference / ideal_ratio
            )
        )

        hole_score = (
            circularity * 0.45
            +
            center_score * 0.35
            +
            size_score * 0.20
        )

        if hole_score > best_score:

            best_score = hole_score
            best_hole = contour

    if best_hole is None:
        return None, 0.0

    return (
        best_hole,
        round(best_score * 100, 2)
    )


# --------------------------------
# CALCULATE CRISPINESS
# --------------------------------

def calculate_crispiness(
    gray,
    vada_mask
):
    """
    Estimate crispiness using
    texture and edge density.
    """

    masked_gray = cv2.bitwise_and(
        gray,
        gray,
        mask=vada_mask
    )

    laplacian = cv2.Laplacian(
        masked_gray,
        cv2.CV_64F
    )

    texture_value = laplacian.var()

    edges = cv2.Canny(
        masked_gray,
        50,
        150
    )

    edge_pixels = np.count_nonzero(
        edges
    )

    vada_pixels = np.count_nonzero(
        vada_mask
    )

    if vada_pixels == 0:
        return 0.0

    edge_density = (
        edge_pixels
        / vada_pixels
    )

    texture_score = min(
        100,
        (texture_value / 500) * 100
    )

    edge_score = min(
        100,
        (edge_density / 0.20) * 100
    )

    crispiness = (
        texture_score * 0.6
        +
        edge_score * 0.4
    )

    crispiness = max(
        0.0,
        min(100.0, crispiness)
    )

    return round(
        crispiness,
        2
    )


# --------------------------------
# CALCULATE VADA IQ
# --------------------------------

def calculate_vada_iq(
    circularity,
    symmetry,
    hole_quality,
    crispiness
):

    vada_iq = (
        circularity * 0.30
        +
        symmetry * 0.25
        +
        hole_quality * 0.25
        +
        crispiness * 0.20
    )

    vada_iq = max(
        0.0,
        min(100.0, vada_iq)
    )

    return round(
        vada_iq,
        2
    )


# --------------------------------
# CREATE DEBUG IMAGE
# --------------------------------

def create_debug_image(
    image,
    vada_contour,
    hole_contour
):
    """
    Draw OpenCV detection results.
    """

    debug_image = image.copy()

    # Draw outer vada contour
    if vada_contour is not None:

        cv2.drawContours(
            debug_image,
            [vada_contour],
            -1,
            (0, 255, 0),
            4
        )

        moments = cv2.moments(
            vada_contour
        )

        if moments["m00"] != 0:

            center_x = int(
                moments["m10"]
                / moments["m00"]
            )

            center_y = int(
                moments["m01"]
                / moments["m00"]
            )

            # Blue center point
            cv2.circle(
                debug_image,
                (center_x, center_y),
                8,
                (255, 0, 0),
                -1
            )

    # Draw detected hole
    if hole_contour is not None:

        cv2.drawContours(
            debug_image,
            [hole_contour],
            -1,
            (0, 0, 255),
            4
        )

    return debug_image


# --------------------------------
# MAIN IMAGE ANALYSIS
# --------------------------------

def analyze_image(image_bytes):
    """
    Main function used by FastAPI.
    """

    try:

        # 1. Decode image
        image = decode_image(
            image_bytes
        )

        if image is None:
            return {
                "success": False,
                "message": "Could not decode image."
            }

        # 2. Resize
        image = resize_image(
            image
        )

        # 3. Convert to grayscale
        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        # 4. Detect vada contour
        contour = find_vada_contour(
            image
        )

        if contour is None:
            return {
                "success": False,
                "message": (
                    "Could not detect a vada "
                    "in this image."
                )
            }

        # 5. Create vada mask
        vada_mask = create_vada_mask(
            image,
            contour
        )

        # 6. Calculate circularity
        circularity = calculate_circularity(
            contour
        )

        # 7. Calculate symmetry
        symmetry = calculate_symmetry(
            vada_mask
        )

        # 8. Detect center hole
        hole_contour, hole_quality = find_best_hole(
            gray,
            vada_mask,
            contour
        )

        # 9. Calculate crispiness
        crispiness = calculate_crispiness(
            gray,
            vada_mask
        )

        # 10. Calculate Vada IQ
        vada_iq = calculate_vada_iq(
            circularity,
            symmetry,
            hole_quality,
            crispiness
        )

        # 11. Create debug visualization
        debug_image = create_debug_image(
            image,
            contour,
            hole_contour
        )

        # 12. Convert debug image to JPEG bytes
        encode_success, buffer = cv2.imencode(
            ".jpg",
            debug_image
        )

        debug_image_bytes = None

        if encode_success:
            debug_image_bytes = buffer.tobytes()

        # 13. Return analysis
        return {
            "success": True,

            "stats": {
                "circularity": circularity,
                "symmetry": symmetry,
                "holeQuality": hole_quality,
                "crispiness": crispiness,
                "vadaIQ": vada_iq
            },

            "debug_image": debug_image_bytes
        }

    except Exception as error:

        return {
            "success": False,
            "message": str(error)
        }