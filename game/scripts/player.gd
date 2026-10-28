class_name Player
extends Area2D

signal shot_requested(origin: Vector2, damage: float)
signal health_changed(current: float, maximum: float)
signal damage_taken(amount: float, remaining: float)
signal died

const CONFIRMED_BASE_HP := 2500.0
const CONFIRMED_HIT_INVULNERABILITY_SECONDS := 3.0

@export var move_speed := 9.0
@export var smoothing_rate := 14.0

var current_health := CONFIRMED_BASE_HP
var maximum_health := CONFIRMED_BASE_HP
var shot_damage := 0.0
var fire_period_seconds := 0.24
var movement_bounds := Rect2(-4.8, -8.4, 9.6, 16.5)

var _dragging := false
var _move_target := Vector2.ZERO
var _fire_elapsed := 0.0
var _invulnerability_elapsed := 0.0
var _is_dead := false


func _ready() -> void:
	add_to_group("player")
	collision_layer = 1
	collision_mask = 28
	area_entered.connect(_on_area_entered)
	_move_target = global_position
	health_changed.emit(current_health, maximum_health)
	queue_redraw()


func configure_weapon(damage: float, fire_period: float) -> void:
	shot_damage = maxf(damage, 0.0)
	fire_period_seconds = maxf(fire_period, 0.05)


func configure_health(base_hp: float) -> void:
	maximum_health = maxf(base_hp, 1.0)
	current_health = maximum_health
	health_changed.emit(current_health, maximum_health)
	queue_redraw()


func set_movement_bounds(bounds: Rect2) -> void:
	movement_bounds = bounds
	global_position = _clamp_to_bounds(global_position)
	_move_target = _clamp_to_bounds(_move_target)


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventScreenTouch:
		if event.pressed:
			_dragging = true
			_set_drag_target(event.position)
		else:
			_dragging = false
	elif event is InputEventScreenDrag:
		_set_drag_target(event.position)
	elif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		_dragging = event.pressed
		if event.pressed:
			_set_drag_target(event.position)
	elif event is InputEventMouseMotion and (event.button_mask & MOUSE_BUTTON_MASK_LEFT) != 0:
		_set_drag_target(event.position)


func _physics_process(delta: float) -> void:
	var keyboard_direction := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	if keyboard_direction.length_squared() > 0.0:
		_dragging = false
		global_position += keyboard_direction * move_speed * delta
	elif _dragging:
		var blend := 1.0 - exp(-smoothing_rate * delta)
		global_position = global_position.lerp(_move_target, blend)
	global_position = _clamp_to_bounds(global_position)


func _process(delta: float) -> void:
	if _invulnerability_elapsed > 0.0:
		_invulnerability_elapsed = maxf(_invulnerability_elapsed - delta, 0.0)
		queue_redraw()
	if _is_dead:
		return
	_fire_elapsed += delta
	if _fire_elapsed >= fire_period_seconds:
		# Do not backfill missed shots after a stall; one input tick produces at most one shot.
		_fire_elapsed = fposmod(_fire_elapsed, fire_period_seconds)
		shot_requested.emit(global_position + Vector2(0.0, -0.58), shot_damage)


func take_damage(amount: float) -> bool:
	if _is_dead or _invulnerability_elapsed > 0.0:
		return false
	var applied := maxf(amount, 0.0)
	current_health = maxf(current_health - applied, 0.0)
	_invulnerability_elapsed = CONFIRMED_HIT_INVULNERABILITY_SECONDS
	damage_taken.emit(applied, current_health)
	health_changed.emit(current_health, maximum_health)
	queue_redraw()
	if current_health <= 0.0:
		_is_dead = true
		died.emit()
	return true


func _set_drag_target(screen_position: Vector2) -> void:
	var world_position := get_viewport().get_canvas_transform().affine_inverse() * screen_position
	_move_target = _clamp_to_bounds(world_position)


func _clamp_to_bounds(point: Vector2) -> Vector2:
	return Vector2(
		clampf(point.x, movement_bounds.position.x, movement_bounds.end.x),
		clampf(point.y, movement_bounds.position.y, movement_bounds.end.y)
	)


func _on_area_entered(area: Area2D) -> void:
	if area.is_in_group("enemies"):
		var contact_damage := float(area.get("contact_damage"))
		if contact_damage > 0.0:
			take_damage(contact_damage)


func _draw() -> void:
	var flicker := 1.0
	if _invulnerability_elapsed > 0.0 and int(Time.get_ticks_msec() / 90) % 2 == 0:
		flicker = 0.42
	var hull := Color(0.30, 0.88, 1.0, flicker)
	var highlight := Color(0.90, 0.98, 1.0, flicker)
	var accent := Color(1.0, 0.72, 0.31, flicker)

	# All ship shapes are original vector artwork created in GDScript.
	draw_colored_polygon(
		PackedVector2Array(
			[
				Vector2(0.0, -0.62),
				Vector2(0.46, 0.30),
				Vector2(0.16, 0.19),
				Vector2(0.0, 0.42),
				Vector2(-0.16, 0.19),
				Vector2(-0.46, 0.30)
			]
		),
		hull
	)
	draw_colored_polygon(
		PackedVector2Array([Vector2(0.0, -0.43), Vector2(0.105, 0.10), Vector2(-0.105, 0.10)]),
		highlight
	)
	draw_colored_polygon(
		PackedVector2Array([Vector2(-0.31, 0.25), Vector2(-0.20, 0.57), Vector2(-0.08, 0.32)]),
		accent
	)
	draw_colored_polygon(
		PackedVector2Array([Vector2(0.31, 0.25), Vector2(0.20, 0.57), Vector2(0.08, 0.32)]), accent
	)
	draw_line(
		Vector2(-0.10, 0.50), Vector2(0.0, 0.72), Color(0.28, 0.74, 1.0, flicker * 0.75), 0.075
	)
	draw_line(
		Vector2(0.10, 0.50), Vector2(0.0, 0.72), Color(0.28, 0.74, 1.0, flicker * 0.75), 0.075
	)
