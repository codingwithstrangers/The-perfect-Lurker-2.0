@tool
extends Sprite2D
@export var shell_images: Array[Texture2D]
var last_postion : Vector2

# Called when the node enters the scene tree for the first time.
func _ready():

	
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if global_position == last_postion:
		return
	#assuming right up left down is our sequence we can cal. the direction and texture using
	var delta_position = global_position - last_postion
	#angle index using pi ()remember this is 4 images
	var angle_position = roundi((delta_position.angle() + PI - PI / 8) / PI / 2 * 4) % 4
	texture = shell_images[angle_position]
	print(angle_position, ', ', delta_position.angle())
	flip_h = angle_position == 2
	last_postion = global_position
	pass
