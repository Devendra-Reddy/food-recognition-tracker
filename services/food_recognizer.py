# food_recognizer.py

import os
from io import BytesIO

# (Optionally, your RoboflowRecognizer class can be in here too)

def recognize_food(image_path, api_choice="nutrition", filename_hint=None):
    # Fake logic for demo/testing or for non-roboflow
    if api_choice == "roboflow":
        try:
            # from PIL import Image
            # recognizer = RoboflowRecognizer()
            # with open(image_path, "rb") as f:
            #     image_bytes = BytesIO(f.read())
            # result = recognizer.recognizefood(image_bytes)
            # if result and "predictions" in result and result["predictions"]:
            #     return result["predictions"][0].get("class", "Unknown Food")
            # return "Unknown Food"
            # DEMO: skip actual API call for now
            return "Detected Food"
        except Exception:
            pass
    if filename_hint:
        return os.path.splitext(os.path.basename(filename_hint))[0].replace("_", " ").title()
    return "Sample Food"
