extends Node
@export var event_dispatcher: EventDispatcher
# The URL we will connect to
var websocket_url = "ws://localhost:8766"

var socket = WebSocketPeer.new()

func _ready() -> void:
	socket.connect_to_url(websocket_url)
	socket.set_no_delay(true)

func _process(_delta):
	socket.poll()
	var state = socket.get_ready_state()
	if state == WebSocketPeer.STATE_OPEN:
		while socket.get_available_packet_count():
			event_dispatcher.handle_events(socket.get_packet().get_string_from_utf8())
	elif state == WebSocketPeer.STATE_CLOSING:
		# Keep polling to achieve proper close.
		pass
	elif state == WebSocketPeer.STATE_CLOSED:
		var code = socket.get_close_code()
		var reason = socket.get_close_reason()
		print("WebSocket closed with code: %d, reason %s. Clean: %s" % [code, reason, code != -1])
		set_process(false) # Stop processing.

