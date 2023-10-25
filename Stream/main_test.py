
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

    next_lurkers = lurker_gang.lurkers_in_front_of(attacking_lurker)
    
    #then the return should be the lurker (only person in race)
    print(attacking_lurker,"==", next_lurkers)
    assert [attacking_lurker]== next_lurkers

#When 2 or more person in the race attacking lurker should return hit lurker who is directly infront of attacking lurker
def test_attacking_lurker_should_return_hit_lurker_who_is_directly_infront():
    event_stream = EventStream()
    lurker_gang = LurkerGang(event_stream)
    
    for i in range(10):
        new_lurker=Lurker(str(i), str(i))
        new_lurker.race_status = status_in_race
        new_lurker.points = i
        lurker_gang.add(new_lurker)

    print(lurker_gang._lurkers)
    print(lurker_gang.lurkers_in_front_of (lurker_gang["2"]))
    assert [lurker_gang["3"]] == lurker_gang.lurkers_in_front_of (lurker_gang["2"])


def test_attacking_lurkershould_return_a_hit_lurker_in_reverse_order():
    event_stream = EventStream()
    lurker_gang = LurkerGang(event_stream)
    
    for i in range(10,1,-1):
        new_lurker=Lurker(str(i), str(i))
        new_lurker.race_status = status_in_race
        new_lurker.points = i
        lurker_gang.add(new_lurker)

    print(lurker_gang._lurkers)
    print(lurker_gang.lurkers_in_front_of (lurker_gang["2"]))
    assert [lurker_gang["3"]] == lurker_gang.lurkers_in_front_of (lurker_gang["2"])

#When 2 or more lurkers are in the race and 2 or more lurkers are in the same place as hit lurkers attacking lurker should hit both or all users
def test_if_attacking_lurker_hits_two_or_more_lurkers_with_same_score():
    event_stream = EventStream()
    lurker_gang = LurkerGang(event_stream)
    
    for i in range(10,1,-1):
        new_lurker=Lurker(str(i), str(i))
        new_lurker.race_status = status_in_race
        new_lurker.points = i//3
        lurker_gang.add(new_lurker)

    print(lurker_gang._lurkers)
    print(lurker_gang.lurkers_in_front_of (lurker_gang["3"]))
    assert [lurker_gang["8"], lurker_gang["7"], lurker_gang["6"]] == lurker_gang.lurkers_in_front_of (lurker_gang["3"])

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
# Step 2: Run the tests, the test should fail
# Step 3: Write the least amount of code to make the test pass
# Step 4: Run the tests, the test should pass
# Step 5 optional: Update the code to look nicer, re-running the tests until the code is clean
# Repeat for each test