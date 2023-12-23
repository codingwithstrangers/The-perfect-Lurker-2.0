class_name EventDispatcher extends Node
signal lurker_joined(lurker_name: String, image_url: String)
signal lurker_left(lurker_name: String)
signal lurker_points(lurker_name: String, lurker_point: int)
signal lurker_drop_banana(lurker_name: String, lurker_point: int)
signal lurker_hit_yellow_trap(lurker_name: String, lurker_position: int) 
signal lurker_drop_redshell(hit_lurker_name: String, hit_lurker_point: int, attack_lurker_name: String, attack_lurker_point: int, red_delay: int)
signal lurker_hit_redshell(hit_lurker_name: String, hit_lurker_point: int, attack_lurker_name: String, attack_lurker_point: int)


#index of event types
const setting_lurker_points = 3
const yellow_banana_drop =4
const yellow_banana_hit= 5
const yellow_banana_shield = 14
const red_shell_drop = 6
const red_shell_shield =8
const red_shell_hit = 7
const blue_shell_shield = 9
const lurker_join_race = 1
const lurker_left_race = 2
const shield_start = 11
const shield_stop = 12

func handle_events(raw_events: String) -> void:
	#for joining race we want the dispatch to listen for 9 in the first spot
	for event in raw_events.split("\n",false):
		var event_split = event.split(",")
		var event_index = event_split[0].to_int()
		match event_index:
			lurker_join_race:
				var event_lurker_name = event_split[1]
				var event_image_url = event_split[2]
				lurker_joined.emit(event_lurker_name,event_image_url)
			setting_lurker_points:
				var event_lurker_name = event_split[1]
				var event_points = event_split[2].to_int()
				lurker_points.emit(event_lurker_name,event_points)
			lurker_left_race:
				var event_lurker_name = event_split[1]
				lurker_left.emit(event_lurker_name)
			yellow_banana_drop:
				var event_lurker_name = event_split[1]
				var event_points = event_split[2].to_int()
				lurker_drop_banana.emit(event_lurker_name,event_points)
			yellow_banana_hit:
				var event_lurker_name = event_split[2]
				var yellow_trap_location = event_split[1].to_int()
				lurker_hit_yellow_trap.emit(event_lurker_name,yellow_trap_location)
			red_shell_drop:
				var event_attack_lurker_name = event_split[1]
				var event_attack_points = event_split[2].to_int()
				var event_hit_lurker_name = event_split[3]
				var event_hit_points = event_split[4].to_int()
				var event_red_delay = event_split[5].to_int()
				lurker_drop_redshell.emit(event_hit_lurker_name,event_hit_points,event_attack_lurker_name,event_attack_points, event_red_delay)
			red_shell_hit:
				var event_hit_lurker_name = event_split[1]
				var event_hit_points = event_split[2].to_int()
				var event_attack_lurker_name = event_split[3]
				var event_attack_points = event_split[4].to_int()
				lurker_hit_redshell.emit(event_hit_lurker_name,event_hit_points,event_attack_lurker_name,event_attack_points)
				
				
			
				
				
				
				
			
	
			
		
	
