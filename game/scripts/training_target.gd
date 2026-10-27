class_name TrainingTarget
extends Area2D

signal hit_registered(total_hits: int)

var total_hits := 0
var _flash_seconds := 0.0


func _ready() -> void:
	add_to_group("shootable")
	collision_layer = 4
	collision_mask = 2
	area_entered.connect(_on_area_entered)


func _process(delta: float) -> void:
	if _flash_seconds > 0.0:
		_flash_seconds = maxf(_flash_seconds - delta, 0.0)
		queue_redraw()


func take_damage(_amount: float) -> void:
	# The training beacon has no fabricated HP value; it records successful hits only.
	total_hits += 1
	_flash_seconds = 0.16
	hit_registered.emit(total_hits)
	queue_redraw()


func _on_area_entered(area: Area2D) -> void:
	if area.is_in_group("player"):
		return


func _draw() -> void:
	var glow_alpha := 0.45 if _flash_seconds > 0.0 else 0.18
	draw_circle(Vector2.ZERO, 0.78, Color(0.09, 0.82, 0.95, glow_alpha))
	draw_arc(Vector2.ZERO, 0.61, 0.0, TAU, 48, Color(0.28, 0.88, 1.0, 0.82), 0.035, true)
	draw_arc(Vector2.ZERO, 0.39, 0.0, TAU, 48, Color(0.43, 0.66, 0.99, 0.68), 0.025, true)
	draw_colored_polygon(
		PackedVector2Array(
			[Vector2(0.0, -0.25), Vector2(0.25, 0.0), Vector2(0.0, 0.25), Vector2(-0.25, 0.0)]
		),
		Color(0.92, 0.98, 1.0, 0.94)
	)
