extends Node2D

## Art-QA stage: ONE boss, no HUD, fixed close camera, turrets sweeping.
##
## Why a separate scene instead of reusing scenes/main.tscn: the run scene owns a
## camera that reframes itself on every viewport change and a HUD that draws
## banners across the hull, and the earlier attempt to repurpose it produced
## frames of empty starfield. This stage does one job - show the boss art at a
## readable size with the pods turning - so the frame sequence can answer the
## only question it exists for: does the pod seam open, does the core sit on the
## hull centre, does the body stay still while the turrets move.
##
## Segment (tools/motion_capture.gd): "turret", 3.4 s.

const BOSS_SCENE := preload("res://scenes/boss.tscn")
const BossPatternScript := preload("res://scripts/boss_pattern.gd")
const MotionTuningScript := preload("res://scripts/motion_tuning.gd")

## World units visible from top to bottom. The boss is 2.4 units tall and drifts
## in from 4.2 units above the station, so 9 units keeps it in frame the whole
## time without shrinking the art.
@export var visible_units := 9.0
@export var zoom_factor := 2.0

var _elapsed := 0.0
var _camera: Camera2D
var _boss: SliceBoss


func _ready() -> void:
	_camera = Camera2D.new()
	_camera.position = Vector2(0.0, -1.6)
	add_child(_camera)
	_configure_camera()
	get_viewport().size_changed.connect(_configure_camera)

	var pattern: BossPattern = BossPatternScript.new()
	if not pattern.load_default():
		push_error("turret QA stage: %s" % pattern.error)
	var gun_profile: Dictionary = {}
	_boss = BOSS_SCENE.instantiate() as SliceBoss
	_boss.configure(
		{
			"pattern": pattern,
			"hp": pattern.hp_max,
			"target": self,
			"station": Vector2.ZERO,
			"spawn_position": Vector2(0.0, -4.2),
			"slot": 0,
			"gun_profile": gun_profile,
			"contact_damage": 0.0,
		}
	)
	_boss.set("capture_turret_sweep", true)
	add_child(_boss)


func _process(delta: float) -> void:
	_elapsed += delta


func _configure_camera() -> void:
	var size := get_viewport_rect().size
	if size.x <= 0.0 or size.y <= 0.0:
		return
	var pixels_per_unit := size.y / maxf(visible_units, 1.0)
	_camera.zoom = Vector2(pixels_per_unit * maxf(zoom_factor, 0.1), pixels_per_unit * maxf(zoom_factor, 0.1))


func capture_time() -> float:
	return _elapsed

