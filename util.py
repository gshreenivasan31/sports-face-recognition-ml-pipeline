import joblib
import json
import numpy as np
import base64
import cv2
import os

from wavelet import w2d

# ===== GEMINI (google-genai) SETUP =====
from google import genai  # comes from the `google-genai` package

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

if GEMINI_API_KEY:
    try:
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        print("Gemini client initialized")
    except Exception as e:
        print("Failed to initialize Gemini client:", e)
        gemini_client = None
else:
    print("WARNING: GEMINI_API_KEY not set. AI summaries will fall back to a basic message.")
    gemini_client = None


def _pretty_name_from_label(label: str) -> str:
    """Convert 'virat_kohli' -> 'Virat Kohli'."""
    if not label:
        return ""
    return label.replace("_", " ").title()


def get_celebrity_summary(label: str) -> str:
    """
    Use Gemini (google-genai SDK) to generate a short profile of the predicted celebrity.
    If GEMINI_API_KEY is not set or an error occurs, returns a fallback string.
    """
    name = _pretty_name_from_label(label)

    if not name:
        return "Unknown person."

    if gemini_client is None:
        return f"{name} is a famous sports personality. (AI summary not available because Gemini is not configured.)"

    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                f"Give a concise, engaging profile (around 120-180 words) of the sports person {name}. "
                f"Include: sport, nationality, major achievements/titles, style of play, impact on their sport, "
                f"and 1–2 interesting or fun facts. "
                f"Write in plain text (no bullet points, no headings)."
            ],
        )

        text = (response.text or "").strip()
        if not text:
            return f"{name} is a well-known sportsperson, but I couldn’t fetch detailed information right now."

        return text

    except Exception as e:
        print("Gemini error:", e)
        return f"Could not fetch AI summary for {name} at the moment."


# ===== ORIGINAL CLASSIFIER CODE =====

__class_name_to_number = {}
__class_number_to_name = {}
__model = None


def classify_image(image_base64_data, file_path=None):
    """
    Takes base64-encoded image (from browser) or file_path, crops faces with 2 eyes,
    extracts raw+wavelet features, and returns model predictions.
    """
    imgs = get_cropped_image_if_2_eyes(file_path, image_base64_data)

    result = []
    for img in imgs:
        scalled_raw_img = cv2.resize(img, (32, 32))
        img_har = w2d(img, 'db1', 5)
        scalled_img_har = cv2.resize(img_har, (32, 32))

        combined_img = np.vstack((
            scalled_raw_img.reshape(32 * 32 * 3, 1),
            scalled_img_har.reshape(32 * 32, 1)
        ))

        len_image_array = 32 * 32 * 3 + 32 * 32
        final = combined_img.reshape(1, len_image_array).astype(float)

        result.append({
            'class': class_number_to_name(__model.predict(final)[0]),
            'class_probability': np.around(__model.predict_proba(final) * 100, 2).tolist()[0],
            'class_dictionary': __class_name_to_number
        })

    return result


def class_number_to_name(class_num):
    return __class_number_to_name[class_num]


def load_saved_artifacts():
    print("loading saved artifacts...start")
    global __class_name_to_number
    global __class_number_to_name
    global __model

    with open("./artifacts/class_dictionary.json", "r") as f:
        __class_name_to_number = json.load(f)
        __class_number_to_name = {v: k for k, v in __class_name_to_number.items()}

    if __model is None:
        with open('./artifacts/saved_model.pkl', 'rb') as f:
            __model = joblib.load(f)

    print("loading saved artifacts...done")


def get_cv2_image_from_base64_string(b64str):
    """
    Convert base64 string (from browser) to cv2 image.
    """
    encoded_data = b64str.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


def get_cropped_image_if_2_eyes(image_path, image_base64_data):
    face_cascade = cv2.CascadeClassifier('./opencv/haarcascades/haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('./opencv/haarcascades/haarcascade_eye.xml')

    if image_path:
        img = cv2.imread(image_path)
    else:
        img = get_cv2_image_from_base64_string(image_base64_data)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    cropped_faces = []
    for (x, y, w, h) in faces:
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = img[y:y + h, x:x + w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        if len(eyes) >= 2:
            cropped_faces.append(roi_color)

    return cropped_faces


def get_b64_test_image_for_virat():
    with open("b64.txt") as f:
        return f.read()


if __name__ == '__main__':
    load_saved_artifacts()
    print(classify_image(get_b64_test_image_for_virat(), None))
    # For manual test of summary (run this file directly):
    # print(get_celebrity_summary("virat_kohli"))
