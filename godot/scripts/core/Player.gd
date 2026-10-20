extends Node2D
## Player.gd — ĐIỀU KHIỂN VIẾT MỚI HOÀN TOÀN (không dùng code cũ):
##  * Kéo NGÓN TAY ở bất kỳ đâu: tàu bám 1:1 theo toạ độ canvas (stretch
##    canvas_items đảm bảo tỉ lệ đúng trên mọi kích cỡ màn) + grab-offset
##    kẹp ±(140,220) để tàu luôn NỔI TRÊN ngón tay, không bị che.
##  * Làm mượt frame-rate độc lập: pos += (target-pos) * (1-exp(-k*dt)).
##  * Auto-fire; hitbox 8px vs sprite ~90px (spec shmup); 3 mạng; khiên;
##    invuln 3s nháy; bom.
signal died
signal lives_changed(lives: int)
signal shields_changed(shields: int)
signal weapon_changed(level: int)
signal bombs_changed(bombs: int)


var stats: Dictionary = {}
var lives: int = Balance.PLAYER["lives"]
var bombs: int = Balance.PLAYER["bombs"]
var shields: int = 0
var weapon_level: int = 1
var max_hp: int = 100
var hp: int = 100
var invuln_t := 0.0
var alive := true
var dragging := false
var target := Vector2.ZERO
var grab_offset := Vector2.ZERO
var fire_t := 0.0
var tilt := 0.0
var run: Node = null                 # RunScene cha (spawn đạn qua run)

const FLAME_BASE := 24

var sprite: Sprite2D
var flame: CPUParticles2D
var hitbox_debug: Node2D

func setup(ship_id: String, run_ref: Node) -> void:
	run = run_ref
	stats = Game.stats_now() if ship_id == "" else Balance.ship_stats(ship_id, Game.ship_level(ship_id), Game.tech_levels())
	max_hp = int(stats["hp"])
	hp = max_hp
	shields = int(stats["shield_start"])
	weapon_level = clampi(int(stats["weapon_start"]), 1, 5)
	# gói tiếp viện từ cửa hàng: +1 bom, +1 khiên, súng LV2 (dùng 1 lần)
	if bool(Game.data.get("supply", false)):
		Game.data["supply"] = false
		Game.save_game()
		bombs += 1
		shields = mini(shields + 1, int(stats["shield_cap"]))
		weapon_level = maxi(weapon_level, 2)
	target = Vector2(Balance.VIEW.x * 0.5, Balance.VIEW.y - 220.0)
	position = target

func _ready() -> void:
	sprite = Sprite2D.new()
	var tex: Texture2D = null
	var ship_id := Game.current_ship()
	var path := "res://assets/ships/%s.png" % ship_id
	if ResourceLoader.exists(path):
		tex = load(path)
	if tex != null:
		sprite.texture = tex
		var longest := maxf(tex.get_width(), tex.get_height())
		var s: float = 96.0 / longest * float(Balance.PLAYER["sprite_scale"])
		sprite.scale = Vector2(s, s)
	add_child(sprite)
	flame = CPUParticles2D.new()
	flame.position = Vector2(0, 40)
	flame.amount = 24
	flame.lifetime = 0.35
	flame.direction = Vector2(0, 1)
	flame.spread = 14.0
	flame.gravity = Vector2(0, 420)
	flame.initial_velocity_min = 90.0
	flame.initial_velocity_max = 180.0
	flame.scale_amount_min = 1.5
	flame.scale_amount_max = 3.5
	flame.color = Color("#7fe0ff")
	flame.color_ramp = _flame_ramp()
	add_child(flame)
	hitbox_debug = Node2D.new()
	hitbox_debug.visible = false
	hitbox_debug.set_script(preload("res://scripts/core/HitboxDraw.gd"))
	add_child(hitbox_debug)
	z_index = 20

func _flame_ramp() -> Gradient:
	var g := Gradient.new()
	g.set_color(0, Color(1, 1, 1, 0.95))
	g.set_color(1, Color(0.3, 0.7, 1, 0.0))
	return g

# ------------------------------------------------------------------ input MỚI
func _unhandled_input(event: InputEvent) -> void:
	if not alive:
		return
	var pos: Vector2
	if event is InputEventScreenTouch:
		if event.pressed:
			dragging = true
			_begin_drag(event.position)
		elif dragging:
			dragging = false
		get_viewport().set_input_as_handled()
	elif event is InputEventScreenDrag:
		pos = _to_world(event.position)
		target = _clamp_target(pos + grab_offset)
		get_viewport().set_input_as_handled()
	elif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		dragging = event.pressed
		if event.pressed:
			_begin_drag(event.position)
	elif event is InputEventMouseMotion and dragging:
		pos = _to_world(event.position)
		target = _clamp_target(pos + grab_offset)

## Ngón chạm xuống: giữ offset tàu-ngón (kẹp trong khoảng) => không giật cục,
## tàu không nằm dưới ngón tay (tỉ lệ 1:1, bù offset).
func _begin_drag(screen_pos: Vector2) -> void:
	var p := _to_world(screen_pos)
	grab_offset = _clamp_vec(position - p, Vector2(Balance.PLAYER["grab_clamp_x"], Balance.PLAYER["grab_clamp_y"]))
	target = _clamp_target(p + grab_offset)

func _to_world(screen_pos: Vector2) -> Vector2:
	var w := get_parent() as Node2D
	if w != null:
		return screen_pos - w.position
	return screen_pos

func _clamp_vec(v: Vector2, lim: Vector2) -> Vector2:
	return Vector2(clampf(v.x, -lim.x, lim.x), clampf(v.y, -lim.y, lim.y))

func _clamp_target(t: Vector2) -> Vector2:
	var m: int = Balance.PLAYER["bounds_margin"]
	return Vector2(clampf(t.x, m, Balance.VIEW.x - m), clampf(t.y, m + 120, Balance.VIEW.y - m))

func _physics_process(delta: float) -> void:
	if not alive:
		return
	# bàn phím (desktop): mũi tên/WASD dời target
	var key := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	if key != Vector2.ZERO:
		target = _clamp_target(target + key * stats["speed"] * delta)
	# bám mục tiêu — mượt, độc lập FPS
	var k: float = Balance.PLAYER["follow_k"]
	var prev := position
	position += (target - position) * (1.0 - exp(-k * delta))
	position = _clamp_target(position)   # không bao giờ lọt khỏi biên
	var vx := (position.x - prev.x) / maxf(delta, 0.0001)
	tilt = clampf(vx * 0.00035, -0.35, 0.35)
	rotation = lerpf(rotation, tilt, 1.0 - exp(-12.0 * delta))
	# CPUParticles2D không có amount_ratio → chỉnh amount (chỉ khi đổi số)
	var want := int(FLAME_BASE * clampf(0.4 + absf(vx) / 500.0, 0.4, 1.0))
	if flame.amount != want:
		flame.amount = want
	# nháy invuln
	if invuln_t > 0.0:
		invuln_t -= delta
		var blink := 0.35 + 0.65 * absf(sin(float(Time.get_ticks_msec()) / 1000.0 * float(Balance.PLAYER["blink_hz"]) * PI))
		sprite.modulate.a = blink if invuln_t > 0.0 else 1.0
	else:
		sprite.modulate.a = 1.0
	# auto-fire
	fire_t -= delta
	if fire_t <= 0.0 and run != null:
		fire_t = 1.0 / float(stats["fire_rate"])
		run.fire_player_weapon(self)

# ------------------------------------------------------------------ combat
func hit() -> int:
	## 0 = bỏ qua (bất tử/chết), 1 = khiên đỡ, 2 = MẤT MẠNG.
	if not alive or invuln_t > 0.0:
		return 0
	if shields > 0:
		shields -= 1
		invuln_t = 1.0
		shields_changed.emit(shields)
		Sfx.play("shield_hit")
		return 1
	lives -= 1
	lives_changed.emit(lives)
	Sfx.play("player_hit")
	if lives <= 0:
		alive = false
		died.emit()
		return 2
	invuln_t = Balance.PLAYER["invuln"]
	hp = max_hp
	position = Vector2(Balance.VIEW.x * 0.5, Balance.VIEW.y - 180.0)
	target = position
	return 2

func heal(amount: int) -> void:
	hp = mini(max_hp, hp + amount)

func add_shield() -> void:
	shields = mini(int(stats["shield_cap"]), shields + 1)
	shields_changed.emit(shields)

func raise_weapon() -> void:
	weapon_level = mini(5, weapon_level + 1)
	weapon_changed.emit(weapon_level)

func use_bomb() -> bool:
	if bombs <= 0 or not alive:
		return false
	bombs -= 1
	bombs_changed.emit(bombs)
	Sfx.play("bomb")
	return true

func show_hitbox(v: bool) -> void:
	hitbox_debug.visible = v
