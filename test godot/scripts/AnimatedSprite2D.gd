extends AnimatedSprite2D


# Called when the node enters the scene tree for the first time.
func _ready():
	var animation_player = AnimationPlayer.new()
	sprite.add_child(animation_player)


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass
