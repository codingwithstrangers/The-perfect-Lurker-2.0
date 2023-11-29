import pprint
import functools
from collections.abc import Iterator, Awaitable
from typing import Callable, List, Optional, Dict, Tuple,TypeVar
import inspect
from twitchio.ext import pubsub, commands, routines
import twitchio
from configuration import *
import logging
import asyncio
from websockets.server import serve, WebSocketServerProtocol


#info
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger("twitchio.http")
logger.setLevel(logging.WARN)

log = logging.getLogger('event_stream')
log.setLevel(logging.INFO)

#custom_id for channel points
perfect_lurker_channel_id="a374b031-d275-4660-9755-9a9977e7f3ae"
talking_lurker_id="d229fa01-0b61-46e7-9c3c-a1110a7d03d4"
yellow_channel_point = 'bb5f96f3-714d-4b09-9203-9b698a97aa7f'
red_chanel_point = ''
blue_chanel_point = ''
shield_chanel_point = ''

all_viewers ="All_Viewers.txt"

status_in_race = "in_race"
"Lurker state indicating we are actively in the race"
status_out_race = "out_race"
"Lurker state indicating we are not yet in the race"
status_removed_race = "left_race"
"Lurker state indicating we have left the race, and can not re-enter"


#Class for Stream producer and consumers
class Event:
    """
    Base class of any event, completely empty.
    """

    def __repr__(self) -> str:
        return str(self.__dict__)
    
_E = TypeVar("_E", bound=Event)
TypedConsumerDelegate = Tuple[_E, Callable[[_E], Awaitable[None]]]
"""
Kinda magic type of storing a list of consumers based on what subclassed event
they are listening for.
"""
    
class EventStream:
    """
    EventStream allows producers of events to add events, and for consumers of the events
    to read events and handle them.
    Any number of consumers can be added and events will be sent to all of them.
    For producers, anything that should produce events for the game should send an event.
    """

    def __init__(self):
        """
        Create a new event stream that stores our consumers and will route events to them.
        """

        self._consumers: List[TypedConsumerDelegate[Event]] = []

    def add_consumer(self, consumer: Callable[[_E], Awaitable[None]]):
        """
        Register a consumer delegate to listen for events as they come in.
        Consumers must be async handlers.
        You are able to listen for the exact event type by using the type annotation
        for the subclassed event.
        ```python
        def handle_only_join_events(ev: JoinedRaceEvent):
            print(ev.user_name, "joined the race")
        ```
        """

        # Do some fancy work to grab our event type from the callable signature
        # this is probably a little slow but only happens once on startup.
        sig = inspect.signature(consumer)
        param = list(sig.parameters.values())[0]

        log.info("adding consumer: %s", sig)
        self._consumers.append((param.annotation, consumer))  # type: ignore

    async def send(self, ev: Event):
        """
        Send a new event to all our consumers.
        """
        log.info("sending event %s %s", ev.__class__.__name__, ev)


        for con in self._consumers:
            if isinstance(ev, con[0]):  # type: ignore
                await con[1](ev)

event_separator = ","
"how our event code and values are separated in our websocket packets"



class Lurker:
    """
    Lurker manages all the data and state for our lurkers in the race.
    It changes when our lurker functionality is expanded.
    """

    def __init__(self, user_name: str, image_url: str):
        """
        Create a new lurker with a name and profile image.
        """

        self.image_url = image_url
        "URL of our lurkers profile image that we use on our field"

        self.user_name = user_name
        "Twitch user name of our lurker"

        self.race_status = status_out_race
        "Current race status of our lurker"

        self.points = 0
        "How many points we have"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Lurker):
            return False
        return self.user_name == other.user_name

    def __repr__(self):
        return f"name:{self.user_name} race:{self.race_status} points:{self.points}"

    async def join_race(self, event_stream: EventStream):
        """
        Adds our lurker to the race.
        Lurkers must not already be in the race, and must not have left the race before.
        Events Emitted:
        1. `.events.ChatMessageEvent` when lurker already in the race
        1. `.events.ChatMessageEvent` when lurker already left the race
        1. `.events.JoinedRaceEvent` if we successfully joined
        1. `.events.ChatMessageEvent` when lurker joined
        """

        if self.race_status == status_in_race:
            log.info(
                "lurker %s tried to join the race but is already in it", self.user_name
            )
            await event_stream.send(
                ChatMessageEvent(f"@{self.user_name} you are already in the race")
            )
            return

        if self.race_status == status_removed_race:
            log.info(
                "lurker %s tried to join the race but already left", self.user_name
            )
            await event_stream.send(
                ChatMessageEvent(f"@{self.user_name} you already left the race")
            )
            return

        log.info("lurker %s joined the race", self.user_name)
        self.race_status = status_in_race
        await event_stream.send(JoinedRaceEvent(self))
        await event_stream.send(
            ChatMessageEvent(f" @{self.user_name} Start Your Mother Loving Engines!! You are in the race Now!")
        )

    async def leave_race(self, event_stream: EventStream):
        """
        Moves our lurker out of the race.
        Lurker must be in the race in order to leave.
        Events Emitted:
        1. `.events.ChatMessageEvent` when lurker is not in race
        1. `.events.LeftRaceEvent` if we successfully left
        1. `.events.ChatMessageEvent` when lurker is removed
        """

        if self.race_status != status_in_race:
            log.info("lurker %s tried to leave the race", self.user_name)
            await event_stream.send(
                ChatMessageEvent(f"@{self.user_name} DADDY CHILL You not even in the Race")
            )
            return

        log.info("lurker %s left the race", self.user_name)
        self.race_status = status_removed_race
        await event_stream.send(LeftRaceEvent(self))
        await event_stream.send(
            ChatMessageEvent(f"@{self.user_name} It's Soooo Hard to say GOODBYE!!!!")
        )

    async def add_points(self, event_stream: EventStream, delta: int):
        """
        Add or remove points from our lurker.
        To remove points pass a negative value for delta.
        Events Emitted:
        1. `.events.SetPointsEvent` with our updated points value
        """

        if self.race_status != status_in_race:
            log.debug(
                "%s tried to get %d points without being in the race",
                self.user_name,
                delta,
            )
            return

        new_points = max(self.points + delta, 0)
        if new_points == self.points:
            log.debug(
                "%s tried to get %d points but there was no change",
                self.user_name,
                delta,
            )
            return

        self.points = new_points
        await event_stream.send(SetPointsEvent(self, new_points))

    @property
    def position(self) -> int:
        """
        What position we are on in the minimap accounting for laps around.
        """

        return self.points % 60

    @property
    def in_race(self) -> bool:
        """
        Whether or not our lurker is currently in the race.
        """

        return self.race_status == status_in_race

    # def set_shield(self, value: int):
    # self.shield_points = value

    # Take some damage, if we have a shield, that will be used first.
    # Returns whether or not we took any damage.
    # def take_damage(self, value: int) -> bool:
    # if self.shield_points >= value:
    # self.shield_points -= value
    # return False
    # self.shield_points = 0
    # return True


class LurkerEvent(Event):
    """
    Base class of any event that simply indicates the lurker did, or attempted to do something.
    We source the event by the lurkers name as it may or may not be a valid lurker yet.
    """

    def __init__(self, user_name: str):
        self.user_name = user_name
        """ Username of the lurker who caused the event """

    def __eq__(self, other: object):
        return (
            self.__class__.__name__ != other.__class__.__name__
            and isinstance(other, LurkerEvent)
            and self.user_name == other.user_name
        )

class JoinRaceAttemptedEvent(LurkerEvent):
    """
    Event used when a chatter attempts to join the race
    """

class TalkingLurkerEvent(LurkerEvent):
    ''''
    Ayo  (lol) this is the event used to send an event of 
    a talking lurker
    '''

class TalkingChannelPointEvent(LurkerEvent):
    '''This is the event to sent a notice of a lurker talking_lurker_id
    butt they are using a channel point'''


class LeaveRaceAttemptedEvent(LurkerEvent):
    """
    Event used when a chatter attempts to leave the race
    """

class LurkerGang:
    """
    Track our lurkers in a single collection.
    You can loop over all lurkers using a for loop.
    ```python
    gang = LurkerGang()
    gang.add(Lurker("a", "a profile"))
    for lurker in gang:
        print(lurker.user_name)
    ```
    You can query for a single lurker using the user name.
    ```python
    gang = LurkerGang()
    gang.add(Lurker("a", "a profile"))
    from_gang = gang["a"]
    ```
    """

    def __init__(self, event_stream: EventStream):
        """
        Create a new empy lurker gang.
        We also need to register ourself as a consumer of events.
        """

        self._lurkers: Dict[str, Lurker] = {}
        self._event_stream = event_stream
        event_stream.add_consumer(self._on_join_attempt)
        event_stream.add_consumer(self._on_leave_attempt)
        event_stream.add_consumer(self._on_talking_lurker)
        # event_stream.add_consumer(self._on_talking_channel_point)

    def __getitem__(self, key: str) -> Optional[Lurker]:
        return self._lurkers.get(key.lower())

    def __iter__(self) -> Iterator[Lurker]:
        return self._lurkers.values().__iter__()

    def add(self, lurker: Lurker):
        """
        Add a lurker to our gang.
        """

        log.info("adding %s to lurker gang", lurker.user_name)
        self._lurkers[lurker.user_name.lower()] = lurker


    async def _on_join_attempt(self, ev: JoinRaceAttemptedEvent):
        lurk = self[ev.user_name]
        if not lurk:
            return
        await lurk.join_race(self._event_stream)

    async def _on_talking_lurker(self, ev: TalkingLurkerEvent):
        
        lurk = self[ev.user_name]
        if not lurk:
            return
        await lurk.add_points(self._event_stream,-1)

    async def _on_leave_attempt(self, ev: LeaveRaceAttemptedEvent):
        lurk = self[ev.user_name]
        if not lurk:
            return
        await lurk.leave_race(self._event_stream)

    # async def _on_talking_channel_point(self, ev: TalkingChannelPointEvent):
    #     lurk = self[ev.user_name]
    #     if not lurk:
    #         return 
    #     await lurk.add_points(self._event_stream, 1)

    #the test for TDD we want this match up with the left with the least amount of code
    def lurkers_in_front_of(self, attacking_lurker: Lurker) -> List[Lurker]:
        # next_lurkers = ['this hint come next on dbz try and make right side give me the left side also dont change left side ']
        # next_lurker = [Lurker]
        # hit_lurker = [Lurker]
        for other in self:
            #this is how the guard claus works to 
            # make it false to push it to contiue 
            if other.points <= attacking_lurker.points:
                continue
            if not next_lurker or other.points < next_lurker.points:
                next_lurker = hit_lurker
        return [] if next_lurker else [attacking_lurker]

class SocketEvent(Event):
    """
    Base class of any socket event that occurs in our system.
    Socket events are ones where we expect to send this value over a websocket
    to any downstream listener.
    """

    def __init__(self, code: int, values: List[str]):
        """
        Create a new event with a code and some values.
        In most cases you would likely be creating an event using an inherited class.
        """

        self.code = code
        "A unique numbered code for each event for indexing."
        self.values = values
        "Any extra values for each event such as lurker name, unique per event."

    def __eq__(self, other: object) -> bool:
        return isinstance(other, SocketEvent) and self.packet() == other.packet()

    def packet(self) -> str:
        """
        Stringified representation of our event data that will be sent as a web socket packet.
        """
        return event_separator.join([str(self.code), *self.values])


class ChatMessageEvent(Event):
    """
    Event used to send a message to twitch chat.
    """

    def __init__(self, message: str):
        self.message = message
        "Message we want to send to our chat."

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ChatMessageEvent) and self.message == other.message


class JoinedRaceEvent(SocketEvent):
    """
    Event for when a lurker joins the race.
    """

    def __init__(self, lurker: "Lurker"):
        super().__init__(1, [lurker.user_name])
        self.lurker = lurker
        "Lurker who joined the race"


class LeftRaceEvent(SocketEvent):
    """
    Event for when a lurker leaves the race.
    """

    def __init__(self, lurker: "Lurker"):
        super().__init__(2, [lurker.user_name])
        self.lurker = lurker
        "Lurker who joined the race"


class SetPointsEvent(SocketEvent):
    """
    Event used to update the points of a lurker.
    """

    def __init__(self, lurker: "Lurker", points: int):
        super().__init__(3, [lurker.user_name, str(points)])
        self.lurker = lurker
        "Lurker who joined the race"
        self.points = points
        "Current points of our lurker"


class DropBananaEvent(SocketEvent):
    def __init__(self, lurker: "Lurker"):
        one_position_back = (lurker.position + 59) % 60
        super().__init__(4, [lurker.user_name, str(one_position_back)])
        self.lurker = lurker
        "Lurker who joined the race"
        self.position = one_position_back
        "Where the banana was dropped on the field"


class HitBananaEvent(SocketEvent):
    def __init__(self, position: int, hit_lurker: "Lurker", attack_lurker: "Lurker"):
        super().__init__(
            5, [str(position), hit_lurker.user_name, attack_lurker.user_name]
        )
        self.hit_lurker = hit_lurker
        "Lurker who got hit by the banana"
        self.attack_lurker = attack_lurker
        "Lurker who dropped the banana, may by the same as hit_lurker"
        self.position = position
        "Where the banana was dropped on the field"
 
# class ChannelPointForTalkingLurkers(SocketEvent):
#     def __init__(self, ]):
#         super().__init__(code, values)\

# The field
class Field:
    """
    Field manages any race wide events such as items dropped.
    """

    def __init__(self, lurker_gang: LurkerGang, event_stream: EventStream):
        """
        Create a new field.
        """

        self._lurker_gang = lurker_gang
        event_stream.add_consumer(self._on_set_points)
        event_stream.add_consumer(self._on_drop_banana)
        self._event_stream = event_stream

        # we may want to create a base Item class, but for now just bananas is fine.
        self._bananas: Dict[int, List[Lurker]] = {}

    async def _on_set_points(self, ev: SetPointsEvent):
        """
        When a lurker has there points updated, they may have hit a banana
        Events Emitted:
        1. `.events.SetPointsEvent` when a banana is hit and a lurker loses points
        1. `.events.ChatMessageEvent` when a banana is hit
        1. `.events.HitBananaEvent` for who hit the banana
        """

        if ev.lurker.position in self._bananas:
            attacking_lurker = self._bananas[ev.lurker.position].pop(0)
            # if we have no more bananas here then we can delete it
            if not self._bananas[ev.lurker.position]:
                del self._bananas[ev.lurker.position]
                
            if ev.lurker == attacking_lurker:
                log.info("lurker %s hit there own banana", ev.lurker.user_name)
                await ev.lurker.add_points(self._event_stream, -2)
                await self._event_stream.send(
                    HitBananaEvent(ev.lurker.position, ev.lurker, ev.lurker)
                )
                await self._event_stream.send(
                    ChatMessageEvent(
                        f"@{ev.lurker.user_name} What are you doing hitting your own trap "
                    )
                )
            else:
                log.info(
                    "lurker %s hit %s's banana",
                    ev.lurker.user_name,
                    attacking_lurker.user_name,
                )
                await ev.lurker.add_points(self._event_stream, -1)
                await self._event_stream.send(
                    HitBananaEvent(ev.lurker.position, ev.lurker, attacking_lurker)
                )
                await self._event_stream.send(
                    ChatMessageEvent(
                        f"@{ev.lurker.user_name} hit the banana set by @{attacking_lurker.user_name}"
                    )
                )

            



    async def _on_drop_banana(self, ev: DropBananaEvent):
        """
        When a banana is dropped, check to see if any lurker is immediately hit by it
        and if not, save it for later.
        Bananas can stack on at the same position if two lurkers drop them from the same point.
        Events Emitted:
        1. `.events.SetPointsEvent` when a banana is hit immediately and a lurker loses points
        1. `.events.ChatMessageEvent` when a banana is hit immediately
        1. `.events.HitBananaEvent` for who hit the banana
        """
        if not ev.lurker.in_race:
            await self._event_stream.send(
                    ChatMessageEvent(
                        f"@{ev.lurker.user_name} hit the banana just set by @{ev.lurker.user_name}"
                    )
                ) 
            return
        
        for lurker in self._lurker_gang:
            if not lurker.in_race:
                continue

            if lurker.position == ev.position:
                log.info(
                    "lurker %s hit %s's banana that was just dropped",
                    lurker.user_name,
                    ev.lurker.user_name,
                )
                await lurker.add_points(self._event_stream, -1)
                await self._event_stream.send(
                    HitBananaEvent(ev.lurker.position, lurker, ev.lurker)
                )
                await self._event_stream.send(
                    ChatMessageEvent(
                        f"@{lurker.user_name} hit the banana just set by @{ev.lurker.user_name}"
                    )
                )
                return

        log.info("banana dropped at %d by %s", ev.position, ev.lurker.user_name)

        if ev.position not in self._bananas:
            self._bananas[ev.position] = []
        self._bananas[ev.position].append(ev.lurker)


    

class Bot_one(commands.Bot):
    def __init__(self,lurker_gang: LurkerGang, event_stream:EventStream):
        super().__init__(token= USER_TOKEN , prefix='!', initial_channels=['codingwithstrangers'],
            nick = "Perfect_Lurker",)
        
        event_stream.add_consumer(self.consume_chat_message)
        self.pubsub = pubsub.PubSubPool(self)
        self.lurker_gang = lurker_gang
        self.event_stream = event_stream
        self.channel_point_handlers:Dict[str,Callable] = {
            perfect_lurker_channel_id: self.lurker_joins_race,
            yellow_channel_point: self.yellow_trap}

    async def event_pubsub_channel_points(self, event: pubsub.PubSubChannelPointsMessage):
        if event.user.name is None:
            return

        pprint.pprint(event.reward) #rerun in terminal look for id
        if event.reward.id in self.channel_point_handlers:
            await self.channel_point_handlers[event.reward.id](event)


    async def create_lurker(self, name: str):
        lower_case_name = name.lower()
        new_lurker = self.lurker_gang[lower_case_name]
        if new_lurker is not None:
            return new_lurker
        user_profiles = await self.fetch_users(names=[lower_case_name])
        logger.info(user_profiles[0].profile_image)
        new_lurker = Lurker(user_name=lower_case_name, image_url=user_profiles[0].profile_image)
        self.lurker_gang.add(new_lurker)
        return new_lurker

    #channelpoint for talking
    async def yellow_trap(self, event: pubsub.PubSubChannelPointsMessage):  
        if event.user.name is None:
            return 

        channel_point_lurker= await self.create_lurker(event.user.name)
        await self.event_stream.send(DropBananaEvent(channel_point_lurker))
        
        
    #message for joining race
    async def lurker_joins_race(self, event: pubsub.PubSubChannelPointsMessage):
        if event.user.name is None:
            return

        await self.create_lurker(event.user.name)
        await self.event_stream.send(JoinRaceAttemptedEvent(event.user.name))
        

    async def consume_chat_message(self,event: ChatMessageEvent):
        channel= self.connected_channels[0]
        await channel.send(event.message)

      
    #leave race
    @commands.command()
    async def kick(self, ctx: commands.Context, user: twitchio.PartialChatter):
        if ctx.author.is_broadcaster:
            await self.event_stream.send(LeaveRaceAttemptedEvent(user.name))    

    async def remove(self, ctx: commands.Context):
        if ctx.author.name is None:
            return

        await self.create_lurker(ctx.author.name)
        await self.event_stream.send(LeaveRaceAttemptedEvent(ctx.author.name))    
    

    #remove points for talking 
    async def event_message(self, message):
        if message.echo or message.author is None or message.author.name is None:
            return
            
        if 'custom-reward-id' not in message.tags or message.tags['custom-reward-id'] != talking_lurker_id:
            await self.create_lurker(message.author.name)        
            await self.event_stream.send(TalkingLurkerEvent(message.author.name))
        # print('TAGS:', message.tags)
        # talking_lurker = await self.create_or_get_lurker(message.author.name)
        # talking_lurker.add_points(-1)
        await self.handle_commands(message)
        # return
        # self.message_queue.append(f'{setting_lurker_points},{talking_lurker.user_name},{talking_lurker.points}')
        # await self.check_yellow_items()


    @commands.command()
    async def points(self, ctx: commands.Context):
        if ctx.author.name != "codingwithstrangers":
            return 
        for lurker in self.lurker_gang:
            print(lurker)
        
 
    #last function
    async def run(self):
        topics = [
            pubsub.channel_points(USER_TOKEN)[int(BROADCASTER_ID)],
            pubsub.channel_points(MOD_TOKEN)[int(MODERATOR_ID)]
        ]
        await self.pubsub.subscribe_topics(topics)
        print('this shit work? pt2')
        await self.start()

async def point_timer(lurker_gang: LurkerGang, event_stream: EventStream):
    for lurk in lurker_gang:
        await lurk.add_points(event_stream, delta=1)

#this is an entry point, that wires everything together and make sure it reads this file directly 
if __name__ == '__main__':
    event_stream = EventStream()
    lurker_gang = LurkerGang(event_stream)
    field= Field(lurker_gang,event_stream)
    bot = Bot_one(lurker_gang,event_stream)
    point_partial = functools.partial(point_timer,lurker_gang,event_stream)
    routines.routine(seconds=10)(point_partial).start()
    lurker_task_made = bot.loop.create_task(bot.run())
    # task_for_botgodot = bot.loop.create_task(bot.pytogodot())
    gather_both_task = asyncio.gather(lurker_task_made)
    bot.loop.run_until_complete(gather_both_task)