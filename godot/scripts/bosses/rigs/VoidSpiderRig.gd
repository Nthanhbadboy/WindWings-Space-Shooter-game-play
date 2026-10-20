extends "res://scripts/bosses/BossRig.gd"
## VoidSpiderRig — nhện hư không: 6 chân Line2D 3 điểm (hông-gối-bàn) giải
## IK 2 khớp mỗi frame, dáng đi so le; khi charge cả 6 chân GIƠ LÊN co cụm,
## fire thì ĐẬP XUỐNG. Ngực giáp, bụng phình với hoa văn đỏ, nanh độc,
## cụm 6 mắt phát sáng theo telegraph.

var legs: Array[Line2D] = []
var leg_hip: Array[Vector2] = []
var leg_foot: Array[Vector2] = []
var leg_gait: Array[float] = []
var fang_l: Polygon2D
var fang_r: Polygon2D
var eyes: Array[Polygon2D] = []
var abdomen: Polygon2D
var pt := 0.0
var slam_t := 0.0
var last_shots := -1

const L1 := 62.0
const L2 := 66.0
const CHITIN := Color("#3d1220")
const PLATE := Color("#5c1a2e")

func _build_parts() -> void:
	# 6 chân (3 mỗi bên) — tạo trước để nằm DƯỚI thân
	for i in 6:
		var side := -1.0 if i < 3 else 1.0
		var row := float(i % 3)
		var hip := Vector2(side * 34.0, -34.0 + row * 40.0)
		var foot := Vector2(side * (128.0 + row * 10.0), 74.0 - absf(row - 1.0) * 22.0)
		leg_hip.append(hip)
		leg_foot.append(foot)
		leg_gait.append(pt + row * 2.1 + (0.0 if side < 0.0 else PI))
		var l := line_part("Leg%d" % i, PackedVector2Array([hip, hip, foot]), Color("#7a2438"), 9.0 - row)
		legs.append(l)
	# bụng (phía trên = phía sau khi bay xuống)
	abdomen = circle_part("Abdomen", 66.0, CHITIN, Vector2(0, -52))
	# hoa văn bụng: chữ V đỏ phát sáng
	line_part("Mark1", PackedVector2Array([Vector2(-30, -74), Vector2(0, -46), Vector2(30, -74)]), Color("#ff3c5a", 0.9), 7.0)
	line_part("Mark2", PackedVector2Array([Vector2(-20, -96), Vector2(0, -74), Vector2(20, -96)]), Color("#ff3c5a", 0.7), 5.0)
	# ngực
	poly("Thorax", PackedVector2Array([
		Vector2(-44, -26), Vector2(-30, 30), Vector2(0, 46), Vector2(30, 30), Vector2(44, -26), Vector2(0, -44),
	]), PLATE)
	# giáp ngực
	poly("ThoraxPlate", PackedVector2Array([Vector2(-20, -20), Vector2(20, -20), Vector2(12, 18), Vector2(-12, 18)]), Color("#7a2438"))
	# nanh độc
	fang_l = poly("FangL", PackedVector2Array([Vector2(-8, 0), Vector2(4, 0), Vector2(-2, 34)]), Color("#ffd23c"), Vector2(-18, 40))
	fang_r = poly("FangR", PackedVector2Array([Vector2(-4, 0), Vector2(8, 0), Vector2(2, 34)]), Color("#ffd23c"), Vector2(18, 40))
	fang_l.scale = Vector2(1, 0.4)
	fang_r.scale = Vector2(1, 0.4)
	# cụm 6 mắt
	var eye_pos := [Vector2(-22, 6), Vector2(-10, -2), Vector2(10, -2), Vector2(22, 6), Vector2(-16, 16), Vector2(16, 16)]
	for i in 6:
		eyes.append(circle_part("Eye%d" % i, 6.0 if i < 4 else 4.5, Color("#ff3c5a", 0.5), eye_pos[i]))

func muzzle(name: String) -> Vector2:
	match name:
		"fang_l":
			return Vector2(-18, 66)
		"fang_r":
			return Vector2(18, 66)
	return super.muzzle(name)

func _add_charge_tracks(a: Animation) -> void:
	_track3(a, "Body/Abdomen:scale", [0.0, 0.55], [Vector2.ONE, Vector2(1.14, 1.18)])

func _add_fire_tracks(a: Animation) -> void:
	_track3(a, "Body/Abdomen:scale", [0.0, 0.07, 0.32], [Vector2(1.14, 1.18), Vector2(0.9, 0.88), Vector2.ONE])

## IK 2 khớp: trả về gối sao cho chân gập ra ngoài.
func _knee(hip: Vector2, foot: Vector2, bend: float) -> Vector2:
	var d := foot - hip
	var dist := clampf(d.length(), absf(L1 - L2) + 0.5, L1 + L2 - 0.5)
	var a := acos(clampf((L1 * L1 + dist * dist - L2 * L2) / (2.0 * L1 * dist), -1.0, 1.0))
	return hip + d.normalized().rotated(a * bend) * L1

func _process(delta: float) -> void:
	pt += delta
	slam_t = maxf(0.0, slam_t - delta * 4.0)
	if boss != null and boss.shots_fired != last_shots:
		last_shots = boss.shots_fired
		slam_t = 1.0
	var raise := 0.0
	var prog := 0.0
	if boss != null and boss.tele_active:
		prog = clampf(boss.tele_t / boss.tele_dur, 0.0, 1.0)
		raise = prog
	for i in legs.size():
		var side := -1.0 if i < 3 else 1.0
		var gait: float = leg_gait[i]
		var swing := sin(pt * 2.6 + gait)
		var foot := leg_foot[i]
		# bước đi: rê ngang + nhấc chân
		foot.x += swing * 14.0 * (1.0 - raise)
		foot.y -= maxf(0.0, swing) * 16.0 * (1.0 - raise)
		# charge: co chân giơ lên; slam: duỗi đạp mạnh xuống
		foot.y -= raise * 74.0
		foot.x -= side * raise * 30.0
		foot.y += slam_t * 40.0
		var knee := _knee(leg_hip[i], foot, side)
		var l := legs[i]
		var pts := l.points
		pts[0] = leg_hip[i]
		pts[1] = knee
		pts[2] = foot
		l.points = pts
	# nanh thò ra theo charge, há khi fire
	var ext := 0.4 + raise * 0.9 + slam_t * 0.35
	fang_l.scale = Vector2(1, ext)
	fang_r.scale = Vector2(1, ext)
	fang_l.rotation = -raise * 0.3 - slam_t * 0.12
	fang_r.rotation = raise * 0.3 + slam_t * 0.12
	# bụng thở
	if raise <= 0.0:
		abdomen.scale = Vector2.ONE * (1.0 + 0.04 * sin(pt * 2.2))
	# mắt rực theo telegraph + cuồng nộ
	var glow := 0.4 + prog * 0.6 + slam_t * 0.4
	if boss != null and boss.enraged:
		glow = maxf(glow, 0.8 + 0.2 * sin(pt * 11.0))
	for i in eyes.size():
		eyes[i].modulate = Color(1.0 + prog, 0.5, 0.5, clampf(glow, 0.3, 1.0))
