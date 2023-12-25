extends Node
@export var event_dispatcher: EventDispatcher
@export var gold_node:Node2D
@export var silver_node:Node2D
@export var bronze_node:Node2D

var crown_points:Array[SortedCrowns] = []
var is_dirty = false

# Called when the node enters the scene tree for the first time.
func _ready():
	event_dispatcher.lurker_joined.connect(lurker_join_race)
	event_dispatcher.lurker_left.connect(lurker_left)
	event_dispatcher.lurker_points.connect(lurker_points)
	
func lurker_points(lurker_name: String, lurker_point: int):
	is_dirty = true
	for crown_point in crown_points:
		if crown_point.lurker_name == lurker_name:
			crown_point.lurker_points =lurker_point
			return
	
	
func lurker_left(lurker_name: String):
	pass
	
	
#not enough lurkers what to do with 2 and 3	
func _process(delta):
	var offset = Vector2(10, 10) 
	if not is_dirty:
		return
	is_dirty = false
	crown_points.sort_custom(sort_crowns)
	var first_place = crown_points[0]
	if first_place.lurker_follow == null:
		first_place.lurker_follow = %Path2D_yellow.get_node(first_place.lurker_name + '_follow')
	gold_node.global_position = first_place.lurker_follow.global_position + offset
	
	if crown_points.size()>=2:
		var second_place = crown_points[1]
		if second_place.lurker_follow == null:
			second_place.lurker_follow = %Path2D_yellow.get_node(second_place.lurker_name + '_follow')
		silver_node.global_position = second_place.lurker_follow.global_position
	if crown_points.size()>=3:
		var third_place = crown_points[2]
		if third_place.lurker_follow == null:
			third_place.lurker_follow = %Path2D_yellow.get_node(third_place.lurker_name + '_follow')
		bronze_node.global_position = third_place.lurker_follow.global_position

#we dont have the lurkers path follows we may need to



func lurker_join_race(lurker_name: String, _image_url: String):
	var new_lurker = SortedCrowns.new()
	new_lurker.lurker_name = lurker_name
	crown_points.append(new_lurker)

func sort_crowns(a,b):
	return a.lurker_points > b.lurker_points

class SortedCrowns:
	var lurker_points = 0
	var lurker_name =""
	var lurker_follow: PathFollow2D
