# import pprint
# from typing import Optional, Dict
# from twitchio.ext import pubsub, commands, routines
# from configuration import *
import logging
# import datetime
# import random
# import websockets
# import asyncio
# import time
# from websockets.server import serve, WebSocketServerProtocol

#Debug
logging.basicConfig(level=logging.INFO) # Set this to DEBUG for more logging, INFO for regular logging
logger = logging.getLogger("twitchio.http")

# #custom_id for channel points
# yellow_channel_point = ''
# red_chanel_point = ''
# blue_chanel_point = ''
# shield_chanel_point = ''

#class will have atributes and function we need 
class Item: 
    def __init__(self, hit_lurker, position, player, type_of_item) -> None:
        self.hit_player = hit_lurker #this is going to help me find people being attacked
        self.position = position  # Position where the item was dropped
        self.player = player  # Player who dropped the item
        self.type = type_of_item #this is telling use what item is being used

    def use(self):
        """Use the item."""
        print(f"{self.player} used {self.hit_player} at {self.position}")

    def __str__(self):
        return f"{self.hit_player} dropped by {self.player}, it was {self.type} at {self.position}"