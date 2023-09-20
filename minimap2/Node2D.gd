extends Node

# The URL we will connect to
var websocket_url = "ws://localhost:8765"

var socket = WebSocketPeer.new()


class LurkerGang:
	func get_lurker(key: String) -> Lurker:
		return _lurkers.get(key)


	func _process(delta):
		socket.poll()
		var state = socket.get_ready_state()
		if state == WebSocketPeer.STATE_OPEN:
			while socket.get_available_packet_count():
				var packet_data = socket.get_packet().get_string_from_utf8()
				print("Packet: ", packet_data)
				return packet_data
		elif state == WebSocketPeer.STATE_CLOSING:
			# Keep polling to achieve proper close.
			pass
		elif state == WebSocketPeer.STATE_CLOSED:
			var code = socket.get_close_code()
			var reason = socket.get_close_reason()
			print("WebSocket closed with code: %d, reason %s. Clean: %s" % [code, reason, code != -1])
			set_process(false) # Stop processing.
			
			
			
	# Builing out the Bot code 
	#View port scaling 
	#var user_info_dict ={}
	#var crown_follow
	#
	#
	#
	#
	#func _ready():
	#	var timer = Timer.new()
	#	timer.autostart = true
	#	timer.wait_time = 3
	#	add_child(timer)
	#	timer.timeout.connect(not_ready)
	#
	#	crown_follow = PathFollow2D.new()
	#	crown_follow.name = "crown_follow"
	#	crown_follow.rotates = false
	#	add_child(crown_follow)
	#
	#	var crown_sprite = Sprite2D.new()
	#	crown_sprite.name = "crown"
	#	crown_follow.add_child(crown_sprite)
	#	crown_follow.rotation = 0
	#
	#	#load image of crown
	#	var crown_texture = preload("res://pngwing.com.png")
	#	# Apply the ImageTexture to the crown sprite
	#	crown_sprite.texture = crown_texture
	#	crown_sprite.scale = Vector2(.07,.07)
	##add offset and data here 
	#	var offset = Vector2(0,-50)
	#	crown_sprite.position = offset
	#	not_ready()
	#
	#func not_ready():
	#	var updated_dict = csv_to_dict()
	#	for name in updated_dict.keys():
	##		var username = [content[0]] #name 
	#		var points = updated_dict[name]["points"]
	#		var image_url = updated_dict[name]["image_url"]
	#
	#		#check both dicts to find duplicates for the adding of user
	#		var already_in_race = user_info_dict.has(name)
	#		if not already_in_race:
	#			var follow = PathFollow2D.new()
	#			follow.name = name + "_follow"
	#			var sprite = Sprite2D.new()
	#			sprite.name=name
	#			add_child(follow)
	#			follow.add_child(sprite)
	#			follow.rotates=false
	#			follow.rotation = 0
	#
	#			#for every user make 2d sprite
	#			load_image_into_sprite(image_url,sprite)
	#			sprite.scale = Vector2(0.20,0.20)
	#
	#			#use line 23 to make changes and add to child 
	#			var score = Label.new()
	#			sprite.add_child(score)
	#
	#			score.scale = Vector2(5,5)
	#			score.position.y = -250
	#			score.position.x = -150
	#
	#			score = Label.new()
	#			sprite.add_child(score)
	#
	#			score.scale = Vector2(5, 5)
	#			score.position.y = -250
	#			score.position.x = -150
	#
	#
	#			#adding user to global user and the nods we want to update in the future
	#			user_info_dict[name] = {"follow": follow,'score_label':score}
	#
	#		user_info_dict[name]['score_label'].text = str(points)
	#		user_info_dict[name]['follow'].progress_ratio = points /60.0
	#
	#
	#		#print some ish
	#		print(points)
	#	#this will remove users from the race
	#	for existing_user in user_info_dict.keys():
	#		if not updated_dict.has(existing_user):
	#			user_info_dict[existing_user]['follow'].queue_free()
	#			user_info_dict.erase(existing_user)
	#
	#	#find top score to get the 
	#	var top_score = find_top_score_(updated_dict)
	#	crown_follow.progress_ratio = top_score/60.0

	#func find_top_score_(updated_dict):
	#	var top_score = -1
	#
	#	for name in updated_dict.keys():
	#		var points = updated_dict[name]['points']
	#
	#		if points > top_score:
	#			top_score = points
	#	print(top_score,"pokemon")		
	#	return top_score
	#
	#	#this is the func to open and get all the data
	#func csv_to_dict():
	#	var file = FileAccess.open("F://Coding with Strangers//Path2partnership//lurker_points.csv", FileAccess.READ)
	#	var users = {}
	#	while not file.eof_reached():
	#		var content = file.get_csv_line()
	#		print(content, 'hell yea')
	#		if content.size() > 1:
	#			users[content[0]] = {"points": int(content[1]), "image_url": content[2]}
	#	print(users)
	#	return users
	#
		
		#creates image type to store image url string 
	func image_type(url: String) ->String:
		var split = url.split('.')
		if  split.size() > 1:
			var file_extentsion = split[split.size() - 1]
			print (file_extentsion)
			return file_extentsion.to_lower()
			
		else:
			return "If you are reading this its already to late"
		
		
		#this is the request used to acll the url stored
	func load_image_into_sprite(url: String, sprite: Sprite2D):
		var http_request = HTTPRequest.new()
		add_child(http_request)
		http_request.request_completed.connect(self._on_HTTPRequest_request_completed.bind(sprite, url, http_request))
		var error = http_request.request(url)
		if error != OK:
			push_error("An error occurred in the HTTP request.")
			
	#image types and storying types also erros to follow
	func _on_HTTPRequest_request_completed(result, response_code, headers, body, sprite, url, http_request):
		if response_code == 200:
			var error = FAILED
			var url_ext = image_type(url)
			var image = Image.new()
			if url_ext == 'jpg':
				error = image.load_jpg_from_buffer(body)
				
			elif url_ext == 'png':
				error = image.load_png_from_buffer(body)
				
			elif url_ext == 'jpeg':
				error = image.load_jpg_from_buffer(body)
				print("loading jpeg", error)
				
			if error == OK:
				print("Downloaded " + url + " successfully")
				var texture = ImageTexture.create_from_image(image)
				# Apply the texture to the sprite
				var target_sprite = sprite as Sprite2D
				target_sprite.texture = texture
				add_child(target_sprite)
				
			else:
				print("Failed to load image from", sprite)
		else:
			print("Failed to fetch image: response_code=", response_code)
		
		#delete http_request node once done
		http_request.queue_free()


