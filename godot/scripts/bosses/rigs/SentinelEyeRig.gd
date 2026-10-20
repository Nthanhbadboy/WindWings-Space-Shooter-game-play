extends "res://scripts/bosses/BossRig.gd"
## SentinelEyeRig — mắt thần vệ tinh: cầu mắt (củng mạc + mống + đồng tử)
## procedural đuổi người chơi; mi trên/dưới ĐÓNG KẸT khi charge, MỞ TOÁC khi
## fire; 2 vành quỹ đạo Line2D xoay ngược chiều + 6 khối vệ tinh bay theo;
## tia quét đỏ ngắm thẳng trong lúc telegraph đòn định hướng.

var ring1: Line2D
var ring2: Line2D
var sats: Array[Polygon2D] = []
var lid_top: Polygon2D
var lid_bottom: Polygon2D
var iris: Polygon2D
var pupil: Polygon2D
var iris_glow: Polygon2D
var scan: Line2D
var shell_l: Polygon2D
var shell_r: Polygon2D
var rivets: Array[Polygon2D] = []
var pt := 0.0
var lid_prog := 0.0
var last_shots := -1
var open_snap := 0.0

const SCLERA_R := 78.0

func _build_parts() -> void:
	# vành quỹ đạo sau
	ring2 = line_part("Ring2", ring_points(148.0, 56), Color("#2f9fe0", 0.5), 3.0)
	ring1 = line_part("Ring1", ring_points(118.0, 48), Color("#46c6f4", 0.7), 4.0)
	# 6 khối vệ tinh trên 2 vành
	for i in 6:
		sats.append(poly("Sat%d" % i, PackedVector2Array([
			Vector2(-7, -7), Vector2(7, -7), Vector2(7, 7), Vector2(-7, 7),
		]), Color("#8ad4ff") if i % 2 == 0 else Color("#ffb700")))
	# giáp vỏ hai bên
	shell_l = poly("ShellL", PackedVector2Array([
		Vector2(-118, -30), Vector2(-84, -66), Vector2(-70, 0), Vector2(-84, 66), Vector2(-118, 30),
	]), Color("#22415e"))
	shell_r = poly("ShellR", PackedVector2Array([
		Vector2(118, -30), Vector2(84, -66), Vector2(70, 0), Vector2(84, 66), Vector2(118, 30),
	]), Color("#22415e"))
	for i in 4:
		rivets.append(circle_part("Rivet%d" % i, 4.0, Color("#8fb8dc"), Vector2((-1.0 if i < 2 else 1.0) * 96.0, -34.0 + float(i % 2) * 68.0)))
	# củng mạc
	circle_part("Sclera", SCLERA_R, Color("#dff2ff"))
	iris_glow = circle_part("IrisGlow", 52.0, Color("#4de1ff", 0.35))
	iris = circle_part("Iris", 44.0, Color("#1d8fd0"))
	pupil = circle_part("Pupil", 19.0, Color("#04101e"))
	circle_part("Glint", 7.0, Color(1, 1, 1, 0.9), Vector2(-14, -16))
	# mi mắt (nửa đĩa, đóng từ trên/xuống)
	var lid_pts := PackedVector2Array()
	for i in 21:
		var a := PI * float(i) / 20.0
		lid_pts.append(Vector2(cos(a), -sin(a)) * (SCLERA_R + 10.0))
	lid_pts.append(Vector2(-(SCLERA_R + 10.0), -26.0))
	lid_pts.append(Vector2(SCLERA_R + 10.0, -26.0))
	lid_top = poly("LidTop", lid_pts, Color("#2c5578"), Vector2(0, -SCLERA_R - 30.0))
	var lid_b := PackedVector2Array()
	for i in 21:
		var a := PI * float(i) / 20.0
		lid_b.append(Vector2(cos(a), sin(a)) * (SCLERA_R + 10.0))
	lid_b.append(Vector2(-(SCLERA_R + 10.0), 26.0))
	lid_b.append(Vector2(SCLERA_R + 10.0, 26.0))
	lid_bottom = poly("LidBottom", lid_b, Color("#2c5578"), Vector2(0, SCLERA_R + 30.0))
	line_part("LidLineT", PackedVector2Array([Vector2(-(SCLERA_R + 8), 0), Vector2(SCLERA_R + 8, 0)]), Color("#46c6f4", 0.9), 3.0, Vector2(0, -SCLERA_R - 30.0))
	# tia quét (procedural bật khi telegraph đòn định hướng)
	scan = line_part("Scan", PackedVector2Array([Vector2.ZERO, Vector2(0, 900)]), Color("#ff3c5a", 0.0), 6.0)

func _add_charge_tracks(a: Animation) -> void:
	_track3(a, "Body/IrisGlow:scale", [0.0, 0.55], [Vector2.ONE, Vector2(1.7, 1.7)])
	_track3(a, "Body/IrisGlow:modulate", [0.0, 0.55], [Color(1, 1, 1, 0.35), Color(1.8, 1.2, 1.2, 0.9)])

func _add_fire_tracks(a: Animation) -> void:
	_track3(a, "Body/IrisGlow:scale", [0.0, 0.08, 0.32], [Vector2(1.7, 1.7), Vector2(2.2, 2.2), Vector2.ONE])
	_track3(a, "Body/IrisGlow:modulate", [0.0, 0.08, 0.32], [Color(1.8, 1.2, 1.2, 0.9), Color(2.4, 2.4, 2.8, 1), Color(1, 1, 1, 0.35)])

func _process(delta: float) -> void:
	pt += delta
	if boss != null and boss.shots_fired != last_shots:
		last_shots = boss.shots_fired
		open_snap = 1.0
	open_snap = maxf(0.0, open_snap - delta * 3.5)
	# vành xoay ngược chiều
	ring1.rotation += delta * 0.8
	ring2.rotation -= delta * 1.25
	for i in sats.size():
		var r := 118.0 if i % 2 == 0 else 148.0
		var w := 0.8 if i % 2 == 0 else -1.25
		var a := pt * w + TAU * float(i) / 6.0
		sats[i].position = Vector2(cos(a), sin(a)) * r
		sats[i].rotation = a * 2.0
	# mục tiêu nhìn
	var pl := player_local()
	var look := pl.normalized() * minf(pl.length() * 0.12, 24.0)
	iris.position = look
	pupil.position = look * 1.15
	parts["Glint"].position = Vector2(-14, -16) + look
	iris_glow.position = look
	# đồng tử co giãn: charge = co nhỏ tích tụ, fire = nở
	var prog := 0.0
	if boss != null and boss.tele_active:
		prog = clampf(boss.tele_t / boss.tele_dur, 0.0, 1.0)
	var ps := 1.0 - prog * 0.45 + open_snap * 0.5
	pupil.scale = Vector2(ps, ps)
	# mi mắt: mở khi idle, KÉP KÍN khi charge, mở toác khi fire
	var lid_close := prog - open_snap * 1.4
	lid_prog = clampf(lid_close, -0.35, 1.0)
	var travel := SCLERA_R + 30.0
	lid_top.position = Vector2(0, -travel + lid_prog * travel)
	lid_bottom.position = Vector2(0, travel - lid_prog * travel)
	parts["LidLineT"].position = lid_top.position
	# tia quét đỏ khi charge đòn định hướng
	var directional := false
	if boss != null and boss.tele_active:
		directional = String(boss.tele_pattern.get("kind", "")) in ["beam_row", "aimed", "dash", "twin", "core", "slam", "spikes"]
	if directional:
		scan.visible = true
		scan.default_color = Color("#ff3c5a", 0.15 + prog * 0.5)
		scan.points = PackedVector2Array([Vector2.ZERO, Vector2(0, clampf(pl.length(), 40.0, 1400.0))])
		scan.rotation = pl.angle() - PI * 0.5
	else:
		scan.visible = false
	# cuồng nộ: tròng đỏ
	if boss != null and boss.enrage_active:
		iris.color = Color("#d01d3f")
		iris_glow.color = Color("#ff3c5a", 0.4 + 0.2 * sin(pt * 9.0))
	for i in rivets.size():
		rivets[i].modulate = Color(1, 1, 1, 0.6 + 0.4 * sin(pt * 2.0 + float(i)))
