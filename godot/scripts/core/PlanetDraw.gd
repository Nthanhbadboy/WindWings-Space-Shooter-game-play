extends Node2D
## Hành tinh vẽ bằng code (vòng sáng + vành đai), lớp gần nhất của parallax.

var base_color := Color("#c98a4b")
var rim_color := Color("#59d8ff")
var radius := 90.0
var has_ring := true
var _t := 0.0

func _ready() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(position)
	radius = rng.randf_range(60.0, 130.0)
	has_ring = rng.randf() < 0.5

func set_palette(base: Color, rim: Color) -> void:
	base_color = base
	rim_color = rim
	queue_redraw()

func _process(delta: float) -> void:
	_t += delta
	queue_redraw()

func _draw() -> void:
	# thân hành tinh: 3 vòng tròn giả lập gradient cầu
	draw_circle(Vector2.ZERO, radius, base_color.darkened(0.55))
	draw_circle(Vector2(-radius * 0.18, -radius * 0.18), radius * 0.82, base_color.darkened(0.2))
	draw_circle(Vector2(-radius * 0.3, -radius * 0.3), radius * 0.55, base_color)
	# viền khí quyển
	draw_arc(Vector2.ZERO, radius * 1.03, 0, TAU, 48, Color(rim_color, 0.5), 3.0)
	if has_ring:
		# vành đai nghiêng, xoay chậm
		var tilt := 0.45 + 0.05 * sin(_t * 0.3)
		draw_set_transform(Vector2.ZERO, 0.0, Vector2(1.0, tilt))
		draw_arc(Vector2.ZERO, radius * 1.55, 0, TAU, 64, Color(rim_color, 0.35), 6.0)
		draw_arc(Vector2.ZERO, radius * 1.75, 0, TAU, 64, Color(rim_color, 0.18), 3.0)
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
