extends Node2D

const PLAYER_INDEX := 0
const FALLBACK_PLAYER_HP := 2500.0
const PROJECTILE_SCENE := preload("res://scenes/projectile.tscn")

var _rng := RandomNumberGenerator.new()
var _player_shots := 0
var _near_misses := 0
var _player_bullet_speed := 18.0
var _training_gun: Dictionary = {}
var _training_gun_start := 0.0
var _training_gun_reload := 0.0
var _training_gun_mags_left := 0
var _training_waiting_round := false
var _training_round_wait := 0.0
var _game_over := false

@onready var camera: Camera2D = $Camera2D
@onready var world: Node2D = $World
@onready var player: Player = $World/Player
@onready var training_target: TrainingTarget = $World/TrainingTarget
@onready var hud: GameHUD = $CanvasLayer/HUD


func _ready() -> void:
	_rng.seed = 0x20330D0E
	_configure_camera()
	get_viewport().size_changed.connect(_configure_camera)
	player.shot_requested.connect(_on_player_shot_requested)
	player.health_changed.connect(_on_health_changed)
	player.died.connect(_on_player_died)
	training_target.hit_registered.connect(_on_target_hit)
	hud.pause_requested.connect(_on_pause_requested)
	hud.retry_requested.connect(_on_retry_requested)
	var player_stats := _read_json("res://data/player_start_stats.json")
	var damage_values := _get_field_values(player_stats, "StartMainCannonDamages")
	if damage_values.size() != 24:
		push_error(
			"Expected the decoded 24-entry player damage array; see game/data/player_start_stats.json"
		)
		return
	var baseline := _read_json("res://data/player_baseline.json")
	var tuning := _read_json("res://data/prototype_tuning.json")
	_training_gun = _read_json("res://data/training_gun.json")
	var base_hp := float(baseline.get("base_hp", FALLBACK_PLAYER_HP))
	var fire_period := float(tuning.get("player_fire_period_seconds", 0.24))
	_player_bullet_speed = float(tuning.get("player_projectile_speed_units_per_second", 18.0))
	_training_gun_start = float(_training_gun.get("time_start_seconds", 1.0))
	# STATIC_CONFIRMED: array index 0 is 4500. The index-to-ship-ID binding is not asserted here.
	player.configure_weapon(float(damage_values[PLAYER_INDEX]), fire_period)
	player.configure_health(base_hp)
	_update_hud()


func _process(delta: float) -> void:
	if _game_over:
		return
	_update_training_gun(delta)


func _configure_camera() -> void:
	var viewport_size := get_viewport_rect().size
	if viewport_size.x <= 0.0 or viewport_size.y <= 0.0:
		return
	# Camera contract: half-height = max((h / w) * 5.4, 9.6); visible width stays 10.8
	# at portrait ratios. This is the Godot zoom equivalent of the reference orthographic formula.
	var half_height := maxf((viewport_size.y / viewport_size.x) * 5.4, 9.6)
	var pixels_per_world_unit := viewport_size.y / (half_height * 2.0)
	camera.zoom = Vector2(pixels_per_world_unit, pixels_per_world_unit)
	var half_width := viewport_size.x / pixels_per_world_unit * 0.5
	player.set_movement_bounds(
		Rect2(
			-half_width + 0.48,
			-half_height + 0.82,
			(half_width - 0.48) * 2.0,
			(half_height - 0.82) * 2.0
		)
	)


func _update_training_gun(delta: float) -> void:
	if _training_gun_start > 0.0:
		_training_gun_start -= delta
		if _training_gun_start <= 0.0:
			_training_gun_mags_left = int(_training_gun.get("count_mags", 3))
			_training_gun_reload = 0.0
		return
	if _training_gun_mags_left > 0:
		_training_gun_reload -= delta
		if _training_gun_reload <= 0.0:
			_spawn_training_projectile()
			_training_gun_mags_left -= 1
			if _training_gun_mags_left > 0:
				_training_gun_reload = float(_training_gun.get("time_reload_seconds", 0.4))
			else:
				_training_waiting_round = true
				_training_round_wait = float(_training_gun.get("time_rounds_seconds", 1.0))
		return
	if _training_waiting_round:
		_training_round_wait -= delta
		if _training_round_wait <= 0.0:
			_training_waiting_round = false
			_training_gun_mags_left = int(_training_gun.get("count_mags", 3))
			_training_gun_reload = 0.0


func _spawn_training_projectile() -> void:
	var spawn_position := Vector2(_rng.randf_range(-3.8, 3.8), -9.4)
	var shot := PROJECTILE_SCENE.instantiate() as Projectile
	shot.faction = Projectile.Faction.ENEMY
	shot.position = spawn_position
	shot.direction = (player.global_position - spawn_position).normalized()
	shot.speed = float(_training_gun.get("speed", 4.0))
	shot.damage = float(_training_gun.get("damage", 400.0))
	shot.lifetime_seconds = float(_training_gun.get("lifetime_seconds", 8.0))
	shot.target = player
	shot.near_miss.connect(_on_near_miss)
	world.add_child(shot)


func _on_player_shot_requested(origin: Vector2, damage: float) -> void:
	_player_shots += 1
	var shot := PROJECTILE_SCENE.instantiate() as Projectile
	shot.faction = Projectile.Faction.PLAYER
	shot.position = origin
	shot.direction = Vector2.UP
	shot.speed = _player_bullet_speed
	shot.damage = damage
	shot.lifetime_seconds = 3.0
	world.add_child(shot)
	_update_hud()


func _on_near_miss() -> void:
	_near_misses += 1
	_update_hud()


func _on_health_changed(_current: float, _maximum: float) -> void:
	_update_hud()


func _on_target_hit(_total_hits: int) -> void:
	_update_hud()


func _on_player_died() -> void:
	_game_over = true
	hud.show_game_over()
	get_tree().paused = true


func _on_pause_requested() -> void:
	if _game_over:
		return
	var should_pause := not get_tree().paused
	get_tree().paused = should_pause
	hud.set_paused(should_pause)


func _on_retry_requested() -> void:
	get_tree().paused = false
	get_tree().reload_current_scene()


func _update_hud() -> void:
	if not is_instance_valid(hud) or not is_instance_valid(player):
		return
	hud.update_status(
		{
			"wave": "WAVE 00  ·  TRAINING RANGE",
			"hp": player.current_health,
			"max_hp": player.maximum_health,
			"coins": 0,
			"hits": training_target.total_hits,
			"near_misses": _near_misses,
			"shots": _player_shots
		}
	)


func _read_json(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		push_error("Missing runtime data file: %s" % path)
		return {}
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not parsed is Dictionary:
		push_error("Expected a JSON object in %s" % path)
		return {}
	return parsed


func _get_field_values(data: Dictionary, field_name: String) -> Array:
	for row: Dictionary in data.get("fields", []):
		if row.get("field", "") == field_name:
			return row.get("values", [])
	return []
