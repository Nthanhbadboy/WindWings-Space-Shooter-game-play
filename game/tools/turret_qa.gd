extends Node2D

## Art-QA stage: ONE boss, no HUD, camera locked on the hull, turrets sweeping.
##
## Why a separate scene instead of reusing scenes/main.tscn: the run scene owns a
## camera that reframes itself on every viewport change and a HUD that draws
## banners across the hull, and the earlier attempt to repurpose it produced
## frames of empty starfield. This stage does one job - show the boss art at a
## readable size with the pods turning - so the frame sequence can answer the
## only question it exists for: does the pod seam open, does the core sit on the
## hull centre, does the body stay still while the turrets move.
##
## Segment (tools/motion_capture.gd): "turret", 3.4 s. The entrance is skipped so
## all 3.4 s show the turrets turning (+45 deg at ~1.0 s, -45 deg at ~2.9 s).

const BOSS_SCENE := preload("res://scenes/boss.tscn")
const BossPatternScript := preload("res://scripts/boss_pattern.gd")
const MotionTuningScript := preload("res://scripts/motion_tuning.gd")

## World units from top to bottom. The boss is 2.4 units tall, so ~5.2 units
## frames the whole hull plus a little air while keeping the art readable.
@export var visible_units := 5.2

var _elapsed := 0.0
var _camera: Camera2D
var _boss: SliceBoss


func _ready() -> void:
	_camera = Camera2D.new()
	_camera.position = Vector2.ZERO
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
	_boss.set("capture_hide_health_bar", true)
	# Skip the 2.4 s entrance: this camera follows the boss, so the descent shows
	# up as a frozen frame, and the sweep only starts once the entrance ends.
	_boss.set("capture_skip_intro", true)
	add_child(_boss)


func _process(delta: float) -> void:
	_elapsed += delta
	# Follow the boss: it descends for 2.4 s and then drifts, so a camera locked
	# to the spawn point would lose it (that was the empty-starfield attempt).
	if _boss != null and is_instance_valid(_boss):
		_camera.position = _boss.global_position


func _configure_camera() -> void:
	var size := get_viewport_rect().size
	if size.x <= 0.0 or size.y <= 0.0:
		return
	var pixels_per_unit := size.y / maxf(visible_units, 1.0)
	_camera.zoom = Vector2(pixels_per_unit, pixels_per_unit)


func capture_time() -> float:
	return _elapsed

