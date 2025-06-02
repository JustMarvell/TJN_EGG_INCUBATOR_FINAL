import requests
import settings
import discord
import time
import asyncio

async def get_temperature() -> str:
    requests.put(settings.FIREBASE_COMMAND_PATH, json='read_temperature')
    
    for _ in range(20):
        response = requests.get(settings.FIREBASE_DHT_PATH)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "done":
                read = data.get("temperature")
                requests.put(f'{settings.FIREBASE_API_SECRET}/device_responses/dht/status.json', json="waiting")
                return read
        await asyncio.sleep(0.5)
        
    requests.put(settings.FIREBASE_COMMAND_PATH, json="idle")
    return None

async def get_humidity() -> str:
    requests.put(settings.FIREBASE_COMMAND_PATH, json='read_humidity')
    
    for _ in range(20):
        response = requests.get(settings.FIREBASE_DHT_PATH)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "done":
                read = data.get("humidity")
                requests.put(f'{settings.FIREBASE_API_SECRET}/device_responses/dht/status.json', json="waiting")
                return read
        await asyncio.sleep(0.5)
        
    requests.put(settings.FIREBASE_COMMAND_PATH, json="idle")
    return None
    
#region old
#     # send command
#     command_post = requests.put(settings.FIREBASE_API_SECRET + "/device_commands/command.json", json="read_temperature")
#     if command_post.status_code != 200:
#         print("Failed to send get_temperature command.")
#         return None
#     print("Command sent. Waiting for temperature data...")

#     time.sleep(1) 
    
#     status_response = await get_status()
    
#     if status_response == None:
#         print("Timed out waiting for the temperature. Retrying again (1)")
        
#         time.sleep(1)
#         status_response = await get_status()
#         if status_response == None:
#             print("Timed out waiting for the temperature. Retrying again (2)")
            
#             time.sleep(1)
#             status_response = await get_status()
#             if status_response == None:
#                 print("Timed out waiting for the temperature.")
#                 return None
    
#     temperature_response = requests.get(settings.FIREBASE_API_SECRET + "/sensor_data/temperature.json")
#     if temperature_response.status_code == 200:
#         temperature = temperature_response.json()
#         if temperature == None:
#             print("No temperature data found.")
#             return None
#         temp = str(temperature)
#         return temp
    
# async def get_humidity() -> str:
#     # send command
#     command_post = requests.put(settings.FIREBASE_API_SECRET + "/device_commands/command.json", json="read_humidity")
#     if command_post.status_code != 200:
#         print("Failed to send get_temperature command.")
#         return None
#     print("Command sent. Waiting for temperature data...")

#     time.sleep(1) 
    
#     status_response = await get_status()
    
#     if status_response == None:
#         print("Timed out waiting for the temperature. Retrying again (1)")
        
#         time.sleep(1)
#         status_response = await get_status()
#         if status_response == None:
#             print("Timed out waiting for the temperature. Retrying again (2)")
            
#             time.sleep(1)
#             status_response = await get_status()
#             if status_response == None:
#                 print("Timed out waiting for the temperature.")
#                 return None
    
#     humidity_response = requests.get(settings.FIREBASE_API_SECRET + "/sensor_data/humidity.json")
#     if humidity_response.status_code == 200:
#         humidity = humidity_response.json()
#         if humidity == None:
#             print("No humidity data found.")
#             return None
#         hum = str(humidity)
#         return hum
    
# async def get_status():
#     # wait for status
#     time.sleep(1)  # delay
#     status_response = requests.get(settings.FIREBASE_API_SECRET + "/sensor_data/status.json")
#     if status_response.status_code == 200:
#         status = status_response.json()
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
        