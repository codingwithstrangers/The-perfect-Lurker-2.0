extends Node2D
@export var event_dispatcher: EventDispatcher

# Called when the node enters the scene tree for the first time.
func _ready():
	event_dispatcher.lurker_joined.connect(lurker_join_race)
	event_dispatcher.lurker_left.connect(lurker_left)
	event_dispatcher.lurker_points.connect(lurker_points)
#	event_dispatcher.lurker_hit_yellow_trap.connect()
	
func lurker_points(lurker_name: String, lurker_point: int):
	var path_follow = get_node(lurker_name + "_follow")
	path_follow.progress_ratio = lurker_point/60.0
	
	
func lurker_left(lurker_name: String):
	var remove = get_node(lurker_name + "_follow")
	remove.queue_free()
	

func lurker_join_race(lurker_name: String, image_url: String):

	var follow = PathFollow2D.new()
	follow.name = lurker_name + "_follow"
	var sprite = Sprite2D.new()
	sprite.name=name
	add_child(follow)
	follow.add_child(sprite)
	follow.rotates=false
	follow.rotation = 0
	
		#for every user make 2d sprite
	load_image_into_sprite(image_url,sprite)
	sprite.scale = Vector2(0.20,0.20)
	
	#use line 23 to make changes and add to child 
	var score = Label.new()
	sprite.add_child(score)
	
	score.scale = Vector2(5,5)
	score.position.y = -250
	score.position.x = -150
	
	score = Label.new()
	sprite.add_child(score)

	score.scale = Vector2(5, 5)
	score.position.y = -250
	score.position.x = -150
	
	#for every user make 2d sprite
	load_image_into_sprite(image_url,sprite)
	sprite.scale = Vector2(0.20,0.20)
	
	

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
func _on_HTTPRequest_request_completed(_result, response_code, _headers, body, sprite, url, http_request):
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
#			add_child(target_sprite)
			
		else:
			print("Failed to load image from", sprite)
	else:
		print("Failed to fetch image: response_code=", response_code)
	
	#delete http_request node once done
	http_request.queue_free()
	
