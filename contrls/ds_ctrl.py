import requests
import settings
import discord
from conns import firebase as fb

async def get_distance() -> str:
    status = await fb.check_status()
    
    if status == 'NONE':
        return 'Error: Unable to fetch distance data'
    else:
        response = requests.get(settings.FIREBASE_API_SECRET + "/test_data/distance.json")
        if response.status_code == 200:
            data = response.json()
            distance = "Distance: " + str(data) + " cm"
            return distance
        else:
            return "Error: Unable to fetch distance data"