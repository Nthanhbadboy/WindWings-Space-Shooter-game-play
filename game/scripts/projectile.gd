class_name Projectile
extends Area2D

signal near_miss

enum Faction { PLAYER, ENEMY }

var faction: Faction = Faction.PLAYER
var direction := Vector2.UP
var speed := 18.0
var damage := 0.0
var lifetime_seconds := 3.0
var target: Node2D

var _age := 0.0
var _near_miss_registered := false
var _previous_position := Vector2.ZERO


func _ready() -> void:
	add_to_group("projectiles")
	if faction == Faction.PLAYER:
		collision_layer = 2
		collision_mask = 4
	else:
		add_to_group("enemy_projectiles")
		collision_layer = 8
		collision_mask = 1
	area_entered.connect(_on_area_entered)
	_previous_position = global_position
	queue_redraw()


func _physics_process(delta: float) -> void:
	_age += delta
	_previous_position = global_position
	global_position += direction.normalized() * speed * delta
	if faction == Faction.ENEMY:
		_check_near_miss()
	if _age >= lifetime_seconds or absf(global_position.x) > 20.0 or absf(global_position.y) > 30.0:
		queue_free()


func _on_area_entered(area: Area2D) -> void:
	if faction == Faction.PLAYER and area.has_method("take_damage"):
		if area.is_in_group("shootable") or area.is_in_group("enemies"):
			area.take_damage(damage)
			queue_free()
	elif faction == Faction.ENEMY and area.is_in_group("player"):
		if area.has_method("take_damage"):
			area.take_damage(damage)
		queue_free()


func _check_near_miss() -> void:
	if _near_miss_registered or not is_instance_valid(target):
		return
	var crossed_player_y := (
		direction.y > 0.0
		and _previous_position.y < target.global_position.y
		and global_position.y >= target.global_position.y
	)
	if not crossed_player_y:
		return
	var horizontal_gap := absf(global_position.x - target.global_position.x)
	if horizontal_gap > 0.34 and horizontal_gap < 1.35:
		_near_miss_registered = true
		near_miss.emit()


func _draw() -> void:
	if faction == Faction.PLAYER:
		draw_line(Vector2(0.0, 0.16), Vector2(0.0, -0.22), Color(0.45, 0.95, 1.0, 0.96), 0.12)
		draw_circle(Vector2.ZERO, 0.075, Color(0.84, 1.0, 1.0, 0.95))
	else:
		draw_circle(Vector2.ZERO, 0.105, Color(1.0, 0.40, 0.30, 0.95))
		draw_circle(Vector2.ZERO, 0.045, Color(1.0, 0.88, 0.58, 1.0))
