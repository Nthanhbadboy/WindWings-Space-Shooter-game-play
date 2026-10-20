extends "res://scripts/bosses/BossRig.gd"
## ImperatorRig — soái hạm: thân art imperial, 2 tháp pháo (procedural xoay
## ngắm người chơi, giật lùi khi fire), cửa hangar mở dần khi charge,
## đèn cầu + đèn động cơ nhấp nháy, cột ăng-ten quét.

var turret_l: Node2D
var turret_r: Node2D
var barrel_l: Polygon2D
var barrel_r: Polygon2D
var flash_l: Polygon2D
var flash_r: Polygon2D
var hangar_door: Polygon2D
var hangar_dark: Polygon2D
var lights: Array[Polygon2D] = []
var engine_l: Polygon2D
var engine_r: Polygon2D
var pt := 0.0
var recoil_t := 0.0
var last_shots := -1

func _build_parts() -> void:
	# thân chính — art imperial
	sprite_part("HullArt", "res://assets/bosses/boss_imperial.png", 236.0, Vector2(0, -10))
	# sống lưng giáp
	poly("Spine", PackedVector2Array([Vector2(-14, -108), Vector2(14, -108), Vector2(20, 60), Vector2(-20, 60)]), Color("#5a6a86"))
	# đèn cầu nhấp nháy
	for i in 5:
		lights.append(circle_part("BridgeLight%d" % i, 5.0, Color("#ffd76a"), Vector2(-48.0 + i * 24.0, -58.0)))
	# hangar (hốc tối + cửa trượt)
	hangar_dark = poly("HangarDark", PackedVector2Array([Vector2(-44, 0), Vector2(44, 0), Vector2(44, 40), Vector2(-44, 40)]), Color("#0a0f1e"), Vector2(0, 44))
	hangar_door = poly("HangarDoor", PackedVector2Array([Vector2(-46, 0), Vector2(46, 0), Vector2(46, 14), Vector2(-46, 14)]), Color("#8a9ab8"), Vector2(0, 44))
	line_part("HangarLine", PackedVector2Array([Vector2(-46, 7), Vector2(46, 7)]), Color("#ff7a4a", 0.8), 2.0, Vector2(0, 44))
	# tháp pháo trái/phải: đế + nòng (nòng xoay quanh đế)
	turret_l = Node2D.new()
	turret_l.name = "TurretLNode"
	turret_l.position = Vector2(-84, 6)
	body.add_child(turret_l)
	barrel_l = Polygon2D.new()
	barrel_l.name = "Barrel"
	barrel_l.polygon = PackedVector2Array([Vector2(-7, 10), Vector2(7, 10), Vector2(5, -46), Vector2(-5, -46)])
	barrel_l.color = Color("#7086a8")
	turret_l.add_child(barrel_l)
	circle_part("TurretBaseL", 18.0, Color("#4a5a78"), Vector2(-84, 6))
	flash_l = circle_part("FlashL", 12.0, Color("#ffcf6a", 0.0), Vector2(-84, -44))
	turret_r = Node2D.new()
	turret_r.name = "TurretRNode"
	turret_r.position = Vector2(84, 6)
	body.add_child(turret_r)
	barrel_r = Polygon2D.new()
	barrel_r.name = "Barrel"
	barrel_r.polygon = barrel_l.polygon
	barrel_r.color = Color("#7086a8")
	turret_r.add_child(barrel_r)
	circle_part("TurretBaseR", 18.0, Color("#4a5a78"), Vector2(84, 6))
	flash_r = circle_part("FlashR", 12.0, Color("#ffcf6a", 0.0), Vector2(84, -44))
	# động cơ (phía trên — tàu bay lên)
	engine_l = circle_part("EngineL", 14.0, Color("#6ad0ff", 0.9), Vector2(-40, -96))
	engine_r = circle_part("EngineR", 14.0, Color("#6ad0ff", 0.9), Vector2(40, -96))
	# ăng-ten quét
	line_part("Mast", PackedVector2Array([Vector2(0, 0), Vector2(0, -34)]), Color("#c8d4ea"), 3.0, Vector2(0, -104))
	circle_part("MastTip", 5.0, Color("#ff4a4a"), Vector2(0, -140))

func muzzle(name: String) -> Vector2:
	match name:
		"cannon_l":
			return Vector2(-84, -40)
		"cannon_r":
			return Vector2(84, -40)
		"wing_l":
			return Vector2(-104, 10)
		"wing_r":
			return Vector2(104, 10)
	return super.muzzle(name)

func _add_charge_tracks(a: Animation) -> void:
	# hangar mở dần
	_track3(a, "Body/HangarDoor:position", [0.0, 0.55], [Vector2(0, 44), Vector2(0, 66)])
	_track3(a, "Body/HangarDoor:modulate", [0.0, 0.55], [Color.WHITE, Color(1.2, 1.05, 0.9, 1)])

func _add_fire_tracks(a: Animation) -> void:
	_track3(a, "Body/HangarDoor:position", [0.0, 0.32], [Vector2(0, 66), Vector2(0, 44)])

func _process(delta: float) -> void:
	pt += delta
	recoil_t = maxf(0.0, recoil_t - delta)
	# tháp pháo ngắm người chơi
	if boss != null and boss.run != null:
		var pl := player_local()
		var aim_l := (pl - turret_l.position).angle() + PI * 0.5
		var aim_r := (pl - turret_r.position).angle() + PI * 0.5
		turret_l.rotation = lerpf(turret_l.rotation, clampf(aim_l, -1.2, 1.2), 1.0 - exp(-6.0 * delta))
		turret_r.rotation = lerpf(turret_r.rotation, clampf(aim_r, -1.2, 1.2), 1.0 - exp(-6.0 * delta))
	# giật lùi nòng khi vừa bắn
	if boss != null and boss.shots_fired != last_shots:
		last_shots = boss.shots_fired
		recoil_t = 0.16
	var rec := (recoil_t / 0.16) * 10.0
	barrel_l.position = Vector2(0, rec)
	barrel_r.position = Vector2(0, rec)
	var fa := recoil_t / 0.16
	flash_l.modulate = Color(1, 1, 1, fa)
	flash_r.modulate = Color(1, 1, 1, fa)
	# đèn cầu nhấp nháy so le
	for i in lights.size():
		var on := 0.35 + 0.65 * maxf(0.0, sin(pt * 3.4 + float(i) * 1.3))
		lights[i].modulate = Color(1, 1, 1, on)
	# động cơ phập phồng
	var e := 1.0 + 0.18 * sin(pt * 7.0)
	engine_l.scale = Vector2(e, e * 1.3)
	engine_r.scale = Vector2(e, e * 1.3)
	# ăng ten quay
	parts["MastTip"].position = Vector2(cos(pt * 1.6) * 10.0, -140 + sin(pt * 1.6) * 4.0)
	# cuồng nộ: đèn cầu đỏ
	if boss != null and boss.enraged:
		for i in lights.size():
			lights[i].color = Color("#ff4a4a")
