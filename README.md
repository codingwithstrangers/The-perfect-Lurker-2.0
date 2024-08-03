<div id="header" align="center">
  <img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNjAyMXphYmdkeWhsZjdzNWIyMjg0MGt5N3Rxd3dvZnFjZ2NuZXExMSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/jvOHlU7qhcnsEGuTQZ/giphy.gif" width="150"/>
</div>

### The Perfect Lurker

I have two bots that run on my channel: one is called The Perfect Stranger, and this one is The Perfect Lurker. The Perfect Stranger gives people points based on their chat engagement. However, @profuctivetime and @xowilough (go follow them and tell them a stranger sent you) felt left out from my stream. They are known as lurkers on Twitch.

<pre align="center">
----------------------------------------------------
</pre>

<div align="center"><h3>Lurk:</h3> To "lurk" means to watch a stream or keep a browser tab open without actively engaging. The sole objective is to support the stream without directly interacting with the chat, host, games, or other features. Being a lurker isn’t a bad thing; many people prefer to watch or work without engaging. As a host, it is important to respect lurkers and view them as an asset to your stream.</div>

<pre align="center">
----------------------------------------------------
</pre>

Feel free to use this, but I will be honest: it will take some elbow grease to get it working!

### What is This

It is a Twitch bot that handles various interactive events such as joining, setting and updating points, and managing special in-game items like yellow traps and red traps. It also integrates with Twitch's PubSub system for channel points and manages chat messages.

### Why Did I Do This

Many streamers get upset because they feel lurkers don't engage with the platform enough. With The Perfect Lurker, you can now see the people lurking on your stream and make them feel seen without requiring too much effort from them. I was inspired by my time playing N64 Mario Kart (chill Mario). I always thought the mini-map was so cool; I could look at it all day. It showed me where everyone was and where the traps were set. So, I took the mini-map concept and brought it to the stream.

### How Users Can Use This

**For Users:**
- Hire a programmer.
- Tell them to read this.

**For Programmers:**
Here’s a summary of how it works. Be advised that the Godot aspect is used for display purposes. You can send the event to any platform to display the stream; I just prefer Godot.

1. **Event Handling and Lurker Management**

   **Event Handling**
   The code contains several event handler methods that respond to various events:

   - `_on_join_attempt`: Handles an event where a lurker attempts to join the race. If the lurker exists, it calls the `join_race` method on the lurker.
   - `_on_talking_lurker`: Handles an event where a lurker talks in chat, reducing the lurker's points by 1.
   - `_on_leave_attempt`: Handles an event where a lurker attempts to leave the race. It calls the `leave_race` method on the lurker.
   - `_on_red_shell_channel_point`: Handles a red shell channel point event. It affects lurkers in front of the attacking lurker by sending events that drop a red shell and handle hits.
   - `_on_delay_hit_redshell`: Handles the event of hitting a red shell. It adjusts points based on whether the attacker hits themselves or another lurker.

   **Lurker Management**
   - `lurker_place`: Calculates the position of a specific lurker based on their points relative to others.
   - `ranking_lurker`: Returns the top 3 lurkers sorted by their points.
   - `lurkers_in_front_of`: Determines which lurkers are in front of a given attacking lurker based on points.

2. **Event Classes**
   Event classes encapsulate data associated with specific events. Each class includes:

   - `__init__` Method: Initializes the event with necessary attributes.
   - `dump` Method: Converts the event to a JSON string for serialization.

   **Example Events:**
   - `JoinedRaceEvent`: Represents a lurker joining the race.
   - `LeftRaceEvent`: Represents a lurker leaving the race.
   - `SetPointsEvent`: Used to update a lurker's points.
   - `DropBananaEvent`: Represents a lurker dropping a banana on the track.
   - `HitBananaEvent`: Represents the event of hitting a banana.

3. **Field Class**
   The Field class manages race-wide events such as items dropped (bananas). It:
   - Handles Banana Drops: Stores bananas by their position and checks if a lurker hits a banana.
   - Updates Points: Adjusts points and sends messages when a lurker hits a banana.

4. **Bot and Command Handling**

   **Bot_one Class:**
   This class represents a Twitch bot with several functionalities:
   - `event_pubsub_channel_points`: Handles channel point events and calls the appropriate handler.
   - `create_lurker`: Creates a new lurker or fetches an existing one.
   - `red_trap`: Handles red shell channel points.
   - `yellow_trap`: Handles yellow trap (banana) channel points.
   - `lurker_joins_race`: Handles lurkers joining the race via channel points.
   - `consume_chat_message`: Processes chat messages and handles commands.
   - `ranked`: Provides rankings of top lurkers.
   - `place`: Tells a lurker their current place in the race.

5. **Utility Functions**
   - `point_timer`: Periodically adds points to lurkers based on a list of viewers from a file.
   - `check_and_run`: Checks if a script (`viewers.py`) is running and starts it if it isn’t.

6. **Execution and Scheduling**
   - `main` Function: Sets up a scheduled job to check and run `viewers.py` periodically.

### Need Help?

[![Twitter Follow](https://img.shields.io/badge/Twitter-Follow%20%40strangestcoder-1DA1F2?style=for-the-badge&logo=twitter)](https://x.com/strangestcoder)

[![Twitch Status](https://img.shields.io/badge/Twitch-Live%20Codingwithstrangers-9146FF?style=for-the-badge&logo=twitch)](https://www.twitch.tv/codingwithstrangers)

### Who is Doing This

Coding with Strangers, aka Heero

### Features

**Summary**
The code represents a complex system for managing a Twitch-based racing game, with features like:
- Event handling for race actions (joining, leaving, item drops).
- Managing lurker points and positions.
- Interacting with Twitch chat through commands and channel points.
- Serializing events for storage or further processing.

### What You Will Need

**Files Included:**
- `main.py` – Handles all the events and is the main file that needs to run. Be advised this needs to run first before the rest.
- `viewer.py` – Scrapes your chat to get your viewer info and may need to be restarted to ensure it is running.
- `lurker_item.py` – Tracks all items lurkers can use.
- `configuration.py` – Holds all passwords and keys.
- `yellow_item.py` – Maps how yellow traps are set due to their placement on the map.

### Prerequisites

Before running the project, ensure you have the following:
- Godot installed
- Python 3.10.16
- `pip install twitchio`
- `pip install requests`

### Bugs

I really enjoyed working on this project; it pushed me to learn a lot about streaming events, cross-platform connections, and how to structure my code better. If I return to this code, I might do it fully in Godot and link it to a server so it can run in the cloud. However, if you want to find new bugs and fix old ones, feel free to dive in!

- [ ] Add Blue Shell: Randomly hits people as it travels to 1st place and deals 2 hit damage.
- [ ] Add Direct Mail: Lets you @ a user in the race.
- [ ] Shield: Blocks up to 3 hits.
- [ ] Add a function to show what lap the lurker is on above their icon.
- [ ] Improve animation in Godot for the red shell to be smoother.
- [ ] Give the host the ability to kick users both in Godot and the race.
- [ ] Allow users to leave the race in Godot too.
- [ ] Better way to track lurkers in chat; the scrape method takes forever to start. Maybe add a check to auto-rerun if it stops.
- [ ] Twitchio doesn’t have a way to refresh your token, so you need to do it manually (https://twitchtokengenerator.com/).
- [ ] Fix the issue where you can somehow throw a red shell without being in the race.

### Updates
I want to make it so that two streamers hell, up to 10 streamers can have their chat go head to head.
