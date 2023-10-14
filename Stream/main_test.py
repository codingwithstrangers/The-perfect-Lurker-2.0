
from main import *
# from .Stream.main import *


def test_can_compare_lurkers():
    lurk_a1 = Lurker("a", "image_a")
    lurk_a2 = Lurker("a", "image_a")
    assert lurk_a1 == lurk_a2


#When trying to find lurkers in race if I am the only lurker in race I should return myself

def test_to_find_who_is_infront_of_attackinglurker():
    #given check place in race (tot points)
    event_stream = EventStream()
    lurker_gang = LurkerGang(event_stream)
    attacking_lurker = Lurker('attacking','attack_image')
    attacking_lurker.points = 2
    lurker_gang.add(attacking_lurker)
    attacking_lurker.race_status = status_in_race
    #when redshell is used by a lurker in the (single function call sometimes)

    next_lurker = lurker_gang.lurker_in_front_of(attacking_lurker)
    
    #then the return should be the lurker (only person in race)
    # print(attacking_lurker, next_lurker)
    assert attacking_lurker == next_lurker

#When 2 or more person in the race attacking lurker should return hit lurker who is directly infront of attacking lurker
def test_attacking_lurker_should_return_hit_lurker_who_is_directly_infront():
    event_stream = EventStream()
    lurker_gang = LurkerGang(event_stream)
    attacking_lurker = Lurker('attacking','attack_image')
    attacking_lurker.points = 2
    lurker_gang.add(attacking_lurker)
    attacking_lurker.race_status = status_in_race
    hit_lurker = Lurker('hit','hit_image')
    hit_lurker.points = 4
    lurker_gang.add(hit_lurker)
    hit_lurker.race_status = status_in_race
    #when reshell is used by a attacking_lurker in a race with a hit_lurker in front
    next_lurker = lurker_gang.lurker_in_front_of (attacking_lurker)
    print(hit_lurker,"==",next_lurker)
    assert hit_lurker == next_lurker

# for loop test do that here 
def test_attacking_lurker_should_return_hit_lurker_who_is_directly_infront_addingnewlurker():
    event_stream = EventStream()
    lurker_gang = LurkerGang(event_stream)
    attacking_lurker = Lurker('attacking','attack_image')
    attacking_lurker.points = 2
    lurker_gang.add(attacking_lurker)
    attacking_lurker.race_status = status_in_race
    hit_lurker = Lurker('hit','hit_image')
    hit_lurker.points = 4
    lurker_gang.add(hit_lurker)
    hit_lurker.race_status = status_in_race
    #when reshell is used by a attacking_lurker in a race with a hit_lurker in front
    next_lurker = lurker_gang.lurker_in_front_of (attacking_lurker)
    print(hit_lurker,"==",next_lurker)
    assert hit_lurker == next_lurker

#When 2 or more lurkers are in the race and 2 or more lurkers are in the same place as hit lurkers attacking lurker should hit both or all users

#process for Hit Lurker
#A hit lurker was hit by an attacking lurker if the hit lurker and attacking lurker are the same the hit lurker takes double damage -4

#If there are two 1st place lurkers and 1 uses a red shell becoming an attacing lurker the only hit lurker should be the other lurker sharing the space (thus becoming the hit lurker)-2

#If hit lurker is not the attacking lurker and in front (more tot points than attacking lurker) hit lurker will be hit -2


copy_dict = dict(locals())
for func in copy_dict.values():
    if callable(func) and func.__name__.startswith("test_"):
        print("running test:", func.__name__)
        func()

# Step 1: Write the test
# Step 2: Run the tests, they should fail
# Step 3: Write the least amount of code to make the test pass
# Step 4: Run the tests, they should pass
# Step 5 optional: Update the code to look nicer, re-running the tests until the code is clean
# Repeat for each test