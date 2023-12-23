extends Node

@export var event_dispatcher: EventDispatcher
@export var console_container: BoxContainer
@export var console_editor: TextEdit
@export var key_console_open: InputEventKey
@export var key_console_close: InputEventKey
@export var key_console_send: InputEventKey

func _ready() -> void:
	console_editor.gui_input.connect(_on_event_editor_gui_input)

func _input(event: InputEvent) -> void:
	if event.is_echo() || !event.is_pressed():
		return

	if key_console_open.is_match(event, true):
		console_container.visible = true
		console_editor.grab_focus.call_deferred()
	elif key_console_close.is_match(event, true):
		console_container.visible = false

func _on_event_editor_gui_input(event: InputEvent) -> void:
	if event.is_echo() || !event.is_pressed():
		return

	if event.is_match(key_console_send):
		event_dispatcher.handle_events(console_editor.text)
		console_editor.text = ""
		console_container.visible = false

