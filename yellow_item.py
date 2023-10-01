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
from lurker_item import *
# from websockets.server import serve, WebSocketServerProtocol

#Debug
logging.basicConfig(level=logging.INFO) # Set this to DEBUG for more logging, INFO for regular logging
logger = logging.getLogger("twitchio.http")


class Yellowitem(Item):
    def __init__(self, position, player):
        super().__init__('', position, player, 'yellow_item')

    def use(self):
        print(f"{self.player} used yellow item, at {self.position}")
        lurker_message = (f'@{self.player}, just set a TRAP!!')
        godot_message = (f'{self.player}')
        return lurker_message, godot_message
    
    def damage(self, hit_player):
        #if its me
        if self.player == hit_player:
            return -2
        #if it hits another player
        return -1

