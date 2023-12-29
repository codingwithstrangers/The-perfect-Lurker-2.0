from twitchio.ext import commands
import asyncio




import requests
# import configuration
from  configuration import *

# Set the URL for the token request
TOKEN_URL = "https://id.twitch.tv/oauth2/token"

# Set the request headers
def refresh_access_token(client_id, client_secret, refresh_token):

    # headers = None
    body={
        "client_id":  CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        'grant_type':'refresh_token',
        "refresh_token":REFRESH_TOKEN,
        }

    # Make the request to generate a new access token
    response = requests.post(TOKEN_URL, headers=None, data=body)

    # If the request is successful
    if response.status_code == 200:
        # Extract the new access token
        print("Access token obtained successfully!")
        access_token = response.json()['access_token']
        print(response, access_token)
        return access_token
    
    else:
        print("Error obtaining access token")
        print("Response status code:", response.status_code)
        print("Response text:", response.text)
        return None



# Replace these with your actual Twitch app credentials and refresh token
# CLIENT_ID = 'YOUR_CLIENT_ID'
# CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
# REFRESH_TOKEN = 'YOUR_REFRESH_TOKEN'

# bot = commands.Bot(
#     # Set up bot credentials
#     client_id=CLIENT_ID,
#     client_secret=CLIENT_SECRET,
#     token=REFRESH_TOKEN
# )

# @bot.event
# async def event_ready():
#     print(f"Logged in as {bot.nick}")

# # Refresh token every hour
# async def refresh_token():
#     while True:
#         await asyncio.sleep(3600)  # Sleep for 1 hour
#         await bot._ws._oauth.refresh()  # Refresh the token

# # Start the bot and token refreshing loop
# bot.loop.create_task(refresh_token())
# bot.run()