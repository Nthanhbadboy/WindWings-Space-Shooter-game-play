extends Node
## SmokeTest.gd — bộ kiểm thử headless chạy trong CI (Godot --headless).
## Phủ: dữ liệu 60 màn, parallax >= 3 lớp có mirroring, điều khiển người chơi
## MỚI (hội tụ 1:1 + kẹp biên), 5 cấp vũ khí, 6 loại địch, 6 BOSS (rig +
## anim + HARD RULE telegraph: không đạn nào sinh ra trước khi telegraph hết,
## 3 pha + cuồng nộ + chết), save roundtrip, RunScene thật dựng được.
## Chờ theo GIÂY MÔ PHỎNG (không phụ thuộc FPS) + watchdog tự quit(1).
## In [SMOKE][PASS/FAIL]; quit(1) nếu có bất kỳ FAIL nào.

const StubRun := preload("res://tests/StubRun.gd")
const ParallaxSpace := preload("res://scripts/core/ParallaxSpace.gd")
const PlayerScript := preload("res://scripts/core/Player.gd")
const EnemyScript := preload("res://scripts/core/Enemy.gd")
const Spawner := preload("res://scripts/core/Spawner.gd")
const RunScene := preload("res://scripts/core/RunScene.gd")

const BOSS_IDS := ["void_tyrant", "queen_wasp", "imperator", "void_spider", "sentinel_eye", "omega_dreadnought"]
const REQUIRED_ANIMS := ["idle", "charge", "fire", "hurt", "phase_shift", "enrage", "death"]
const WATCHDOG_SIM_SECONDS := 900.0

var fails := 0
var checks := 0
var world: Node2D
var sim_t := 0.0

func _physics_process(delta: float) -> void:
	sim_t += delta
	if sim_t > WATCHDOG_SIM_SECONDS:
		printerr("[SMOKE][FAIL] WATCHDOG: vượt %.0fs mô phỏng — có vòng lặp treo" % WATCHDOG_SIM_SECONDS)
		print("[SMOKE] RESULT: FAIL (watchdog)")
		get_tree().quit(1)

func _ready() -> void:
	print("[SMOKE] WindWings Galaxy Ace — bắt đầu kiểm thử headless")
	world = Node2D.new()
	add_child(world)
	_run.call_deferred()

func _check(cond: bool, name: String) -> void:
	checks += 1
	if cond:
		print("[SMOKE][PASS] " + name)
	else:
		fails += 1
		printerr("[SMOKE][FAIL] " + name)

## Chờ cond() đúng, tối đa max_sec giây mô phỏng. Trả về true nếu cond đúng.
func _until(cond: Callable, max_sec: float) -> bool:
	var t0 := sim_t
	while sim_t - t0 < max_sec:
		if cond.call():
			return true
		await get_tree().physics_frame
	return cond.call()

func _wait(sec: float) -> void:
	var t0 := sim_t
	while sim_t - t0 < sec:
		await get_tree().physics_frame

func _run() -> void:
	_test_balance()
	await _test_parallax()
	await _test_player()
	await _test_weapons()
	await _test_enemies()
	await _test_bosses()
	_test_save()
	await _test_runscene()
	Engine.time_scale = 1.0
	print("[SMOKE] checks=%d fails=%d" % [checks, fails])
	print("[SMOKE] RESULT: " + ("PASS" if fails == 0 else "FAIL"))
	get_tree().quit(1 if fails > 0 else 0)

# ---------------------------------------------------------------- dữ liệu
func _test_balance() -> void:
	_check(Balance.TOTAL_LEVELS == 60, "60 màn chơi")
	var boss_levels_ok := true
	var rewards_ok := true
	for n in range(1, 61):
		var info := Balance.level_info(n)
		if n % 10 == 0:
			if not (bool(info["is_boss"]) and Balance.BOSSES.has(String(info["boss_id"]))):
				boss_levels_ok = false
		elif bool(info["is_boss"]):
			boss_levels_ok = false
		if int(info["reward"]) <= 0:
			rewards_ok = false
	_check(boss_levels_ok, "màn 10/20/../60 là boss đúng chủ thể chương")
	_check(rewards_ok, "mọi màn có thưởng > 0")
	var a := str(Balance.wave_script(7))
	var b := str(Balance.wave_script(7))
	_check(a == b and a.length() > 100, "wave_script tất định theo seed")
	var pats_ok := true
	for id in Balance.BOSSES:
		for pname in (Balance.BOSSES[id]["patterns"] as Array):
			if not Balance.PATTERNS.has(String(pname)):
				pats_ok = false
	_check(pats_ok, "mọi pattern boss có định nghĩa trong PATTERNS")
	var R := Balance.BOSS_RULES
	_check(float(R["telegraph_min"]) >= 0.6 and float(R["enrage_telegraph_mul"]) == 0.7, "HARD RULE telegraph 0.6s / enrage x0.7")
	_check(float(R["phase2_at"]) > float(R["phase3_at"]) and float(R["phase3_at"]) > float(R["enrage_at"]), "ngưỡng pha 0.66 > 0.33 > 0.10")
	_check(Balance.WEAPONS.size() == 5, "5 cấp vũ khí L1-L5")
	_check(Balance.ENEMIES.size() >= 5, "ít nhất 5 loại địch")
	_check(Balance.SHIPS.size() == 8 and Balance.TECH.size() == 5, "8 tàu + 5 nhánh tech")

# ---------------------------------------------------------------- parallax
func _test_parallax() -> void:
	var p: ParallaxBackground = ParallaxSpace.new()
	add_child(p)
	await _wait(0.2)
	var layers := 0
	var mirrored := 0
	var scales: Array[Vector2] = []
	for c in p.get_children():
		if c is ParallaxLayer:
			layers += 1
			var l := c as ParallaxLayer
			if l.motion_mirroring != Vector2.ZERO:
				mirrored += 1
			scales.append(l.motion_scale)
	_check(layers >= 3, "ParallaxBackground có >= 3 ParallaxLayer (thực tế %d)" % layers)
	_check(mirrored == layers, "mọi lớp có motion_mirroring (loop vô tận)")
	_check(scales.size() >= 3 and not (scales[0] == scales[1] or scales[1] == scales[2]), "3 lớp có tốc độ cuộn khác nhau")
	var off1: Vector2 = p.scroll_offset
	await _wait(0.4)
	_check(p.scroll_offset != off1, "nền đang cuộn (scroll_offset đổi theo delta)")
	p.queue_free()

# ---------------------------------------------------------------- điều khiển MỚI
func _test_player() -> void:
	var stub: Node = StubRun.new()
	add_child(stub)
	var pl: Node2D = PlayerScript.new()
	world.add_child(pl)
	pl.setup("striker", stub)
	await _wait(0.1)
	# 1) chạm-kéo: tàu nổi TRÊN ngón tay nhờ grab_offset kẹp ±(140,220)
	pl.position = Vector2(360, 900)
	pl.target = pl.position
	pl._begin_drag(Vector2(360, 1050))   # ngón tay DƯỚI tàu 150px
	_check(pl.grab_offset.y <= -100.0, "grab_offset giữ tàu NỔI TRÊN ngón tay (dy=%.0f)" % pl.grab_offset.y)
	pl.target = Vector2(200, 600)
	await _wait(0.8)
	_check(pl.position.distance_to(Vector2(200, 600)) < 6.0, "bám mục tiêu 1:1 hội tụ (<6px sau 0.8s)")
	# 2) kẹp biên
	pl.target = Vector2(-500, 5000)
	await _wait(0.8)
	var m: int = Balance.PLAYER["bounds_margin"]
	_check(pl.position.x >= m - 1.0 and pl.position.y <= Balance.VIEW.y - m + 1.0, "kẹp trong biên màn hình")
	# 3) tự bắn
	var v0: int = stub.weapon_volleys
	await _wait(1.0)
	_check(stub.weapon_volleys > v0, "auto-fire đang bắn")
	# 4) khiên đỡ trước, mất mạng sau
	pl.shields = 1
	pl.invuln_t = 0.0
	_check(pl.hit() == 1 and pl.shields == 0, "khiên đỡ đòn (hit=1)")
	pl.invuln_t = 0.0
	var lives0: int = pl.lives
	_check(pl.hit() == 2 and pl.lives == lives0 - 1, "hết khiên thì mất mạng (hit=2)")
	_check(pl.invuln_t > 0.0, "bất tử ngắn sau khi trúng đòn")
	pl.queue_free()
	stub.queue_free()
	await _wait(0.05)

# ---------------------------------------------------------------- vũ khí
func _test_weapons() -> void:
	var stub: Node = StubRun.new()
	add_child(stub)
	var pl: Node2D = PlayerScript.new()
	world.add_child(pl)
	pl.setup("striker", stub)
	await _wait(0.05)
	var expected := [1, 2, 3, 5, 7]
	for lv in range(1, 6):
		pl.weapon_level = lv
		stub.player_bullets = 0
		Spawner.player_weapon(stub, pl)
		_check(stub.player_bullets == int(expected[lv - 1]), "L%d bắn %d viên (mong %d)" % [lv, stub.player_bullets, int(expected[lv - 1])])
	pl.alive = false   # chặn auto-fire bắn nhiễu bộ đếm
	pl.queue_free()
	stub.queue_free()
	await _wait(0.05)

# ---------------------------------------------------------------- địch
func _test_enemies() -> void:
	var stub: Node = StubRun.new()
	add_child(stub)
	stub.player_pos = Vector2(360, 1050)
	for type in Balance.ENEMIES:
		var e: Node2D = EnemyScript.new()
		world.add_child(e)
		e.setup(String(type), 1.2, 1.1, 1.0, stub, Vector2(360, -60))
		var y0: float = e.position.y
		await _wait(1.5)
		_check(e.position.y > y0 + 20.0, "địch '%s' di chuyển vào màn" % type)
		await _wait(4.0)
		e.queue_free()
	await _wait(0.1)
	_check(stub.enemy_bullets > 0, "địch có bắn (hornet/bomber/tank/interceptor đã nhả đạn)")
	stub.queue_free()
	await _wait(0.05)

# ---------------------------------------------------------------- 6 boss
func _test_bosses() -> void:
	for id in BOSS_IDS:
		print("[SMOKE] --- boss: " + String(id))
		await _test_one_boss(String(id))

func _test_one_boss(id: String) -> void:
	var stub: Node = StubRun.new()
	add_child(stub)
	var boss: Node2D = (Spawner.BOSS_SCRIPTS[id] as Script).new()
	world.add_child(boss)
	boss.setup(id, 1.0, 1.0, stub)
	await _wait(0.1)
	# rig + animation
	var rig: Node2D = boss.rig
	_check(rig != null, "%s: rig tồn tại" % id)
	var anim: AnimationPlayer = rig.anim
	var anims_ok := true
	for a in REQUIRED_ANIMS:
		if anim == null or not anim.has_animation(a) or anim.get_animation(a).length <= 0.0:
			anims_ok = false
	_check(anims_ok, "%s: đủ 7 animation code-built có độ dài" % id)
	_check(rig.parts.size() >= 5, "%s: rig nhiều bộ phận (%d part)" % [id, rig.parts.size()])
	# bay vào sân
	_check(await _until(func(): return boss.state == "fight", 6.0), "%s: bay vào sân (state=fight)" % id)
	# chờ telegraph đầu tiên
	_check(await _until(func(): return boss.tele_active, 15.0), "%s: có telegraph trước khi đánh" % id)
	if boss.tele_active:
		_check(boss.tele_dur >= 0.6 - 0.0001, "%s: telegraph >= 0.6s (thực tế %.2fs)" % [id, boss.tele_dur])
		# HARD RULE: KHÔNG đạn nào sinh ra trong lúc telegraph (lấy mẫu mỗi frame)
		var before := stub.boss_bullets
		var max_during := before
		var t0 := sim_t
		while boss.tele_active and sim_t - t0 < 6.0:
			await get_tree().physics_frame
			max_during = maxi(max_during, stub.boss_bullets)
		_check(max_during == before, "%s: HARD RULE — 0 đạn trong telegraph" % id)
		_check(boss.bullets_during_telegraph == 0, "%s: bộ đếm nội bộ bullets_during_telegraph = 0" % id)
		_check(not boss.tele_active, "%s: telegraph kết thúc và bắn/thả đòn" % id)
		await _wait(0.1)
		_check(stub.boss_bullets > before or stub.enemies_spawned > 0, "%s: telegraph hết mới sinh sát thương" % id)
	# 3 pha + cuồng nộ + chết
	var died_flag := [false]
	boss.boss_died.connect(func(_b): died_flag[0] = true)
	boss.take_damage(boss.max_hp * 0.35)
	await _wait(0.1)
	_check(boss.phase >= 2, "%s: 66%% HP → pha 2" % id)
	await _until(func(): return boss.state == "fight", 5.0)
	boss.take_damage(boss.max_hp * 0.34)
	await _wait(0.1)
	_check(boss.phase == 3, "%s: 33%% HP → pha 3" % id)
	await _until(func(): return boss.state == "fight", 5.0)
	boss.take_damage(boss.max_hp * 0.30)
	await _wait(0.1)
	_check(boss.enraged, "%s: 10%% HP → cuồng nộ" % id)
	boss.take_damage(boss.hp + 1.0)
	await _wait(0.1)
	_check(boss.state == "dying", "%s: chết → anim rời từng bộ phận" % id)
	_check(await _until(func(): return boss.state == "dead", 6.0), "%s: trạng thái dead" % id)
	_check(died_flag[0], "%s: phát tín hiệu boss_died" % id)
	boss.queue_free()
	stub.queue_free()
	await _wait(0.1)

# ---------------------------------------------------------------- save
func _test_save() -> void:
	Game.add_coins(250)
	Game.add_gems(3)
	Game.save_game()
	var coins: int = Game.data["coins"]
	Game.data["coins"] = -999
	Game.load_game()
	_check(Game.data["coins"] == coins, "save/load roundtrip giữ nguyên xu")
	Game.reset_all()
	_check(int(Game.data["coins"]) >= 0 and Game.data["ship_id"] == "striker", "reset_all về mặc định")

# ---------------------------------------------------------------- RunScene thật
func _test_runscene() -> void:
	var run: Node = RunScene.new()
	run.attach(self, {"level": 3, "mode": "campaign"})
	add_child(run)
	await _wait(0.2)
	_check(run.hud != null and run.player != null and run.director != null, "RunScene dựng đủ player/hud/director")
	var layers := 0
	for c in run.get_children():
		if c is ParallaxBackground:
			for l in c.get_children():
				if l is ParallaxLayer:
					layers += 1
	_check(layers >= 3, "RunScene có nền parallax 3 lớp")
	_check(await _until(func(): return run.state == "playing", 8.0), "intro đếm ngược xong → playing")
	_check(await _until(func(): return run.enemies_node.get_child_count() > 0 or run.kills > 0, 20.0), "sóng địch đã xuất hiện")
	# pause đóng băng telegraph (mô phỏng: pause + kiểm tra tree.paused)
	run.toggle_pause()
	_check(get_tree().paused, "toggle_pause → tree.paused")
	run.toggle_pause()
	_check(not get_tree().paused, "bỏ pause")
	# bom
	run.player.bombs = 2
	run.use_bomb()
	_check(run.player.bombs == 1, "bom tiêu hao 1")
	Engine.time_scale = 1.0
	run.state = "result"   # chặn vòng thắng/thua tự nhiên
	get_tree().paused = false
	run.queue_free()
	await _wait(0.2)
