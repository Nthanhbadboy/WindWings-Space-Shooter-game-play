extends "res://scripts/bosses/BossRig.gd"
## QueenWaspRig — ong chúa: thân art pancake, 4 cánh màng vỗ rung (procedural
## sin tần số cao — không dùng anim loop để không đụng AnimationPlayer),
## ngòi chích thò ra khi charge, vương miện ong chúa, râu lắc, sọc bụng.

var wings: Array[Polygon2D] = []
var stinger: Polygon2D
var abdomen: Polygon2D
var ant_l: Line2D
var ant_r: Line2D
var eye_l: Polygon2D
var eye_r: Polygon2D
var pt := 0.0

const WING_COLOR := Color(0.72, 0.92, 1.0, 0.38)

func _build_parts() -> void:
	# 4 cánh (2 trước 2 sau)
	var wpts := PackedVector2Array([Vector2.ZERO, Vector2(70, -34), Vector2(104, 4), Vector2(52, 30)])
	for i in 4:
		var side := -1.0 if i % 2 == 0 else 1.0
		var back := 1.0 if i < 2 else 0.72
		var w := poly("Wing%d" % i, _scaled(wpts, side * back, back), WING_COLOR, Vector2(side * 30.0, -34.0 + (0.0 if i < 2 else 26.0)))
		wings.append(w)
	# bụng (thở)
	abdomen = poly("Abdomen", PackedVector2Array([
		Vector2(-46, 8), Vector2(-40, 58), Vector2(0, 84), Vector2(40, 58), Vector2(46, 8),
	]), Color("#c94fa8"))
	# sọc bụng
	for i in 3:
		line_part("Stripe%d" % i, PackedVector2Array([Vector2(-36 + i * 5, 22.0 + i * 18.0), Vector2(36 - i * 5, 22.0 + i * 18.0)]), Color("#3a0d30", 0.8), 8.0)
	# ngòi chích (thò ra khi charge)
	stinger = poly("Stinger", PackedVector2Array([Vector2(-9, 0), Vector2(9, 0), Vector2(0, 64)]), Color("#ffd23c"))
	stinger.position = Vector2(0, 76)
	stinger.scale = Vector2(1, 0.35)
	# thân chính — art pancake
	sprite_part("BodyArt", "res://assets/bosses/boss_pancake.png", 200.0, Vector2(0, -18))
	# vương miện
	poly("Crown", PackedVector2Array([
		Vector2(-34, -8), Vector2(-24, -34), Vector2(-12, -16), Vector2(0, -40),
		Vector2(12, -16), Vector2(24, -34), Vector2(34, -8),
	]), Color("#ffec22"), Vector2(0, -84))
	# mắt kép
	eye_l = circle_part("EyeL", 15.0, Color("#ff3c5a"), Vector2(-26, -30))
	eye_r = circle_part("EyeR", 15.0, Color("#ff3c5a"), Vector2(26, -30))
	circle_part("PupilL", 6.0, Color("#2a0a14"), Vector2(-26, -30))
	circle_part("PupilR", 6.0, Color("#2a0a14"), Vector2(26, -30))
	# râu
	ant_l = line_part("AntL", PackedVector2Array([Vector2.ZERO, Vector2(-14, -30), Vector2(-30, -42)]), Color("#ffec22", 0.9), 4.0, Vector2(-18, -66))
	ant_r = line_part("AntR", PackedVector2Array([Vector2.ZERO, Vector2(14, -30), Vector2(30, -42)]), Color("#ffec22", 0.9), 4.0, Vector2(18, -66))

func _scaled(pts: PackedVector2Array, sx: float, sy: float) -> PackedVector2Array:
	var out := PackedVector2Array()
	for p in pts:
		out.append(Vector2(p.x * sx, p.y * sy))
	return out

func _add_charge_tracks(a: Animation) -> void:
	_track3(a, "Body/Stinger:scale", [0.0, 0.55], [Vector2(1, 0.35), Vector2(1.25, 1.15)])
	_track3(a, "Body/Abdomen:scale", [0.0, 0.55], [Vector2.ONE, Vector2(1.1, 1.14)])

func _add_fire_tracks(a: Animation) -> void:
	_track3(a, "Body/Stinger:scale", [0.0, 0.07, 0.32], [Vector2(1.25, 1.15), Vector2(1.4, 1.5), Vector2(1, 0.35)])
	_track3(a, "Body/Abdomen:scale", [0.0, 0.07, 0.32], [Vector2(1.1, 1.14), Vector2(0.92, 0.86), Vector2.ONE])

func _process(delta: float) -> void:
	pt += delta
	# cánh vỗ rung tần số cao (procedural — ONG THẬT phải rung, không đập chậm)
	var buzz := sin(pt * 46.0)
	var amp := 0.5 if (boss == null or not boss.tele_active) else 0.66
	for i in wings.size():
		var side := -1.0 if i % 2 == 0 else 1.0
		wings[i].rotation = side * (0.25 + buzz * amp * (1.0 if i < 2 else 0.8))
	# bụng thở
	if boss == null or not boss.tele_active:
		abdomen.scale = Vector2.ONE * (1.0 + 0.05 * sin(pt * 2.6))
	# râu lắc
	ant_l.rotation = sin(pt * 3.1) * 0.18
	ant_r.rotation = -sin(pt * 3.1 + 0.7) * 0.18
	# mắt liếc theo người chơi
	var look := (player_local() - Vector2(0, -30)).normalized() * 5.0
	eye_l.position = Vector2(-26, -30) + look * 0.6
	eye_r.position = Vector2(26, -30) + look * 0.6
	parts["PupilL"].position = Vector2(-26, -30) + look
	parts["PupilR"].position = Vector2(26, -30) + look
	# cuồng nộ: mắt rực đỏ
	if boss != null and boss.enraged:
		var g := 0.75 + 0.25 * sin(pt * 10.0)
		eye_l.modulate = Color(1.6, 0.6, 0.6, g)
		eye_r.modulate = Color(1.6, 0.6, 0.6, g)
