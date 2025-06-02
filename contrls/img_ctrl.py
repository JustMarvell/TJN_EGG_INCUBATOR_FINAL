import requests
import settings
import discord
import time
import base64
import asyncio
import io
import conns.firebase as firebase
from discord import File

async def get_image():
    requests.put(settings.FIREBASE_COMMAND_PATH, json='take_picture')
    
    for _ in range(20):
        response = requests.get(settings.FIREBASE_PHOTO_PATH)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "done":
                parts = [data.get(f"part{i}") for i in range(1, 6)]
                if all(parts):
                    image_base64 = "".join(parts)
                    requests.put(f'{settings.FIREBASE_API_SECRET}/device_responses/take_picture/status.json', json="waiting")
                    try:
                        image_bytes = base64.b64decode(image_base64)
                        # file = discord.File(fp=discord.File(fp=io.BytesIO(image_bytes), filename="photo.jpg")
                        return image_bytes
                    except Exception as e:
                        return None
        await asyncio.sleep(0.5)
        
    requests.put(settings.FIREBASE_COMMAND_PATH, json="idle")
    return None
    
    
#region old
    # # send command
    # command_post = requests.put(settings.FIREBASE_API_SECRET + "/device_commands/command.json", json="take_picture")
    # if command_post.status_code != 200:
    #     print("Failed to send take_picture command.")
    #     return None
    # print("Command sent. Waiting for image data...")
    
    # time.sleep(1)  # delay
    
    # # wait for status
    
    # time.sleep(1)  # delay
    # status_response = await get_status(0)
    # if status_response == None:
    #     print("Timed out waiting for the image")
    #     return None        
    
    # # reasemble image and return
    # data_response = requests.get(settings.FIREBASE_API_SECRET + "/device_responses/take_picture.json")
    # if data_response.status_code == 200:
    #     p1 = data_response.json().get("part1")
    #     if p1 == None:
    #         print("No image 1 data found.")
    #         return None
    #     p2 = data_response.json().get("part2")
    #     if p2 == None:
    #         print("No image 2 data found.")
    #         return None
    #     p3 = data_response.json().get("part3")
    #     if p3 == None:
    #         print("No image 3 data found.")
    #         return None
    #     p4 = data_response.json().get("part4")
    #     if p4 == None:
    #         print("No image 4 data found.")
    #         return None
    #     p5 = data_response.json().get("part5")
    #     if p4 == None:
    #         print("No image 5 data found.")
    #         return None
        
    #     image_base64 = str(p1 + p2 + p3 + p4 + p5)
        
    #     if not image_base64:
    #         print("No image64 data found.")
    #         return None
        
    #     try:
    #         image_bytes = base64.b64decode(image_base64)
    #         print("Image data received and decoded successfully.")
    #         return image_bytes
    #     except Exception as e:
    #         print(f"Decode error: {e}")
    #         return None
    # else:
    #     print("Failed to get image data.")
    #     return None

# max_attempts = 20
# current_attempts = 0
# async def get_status(attempts: int) -> str:
#     if attempts >= 20:
#         return None
    
#     status_response = requests.get(settings.FIREBASE_API_SECRET + "/device_responses/take_picture.json")
#     if status_response.status_code == 200:
#         status = status_response.json().get("status")
#         if status == "done":
#             print("status : Done")
#             attempts = 0
#             return status
#         else:
#             await asyncio.sleep(1)
#             attempts += 1
#             print(f'Retrying to get status. Attempt(s) : {attempts}')
#             await get_status(attempts=attempts)
            
#endregion

