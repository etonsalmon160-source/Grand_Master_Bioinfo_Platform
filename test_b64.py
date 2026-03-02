import base64
import os

def load_image_as_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

logo_path = "app_logo.png"
if os.path.exists(logo_path):
    b64_logo = load_image_as_base64(logo_path)
    print(f"data:image/png;base64,{b64_logo[:50]}...")
else:
    print("Logo not found")
