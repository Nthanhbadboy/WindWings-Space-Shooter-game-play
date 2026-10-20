extends "res://scripts/bosses/BossRig.gd"
## VoidTyrantRig — sứa: chuông dome + viền sáng + 6 xúc tu Line2D uốn sine
## (biên độ tăng dần về ngọn, nhịp đập theo chuông), 2 mắt đuổi người chơi,
## 2 tua miệng dày. Khi charge: xúc tu co rút giơ lên; fire: quật xuống.

var tentacles: Array[Line2D] = []
var oral_arms: Array[Line2D] = []
var tent_base: Array[Vector2] = []
var eye_l: Polygon2D
var eye_r: Polygon2D
var bell_glow: Polygon2D
var pt := 0.0

const BELL_R := 92.0
const BELL_COLOR := Color("#7a3ce0")
const BELL_HI := Color("#b18cff")
const TENT_COLOR := Color("#9b5cff")
const EYE_COLOR := Color("#ffe36a")

func _build_parts() -> void:
	# tua miệng (sau chuông)
	for i in 2:
		var l := line_part("OralArm%d" % i, PackedVector2Array([Vector2.ZERO, Vector2(0, 60)]), Color("#c9a0ff", 0.9), 12.0)
		l.position = Vector2(-16.0 + i * 32.0, BELL_R * 0.42)
		oral_arms.append(l)
	# xúc tu: 6 tua, mỗi tua 6 đốt
	for i in 6:
		var pts := PackedVector2Array()
		for j in 6:
			pts.append(Vector2(0, j * 30.0))
		var l := line_part("Tentacle%d" % i, pts, Color(TENT_COLOR, 0.85), 7.0 - i % 2 * 2.0)
		var bx := -70.0 + float(i) * 28.0
		l.position = Vector2(bx, BELL_R * 0.5)
		tent_base.append(Vector2(bx, BELL_R * 0.5))
		tentacles.append(l)
	# chuông sứa (dome)
	var bell_pts := PackedVector2Array()
	for i in 25:
		var a := PI + TAU * 0.5 * float(i) / 24.0
		bell_pts.append(Vector2(cos(a), sin(a) * 0.92) * BELL_R)
	bell_pts.append(Vector2(BELL_R * 0.92, BELL_R * 0.42))
	bell_pts.append(Vector2(-BELL_R * 0.92, BELL_R * 0.42))
	poly("Bell", bell_pts, BELL_COLOR)
	# vòm sáng trên chuông
	var hi := PackedVector2Array()
	for i in 17:
		var a := PI * 1.1 + PI * 0.55 * float(i) / 16.0
		hi.append(Vector2(cos(a), sin(a) * 0.9) * BELL_R * 0.72)
	poly("BellHi", hi, Color(BELL_HI, 0.5))
	# lõi phát sáng (điệu theo charge)
	bell_glow = circle_part("BellGlow", 26.0, Color("#e3c8ff", 0.55), Vector2(0, -18))
	# mắt
	eye_l = circle_part("EyeL", 13.0, EYE_COLOR, Vector2(-30, -6))
	eye_r = circle_part("EyeR", 13.0, EYE_COLOR, Vector2(30, -6))
	circle_part("PupilL", 5.0, Color("#2a0a4d"), Vector2(-30, -6))
	circle_part("PupilR", 5.0, Color("#2a0a4d"), Vector2(30, -6))

func _add_charge_tracks(a: Animation) -> void:
	# gồng: chuông phình, lõi sáng rực
	_track3(a, "Body/BellGlow:scale", [0.0, 0.55], [Vector2.ONE, Vector2(2.1, 2.1)])
	_track3(a, "Body/BellGlow:modulate", [0.0, 0.55], [Color(1, 1, 1, 0.55), Color(1.6, 1.4, 2.0, 1.0)])

func _add_fire_tracks(a: Animation) -> void:
	_track3(a, "Body/BellGlow:scale", [0.0, 0.08, 0.32], [Vector2(2.1, 2.1), Vector2(2.6, 2.6), Vector2.ONE])
	_track3(a, "Body/BellGlow:modulate", [0.0, 0.08, 0.32], [Color(1.6, 1.4, 2, 1), Color(2.2, 2.2, 2.6, 1), Color(1, 1, 1, 0.55)])

func _process(delta: float) -> void:
	pt += delta
	# nhịp đập chuông
	var beat := sin(pt * 2.3)
	var pulse := 1.0 + 0.1 * beat
	if parts.has("Bell"):
		parts["Bell"].scale = Vector2(1.0 / pulse, pulse)
	# trạng thái charge/fire ảnh hưởng xúc tu
	var raise := 0.0
	var tele_prog := 0.0
	if boss != null and boss.tele_active:
		tele_prog = clampf(boss.tele_t / boss.tele_dur, 0.0, 1.0)
		raise = tele_prog
	# xúc tu sine IK
	for i in tentacles.size():
		var l := tentacles[i]
		var pts := l.points
		for j in pts.size():
			var f := float(j) / float(pts.size() - 1)
			var amp := (5.0 + f * 26.0) * pulse * (1.0 - raise * 0.65)
			var y := f * 148.0 * (1.0 - raise * 0.5)
			pts[j] = Vector2(sin(pt * 2.2 + float(i) * 0.9 + f * 2.4) * amp, y)
		l.points = pts
		l.position = tent_base[i] + Vector2(0, -raise * 26.0)
	# tua miệng
	for i in oral_arms.size():
		var l := oral_arms[i]
		var pts := l.points
		for j in pts.size():
			var f := float(j)
			pts[j] = Vector2(sin(pt * 1.7 + float(i) * 2.1 + f * 0.7) * (4.0 + f * 5.0) * (1.0 - raise * 0.5), f * 26.0 * (1.0 + beat * 0.08))
		l.points = pts
	# mắt đuổi người chơi
	var pl := player_local()
	var look := (pl - Vector2(0, -6)).normalized() * 7.0
	eye_l.position = Vector2(-30, -6) + look
	eye_r.position = Vector2(30, -6) + look
	if parts.has("PupilL"):
		parts["PupilL"].position = Vector2(-30, -6) + look * 1.5
		parts["PupilR"].position = Vector2(30, -6) + look * 1.5
	# lõi sáng nhấp nháy khi cuồng nộ
	if boss != null and boss.enraged:
		bell_glow.modulate = Color(1.5, 0.7, 0.7, 0.8 + 0.2 * sin(pt * 9.0))
