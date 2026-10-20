extends Node
## RunScene.gd — trận đánh hoàn chỉnh: nền parallax, thế giới entity (va chạm
## vòng tròn tự viết, KHÔNG physics engine), sóng địch, boss, bom, drone,
## combo điểm, pause (đóng băng telegraph), thưởng & kết quả. 4 chế độ:
## campaign / endless / bossrush / daily. Chạy hoàn toàn bằng delta-time.

const Collider := preload("res://scripts/core/Collider.gd")
const Loot := preload("res://scripts/core/Loot.gd")
const Spawner := preload("res://scripts/core/Spawner.gd")
const INTRO_STEPS := [0.0, 0.7, 1.4, 2.1]
const INTRO_TEXTS := ["3", "2", "1", "CHIẾN ĐẤU!"]
const DYING_TIME := 1.5
const BOSS_RUSH_ORDER := ["void_tyrant", "queen_wasp", "imperator", "void_spider", "sentinel_eye", "omega_dreadnought"]

var main: Node = null
var mode := "campaign"
var level := 1
var lap := 1
var info: Dictionary = {}
var state := "intro"        # intro | playing | paused | dying | result
var state_t := 0.0
var intro_step := 0
var score := 0
var combo := 0
var combo_t := 0.0
var coins_earned := 0
var kills := 0
var lives_lost := 0
var survival_t := 0.0
var magnet_t := 0.0
var temp_drone_t := 0.0
var hp_mul := 1.0
var speed_mul := 1.0
var bullet_mul := 1.0
var won := false

var world: Node2D
var enemies_node: Node2D
var bullets_node: Node2D
var powerups_node: Node2D
var player: Node2D
var drones: Node2D
var parallax: ParallaxBackground
var fx: Node
var hud: CanvasLayer
var pause_menu: CanvasLayer
var result_panel: CanvasLayer
var director: RefCounted = null
var boss: Node2D = null
var boss_queue: Array[String] = []
var boss_spawn_t := 0.0
var flash_rect: ColorRect

func attach(main_ref: Node, args: Dictionary) -> void:
	main = main_ref
	mode = String(args.get("mode", "campaign"))
	level = clampi(int(args.get("level", 1)), 1, Balance.TOTAL_LEVELS)

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS   # RunScene sống khi paused (menu)
	info = Balance.level_info(level)
	hp_mul = float(info["hp_mul"])
	speed_mul = float(info["speed_mul"])
	bullet_mul = float(info["bullet_mul"])
	# nền
	parallax = preload("res://scripts/core/ParallaxSpace.gd").new()
	add_child(parallax)
	parallax.call("set_theme", int(info["chapter"]))
	parallax.process_mode = Node.PROCESS_MODE_PAUSABLE
	# thế giới
	world = Node2D.new()
	world.process_mode = Node.PROCESS_MODE_PAUSABLE
	add_child(world)
	enemies_node = Node2D.new()
	bullets_node = Node2D.new()
	powerups_node = Node2D.new()
	world.add_child(enemies_node)
	world.add_child(bullets_node)
	world.add_child(powerups_node)
	# loé sáng toàn màn
	var flash_layer := CanvasLayer.new()
	flash_layer.layer = 50
	add_child(flash_layer)
	flash_rect = ColorRect.new()
	flash_rect.color = Color.WHITE
	flash_rect.modulate.a = 0.0
	flash_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	flash_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	flash_layer.add_child(flash_rect)
	# fx
	fx = preload("res://scripts/fx/Fx.gd").new()
	fx.process_mode = Node.PROCESS_MODE_PAUSABLE
	add_child(fx)
	fx.world = world
	fx.flash_rect = flash_rect
	# người chơi + drone
	player = preload("res://scripts/core/Player.gd").new()
	player.setup(Game.current_ship(), self)
	world.add_child(player)
	player.died.connect(_on_player_died)
	player.lives_changed.connect(func(n): hud.set_lives(n))
	player.shields_changed.connect(func(n): hud.set_shields(n))
	player.weapon_changed.connect(func(n): hud.set_weapon(n))
	player.bombs_changed.connect(func(n): hud.set_bombs(n))
	drones = preload("res://scripts/core/Drones.gd").new()
	drones.run = self
	world.add_child(drones)
	drones.refresh(int(player.stats["drones"]))
	# hud + menu + kết quả (ALWAYS để bấm được khi pause)
	hud = preload("res://scripts/ui/Hud.gd").new()
	add_child(hud)
	hud.call("attach_run", self)
	hud.set_lives(player.lives)
	hud.set_shields(player.shields)
	hud.set_weapon(player.weapon_level)
	hud.set_bombs(player.bombs)
	hud.set_wave(0, _wave_total())
	pause_menu = preload("res://scripts/ui/PauseMenu.gd").new()
	add_child(pause_menu)
	pause_menu.call("attach_run", self)
	pause_menu.visible = false
	result_panel = preload("res://scripts/ui/ResultPanel.gd").new()
	add_child(result_panel)
	result_panel.call("attach_run", self)
	result_panel.visible = false
	# director sóng
	if mode == "bossrush":
		boss_queue = BOSS_RUSH_ORDER.duplicate()
		boss_spawn_t = 1.0
	else:
		director = _make_director()

func _make_director() -> RefCounted:
	var d: RefCounted = preload("res://scripts/core/WaveDirector.gd").new(self, Balance.wave_script(_source_level()))
	d.wave_started.connect(func(i): hud.set_wave(i + 1, _wave_total()))
	return d

func _source_level() -> int:
	if mode == "daily":
		return 30 + (int(Time.get_datetime_dict_from_system()["day"]) % 30)
	if mode == "endless":
		return clampi(6 + lap * 6, 1, Balance.TOTAL_LEVELS)
	return level

func _wave_total() -> int:
	return Balance.wave_script(_source_level()).size()

func _physics_process(delta: float) -> void:
	match state:
		"intro":
			state_t += delta
			while intro_step < INTRO_STEPS.size() and state_t >= INTRO_STEPS[intro_step]:
				fx.call("popup", Vector2(Balance.VIEW.x * 0.5, Balance.VIEW.y * 0.42), INTRO_TEXTS[intro_step], Color("#ffec22"))
				intro_step += 1
			if state_t >= INTRO_STEPS[-1] + 0.55:
				state = "playing"
				if director != null:
					director.start()
		"playing":
			survival_t += delta
			if director != null:
				director.tick(delta)
			if boss == null and boss_spawn_t > 0.0:
				boss_spawn_t -= delta
				if boss_spawn_t <= 0.0:
					_spawn_next_boss()
			combo_t -= delta
			if combo_t <= 0.0 and combo > 0:
				combo = 0
				hud.set_score(score, combo)
			if magnet_t > 0.0:
				magnet_t -= delta
			if temp_drone_t > 0.0:
				temp_drone_t -= delta
				drones.refresh(int(player.stats["drones"]) + 1)
			elif temp_drone_t <= 0.0 and drones.count != int(player.stats["drones"]):
				drones.refresh(int(player.stats["drones"]))
			drones.update(delta, player)
			Collider.process(self)
			Collider.cull(self)
			hud.set_enemy_count(_enemy_count() + (1 if boss != null else 0))
			if Input.is_action_just_pressed("use_bomb"):
				use_bomb()
			_check_progress()
		"dying":
			state_t += delta
			if state_t >= DYING_TIME:
				_finish(false)
	if Input.is_action_just_pressed("ui_cancel") and state in ["playing", "paused"]:
		toggle_pause()

func toggle_pause() -> void:
	if state == "playing":
		state = "paused"
		get_tree().paused = true
		pause_menu.visible = true
		pause_menu.call("open")
	elif state == "paused":
		state = "playing"
		get_tree().paused = false
		pause_menu.visible = false

# ---------------------------------------------------------------- spawning
func player_position() -> Vector2:
	return player.global_position

func spawn_enemy(type: String, x: float, y := -60.0) -> void:
	Spawner.enemy(self, type, x, y)

func spawn_boss(id: String) -> void:
	Spawner.boss(self, id)

func _spawn_next_boss() -> void:
	if boss_queue.is_empty():
		return
	spawn_boss(boss_queue.pop_front())

func spawn_enemy_bullet(pos: Vector2, vel: Vector2, color: Color, radius: float, homing := 0.0) -> void:
	Spawner.bullet(self, 1, pos, vel, color, radius, 0.0, homing)

func spawn_boss_bullet(pos: Vector2, vel: Vector2, color: Color, radius: float, homing := 0.0) -> void:
	Spawner.bullet(self, 1, pos, vel, color, radius, 0.0, homing)

func spawn_player_bullet(pos: Vector2, vel: Vector2, dmg: float, radius: float, color: Color) -> void:
	Spawner.bullet(self, 0, pos, vel, color, radius, dmg, 0.0)

func fire_player_weapon(p: Node2D) -> void:
	Spawner.player_weapon(self, p)

func use_bomb() -> void:
	if not player.use_bomb():
		return
	var P := Balance.PLAYER
	for b in bullets_node.get_children():
		if b.side == 1 and not b.dead:
			b.dead = true
			fx.call("burst", b.global_position, b.color, 3, 90.0)
	for e in enemies_node.get_children():
		e.call("damage", float(P["bomb_damage"]), true)
	if boss != null and boss.is_alive():
		boss.take_damage(float(P["bomb_damage"]) * float(P["bomb_boss_mul"]))
	fx.call("flash", Color(1, 0.95, 0.8), 0.8, 0.45)
	fx.call("shake", 18.0, 0.6)
	fx.call("slow_mo", 0.35, 0.25)
	fx.call("burst", player.global_position, Color("#ffd23c"), 40, 520.0)

func _enemy_count() -> int:
	var n := 0
	for e in enemies_node.get_children():
		if not e.dead:
			n += 1
	return n

# ---------------------------------------------------------------- powerup
func apply_powerup(kind: String, pos: Vector2) -> void:
	Loot.apply_powerup(self, kind, pos)

func has_magnet() -> bool:
	return true

func magnet_radius() -> float:
	return Loot.magnet_radius(self)

func on_enemy_killed(e: Node2D, by_player: bool) -> void:
	Loot.on_enemy_killed(self, e, by_player)

# ---------------------------------------------------------------- boss events
func boss_hp_changed(_b: Node2D) -> void:
	hud.set_boss_hp(boss.hp)

func boss_phase_changed(_b: Node2D, _p: int) -> void:
	fx.call("hitstop", 0.14)
	fx.call("flash", Color(0.8, 0.7, 1.0), 0.4, 0.4)

func boss_enraged(_b: Node2D) -> void:
	fx.call("flash", Color(1.0, 0.25, 0.2), 0.5, 0.6)
	fx.call("shake", 12.0, 0.8)
	hud.set_boss_enraged()

func boss_fired(_b: Node2D, _pattern: String) -> void:
	fx.call("shake", 4.0, 0.18)

func _on_boss_died(_b: Node2D) -> void:
	score += int(Balance.ECONOMY["boss_kill_score"]) * (1 + (5 - (boss_queue.size() if mode == "bossrush" else 0)))
	hud.set_score(score, combo)
	hud.hide_boss()
	fx.call("burst", boss.global_position, Color("#ffd23c"), 40, 520.0)
	boss.queue_free()
	boss = null
	boss_spawn_t = 2.2 if (mode == "bossrush" and not boss_queue.is_empty()) else 0.0

# ---------------------------------------------------------------- thắng/thua
func _on_player_died() -> void:
	state = "dying"
	state_t = 0.0
	fx.call("burst", player.global_position, Color("#ff8a4a"), 30, 420.0)
	fx.call("slow_mo", 0.25, 0.7)
	fx.call("shake", 16.0, 0.8)
	fx.call("flash", Color(1, 0.4, 0.3), 0.6, 0.5)
	Sfx.play("explosion_big")

func _check_progress() -> void:
	if state != "playing":
		return
	if mode == "bossrush":
		if boss == null and boss_spawn_t <= 0.0 and boss_queue.is_empty():
			_finish(true)
		return
	var clear := _enemy_count() == 0 and boss == null
	if director != null and director.finished and clear:
		if mode == "endless":
			lap += 1
			hp_mul += 0.15
			bullet_mul = minf(1.5, bullet_mul + 0.04)
			director = _make_director()
			director.start()
			fx.call("popup", Vector2(Balance.VIEW.x * 0.5, Balance.VIEW.y * 0.4), "VÒNG %d" % lap, Color("#7fe0ff"))
		else:
			_finish(true)
	elif director != null and director.finished and info["is_boss"] and boss == null and clear:
		_finish(true)

func _finish(win: bool) -> void:
	state = "result"
	won = win
	get_tree().paused = false
	var res := _rewards(win)
	if win:
		res["stars"] = 3 if lives_lost == 0 else (2 if lives_lost <= 1 else 1)
		if mode == "campaign":
			var prev_stars := Game.stars_of(level)
			var best := Game.record_clear(level, int(res["stars"]))
			res["new_gems"] = maxi(0, best - prev_stars) * int(Balance.ECONOMY["star_gem"])
			Game.add_coins(int(res["coins"]))
			Game.save_game()
		elif mode == "daily":
			res["daily"] = Game.claim_daily()
			Game.add_coins(int(res["coins"]))
			Game.save_game()
		else:
			Game.add_coins(int(res["coins"]))
			Game.record_best(score)
			Game.save_game()
	result_panel.visible = true
	result_panel.call("show_result", win, res)
	Sfx.play("victory" if win else "defeat")

func _rewards(win: bool) -> Dictionary:
	if not win:
		return {"coins": int(coins_earned * 0.5), "score": score, "kills": kills, "time": survival_t}
	var coins := int(info["reward"]) + coins_earned
	if mode == "endless":
		coins = int(score / 12.0) + coins_earned
	if mode == "bossrush":
		coins = 900 + coins_earned
	return {"coins": coins, "score": score, "kills": kills, "time": survival_t, "level": level, "chapter": int(info["chapter"]), "boss": bool(info["is_boss"])}

# ---------------------------------------------------------------- điều hướng
func restart() -> void:
	get_tree().paused = false
	main.show_screen("run", {"level": level, "mode": mode})

func next_level() -> void:
	get_tree().paused = false
	main.show_screen("run", {"level": mini(level + 1, Balance.TOTAL_LEVELS), "mode": mode})

func quit_to_menu() -> void:
	get_tree().paused = false
	main.show_screen("map", {"chapter": int(info["chapter"]), "mode": mode})

func fx_shake(a: float, d: float) -> void:
	fx.call("shake", a, d)

func fx_flash(c: Color, a: float, d: float) -> void:
	fx.call("flash", c, a, d)

func fx_slow_mo(s: float, d: float) -> void:
	fx.call("slow_mo", s, d)

func fx_burst(pos: Vector2, c: Color, n: int) -> void:
	fx.call("burst", pos, c, n, 200.0)
