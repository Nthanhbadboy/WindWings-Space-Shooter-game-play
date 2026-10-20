extends Node2D
## Enemy.gd — 6 loại địch theo Balance.ENEMIES (wasp / hornet / interceptor /
## bomber / tank / meteor), 4 hành vi (dive / hover / tank / drift). Bắn theo
## chu kỳ delta-time; wing-flap bằng AnimationPlayer dựng trong code;
## hit-flash; HP theo difficulty cap của màn. Không dùng physics engine.

signal died(enemy: Node2D, by_player: bool)

var type := "wasp"
var data: Dictionary = {}
var hp := 1.0
var max_hp := 1.0
var bullet_mul := 1.0
var speed_mul := 1.0
var run: Node = null
var t := 0.0
var fire_t := 0.0
var flash_t := 0.0
var dead := false
var score_value := 0
var coin_value := 0

var vel := Vector2.ZERO
var phase := 0.0            # pha sine riêng (tất định theo spawn)
var strafe_dir := 1.0
var stopping := false
var aim_x := 0.0

var sprite: Sprite2D
var wings: Node2D
var hp_bar: Node2D

func setup(t: String, hp_mul: float, spd_mul: float, b_mul: float, run_ref: Node, spawn_pos: Vector2) -> void:
	type = t
	data = Balance.ENEMIES[t]
	run = run_ref
	max_hp = float(data["hp"]) * hp_mul
	hp = max_hp
	bullet_mul = b_mul
	speed_mul = spd_mul
	position = spawn_pos
	score_value = int(data["score"])
	coin_value = int(data["coins"])
	phase = fmod(spawn_pos.x * 0.017, TAU)
	var spd := float(data["speed"]) * spd_mul
	match String(data["behavior"]):
		"dive":
			vel = Vector2(0, spd)
			aim_x = spawn_pos.x
		"hover":
			vel = Vector2(0, spd)
		"tank":
			vel = Vector2(0, spd)
		"drift":
			vel = Vector2(spd * 0.25 * (1.0 if fmod(spawn_pos.x, 2.0) < 1.0 else -1.0), spd * 0.6)

func _ready() -> void:
	z_index = 10
	sprite = Sprite2D.new()
	var path: String = data["art"]
	if ResourceLoader.exists(path):
		sprite.texture = load(path)
		var s: float = float(data["scale"]) * 92.0 / maxf(sprite.texture.get_width(), sprite.texture.get_height())
		sprite.scale = Vector2(s, s)
		if data.has("tint"):
			sprite.modulate = data["tint"]
	add_child(sprite)
	if type in ["wasp", "interceptor"]:
		_build_wings()
	hp_bar = Node2D.new()
	hp_bar.position = Vector2(0, -radius() - 14.0)
	hp_bar.set_script(preload("res://scripts/core/EnemyHpBar.gd"))
	add_child(hp_bar)

func _build_wings() -> void:
	wings = Node2D.new()
	wings.name = "Wings"
	add_child(wings)
	var r := radius()
	var wl := _wing_poly(-1.0, r)
	var wr := _wing_poly(1.0, r)
	wl.name = "WingL"
	wr.name = "WingR"
	wings.add_child(wl)
	wings.add_child(wr)
	var anim := AnimationPlayer.new()
	wings.add_child(anim)
	var lib := AnimationLibrary.new()
	var a := Animation.new()
	a.length = 0.16
	a.loop_mode = Animation.LOOP_LINEAR
	var tr := a.add_track(Animation.TYPE_VALUE)
	a.track_set_path(tr, NodePath("WingL:rotation"))
	a.track_insert_key(tr, 0.0, -0.55)
	a.track_insert_key(tr, 0.08, -0.10)
	a.track_insert_key(tr, 0.16, -0.55)
	var tr2 := a.add_track(Animation.TYPE_VALUE)
	a.track_set_path(tr2, NodePath("WingR:rotation"))
	a.track_insert_key(tr2, 0.0, 0.55)
	a.track_insert_key(tr2, 0.08, 0.10)
	a.track_insert_key(tr2, 0.16, 0.55)
	lib.add_animation("flap", a)
	anim.add_animation_library("", lib)
	anim.play("flap")

func _wing_poly(side: float, r: float) -> Polygon2D:
	var p := Polygon2D.new()
	p.polygon = PackedVector2Array([
		Vector2(0, -r * 0.2),
		Vector2(side * r * 1.3, -r * 0.8),
		Vector2(side * r * 1.5, r * 0.15),
		Vector2(side * r * 0.2, r * 0.4),
	])
	p.color = Color(0.75, 0.88, 1.0, 0.45)
	return p

func _physics_process(delta: float) -> void:
	if dead:
		return
	t += delta
	var spd := float(data["speed"]) * speed_mul
	var r := float(data["radius"])
	match String(data["behavior"]):
		"dive":
			# liệng sine quanh trục rơi, nghiêng thân theo vận tốc ngang
			var wob: float = float(data.get("wobble", 2.4))
			var amp: float = float(data.get("amp", 60.0))
			position.y += spd * delta
			position.x = aim_x + sin(t * wob + phase) * amp
			rotation = cos(t * wob + phase) * wob * amp * 0.0016
		"hover":
			var stop_y: float = float(data.get("stop_y", 280.0))
			if position.y < stop_y:
				position.y += spd * delta
			else:
				stopping = true
				position.x += strafe_dir * spd * 0.75 * delta
				position.y = stop_y + sin(t * 1.4 + phase) * 9.0
				if position.x < r + 30.0 or position.x > Balance.VIEW.x - r - 30.0:
					strafe_dir = -strafe_dir
			rotation = strafe_dir * 0.08 if stopping else 0.0
		"tank":
			position += vel * delta
			position.x += sin(t * 0.7 + phase) * 12.0 * delta
		"drift":
			position += vel * delta
			position.x += sin(t * 0.9 + phase) * 30.0 * delta
			if data.has("spin"):
				sprite.rotation += delta * float(data["spin"])
	# bắn
	if data.has("fire_cd") and position.y > 10.0 and position.y < Balance.VIEW.y - 130.0:
		fire_t -= delta
		if fire_t <= 0.0:
			fire_t = float(data["fire_cd"]) * randf_range(0.85, 1.2) / bullet_mul
			_fire()
	# hit flash
	if flash_t > 0.0:
		flash_t -= delta
		var base: Color = data.get("tint", Color.WHITE)
		sprite.modulate = base.lerp(Color(4, 4, 4, 1), clampf(flash_t / 0.08, 0.0, 1.0))
	if hp_bar != null:
		hp_bar.call("set_ratio", hp / max_hp)
		hp_bar.visible = hp < max_hp
	# rời màn
	if position.y > Balance.VIEW.y + r + 40.0 or position.x < -r - 90.0 or position.x > Balance.VIEW.x + r + 90.0:
		_leave()

func _fire() -> void:
	if run == null:
		return
	var p: Vector2 = run.player_position()
	var aim := (p - global_position).normalized()
	var bs: float = float(Balance.BULLET["enemy_speed"]) * bullet_mul
	var col: Color = Balance.BULLET["enemy_color"]
	if int(data.get("spread", 1)) >= 3:
		for k in [-1, 0, 1]:
			run.spawn_enemy_bullet(global_position, aim.rotated(0.2 * k) * bs, col, float(Balance.BULLET["enemy_radius"]))
	else:
		run.spawn_enemy_bullet(global_position, aim * bs, col, float(Balance.BULLET["enemy_radius"]))
	Sfx.play("enemy_shot")

func damage(dmg: float, by_player := true) -> void:
	if dead:
		return
	hp -= dmg
	flash_t = 0.08
	if hp <= 0.0:
		dead = true
		if run != null:
			run.on_enemy_killed(self, by_player)
		died.emit(self, by_player)
		queue_free()
	else:
		Sfx.play("hit")

func _leave() -> void:
	dead = true
	died.emit(self, false)
	queue_free()

func radius() -> float:
	return float(data["radius"])
