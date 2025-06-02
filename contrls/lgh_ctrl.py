import requests
import settings
import discord
import time
import asyncio

async def toggle_light(cmd : str):
    if cmd == "status":
        response = requests.get(settings.FIREBASE_LAMP_PATH)
        if response.status_code == 200:
            data = response.json().get("state")
            return data
    else:
        requests.put(settings.FIREBASE_COMMAND_PATH, json=f"lamp_{cmd}")
        
        print(f"Put the command lamp_{cmd} at path : {settings.FIREBASE_COMMAND_PATH}\n")
        print(f"Getting response from path : {settings.FIREBASE_LAMP_PATH}")
        for _ in range(20):
            response = requests.get(settings.FIREBASE_LAMP_PATH)
            if response.status_code == 200:
                print("-")
                data = response.json()
                if data.get("status") == "done":
                    state = data.get("state")
                    print(f"State = {state}")
                    requests.put(f"{settings.FIREBASE_API_SECRET}/device_responses/lamp/status.json", json="waiting")
                    return state
            print(".")
            await asyncio.sleep(0.5)
        
        requests.put(settings.FIREBASE_COMMAND_PATH, json="idle")
        return None
                    
        
        # for _ in range(20):
        #     response = requests.get(settings.FIREBASE_LAMP_PATH)
        #     if response.status_code == 200:
        #         status = response.json().get("status")
        #         if status == "done":
        #             state = response.json().get("state")
        #             requests.put(f"{settings.FIREBASE_API_SECRET}/device_responses/status.json", json="waiting")
        #             return state
        # requests.put(settings.FIREBASE_COMMAND_PATH, json="idle")
        # return None

#region old
#     # send command
#     if cmd != "status":
#         if cmd == "on":
#             c = "lamp_on"
#         else:
#             c = "lamp_off"
#         command_post = requests.put(settings.FIREBASE_API_SECRET + "/device_commands/command.json", json=c)
#         if command_post.status_code != 200:
#             print("Failed to send get_temperature command.")
#             return None
#         print("Command sent. Waiting for temperature data...")

#         time.sleep(1)
        
#         # wait for status
#         status_response = await get_status()
#         if status_response == None:
#             print("Timed out waiting for the temperature. Retrying again (1)")
            
#             time.sleep(1)
#             status_response = await get_status()
#             if status_response == None:
#                 print("Timed out waiting for the temperature. Retrying again (2)")
                
#                 time.sleep(1)
#                 status_response = await get_status()
#                 if status_response == None:
#                     print("Timed out waiting for the temperature.")
#                     return None
    
#     if cmd == "on":
#         # send request to turn on the light
#         response = requests.get(settings.FIREBASE_API_SECRET + "/sensor_data/lamp.json")
#         if response.status_code == 200:
#             data = response.json()
#             if data == False:
#                 # change the value to True to indicate the light is on
#                 request = requests.put(settings.FIREBASE_API_SECRET + "/sensor_data/lamp.json", json=True)
#                 if request.status_code != 200:
#                     return None
#                 return "ON"
#             else:
#                 # The light is already on
#                 return "ON"
#         else:
#             return None
#     elif cmd == "off":
#         # send request to turn off the light
#         response = requests.get(settings.FIREBASE_API_SECRET + "/sensor_data/lamp.json")
#         if response.status_code == 200:
#             data = response.json()
#             if data == True:
#                 request = requests.put(settings.FIREBASE_API_SECRET + "/sensor_data/lamp.json", json=False)
#                 if request.status_code != 200:
#                     return None
#                 return "OFF"
#             else:
#                 # The light is already off
#                 return "OFF"
#         else:
#             return None
#     elif cmd == "status":
#         # send request to get the status of the light
#         response = requests.get(settings.FIREBASE_API_SECRET + "/sensor_data/lamp.json")
#         if response.status_code == 200:
#             data = response.json()
#             status = "ON" if data else "OFF"
#             return status
#         else:
#             return None

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