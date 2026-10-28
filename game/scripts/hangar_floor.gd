extends Node2D

## Hangar backdrop: a slow drifting starfield and a landing pad ring, drawn with
## primitives so the hangar never depends on art being delivered.

var _age := 0.0
var _stars: Array[Vector3] = []


func _ready() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 0x48414E47
	for _index in range(70):
		_stars.append(
			Vector3(rng.randf_range(-5.2, 5.2), rng.randf_range(-5.0, 5.0), rng.randf_range(0.1, 0.6))
		)
	z_index = -5


func _process(delta: float) -> void:
	_age += delta
	queue_redraw()


func _draw() -> void:
	draw_rect(Rect2(-6.0, -5.5, 12.0, 11.0), Color(0.012, 0.021, 0.062))
	for star in _stars:
		var y := fposmod(star.y + _age * star.z * 0.35 + 5.0, 10.0) - 5.0
		draw_circle(Vector2(star.x, y), 0.02 + star.z * 0.02, Color(0.6, 0.8, 1.0, 0.5))
	draw_arc(Vector2(0.0, 1.35), 1.55, 0.0, TAU, 48, Color(0.20, 0.55, 0.85, 0.35), 0.03, true)
	draw_arc(Vector2(0.0, 1.35), 1.15, 0.0, TAU, 40, Color(0.20, 0.55, 0.85, 0.22), 0.02, true)
	for index in range(3):
		var alpha := 0.10 + 0.06 * sin(_age * 1.4 + float(index))
		draw_arc(
			Vector2(0.0, 1.35), 1.35 + float(index) * 0.12, 0.0, TAU, 48, Color(0.3, 0.7, 1.0, alpha), 0.02, true
		)
