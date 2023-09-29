import pprint
from typing import Callable, List, Optional, Dict, Set, Tuple
from twitchio.ext import pubsub, commands, routines
from configuration import *
import logging
import asyncio
from websockets.server import serve, WebSocketServerProtocol


#Debug
logging.basicConfig(level=logging.INFO) # Set this to DEBUG for more logging, INFO for regular logging
logger = logging.getLogger("twitchio.http")


#custom_id for channel points
perfect_lurker_channel_id="a374b031-d275-4660-9755-9a9977e7f3ae"
talking_lurker_id="d229fa01-0b61-46e7-9c3c-a1110a7d03d4"
yellow_channel_point = ''
red_chanel_point = ''
blue_chanel_point = ''
shield_chanel_point = ''

all_viewers ="All_Viewers.txt"


#type of attacks
yellow_attack = "banana"
red_attack = "red_shell"
blue_attack = "blue_shell"

#index of event types
setting_lurker_points = 1
yellow_banana_drop = 2
yellow_banana_hit = 3
yellow_banana_shield = 4
red_shell_drop = 5
red_shell_shield = 6
blue_shell_drop = 7
blue_shell_shield = 8
lurker_join_race = 9
lurker_left_race = 10
shield_on = 11
shield_off = 12


#class global variables for Lurker
status_in_race = "in_race"
status_out_race = "out_race"
status_removed_race ="left_race"

#this isnt the gather this is the player (object oriented design)
class Lurker:
    def __init__(self, user_name: str, image_url: str):
        self.image_url = image_url
        self.user_name = user_name
        self.race_status = status_out_race
        self.shield_points = 0
        self.points = 0
    
    def __str__(self):
        return f"username:{self.user_name} racestatus:{self.race_status} points:{self.points} shield:{self.shield_points}"

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

    #gets point and sets points
    def add_points(self, delta: int)-> bool:
        if self.race_status != status_in_race:
            return False

        new_points = max(self.points+delta, 0)
        if new_points == self.points:
            return False

        print(f"adding {delta} point(s) to {self.user_name}")   
        self.points = new_points
        return True 

    @property
    def position(self) -> int:
        return self.points % 60

    def set_shield(self, value: int):
        self.shield_points = value


class LurkerGang:   
    def __init__(self):
        self._lurkers:Dict[str, Lurker] = {}
        self.yellow_items:Dict[int, Lurker] = {}
        self.find_red_item = {}
        self.find_blue_item = {}

    def __getitem__(self, key:str)-> Optional[Lurker]:
        return self._lurkers.get(key)
    
    def __iter__(self):
        return iter(self._lurkers.values())
    
    def add(self, lurker: Lurker ):
        self._lurkers[lurker.user_name] = lurker
        
    # def hit_shield(self, user_name: str):
        # if user_name in self.lurkers_with_shield:
            # self.lurkers_with_shield[user_name]['hit_point'] -=1
            # if self.lurkers_with_shield[user_name]['hit_point'] <=0:
                # del self.lurkers_with_shield[user_name]
        # return True
    
    def drop_yellow_item(self, lurker: Lurker):
        # drop our banana behind us, like normal
        self.yellow_items[(lurker.points+59)%60] = lurker

    def find_hit_lurkers(self) -> Tuple[List[int], List[Lurker]]:
        hit_items:Set[int] = set()
        hit_lurkers:List[Lurker] = []

        for lurker in self._lurkers.values():
            if lurker.position in self.yellow_items:
                hit_items.add(lurker.position)
                hit_lurkers.append(lurker)

        for hit_item in hit_items:
            del self.yellow_items[hit_item]

        return (list(hit_items), hit_lurkers)
        
    # def use_reditem(self, user_name: str, event_id: str):
        # item_position = self._lurkers[user_name].points%60.0
        # if event_id == red_chanel_point:
            # self.find_red_item[item_position] = (red_attack, user_name)
            # if user_name in self.lurker_position:
                # red_attacking_lurker_position = self.lurker_position[user_name][1]
                # red_lurker_name=self.lurker_position[user_name]
                # if red_attacking_lurker_position > 1:
                    # lurker_infront = list(self.lurker_position.values())[red_attacking_lurker_position-2]
                    # return red_lurker_name, lurker_infront, item_position, None
                # else:
                    # nodody_is_infront= self.lurker_position[user_name], None
                    # return nodody_is_infront
            # else:
                # return
            
    # def use_blueitem(self, user_name: str, event_id: str):
        # item_position = self._lurkers[user_name].points%60.0
        # if event_id == blue_chanel_point:
            # self.find_blue_item[item_position] = (blue_attack, user_name)
            # if user_name in self.lurker_position:
                # blue_attacking_lurker_position = self.lurker_position[user_name][1]
                # if blue_attacking_lurker_position > 1:
                    # lurkers_in_front = list(self.lurker_position.values())[:blue_attacking_lurker_position - 1]
                    # num_users_to_select = max(1, int(0.3 * len(lurkers_in_front))) 
                    # # Always include the person in front
                    # first_lurker = [lurkers_in_front[0][0]]
# 
                    # # Randomly select additional users
                    # random_lurkers = random.sample([lurker[0] for lurker in lurkers_in_front[1:]], num_users_to_select - 1)
# 
                    # # Shuffle the list of random lurkers
                    # random.shuffle(random_lurkers)
# 
                    # # Combine all lurkers into a single list
                    # all_lurkers = first_lurker + random_lurkers
# 
                    # lurker_message = (f'@{user_name}, is Bringing the Pain to {", ".join(all_lurkers)}')
                    # godot_message = (f'{user_name}')
# 
                    # return lurker_message, godot_message, first_lurker, random_lurkers,all_lurkers, item_position, None
                # else:
                    # nodody_is_infront= self.lurker_position[user_name], None
                    # return nodody_is_infront
            # else:
                # return None

    
    #this is running to watch all attacks on pllayer this is designed to listen
    # def run_lap (self):
        # for item in self.find_item:
            # for lurker in self._lurkers.values():
                # if lurker.points%60.0 == item[lurker.points%60.0]:
                    
                    # print('did I ever tell you were my heero')          
                # return lurker


#race management 
class Bot_one(commands.Bot):
    def __init__(self):
        super().__init__(token= USER_TOKEN , prefix='!', initial_channels=['codingwithstrangers'],
            nick = "Perfect_Lurker",)
        self.message_queue = []
        self.active_connection:Optional[WebSocketServerProtocol] = None
        self.pubsub = pubsub.PubSubPool(self)
        self.lurker_gang = LurkerGang()
        self.channel_point_handlers:Dict[str,Callable] = {
            perfect_lurker_channel_id: self.lurker_joins_race,
            talking_lurker_id: self.lurker_safe_chat,
            yellow_channel_point: self.drop_yellow_item,
        }

    async def event_pubsub_channel_points(self, event: pubsub.PubSubChannelPointsMessage):
        if event.user.name is None:
            return

        pprint.pprint(event.reward) #rerun in terminal look for id
        if event.reward.id in self.channel_point_handlers:
            await self.channel_point_handlers[event.reward.id](event)

    async def create_or_get_lurker(self, name: str) -> Lurker:
        lower_case_name = name.lower()
        new_lurker = self.lurker_gang[lower_case_name]
        if new_lurker is None:
            user_profiles = await self.fetch_users(names=[lower_case_name])
            logger.info(user_profiles[0].profile_image)
            new_lurker = Lurker(user_name=lower_case_name, image_url=user_profiles[0].profile_image)
            self.lurker_gang.add(new_lurker)
            
        return new_lurker
        
    #message for joining race
    async def lurker_joins_race(self, event: pubsub.PubSubChannelPointsMessage):
        if event.user.name is None:
            return

        chat_lurker = await self.create_or_get_lurker(event.user.name)
        channel = self.connected_channels[0]
        
        if chat_lurker.join_race():
            await channel.send(f'@{chat_lurker.user_name}, Start Your Mother Loving Engines!! You are in the race Now!')
            self.message_queue.append(f'{lurker_join_race},{chat_lurker.user_name},{chat_lurker.image_url}')
        else:
            await channel.send(f'@{chat_lurker.user_name}, hey sorry you can only enter the race once per stream coding32Whatmybrother ') 

    async def lurker_safe_chat(self, event: pubsub.PubSubChannelPointsMessage):
        if event.user.name is None:
            return

        talking_channel_point = await self.create_or_get_lurker(event.user.name)
        self.message_queue.append(f'{setting_lurker_points},{talking_channel_point.user_name},{talking_channel_point.points}')
        talking_channel_point.add_points(1)

    async def drop_yellow_item(self, event: pubsub.PubSubChannelPointsMessage):
        if event.user.name is None:
            return

        chat_lurker = await self.create_or_get_lurker(event.user.name)
        self.lurker_gang.drop_yellow_item(chat_lurker)

        channel = self.connected_channels[0]
        await channel.send(f'@{event.user.name}, dropped a yellow item')
        self.message_queue.append(f'{yellow_banana_drop},{event.user.name}')

    async def check_yellow_items(self):
        channel = self.connected_channels[0]

        check = self.lurker_gang.find_hit_lurkers()
        for hit_item in check[0]:
            self.message_queue.append(f'{yellow_banana_hit},{hit_item}')

        for hit_lurker in check[1]:
            hit_lurker.add_points(-2)
            self.message_queue.append(f'{setting_lurker_points},{hit_lurker.user_name},{hit_lurker.points}')
            await channel.send(f'@{hit_lurker.user_name} got hit my a banana!')

        # hurt_player = self.lurker_gang.run_lap()
        # if hurt_player != None:
            # hurt_lurker = hurt_player.user_name
            # yellow_attacking_lurker = self.lurker_gang.use_yellowitem()[2]
            # channel = self.connected_channels[0]
            # if hurt_player.user_name in self.lurker_gang.lurkers_with_shield:
                # self.lurker_gang.hit_shield(hurt_lurker)
                # if self.lurker_gang.hit_shield(hurt_lurker)[2] is 0:
                    # hurt_player == self.lurker_gang.use_yellowitem(yellow_attack)
                    # hurt_player.add_points(-1)
                    # await channel.send(f'@{yellow_attacking_lurker}! Just caught {hurt_player} Lacking!')
                    # self.message_queue.append(f'{setting_lurker_points},{hurt_player.user_name},{hurt_player.points}')
                    # #shield check
                    
                    # return hurt_lurker

                # else:
                    # hurt_player = self.lurker_gang.run_lap()
                    # if hurt_player == self.lurker_gang.run_lap():
                        # hurt_player.add_points(-2)
                        # await channel.send(f'@{yellow_attacking_lurker}! You just Ran into Your own Trap? Tragic!')
                        # self.message_queue.append(f'{setting_lurker_points},{hurt_player.user_name},{hurt_player.points}')
                        # if hurt_player.user_name in self.lurker_gang.lurkers_with_shield:
                            # self.lurker_gang.hit_shield(hurt_lurker)[2]
                            # await channel.send(f'@{yellow_attacking_lurker}! You just Ran into Your own Trap? Tragic!')
                            # self.message_queue.append(f'{setting_lurker_points},{hurt_player.user_name},{hurt_player.points}')
                            
        
    # async def damage_from_red_item(self):
        # hurt_player = self.lurker_gang.run_lap()
        # sleep_duration = random.randint(3, 10)
        # if hurt_player != None:
            # hurt_lurker = hurt_player.user_name
            # red_attacking_lurker = self.lurker_gang.use_reditem()[2]
            # channel = self.connected_channels[0]
            # if hurt_player == self.lurker_gang.use_reditem(red_attack):
                # if hurt_player == self.lurker_gang.use_reditem(red_attacking_lurker):
                    # hurt_player.add_points(-4)
                    # await channel.send(f'@{red_attacking_lurker}! STOP HITTING YOURSELF!!!')
                    # self.message_queue.append(f'{setting_lurker_points},{hurt_player.user_name},{hurt_player.points}')
                    # return hurt_lurker
                    
            # else:
                # if hurt_player != self.lurker_gang.use_reditem(red_attacking_lurker):
                    # await channel.send(f'@{red_attacking_lurker}! Is Locked-on {hurt_player} Quick SHEILD UP!')
                    # time.sleep(sleep_duration)
                    # #CHECK IF THE USER HAS A SHIELD
                    # hurt_player.add_points(-2)
                    # self.message_queue.append(f'{setting_lurker_points},{hurt_player.user_name},{hurt_player.points}')
    

    # async def damage_from_blue_item(self):
        # hurt_player = self.lurker_gang.run_lap()
        # sleep_duration = random.randint(3, 10)
        # if hurt_player != None:
            # hurt_lurker = hurt_player.user_name
            # blue_attacking_lurker = self.lurker_gang.use_reditem()[2]
            # channel = self.connected_channels[0]
            # if hurt_player == self.lurker_gang.use_reditem(blue_attack):
                # if hurt_player == self.lurker_gang.use_reditem(blue_attacking_lurker):
                    # hurt_player.add_points(-4)
                    # await channel.send(f'@{blue_attacking_lurker}! STOP HITTING YOURSELF!!!')
                    # self.message_queue.append(f'{setting_lurker_points},{hurt_player.user_name},{hurt_player.points}')
                    # return hurt_lurker
                    
            # else:
                # if hurt_player != self.lurker_gang.use_reditem(blue_attacking_lurker):
                    # await channel.send(f'@{blue_attacking_lurker}! Is Locked-on {self.lurker_gang.use_blueitem()[2]} Quick SHEILD UP!')
                    # time.sleep(sleep_duration)
                    # #CHECK IF THE USER HAS A SHIELD
                    # hurt_player.add_points(-2)
                    # self.message_queue.append(f'{setting_lurker_points},{hurt_player.user_name},{hurt_player.points}')

    #remove points for talking 
    async def event_message(self, message):
        if message.echo or message.author is None or message.author.name is None:
            return

        talking_lurker = await self.create_or_get_lurker(message.author.name)
        talking_lurker.add_points(-1)
        await self.handle_commands(message)
        self.message_queue.append(f'{setting_lurker_points},{talking_lurker.user_name},{talking_lurker.points}')
        await self.check_yellow_items()

    @commands.command()
    async def remove(self, ctx: commands.Context):
        if ctx.author is None or ctx.author.name is None:
            return

        removed_lurker = await self.create_or_get_lurker(ctx.author.name)
        if removed_lurker.leave_race():
            await ctx.send(f'Ok Ok take yo last place havin ass on then @{removed_lurker.user_name}!')
            self.message_queue.append(f'{lurker_left_race},{removed_lurker.user_name}')
        else:
            await ctx.send(f'@{removed_lurker.user_name}! DADDY CHILL... you are not in the race') 

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

        await self.check_yellow_items()

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
        ]
        await self.pubsub.subscribe_topics(topics)
        await self.start()
    
        
bot = Bot_one()
routines.routine(seconds=60)(bot.give_point_timer).start()
lurker_task_made = bot.loop.create_task(bot.run())
task_for_botgodot = bot.loop.create_task(bot.pytogodot())
gather_both_task = asyncio.gather(lurker_task_made,task_for_botgodot)
bot.loop.run_until_complete(gather_both_task)
