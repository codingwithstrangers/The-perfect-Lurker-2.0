import pprint
from typing import Optional, Dict
from twitchio.ext import pubsub, commands, routines
from configuration import *
import logging
import datetime
import random
import websockets
import asyncio
from websockets.server import serve, WebSocketServerProtocol

#Debug
logging.basicConfig(level=logging.INFO) # Set this to DEBUG for more logging, INFO for regular logging
logger = logging.getLogger("twitchio.http")

#Global Variable
racer_csv = "the_strangest_racer.csv"
lurkers_points = 'lurker_points.csv' 

#custom_id for channel points
perfect_lurker_channel_id="a374b031-d275-4660-9755-9a9977e7f3ae"
talking_lurker_id="d229fa01-0b61-46e7-9c3c-a1110a7d03d4"
all_viewers ="All_Viewers.txt"

#index of event types
setting_lurker_points = 1
yellow_banana_drop =2
yellow_banana_hit= 3
yellow_banana_shield = 4
red_shell_drop = 5
red_shell_shield =6
blue_shell_drop = 7
blue_shell_shield = 8
lurker_join_race = 9
lurker_left_race = 10
shield_start = 11
shield_stop = 12


#class global variables for Lurker
status_in_race = "in_race"
status_out_race = "out_race"
status_removed_race ="left_race"
item_none = "none"
item_shield = "shield"
item_trap = "trap"

class Lurker:
    def __init__(self, user_name: str, image_url: str):
        self.image_url = image_url
        self.user_name = user_name
        self.race_status = status_out_race
        self.item = item_none
        self.points = 0
    
    def __str__(self):
        return f"username:{self.user_name} racestatus:{self.race_status} point:{self.points} raceitem:{self.item} "

    def join_race(self)-> bool:
        if self.race_status == status_out_race:
            self.race_status = status_in_race
            return True
        return False

    def leave_race(self)-> bool:
        if self.race_status == status_in_race:
            self.race_status = status_removed_race
            return True
        return False


    def add_points(self, delta: int)-> bool:
        if self.race_status != status_in_race:
            return False
        print(f"adding {delta} point(s) to {self.user_name}")   
        self.points = max(self.points +delta, 0)
        return True 

    def equip_item(self, new_item: str):
        self.item = new_item
    
    def drop_item(self):
        self.item = item_none

        
class LurkerGang:
    def __init__(self):
        self._lurkers:Dict[str, Lurker] = {}

    def __getitem__(self, key:str)-> Optional[Lurker]:
        return self._lurkers.get(key)
    
    def __iter__(self):
        return iter(self._lurkers.values())
    
    def add(self, lurker: Lurker ):
        self._lurkers[lurker.user_name] = lurker
    
    
class Bot_one(commands.Bot):
    def __init__(self):
        super().__init__(token= USER_TOKEN , prefix='!', initial_channels=['codingwithstrangers'],
            nick = "Perfect_Lurker",)
        self.message_queue = []
        self.active_connection:Optional[WebSocketServerProtocol] = None
        self.pubsub = pubsub.PubSubPool(self)
        self.lurker_gang = LurkerGang()
        
    
    async def create_or_get_lurker(self, name: str)-> Lurker:
        lower_case_name =name.lower()
        new_lurker = self.lurker_gang[lower_case_name]
        if new_lurker is None:
            user_profiles = await self.fetch_users(names=[lower_case_name])
            logger.info(user_profiles[0].profile_image)
            new_lurker =  Lurker(user_name=lower_case_name,image_url= user_profiles[0].profile_image)
            self.lurker_gang.add(new_lurker)       
            
        return new_lurker
        

    async def lurker_joins_race(self, event: pubsub.PubSubChannelPointsMessage):
        chat_lurker = await self.create_or_get_lurker(event.user.name)
        channel = self.connected_channels[0]
        
        if chat_lurker.join_race():
            await channel.send(f'@{chat_lurker.user_name}, Start Your Mother Loving Engines!! You are in the race Now!')
            self.message_queue.append(f'{lurker_join_race},{chat_lurker.user_name},{chat_lurker.image_url}')
        else:
            await channel.send(f'@{chat_lurker.user_name}, hey sorry you can only enter the race once per stream coding32Whatmybrother ') 
     
    async def event_pubsub_channel_points(self, event: pubsub.PubSubChannelPointsMessage):
        pprint.pprint(event.reward) #rerun in terminal look for id
        
        if event.reward.id == perfect_lurker_channel_id:
            await self.lurker_joins_race(event)
        if event.reward.id == talking_lurker_id:
            talking_channel_point  = await self.create_or_get_lurker(event.user.name)
            self.message_queue.append(f'{setting_lurker_points},{talking_channel_point.user_name},{talking_channel_point.points}')
            talking_channel_point.add_points(1)

    #remove points for talking 
    async def event_message(self, message):
        if message.echo:
            return
        talking_lurker = await self.create_or_get_lurker(message.author.name)
        talking_lurker.add_points(-1)
        await self.handle_commands(message)
        self.message_queue.append(f'{setting_lurker_points},{talking_lurker.user_name},{talking_lurker.points}')

    #We want toRemove users for m Strangest racer
    #when user use !remove
    @commands.command()
    async def remove(self, ctx: commands.Context):
        removed_lurker = await self.create_or_get_lurker(ctx.author.name)

        if removed_lurker.leave_race():
            await ctx.send(f'Ok Ok take yo last place havin ass on then @{removed_lurker.user_name}!')
            self.message_queue.append(f'{lurker_left_race},{removed_lurker.user_name}')
        else:
            await ctx.send(f'@{removed_lurker.user_name}! DADDY CHILL... you are not in the race') 

    #get points command
    @commands.command()
    async def points(self, ctx: commands.Context):
        if ctx.author.name != "codingwithstrangers":
            return 
        for lurker in self.lurker_gang:
            print(lurker)
        
    #Each event will have a situation that can be tested, this is how we get the websocket
    #connected
    
    async def give_point_timer(self):
        print('timer ticket toc')
        with open(all_viewers, 'r') as file:
            lines = {name.strip() for name in file}
            
            #I want to give everyone who is in lurkergang
            # a point if they are in all_viewers and
            #  they have in race status
        for lurker in self.lurker_gang: 
            if lurker.user_name in lines:
                if lurker.add_points(+1):
                    self.message_queue.append(f'{setting_lurker_points},{lurker.user_name},{lurker.points}')

        print("this is the end of the tic tok")

    async def register(self,websocket):
        self.active_connection=websocket
        try:
            await websocket.wait_closed()
        finally:
            self.active_connection= None

    async def send_messages(self):
        while True:
            if self.active_connection is  None:
                await asyncio.sleep(3)
                continue
            if len(self.message_queue)> 0:
                await self.active_connection.send("\n".join(self.message_queue))
                self.message_queue.clear()
            await asyncio.sleep(.1)

    async def pytogodot(self):
        async with serve(self.register, "localhost", 8765):
            await self.send_messages()  # run forever

   #last function
    async def run(self):
        topics = [
            pubsub.channel_points(USER_TOKEN)[int(BROADCASTER_ID)],
            # pubsub.channel_points(MOD_TOKEN)[int(MODERATOR_ID)]
        ]
        await self.pubsub.subscribe_topics(topics)
        print('this shit work? pt2')
        await self.start()
    
        
bot= Bot_one()
routines.routine(seconds=60)(bot.give_point_timer).start()
lurker_task_made = bot.loop.create_task(bot.run())
task_for_botgodot = bot.loop.create_task(bot.pytogodot())
gather_both_task = asyncio.gather(lurker_task_made,task_for_botgodot)
bot.loop.run_until_complete(gather_both_task)
#
# bot.loop.run_until_complete(bot.__ainit__())
#START UP CODE ENDS
# @client.event()
# async def event_pubsub_channel_points(event: pubsub.PubSubChannelPointsMessage):
#     #how to find the channel reqard point
#     pprint.pprint(event.reward) #rerun in terminal look for id
#     custom_reward_id="a374b031-d275-4660-9755-9a9977e7f3ae"
#     channel = client.get_channel('codingwithstrangers')
#     max_racers = 101
#         # Check if the event's reward ID matches the custom reward ID
#     if event.reward.id == custom_reward_id:
#         user_name = event.user.name
#         print(f"User '{user_name}' redeemed the custom reward.")
#     else:
#         print("Reward ID does not match the custom reward.")

     #set ditc to honor max_racer and add new racers who are true in strangest racer
    # avialable_racers = 0
    # for values in strangest_racers.values():
    #     if values['is_available']:
    #         avialable_racers+=1
    # print(strangest_racers, "wf did I do")

    # if (avialable_racers < max_racers) and (user_name not in strangest_racers.keys()):
    #     #this is how we added the image url and to the dict.
    #     user_profiles = await client.fetch_users(names=[user_name])
    #     logger.info(user_profiles[0].profile_image)
    #     strangest_racers[user_name] = {'is_available':True,'score':0, 'image_url':user_profiles[0].profile_image}     
    #     logger.info(f"Added {user_name}")
    #     await channel.send(f'@{user_name}, Start Your Mother Loving Engines!! You are in the race Now!')
    #     write_to_file()
    # #send a message from the bot
    # else:
    #     logger.info(f'@{user_name}, hey sorry you can only enter the race once per stream coding32Whatmybrother')
    #     await channel.send(f'{user_name}, hey sorry you can only enter the race once per stream coding32Whatmybrother ') 
 

# async def main():
#     topics = [
#         # pubsub.channel_points(users_oauth_token)[int(users_channel_id)],
#         pubsub.channel_points(my_token)[int(mod_channel_id)]
#     ]
#     await client.pubsub.subscribe_topics(topics)
#     await client.start()
# print('this shit work? pt2')


# client.loop.run_until_complete(main())
# #START UP CODE ENDS