class_name SliceBoss
extends Area2D

## Wave boss for the slice. HP and the shot timeline are data; the flight path,
## projectile ballistics fallback and silhouette are new design.

signal defeated(boss: Node)
signal projectile_requested(
	origin: Vector2, direction: Vector2, damage: float, speed: float, lifetime_seconds: float
)

const INTRO_SECONDS := 1.6

var max_hp := 0.0
var current_hp := 0.0
var contact_damage := 0.0

var _pattern: BossPattern
var _target: Node2D
var _station := Vector2.ZERO
var _spawn_point := Vector2.ZERO
var _slot := 0
var _gun: Dictionary = {}
var _elapsed := 0.0
var _shot_elapsed := 0.0
var _dead := false


func configure(data: Dictionary) -> void:
	_pattern = data.get("pattern")
	max_hp = float(data.get("hp", 0.0))
	current_hp = max_hp
	contact_damage = float(data.get("contact_damage", 0.0))
	_station = data.get("station", Vector2.ZERO)
	_spawn_point = data.get("spawn_position", _station)
	_slot = int(data.get("slot", 0))
	var target_value: Variant = data.get("target")
	if target_value is Node2D:
		_target = target_value
	var gun_value: Variant = data.get("gun_profile", {})
	if gun_value is Dictionary:
		_gun = gun_value
	position = _spawn_point


func _ready() -> void:
	add_to_group("enemies")
	add_to_group("shootable")
	add_to_group("bosses")
	collision_layer = 4
	collision_mask = 3
	var shape := CircleShape2D.new()
	shape.radius = 1.15
	var collider := get_node_or_null("CollisionShape2D") as CollisionShape2D
	if collider != null:
		collider.shape = shape
	queue_redraw()


func _physics_process(delta: float) -> void:
	if _dead:
		return
	_elapsed += delta
	var progress := clampf(_elapsed / INTRO_SECONDS, 0.0, 1.0)
	position.y = lerpf(_spawn_point.y, _station.y, progress)
	# New design: slow horizontal sweep once the boss has arrived.
	position.x = _station.x + sin(_elapsed * 0.75 + float(_slot) * 1.7) * 1.35 * progress
	if progress < 1.0:
		return
	var previous := _shot_elapsed
	_shot_elapsed += delta
	if _pattern == null:
		return
	var shots := _pattern.shots_in_interval(previous, _shot_elapsed)
	for _shot in range(shots):
		_fire()


func _fire() -> void:
	if not is_instance_valid(_target) or _gun.is_empty():
		return
	var origin := global_position + Vector2(0.0, 0.9)
	var direction := (_target.global_position - origin).normalized()
	Session.play_sfx("hit")
	projectile_requested.emit(
		origin,
		direction,
		float(_gun.get("damage", 400.0)),
		float(_gun.get("speed", 8.0)),
		float(_gun.get("lifetime_seconds", 6.0))
	)


func take_damage(amount: float) -> void:
	if _dead or amount <= 0.0:
		return
	current_hp = maxf(current_hp - amount, 0.0)
	queue_redraw()
	if current_hp <= 0.0:
		_die()


func _die() -> void:
	_dead = true
	defeated.emit(self)
	queue_free()


func is_defeated() -> bool:
	return _dead


func _draw() -> void:
	var hull := Color(0.62, 0.30, 0.86)
	var glow := Color(1.0, 0.55, 0.42)
	draw_circle(Vector2.ZERO, 1.05, Color(0.16, 0.06, 0.24, 0.9))
	draw_colored_polygon(
		PackedVector2Array(
			[
				Vector2(0.0, -1.0),
				Vector2(1.05, -0.25),
				Vector2(0.78, 0.72),
				Vector2(0.0, 0.45),
				Vector2(-0.78, 0.72),
				Vector2(-1.05, -0.25),
			]
		),
		hull
	)
	draw_circle(Vector2(0.0, -0.15), 0.34, glow)
	draw_circle(Vector2(0.0, -0.15), 0.16, Color(1.0, 0.95, 0.75))
	draw_line(Vector2(-1.05, -0.25), Vector2(-1.45, 0.45), glow, 0.12)
	draw_line(Vector2(1.05, -0.25), Vector2(1.45, 0.45), glow, 0.12)
	if max_hp > 0.0:
		var ratio := clampf(current_hp / max_hp, 0.0, 1.0)
		draw_rect(Rect2(-1.1, -1.45, 2.2, 0.16), Color(0.06, 0.05, 0.1, 0.9))
		draw_rect(Rect2(-1.08, -1.43, 2.16 * ratio, 0.12), Color(1.0, 0.42, 0.34, 0.95))
