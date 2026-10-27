class_name WavePickup
extends Area2D

signal collected(item_index: int)

var item_index := 1
var item_name := "+1Level"
var fall_speed := 2.4
var _age := 0.0


func configure(index: int, display_name: String, spawn_position: Vector2) -> void:
	item_index = index
	item_name = display_name
	position = spawn_position


func _ready() -> void:
	add_to_group("pickups")
	collision_layer = 16
	collision_mask = 1
	area_entered.connect(_on_area_entered)
	queue_redraw()


func _physics_process(delta: float) -> void:
	_age += delta
	position.y += fall_speed * delta
	position.x += sin(_age * 1.5) * 0.22 * delta
	if position.y > 12.0 or _age > 24.0:
		queue_free()


func _on_area_entered(area: Area2D) -> void:
	if area.is_in_group("player"):
		collected.emit(item_index)
		queue_free()


func _draw() -> void:
	var color := Color(0.38, 0.93, 0.78)
	if item_index == 2:
		color = Color(1.0, 0.73, 0.36)
	elif item_index == 3:
		color = Color(0.42, 0.88, 1.0)
	elif item_index >= 100:
		color = Color(0.77, 0.58, 1.0)
	var diamond := PackedVector2Array(
		[Vector2(0.0, -0.28), Vector2(0.28, 0.0), Vector2(0.0, 0.28), Vector2(-0.28, 0.0)]
	)
	draw_colored_polygon(diamond, color)
	draw_polyline(
		PackedVector2Array(
			[
				Vector2(0.0, -0.28),
				Vector2(0.28, 0.0),
				Vector2(0.0, 0.28),
				Vector2(-0.28, 0.0),
				Vector2(0.0, -0.28)
			]
		),
		Color(0.92, 0.99, 1.0, 0.94),
		0.035,
		true
	)
	draw_circle(Vector2.ZERO, 0.065, Color(0.04, 0.09, 0.18, 0.95))
