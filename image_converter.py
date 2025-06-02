import base64
import requests
import json
import os
from io import BytesIO
from PIL import Image

# 🔧 CONFIGURATION
FIREBASE_URL = "https://egg-incubator-iot-discord-default-rtdb.asia-southeast1.firebasedatabase.app/test_data/image_base64.json"
IMAGE_PATH = "uploads/fgr.png"
MAX_BASE64_SIZE = 750 * 1024  # 750 KB

def optimize_image(image_path: str, max_base64_size: int) -> BytesIO:
    img = Image.open(image_path)
    img_format = img.format or "JPEG"
    original_size = os.path.getsize(image_path)
    print(f"Original Image: {img.width}x{img.height} | {original_size / 1024:.2f} KB")

    quality = 85
    scale_factor = 1.0
    final_width, final_height, final_size = img.width, img.height, original_size

    while True:
        buffer = BytesIO()

        # Resize if needed
        if scale_factor < 1.0:
            new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
            resized = img.resize(new_size, Image.Resampling.LANCZOS)
        else:
            resized = img

        # Save with reduced quality
        resized.save(buffer, format=img_format, quality=quality)
        base64_len = len(base64.b64encode(buffer.getvalue()))

        if base64_len <= max_base64_size or quality < 30:
            final_width, final_height = resized.size
            final_size = len(buffer.getvalue())
            break

        # Decrease size
        if scale_factor > 0.5:
            scale_factor -= 0.1
        elif quality > 30:
            quality -= 5
        else:
            break  # Can't shrink more

    print(f"Final Image: {final_width}x{final_height} | {final_size / 1024:.2f} KB")
    buffer.seek(0)
    return buffer

def encode_image_to_base64(image_bytes_io: BytesIO) -> str:
    return base64.b64encode(image_bytes_io.read()).decode('utf-8')

def upload_to_firebase(base64_string: str, firebase_url: str):
    headers = {"Content-Type": "application/json"}
    payload = json.dumps(base64_string)
    response = requests.put(firebase_url, data=payload, headers=headers)
    if response.ok:
        print("\u2705 Image successfully uploaded to Firebase.")
    else:
        print(f"❌ Upload failed. Code: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    optimized_buffer = optimize_image(IMAGE_PATH, MAX_BASE64_SIZE)
    encoded_string = encode_image_to_base64(optimized_buffer)
    upload_to_firebase(encoded_string, FIREBASE_URL)
