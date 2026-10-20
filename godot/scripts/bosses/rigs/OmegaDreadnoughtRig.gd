extends "res://scripts/bosses/BossRig.gd"
## OmegaDreadnoughtRig — trùm cuối: thân art dreadnought; 2 pháo tay
## (Node2D xoay ngắm procedural + nòng giật lùi khi fire); 4 tấm cánh xoè
## theo pha (mỗi pha một thế cánh — boss "lột xác" thấy rõ); lõi phản lực
## scale+đỏ dần theo tiến trình telegraph, nổ trắng khi fire; ống xả xung
## nhịp; đèn thân nhấp nháy so le.

var arm_l: Node2D
var arm_r: Node2D
var barrel_l: Polygon2D
var barrel_r: Polygon2D
var wings: Array[Polygon2D] = []
var wing_base: Array[Vector2] = []
var core: Polygon2D
var core_halo: Polygon2D
var vents: Array[Line2D] = []
var hull_lights: Array[Polygon2D] = []
var engine_a: Polygon2D
var engine_b: Polygon2D
var pt := 0.0
var recoil_t := 0.0
var last_shots := -1
var spread := 1.0
var core_flash := 0.0

const HULL := Color("#3b2a63")
const TRIM := Color("#b07bff")

func _build_parts() -> void:
	# 4 tấm cánh (sau thân) — xếp lớp xòè
	var wpts := PackedVector2Array([Vector2(0, -18), Vector2(96, -34), Vector2(112, 8), Vector2(70, 34), Vector2(0, 20)])
	for i in 4:
		var side := -1.0 if i % 2 == 0 else 1.0
		var back := 0.72 if i >= 2 else 1.0
		var w := poly("WingSeg%d" % i, _mirror(wpts, side), Color(HULL, 0.96) if back == 1.0 else Color("#2c1f4d", 0.96), Vector2(side * 44.0, -14.0 + (0.0 if back == 1.0 else 44.0)))
		w.scale = Vector2(back, back)
		wings.append(w)
		wing_base.append(w.position)
	# viền năng lượng trên cánh
	for i in 4:
		var side := -1.0 if i % 2 == 0 else 1.0
		line_part("WingTrim%d" % i, PackedVector2Array([Vector2(side * 52.0, -12.0), Vector2(side * 130.0, -20.0)]), Color(TRIM, 0.8), 3.0)
	# thân chính — art dreadnought
	sprite_part("HullArt", "res://assets/bosses/boss_dreadnought.png", 240.0, Vector2(0, -6))
	# giáp ngực chữ V
	poly("Chest", PackedVector2Array([Vector2(-52, -60), Vector2(52, -60), Vector2(30, 20), Vector2(0, 46), Vector2(-30, 20)]), Color("#4c367f"))
	# lõi phản lực
	core_halo = circle_part("CoreHalo", 40.0, Color(TRIM, 0.25), Vector2(0, -8))
	core = circle_part("Core", 22.0, Color("#d9b8ff"), Vector2(0, -8))
	circle_part("CoreDot", 8.0, Color.WHITE, Vector2(0, -8))
	# 2 pháo tay cơ khí
	arm_l = _build_arm("L", -1.0)
	arm_r = _build_arm("R", 1.0)
	# ống xả hai bên hông
	for i in 3:
		vents.append(line_part("VentL%d" % i, PackedVector2Array([Vector2(0, 0), Vector2(-16, 10)]), Color("#7fe0ff", 0.7), 4.0, Vector2(-58.0, -30.0 + i * 26.0)))
		vents.append(line_part("VentR%d" % i, PackedVector2Array([Vector2(0, 0), Vector2(16, 10)]), Color("#7fe0ff", 0.7), 4.0, Vector2(58.0, -30.0 + i * 26.0)))
	# đèn thân
	for i in 6:
		hull_lights.append(circle_part("HL%d" % i, 4.0, Color("#ffec22"), Vector2(-50.0 + float(i) * 20.0, 34.0)))
	# động cơ chính (đuôi trên)
	engine_a = circle_part("EngineA", 16.0, Color("#b07bff", 0.9), Vector2(-30, -86))
	engine_b = circle_part("EngineB", 16.0, Color("#b07bff", 0.9), Vector2(30, -86))

func _build_arm(tag: String, side: float) -> Node2D:
	var arm := Node2D.new()
	arm.name = "Arm%sNode" % tag
	arm.position = Vector2(side * 78.0, 10.0)
	body.add_child(arm)
	# khớp vai
	var shoulder := Polygon2D.new()
	shoulder.name = "Shoulder"
	shoulder.polygon = PackedVector2Array([Vector2(-16, -16), Vector2(16, -16), Vector2(12, 16), Vector2(-12, 16)])
	shoulder.color = Color("#5d4494")
	arm.add_child(shoulder)
	# nòng pháo hướng XUỐNG (+y cục bộ của arm khi rotation=0 => aim mặc định xuống)
	var barrel := Polygon2D.new()
	barrel.name = "Barrel"
	barrel.polygon = PackedVector2Array([Vector2(-10, 6), Vector2(10, 6), Vector2(8, 58), Vector2(12, 66), Vector2(-12, 66), Vector2(-8, 58)])
	barrel.color = Color("#705aa8")
	arm.add_child(barrel)
	if tag == "L":
		barrel_l = barrel
	else:
		barrel_r = barrel
	circle_part("Muzzle%s" % tag, 9.0, Color(TRIM), Vector2(side * 78.0, 76.0))
	return arm

func _mirror(pts: PackedVector2Array, side: float) -> PackedVector2Array:
	var out := PackedVector2Array()
	for p in pts:
		out.append(Vector2(p.x * side, p.y))
	return out

func muzzle(name: String) -> Vector2:
	match name:
		"cannon_l":
			return Vector2(-78, 74)
		"cannon_r":
			return Vector2(78, 74)
		"wing_l":
			return Vector2(-140, -20)
		"wing_r":
			return Vector2(140, -20)
		"core":
			return Vector2(0, -8)
	return super.muzzle(name)

func _add_charge_tracks(a: Animation) -> void:
	_track3(a, "Body/Core:scale", [0.0, 0.55], [Vector2.ONE, Vector2(1.6, 1.6)])
	_track3(a, "Body/Core:modulate", [0.0, 0.55], [Color.WHITE, Color(1.9, 1.3, 2.4, 1)])
	_track3(a, "Body/CoreHalo:scale", [0.0, 0.55], [Vector2.ONE, Vector2(1.8, 1.8)])

func _add_fire_tracks(a: Animation) -> void:
	_track3(a, "Body/Core:scale", [0.0, 0.08, 0.32], [Vector2(1.6, 1.6), Vector2(2.1, 2.1), Vector2.ONE])
	_track3(a, "Body/Core:modulate", [0.0, 0.08, 0.32], [Color(1.9, 1.3, 2.4, 1), Color(3, 3, 3.4, 1), Color.WHITE])
	_track3(a, "Body/CoreHalo:scale", [0.0, 0.08, 0.32], [Vector2(1.8, 1.8), Vector2(2.4, 2.4), Vector2.ONE])

func _add_phase_tracks(a: Animation) -> void:
	# đổi pha = cánh xoè mạnh + lõi bùng
	_track3(a, "Body/WingSeg0:rotation", [0.0, 0.6, 1.5], [0.0, -0.5, 0.0])
	_track3(a, "Body/WingSeg1:rotation", [0.0, 0.6, 1.5], [0.0, 0.5, 0.0])

func _process(delta: float) -> void:
	pt += delta
	recoil_t = maxf(0.0, recoil_t - delta)
	core_flash = maxf(0.0, core_flash - delta * 3.0)
	if boss != null and boss.shots_fired != last_shots:
		last_shots = boss.shots_fired
		recoil_t = 0.18
		core_flash = 1.0
	# pháo tay ngắm người chơi (kẹp góc), giật lùi khi fire
	if boss != null and boss.run != null:
		var pl := player_local()
		for side_i in 2:
			var arm: Node2D = arm_l if side_i == 0 else arm_r
			var sgn := -1.0 if side_i == 0 else 1.0
			var want := (pl - arm.position).angle() - PI * 0.5
			arm.rotation = lerpf(arm.rotation, clampf(want, -1.1, 1.1), 1.0 - exp(-7.0 * delta))
			var barrel: Polygon2D = barrel_l if side_i == 0 else barrel_r
			barrel.position = Vector2(0, -(recoil_t / 0.18) * 12.0)
			var mz: Polygon2D = parts["MuzzleL" if side_i == 0 else "MuzzleR"]
			mz.modulate = Color(1, 1, 1, (recoil_t / 0.18) + core_flash * 0.6)
			mz.scale = Vector2.ONE * (1.0 + (recoil_t / 0.18) * 0.8)
	# cánh xoè theo pha — boss "lột xác" mỗi pha
	var target_spread := 1.0
	if boss != null:
		target_spread = 1.0 + float(boss.phase - 1) * 0.3 + (0.35 if boss.enraged else 0.0)
		if boss.state == "transition":
			target_spread += 0.25
	spread = lerpf(spread, target_spread, 1.0 - exp(-2.5 * delta))
	for i in wings.size():
		var side := -1.0 if i % 2 == 0 else 1.0
		var back := 0.72 if i >= 2 else 1.0
		wings[i].position = wing_base[i] + Vector2(side * (spread - 1.0) * 34.0 * back, (spread - 1.0) * 6.0)
		if boss == null or boss.state != "transition":
			wings[i].rotation = side * (spread - 1.0) * 0.5 * back
	# lõi: rực theo telegraph + nổ trắng khi fire
	var prog := 0.0
	if boss != null and boss.tele_active:
		prog = clampf(boss.tele_t / boss.tele_dur, 0.0, 1.0)
	var heat := prog + core_flash * 0.8
	core.modulate = Color(1.0 + heat, 1.0 + heat * 0.4, 1.0 + heat, 1.0)
	if prog <= 0.0 and core_flash <= 0.0:
		var breathe := 1.0 + 0.06 * sin(pt * 3.0)
		core.scale = Vector2(breathe, breathe)
		core_halo.scale = Vector2(breathe, breathe)
	# ống xả xung nhịp
	for i in vents.size():
		var pulse := 0.4 + 0.6 * absf(sin(pt * 5.5 + float(i) * 0.9))
		vents[i].modulate = Color(1, 1, 1, pulse * (0.5 + prog * 0.5))
	# đèn thân so le
	for i in hull_lights.size():
		hull_lights[i].modulate = Color(1, 1, 1, 0.3 + 0.7 * maxf(0.0, sin(pt * 2.8 + float(i) * 1.1)))
	# động cơ
	var e := 1.0 + 0.2 * sin(pt * 8.0) + prog * 0.3
	engine_a.scale = Vector2(e, e * 1.25)
	engine_b.scale = Vector2(e, e * 1.25)
	# cuồng nộ: thân đỏ rực theo nhịp
	if boss != null and boss.enraged:
		var rage := 0.75 + 0.25 * sin(pt * 9.5)
		core_halo.color = Color("#ff3c5a")
		core_halo.modulate = Color(1, 1, 1, rage)
