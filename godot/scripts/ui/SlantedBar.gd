extends Control
## SlantedBar.gd — thanh nghiêng chuẩn WindWings (HP skewX -12°, năng lượng
## skewX -26°): vẽ hình bình hành bằng _draw, mép dốc, viền sáng 2 lớp,
## fill ratio + màu tuỳ chọn. Không texture, không physics, redraw khi đổi.

var ratio := 1.0
var skew: float = float(Balance.UI["hp_skew"])
var fill_a: Color = Balance.UI["hp_fill"]
var fill_b: Color = Color("#8fbf20")
var bg := Color("#12243f")
var rim := Color("#46c6f4")
var pulse_t := 0.0
var pulse := false

func set_ratio(r: float, do_pulse := false) -> void:
	var old := ratio
	ratio = clampf(r, 0.0, 1.0)
	if do_pulse and ratio < old:
		pulse = true
		pulse_t = 0.0
	queue_redraw()

func _process(delta: float) -> void:
	if pulse:
		pulse_t += delta
		if pulse_t > 0.35:
			pulse = false
		queue_redraw()

func _draw() -> void:
	var s := size
	var dx := skew * s.y          # độ nghiêng cạnh
	var pts_bg := PackedVector2Array([
		Vector2(dx, 0), Vector2(s.x, 0), Vector2(s.x - dx, s.y), Vector2(0, s.y),
	])
	# nền
	draw_colored_polygon(pts_bg, bg)
	# fill (cắt theo hình bình hành: tỉ lệ theo chiều ngang)
	if ratio > 0.0:
		var w := (s.x - absf(dx)) * ratio
		var top_r := dx + w
		var bot_r := w
		var fc := fill_a.lerp(fill_b, 1.0 - ratio) if not pulse else Color(1, 1, 1, 0.9).lerp(fill_a, pulse_t / 0.35)
		draw_colored_polygon(PackedVector2Array([
			Vector2(dx, 1.5), Vector2(top_r, 1.5), Vector2(bot_r, s.y - 1.5), Vector2(0, s.y - 1.5),
		]), fc)
		# dải sáng trên fill
		draw_colored_polygon(PackedVector2Array([
			Vector2(dx, 1.5), Vector2(top_r, 1.5), Vector2(top_r - (top_r - dx) * 0.25, s.y * 0.42), Vector2(dx * 0.75, s.y * 0.42),
		]), Color(1, 1, 1, 0.22))
	# viền 2 lớp (rim ngoài sáng, trong tối)
	_pts_outline(pts_bg, rim, 2.0)
	var inner := PackedVector2Array([
		Vector2(dx + 3, 3), Vector2(s.x - 3, 3), Vector2(s.x - dx - 3, s.y - 3), Vector2(3, s.y - 3),
	])
	_pts_outline(inner, Color("#14538c"), 1.5)

func _pts_outline(pts: PackedVector2Array, col: Color, w: float) -> void:
	var n := pts.size()
	for i in n:
		draw_line(pts[i], pts[(i + 1) % n], col, w)
