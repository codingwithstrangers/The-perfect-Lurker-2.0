import os
import json
from dotenv import load_dotenv
load_dotenv()
USER_TOKEN=os.environ['USER_TOKEN']
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET= os.environ['CLIENT_SECRET']
REFRESH_TOKEN = os.environ['REFRESH_TOKEN']
MOD_TOKEN = os.environ['MOD_TOKEN']
CALLBACK = os.environ['CALLBACK']
CHANNEL_NAME = json.loads(os.environ['CHANNEL_NAME'])
BROADCASTER_ID = os.environ['BROADCASTER_ID']
MODERATOR_ID = os.environ['MODERATOR_ID']
WEBHOOK_SECRET = os.environ['WEBHOOK_SECRET']
ESCLIENT_PORT = os.environ['ESCLIENT_PORT']
USER_AUTH_TOKEN = os.environ['USER_OAUTH_TOKEN']
TOKEN = ""