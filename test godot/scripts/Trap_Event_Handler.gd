extends Node
@export var event_dispatcher: EventDispatcher
@export var yellow_trap:Array[PackedScene]
@export var red_trap:Array[PackedScene]
var location_of_yellowtrap = {}
var location_of_redtrap = {}
 

#,ake a class to handle textures and animations or gifs
# Called when the node enters the scene tree for the first time.
func _ready():
	event_dispatcher.lurker_drop_banana.connect(drop_yellow_trap)
	event_dispatcher.lurker_hit_yellow_trap.connect(lurker_hit_yellow)
	event_dispatcher.lurker_drop_redshell.connect(drop_red_trap)
	event_dispatcher.lurker_hit_redshell.connect(lurker_hit_redtrap)
	
func lurker_hit_yellow(_lurker_name: String, lurker_position: int):
	#make a 4 loop to see if the new trap has and equal points with the lurker hit yellow trap
	location_of_yellowtrap[lurker_position].queue_free()
	location_of_yellowtrap.erase(lurker_position)
	pass
	

func drop_yellow_trap(lurker_name: String, lurker_position: int):
	var new_trap = yellow_trap[randi_range(0,yellow_trap.size()-1)].instantiate()
	%Path2D_yellow.add_child(new_trap)
	var follow = new_trap as PathFollow2D
	follow.name = lurker_name + "_follow_trap"
	follow.progress_ratio = lurker_position/60.0
	#storing tap location 
	location_of_yellowtrap[lurker_position]= new_trap


func lurker_hit_redtrap(hit_lurker_name: String, attack_lurker_name: String, hit_lurker_point: int, attack_lurker_point: int):
	#make a 4 loop to see if the new trap has and equal points with the lurker hit yellow trap
	location_of_redtrap[hit_lurker_point].queue_free()
	location_of_redtrap.erase(hit_lurker_point)
	pass
	

	
func drop_red_trap(hit_lurker_name: String, hit_lurker_point: int, attack_lurker_name: String, attack_lurker_point: int, red_delay: int):
	var new_trap = red_trap[randi_range(0,red_trap.size()-1)].instantiate()
#var new_trap = 
	%Path2D_yellow.add_child(new_trap)
#	var trap_starting_position = attack_lurker_point/60.0
	#setting trap to intial position 
	var path = %Path2D_yellow as Path2D
	#gotta get the path running to the correct spot (load)
	var trap_start = attack_lurker_point /60.0
	var trap_end = hit_lurker_point/60.0
	new_trap.progress_ratio = trap_start
	if trap_end < trap_start:
		trap_end+= 1
	
	#create tweens
	var trap_tween = create_tween()
	trap_tween.tween_property(new_trap, "progress_ratio",trap_end, red_delay)
	#stop the tweens once completed
	trap_tween.tween_callback(func():
		new_trap.queue_free()
		)
	location_of_redtrap[hit_lurker_point]= new_trap
	pass
	
	


#	sprite.name=name
#	$Path2D.add_child(follow)
#	follow.add_child(sprite)
#	follow.rotates=false
#	follow.rotation = 0
#	follow.progress_ratio = lurker_points/60.0
#
##for every user make 2d sprite
#	sprite.scale = Vector2(0.20,0.20)
#
#	#use line 23 to make changes and add to child 
#	var score = Label.new()
#	sprite.add_child(score)
#
#	score.scale = Vector2(5,5)
#	score.position.y = -250
#	score.position.x = -150
#
#	score = Label.new()
#	sprite.add_child(score)
#
#	score.scale = Vector2(5, 5)
#	score.position.y = -250
#	score.position.x = -150
#
#	#for every user make 2d sprite
	
#	sprite.scale = Vector2(0.20,0.20)
	
