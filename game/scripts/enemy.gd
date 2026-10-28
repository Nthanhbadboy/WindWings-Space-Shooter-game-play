class_name WaveEnemy
extends Area2D

signal projectile_requested(
	origin: Vector2, direction: Vector2, damage: float, speed: float, lifetime_seconds: float
)
signal defeated(enemy_id: int)
signal escaped(enemy_id: int)

var enemy_id := 0
var prefab_name := ""
var current_health := 0.0
var maximum_health := 0.0
var contact_damage := 0.0
var health_known := false
var movement_speed := 0.0
var is_turret := false
var formation_kind := "point"
var formation_phase := 0.0
var spawner_speed_hint := 0.0
var contact_damage := 0.0

# INFERRED NEW_DESIGN — a turret has no descent in the source rows, and rows can
# spawn above the visible top (y_spawn 12/15), so a stationary enemy would never
# be reachable. Turrets therefore drift down to this world y and hold there.
const TURRET_HOLD_Y := -8.0
const TURRET_DESCENT := 1.8

var _target: Node2D
var _gun_profile: Dictionary = {}
var _gun_start_wait := 0.0
var _gun_wait := 0.0
var _mags_remaining := 0
var _shots_remaining := 0
var _age := 0.0
var _anchor_x := 0.0
var _is_defeated := false


func configure(data: Dictionary) -> void:
	enemy_id = int(data.get("enemy_id", 0))
	prefab_name = str(data.get("prefab_name", ""))
	health_known = bool(data.get("health_known", false))
	maximum_health = float(data.get("health", 0.0))
	current_health = maximum_health
	movement_speed = maxf(float(data.get("movement_speed", 0.0)), 0.0)
	is_turret = bool(data.get("is_turret", false))
	formation_kind = str(data.get("formation_kind", "point"))
	formation_phase = float(data.get("formation_phase", 0.0))
	spawner_speed_hint = float(data.get("spawner_speed_hint", 0.0))
	contact_damage = float(data.get("contact_damage", 0.0))
	position = data.get("spawn_position", Vector2.ZERO)
	_anchor_x = position.x
	var target_value: Variant = data.get("target")
	if target_value is Node2D:
		_target = target_value
	var gun_value: Variant = data.get("gun_profile", {})
	if gun_value is Dictionary:
		_gun_profile = gun_value
		_gun_start_wait = maxf(float(_gun_profile.get("time_start_seconds", 0.0)), 0.0)
	queue_redraw()


func _ready() -> void:
	add_to_group("enemies")
	add_to_group("shootable")
	collision_layer = 4
	collision_mask = 3


func _physics_process(delta: float) -> void:
	_age += delta
	if is_turret or movement_speed <= 0.0:
		if position.y < TURRET_HOLD_Y:
			position.y = minf(position.y + TURRET_DESCENT * delta, TURRET_HOLD_Y)
	else:
		if formation_kind == "path":
			position.x = _anchor_x + sin(_age * 1.15 + formation_phase) * 0.62
		elif formation_kind == "point_range":
			position.x = _anchor_x + sin(_age * 0.72 + formation_phase) * 0.14
		position.y += movement_speed * delta
	_update_weapon(delta)
	if LaunchRules.is_outside_world_border(position):
		escaped.emit(enemy_id)
		queue_free()


func take_damage(amount: float) -> void:
	if _is_defeated or not health_known or amount <= 0.0:
		return
	current_health = maxf(current_health - amount, 0.0)
	queue_redraw()
	if current_health <= 0.0:
		_is_defeated = true
		defeated.emit(enemy_id)
		queue_free()


func _update_weapon(delta: float) -> void:
	if _gun_profile.is_empty() or not is_instance_valid(_target):
		return
	if _gun_start_wait > 0.0:
		_gun_start_wait = maxf(_gun_start_wait - delta, 0.0)
		if _gun_start_wait > 0.0:
			return
	if _gun_wait > 0.0:
		_gun_wait = maxf(_gun_wait - delta, 0.0)
		if _gun_wait > 0.0:
			return
	if _mags_remaining <= 0:
		# Source zero-count semantics are UNKNOWN; this adapter treats zero as one magazine.
		_mags_remaining = maxi(int(_gun_profile.get("count_mags", 1)), 1)
	if _shots_remaining <= 0:
		_shots_remaining = maxi(int(_gun_profile.get("count_shots", 0)), 1)
	_fire_once()
	_shots_remaining -= 1
	if _shots_remaining > 0:
		_gun_wait = maxf(float(_gun_profile.get("time_shot_seconds", 0.0)), 0.0)
	else:
		_mags_remaining -= 1
		if _mags_remaining > 0:
			_gun_wait = maxf(float(_gun_profile.get("time_reload_seconds", 0.0)), 0.0)
		else:
			_gun_wait = maxf(float(_gun_profile.get("time_rounds_seconds", 1.0)), 0.0)


func _fire_once() -> void:
	var origin := global_position + Vector2(0.0, 0.28)
	var direction := Vector2.DOWN
	if is_instance_valid(_target):
		direction = (_target.global_position - origin).normalized()
	projectile_requested.emit(
		origin,
		direction,
		float(_gun_profile.get("damage", 0.0)),
		float(_gun_profile.get("speed", 0.0)),
		float(_gun_profile.get("lifetime_seconds", 1.0))
	)


func _draw() -> void:
	var hull := _family_color()
	if enemy_id % 3 == 0:
		draw_colored_polygon(
			PackedVector2Array(
				[
					Vector2(0.0, -0.34),
					Vector2(0.34, -0.02),
					Vector2(0.21, 0.27),
					Vector2(-0.21, 0.27),
					Vector2(-0.34, -0.02)
				]
			),
			hull
		)
		_draw_outline(hull)
	else:
		draw_colored_polygon(
			PackedVector2Array(
				[Vector2(0.0, -0.37), Vector2(0.32, 0.22), Vector2(0.0, 0.12), Vector2(-0.32, 0.22)]
			),
			hull
		)
		draw_line(Vector2(-0.25, 0.08), Vector2(0.25, 0.08), Color(0.88, 0.96, 1.0, 0.82), 0.045)
	if health_known and maximum_health > 0.0:
		draw_rect(Rect2(-0.34, -0.49, 0.68, 0.065), Color(0.055, 0.08, 0.14, 0.95))
		draw_rect(
			Rect2(-0.33, -0.48, 0.66 * current_health / maximum_health, 0.045),
			Color(0.34, 0.95, 0.81, 0.92)
		)


func _draw_outline(color: Color) -> void:
	var points := PackedVector2Array(
		[
			Vector2(0.0, -0.34),
			Vector2(0.34, -0.02),
			Vector2(0.21, 0.27),
			Vector2(-0.21, 0.27),
			Vector2(-0.34, -0.02),
			Vector2(0.0, -0.34)
		]
	)
	draw_polyline(points, color.lightened(0.35), 0.04, true)


func _family_color() -> Color:
	match prefab_name.get_slice("-", 0):
		"CB":
			return Color(0.29, 0.86, 0.94)
		"CD":
			return Color(1.0, 0.48, 0.31)
		"XB":
			return Color(0.77, 0.52, 1.0)
		"H":
			return Color(1.0, 0.76, 0.35)
		_:
			return Color(0.78, 0.88, 1.0)
