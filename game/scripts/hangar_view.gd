extends Node2D

## Full-screen hangar: camera framing plus the animated ship and floor. Used by
## tools/motion_capture.gd and available as a standalone scene.

const FLOOR_SCRIPT := preload("res://scripts/hangar_floor.gd")
const SHIP_SCENE := preload("res://scenes/hangar_ship.tscn")

@export var ship_id := 10001
@export var show_units := 9.0

var _camera: Camera2D
var _ship: HangarShip
var _elapsed := 0.0


func _ready() -> void:
	_camera = Camera2D.new()
	_camera.position = Vector2(0.0, 0.0)
	add_child(_camera)
	var floor := Node2D.new()
	floor.set_script(FLOOR_SCRIPT)
	add_child(floor)
	_ship = SHIP_SCENE.instantiate() as HangarShip
	add_child(_ship)
	_ship.set_ship(ship_id)
	_configure_camera()
	get_viewport().size_changed.connect(_configure_camera)


func _process(delta: float) -> void:
	_elapsed += delta


func _configure_camera() -> void:
	var size := get_viewport_rect().size
	if size.x <= 0.0 or size.y <= 0.0:
		return
	var pixels_per_unit := size.y / maxf(show_units, 1.0)
	_camera.zoom = Vector2(pixels_per_unit, pixels_per_unit)


func capture_time() -> float:
	return _elapsed


func set_ship(id: int) -> void:
	ship_id = id
	if _ship != null:
		_ship.set_ship(id)
