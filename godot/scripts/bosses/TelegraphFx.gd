extends Node2D
## TelegraphFx.gd — cảnh báo trước đòn boss (HARD RULE: sát thương chỉ xuất
## hiện SAU khi telegraph kết thúc). Hai dạng: vòng tròn nở (đạn toả) và
## tia ngắm thẳng tới người chơi (đòn định hướng), nét đứt, sáng dần.

const DIRECTIONAL := ["aimed", "dash", "beam_row", "slam", "twin", "spikes", "core"]
const SEG := 36

var active := false
var progress := 0.0
var kind := ""
var color := Color("#ffa03c")
var boss_ref: Node2D = null
var aim_local := Vector2.ZERO

func begin(pat: Dictionary, boss: Node2D, col: Color) -> void:
	boss_ref = boss
	kind = String(pat.get("kind", ""))
	color = col
	active = true
	progress = 0.0
	visible = true
	z_index = 9
	queue_redraw()

func finish() -> void:
	active = false
	visible = false
	queue_redraw()

func set_progress(p: float) -> void:
	progress = clampf(p, 0.0, 1.0)
	queue_redraw()

func _process(_delta: float) -> void:
	if active and boss_ref != null and boss_ref.run != null:
		aim_local = to_local(boss_ref.run.player_position())
		if kind in DIRECTIONAL:
			queue_redraw()

func _draw() -> void:
	if not active:
		return
	var a := 0.25 + 0.6 * progress
	if kind in DIRECTIONAL:
		# tia ngắm nét đứt tới người chơi
		var dir := aim_local.normalized()
		var length := aim_local.length()
		var dash := 26.0
		var d := 0.0
		while d < length:
			var s := dir * d
			var e := dir * minf(d + dash * 0.55, length)
			draw_line(s, e, Color(color, a), 5.0)
			d += dash
		draw_arc(aim_local, 20.0 + 8.0 * sin(progress * 14.0), 0, TAU, 20, Color(color, a * 0.9), 3.0)
		draw_circle(aim_local, 4.0, Color(1, 1, 1, a))
	else:
		# vòng tròn nở
		var r := lerpf(70.0, 300.0, progress)
		for i in SEG:
			var a0 := TAU * float(i) / float(SEG)
			var a1 := a0 + TAU / float(SEG) * 0.5
			draw_arc(Vector2.ZERO, r, a0, a1, 3, Color(color, a), 6.0)
		draw_arc(Vector2.ZERO, r * 0.55, 0, TAU, 30, Color(color, a * 0.45), 3.0)
		if progress > 0.8:
			draw_circle(Vector2.ZERO, 240.0 * (progress - 0.8) * 5.0, Color(color, (progress - 0.8) * 0.7))
