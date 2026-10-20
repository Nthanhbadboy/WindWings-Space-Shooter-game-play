extends Node2D
## BossRig.gd — khung xương boss dựng 100% bằng code: các part (Polygon2D /
## Line2D / Sprite2D) + AnimationPlayer với AnimationLibrary tạo track thủ
## công. Mọi boss dùng chung bộ anim: idle (thở), charge (gồng), fire (giật
## lùi), hurt (rung), phase_shift (nổ sáng đổi pha), enrage (hoá đỏ), death
## (RỜI TỪNG BỘ PHẬN — mỗi part văng trễ nhau). Subclass thêm part độc quyền
## + _process() procedural (xúc tu sine, mắt đuổi, chân IK, cánh vỗ...).

var boss: Node2D = null
var anim: AnimationPlayer = null
var lib: AnimationLibrary = null
var body: Node2D = null
var parts := {}
var detach_order: Array[Node2D] = []

const HURT_THROTTLE := 0.18

func build(boss_ref: Node2D) -> void:
	boss = boss_ref
	body = Node2D.new()
	body.name = "Body"
	add_child(body)
	anim = AnimationPlayer.new()
	add_child(anim)
	lib = AnimationLibrary.new()
	anim.add_animation_library("", lib)
	_build_parts()
	_build_common_anims()
	_build_custom_anims()
	anim.animation_finished.connect(_on_anim_finished)
	anim.play("idle")

# ---------------------------------------------------------------- part helpers
func poly(name: String, pts: PackedVector2Array, color: Color, pos := Vector2.ZERO) -> Polygon2D:
	var p := Polygon2D.new()
	p.name = name
	p.polygon = pts
	p.color = color
	p.position = pos
	body.add_child(p)
	parts[name] = p
	detach_order.append(p)
	return p

func circle_part(name: String, r: float, color: Color, pos := Vector2.ZERO, seg := 30) -> Polygon2D:
	var pts := PackedVector2Array()
	for i in seg:
		var a := TAU * float(i) / float(seg)
		pts.append(Vector2(cos(a), sin(a)) * r)
	return poly(name, pts, color, pos)

func line_part(name: String, pts: PackedVector2Array, color: Color, width := 6.0, pos := Vector2.ZERO) -> Line2D:
	var l := Line2D.new()
	l.name = name
	l.points = pts
	l.default_color = color
	l.width = width
	l.position = pos
	body.add_child(l)
	parts[name] = l
	return l

func sprite_part(name: String, path: String, longest: float, pos := Vector2.ZERO) -> Sprite2D:
	var s := Sprite2D.new()
	s.name = name
	if ResourceLoader.exists(path):
		s.texture = load(path)
		var k := longest / maxf(s.texture.get_width(), s.texture.get_height())
		s.scale = Vector2(k, k)
	s.position = pos
	body.add_child(s)
	parts[name] = s
	detach_order.append(s)
	return s

func ring_points(r: float, seg := 40) -> PackedVector2Array:
	var pts := PackedVector2Array()
	for i in seg + 1:
		var a := TAU * float(i) / float(seg)
		pts.append(Vector2(cos(a), sin(a)) * r)
	return pts

func muzzle(name: String) -> Vector2:
	if parts.has(name):
		var p: Node2D = parts[name]
		return p.position
	return Vector2.ZERO

func part_ref(name: String) -> Node2D:
	return parts.get(name, null)

func player_local() -> Vector2:
	if boss != null and boss.run != null:
		return to_local(boss.run.player_position())
	return Vector2(Balance.VIEW.x * 0.5, Balance.VIEW.y - 200.0) - global_position

# ---------------------------------------------------------------- anim chung
func _build_common_anims() -> void:
	# idle — thở 2.6s
	var a := Animation.new()
	a.length = 2.6
	a.loop_mode = Animation.LOOP_LINEAR
	_track3(a, "Body:scale", [0.0, 1.3, 2.6], [Vector2.ONE, Vector2(1.025, 1.045), Vector2.ONE])
	_track3(a, "Body:position", [0.0, 1.3, 2.6], [Vector2.ZERO, Vector2(0, -7), Vector2.ZERO])
	lib.add_animation("idle", a)
	# charge — gồng ngược lên,subclass chèn track phụ
	a = Animation.new()
	a.length = 0.55
	_track3(a, "Body:position", [0.0, 0.35, 0.55], [Vector2.ZERO, Vector2(0, -18), Vector2(0, -14)])
	_track3(a, "Body:scale", [0.0, 0.55], [Vector2.ONE, Vector2(1.07, 1.07)])
	_add_charge_tracks(a)
	lib.add_animation("charge", a)
	# fire — giật lùi bật về
	a = Animation.new()
	a.length = 0.32
	_track3(a, "Body:position", [0.0, 0.07, 0.32], [Vector2(0, -14), Vector2(0, 22), Vector2.ZERO])
	_track3(a, "Body:scale", [0.0, 0.07, 0.32], [Vector2(1.07, 1.07), Vector2(0.96, 1.05), Vector2.ONE])
	_add_fire_tracks(a)
	lib.add_animation("fire", a)
	# hurt — rung ngang
	a = Animation.new()
	a.length = HURT_THROTTLE
	_track3(a, "Body:position", [0.0, 0.05, 0.11, 0.18], [Vector2.ZERO, Vector2(9, 0), Vector2(-7, 0), Vector2.ZERO])
	_track3(a, "Body:modulate", [0.0, 0.05, 0.18], [Color.WHITE, Color(3.2, 3.2, 3.4, 1), Color.WHITE])
	lib.add_animation("hurt", a)
	# phase_shift — nổ sáng + nén giãn
	a = Animation.new()
	a.length = Balance.BOSS_RULES["transition_time"]
	_track3(a, "Body:scale", [0.0, 0.3, 0.7, 1.1, 1.5], [Vector2.ONE, Vector2(1.2, 1.2), Vector2(0.92, 0.92), Vector2(1.08, 1.08), Vector2.ONE])
	_track3(a, "Body:modulate", [0.0, 0.25, 0.6, 1.0, 1.5], [Color.WHITE, Color(2.6, 2.6, 3.0, 1), Color(1.4, 1.2, 2.2, 1), Color.WHITE, Color.WHITE])
	_add_phase_tracks(a)
	lib.add_animation("phase_shift", a)
	# enrage — hoá đỏ cuồng nộ
	a = Animation.new()
	a.length = 0.65
	_track3(a, "Body:modulate", [0.0, 0.15, 0.4, 0.65], [Color.WHITE, Color(1.9, 0.55, 0.55, 1), Color(1.5, 0.8, 0.8, 1), Color.WHITE])
	_track3(a, "Body:scale", [0.0, 0.2, 0.65], [Vector2.ONE, Vector2(1.1, 1.1), Vector2.ONE])
	lib.add_animation("enrage", a)
	# death — rời từng bộ phận, trễ dần
	a = Animation.new()
	a.length = 1.9
	var i := 0
	for p in detach_order:
		var path := _part_path(p)
		var delay := float(i) * 0.07
		var dir := (p.position.normalized() if p.position.length() > 4.0 else Vector2(randf_range(-1, 1), randf_range(0.3, 1)).normalized())
		var dest: Vector2 = p.position + dir * float(90 + (i * 37) % 120)
		_track3(a, path + ":position", [delay, delay + 0.9, 1.85], [p.position, p.position.lerp(dest, 0.55), dest])
		_track3(a, path + ":rotation", [delay, 1.85], [p.rotation, p.rotation + (2.2 if i % 2 == 0 else -2.6)])
		_track3(a, path + ":modulate", [delay + 0.5, 1.8], [Color.WHITE, Color(1, 1, 1, 0)])
		i += 1
	_track3(a, "Body:scale", [0.0, 0.5, 1.85], [Vector2.ONE, Vector2(1.12, 1.12), Vector2(0.85, 0.85)])
	lib.add_animation("death", a)

func _part_path(p: Node2D) -> String:
	var owner_path := p.get_parent().get_path_to(anim)
	# part là con của Body (Body là con của rig, anim là con của rig)
	return "Body/" + String(p.name) if p.get_parent() == body else String(owner_path) + "/" + String(p.name)

func _track3(a: Animation, path: String, times: Array, values: Array) -> void:
	var tr := a.add_track(AnimationTrack.VALUE)
	a.track_set_path(tr, NodePath(path))
	a.track_set_interpolation_type(tr, Animation.INTERPOLATION_CUBIC)
	for i in times.size():
		a.track_insert_key(tr, times[i], values[i])

# hook subclass
func _build_parts() -> void:
	pass

func _build_custom_anims() -> void:
	pass

func _add_charge_tracks(_a: Animation) -> void:
	pass

func _add_fire_tracks(_a: Animation) -> void:
	pass

func _add_phase_tracks(_a: Animation) -> void:
	pass

func play(name: String) -> void:
	if anim != null and anim.has_animation(name):
		anim.play(name)

func _on_anim_finished(name: StringName) -> void:
	if name != &"death" and boss != null and boss.state != "dying":
		anim.play("idle")
