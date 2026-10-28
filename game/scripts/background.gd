extends Node2D

const FIELD_RECT := Rect2(-24.0, -28.0, 48.0, 56.0)
const VIEW_RECT := Rect2(-5.4, -9.6, 10.8, 19.2)
const STAR_COUNT := 96

var _stars: Array[Vector3] = []
var _star_sizes: Array[float] = []
var _star_alpha: Array[float] = []
var _rng := RandomNumberGenerator.new()
var _scroll_offset := 0.0


func _ready() -> void:
	_rng.seed = 0x57494E44
	for index in STAR_COUNT:
		_stars.append(
			Vector3(
				_rng.randf_range(FIELD_RECT.position.x, FIELD_RECT.end.x),
				_rng.randf_range(FIELD_RECT.position.y, FIELD_RECT.end.y),
				_rng.randf_range(0.18, 0.95)
			)
		)
		_star_sizes.append(_rng.randf_range(0.012, 0.04))
		_star_alpha.append(_rng.randf_range(0.2, 0.86))
	queue_redraw()


func _process(delta: float) -> void:
	_scroll_offset = fposmod(_scroll_offset + delta * 0.42, 56.0)
	queue_redraw()


func _draw() -> void:
	draw_rect(FIELD_RECT, Color(0.012, 0.021, 0.062), true)
	# Original procedural nebula bands: the palette and geometry are newly drawn.
	draw_circle(Vector2(-3.8, -4.5), 5.0, Color(0.06, 0.14, 0.31, 0.12))
	draw_circle(Vector2(4.2, 3.5), 4.0, Color(0.11, 0.08, 0.31, 0.10))
	draw_rect(VIEW_RECT, Color(0.025, 0.046, 0.12, 0.24), true)

	for index in _stars.size():
		var star := _stars[index]
		var y := fposmod(star.y + _scroll_offset * star.z + 28.0, 56.0) - 28.0
		var alpha := _star_alpha[index]
		var size := _star_sizes[index]
		var point := Vector2(star.x, y)
		draw_circle(point, size, Color(0.53, 0.78, 1.0, alpha))
		if star.z > 0.72:
			draw_line(
				point, point + Vector2(0.0, 0.12), Color(0.35, 0.70, 1.0, alpha * 0.38), 0.025
			)

	# The fine frame keeps attention on the ship without copying an original screen.
	draw_rect(VIEW_RECT, Color(0.24, 0.71, 0.94, 0.2), false, 0.025)
