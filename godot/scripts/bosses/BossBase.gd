extends Node2D
## BossBase.gd — "linh hồn trò chơi". Máy trạng thái: enter -> fight ->
## transition (đổi pha @0.66/@0.33 HP) -> dying. Cuồng nộ @0.10 HP.
## HARD RULE: mọi đòn đánh đều qua telegraph >= BOSS_RULES.telegraph_min
## (0.6s, enrage x0.7 nhưng vẫn kẹp sàn 0.6); đạn CHỈ sinh ra trong
## _fire_pattern() khi telegraph đã hết — không có đường nào khác.
## Pause đóng băng _physics_process => telegraph đứng yên, đúng luật.

signal boss_died(boss: Node2D)
signal phase_changed(boss: Node2D, p: int)
signal enraged(boss: Node2D)
signal telegraph_started(boss: Node2D, dur: float)
signal telegraph_fired(boss: Node2D)


var boss_id := ""
var data: Dictionary = {}
var run: Node = null
var max_hp := 1.0
var hp := 1.0
var bullet_mul := 1.0
var phase := 1
var enraged := false
var state := "enter"          # enter | fight | transition | dying | dead
var t := 0.0
var fire_cd_t := 2.2
var tele_active := false
var tele_t := 0.0
var tele_dur := 0.0
var tele_pattern: Dictionary = {}
var tele_name := ""
var transition_t := 0.0
var death_t := 0.0
var shots_fired := 0
var attack_count := 0
var hurt_t := 0.0
var rig: Node2D = null
var telegraph_fx: Node2D = null

## Test hook: số đạn boss sinh ra TRONG lúc telegraph đang chạy — luôn = 0.
var bullets_during_telegraph := 0

func setup(id: String, hp_mul: float, b_mul: float, run_ref: Node) -> void:
	boss_id = id
	data = Balance.BOSSES[id]
	max_hp = float(data["hp"]) * hp_mul
	hp = max_hp
	bullet_mul = b_mul
	run = run_ref

func _ready() -> void:
	z_index = 8
	position = Vector2(Balance.VIEW.x * 0.5, float(Balance.BOSS_RULES["enter_y"]))
	rig = _make_rig()
	add_child(rig)
	rig.call("build", self)
	telegraph_fx = Node2D.new()
	telegraph_fx.set_script(preload("res://scripts/bosses/TelegraphFx.gd"))
	add_child(telegraph_fx)

func _make_rig() -> Node2D:
	push_error("BossBase._make_rig must be overridden")
	return Node2D.new()

func _physics_process(delta: float) -> void:
	t += delta
	if hurt_t > 0.0:
		hurt_t -= delta
	match state:
		"enter":
			position.y += float(Balance.BOSS_RULES["enter_speed"]) * delta
			if position.y >= float(Balance.BOSS_RULES["idle_y"]):
				position.y = float(Balance.BOSS_RULES["idle_y"])
				state = "fight"
				fire_cd_t = 1.1
		"fight":
			_sway(delta)
			if tele_active:
				tele_t += delta
				telegraph_fx.call("set_progress", tele_t / tele_dur)
				if tele_t >= tele_dur:
					_fire_pattern()
			else:
				fire_cd_t -= delta
				if fire_cd_t <= 0.0:
					_begin_attack()
		"transition":
			transition_t -= delta
			_sway(delta)
			if transition_t <= 0.0:
				state = "fight"
				fire_cd_t = 0.7
		"dying":
			death_t -= delta
			if death_t <= 0.0:
				state = "dead"
				boss_died.emit(self)
	_check_phase()

func _sway(_delta: float) -> void:
	position.x = Balance.VIEW.x * 0.5 + sin(t * 0.55 + phase) * float(Balance.BOSS_RULES["drift_speed"])
	position.y = float(Balance.BOSS_RULES["idle_y"]) + sin(t * 0.83) * 16.0

func _check_phase() -> void:
	if state == "dying" or state == "dead":
		return
	var ratio := hp / max_hp
	if phase == 1 and ratio <= float(Balance.BOSS_RULES["phase2_at"]):
		_enter_phase(2)
	elif phase == 2 and ratio <= float(Balance.BOSS_RULES["phase3_at"]):
		_enter_phase(3)
	if phase == 3 and ratio <= float(Balance.BOSS_RULES["enrage_at"]) and not enraged:
		enraged = true
		rig.call("play", "enrage")
		enraged.emit(self)
		Sfx.play("boss_roar")

func _enter_phase(p: int) -> void:
	phase = p
	state = "transition"
	transition_t = float(Balance.BOSS_RULES["transition_time"])
	# HARD RULE an toàn: huỷ telegraph đang chờ khi đổi pha — không sát thương
	if tele_active:
		tele_active = false
		telegraph_fx.call("finish")
	rig.call("play", "phase_shift")
	if p == 3:
		hp = minf(max_hp * float(Balance.BOSS_RULES["phase3_at"]) + max_hp * float(Balance.BOSS_RULES["phase3_heal"]), hp + max_hp * float(Balance.BOSS_RULES["phase3_heal"]))
	phase_changed.emit(self, p)
	if run != null:
		run.boss_phase_changed(self, p)
	Sfx.play("boss_phase")

# ---------------------------------------------------------------- tấn công
func _begin_attack() -> void:
	tele_name = _pick_pattern()
	tele_pattern = Balance.PATTERNS[tele_name]
	var raw := float(tele_pattern["telegraph"])
	var mul := float(Balance.BOSS_RULES["enrage_telegraph_mul"]) if enraged else 1.0
	tele_dur = maxf(float(Balance.BOSS_RULES["telegraph_min"]), raw * mul)
	tele_active = true
	tele_t = 0.0
	rig.call("play", "charge")
	telegraph_fx.call("begin", tele_pattern, self, _pattern_color(tele_pattern))
	telegraph_started.emit(self, tele_dur)
	Sfx.play("telegraph")

func _pick_pattern() -> String:
	var pool: Array = data["patterns"].duplicate()
	if phase >= 2:
		pool.append_array(data["patterns"])
	# pha 3: mỗi đòn thứ 3 là đòn chữ ký (cuối danh sách)
	if phase == 3 and attack_count % 3 == 2 and pool.size() > 1:
		return String(pool[pool.size() - 1])
	var pick := String(pool[randi() % pool.size()])
	if pick == tele_name and pool.size() > 1:
		pick = String(pool[(pool.find(pick) + 1) % pool.size()])
	return pick

func _fire_pattern() -> void:
	tele_active = false
	shots_fired += 1
	attack_count += 1
	telegraph_fx.call("finish")
	rig.call("play", "fire")
	_execute_pattern(tele_pattern)
	telegraph_fired.emit(self)
	var cd: float = float((Balance.BOSS_RULES["attack_cd"] as Array)[clampi(phase - 1, 0, 2)])
	fire_cd_t = cd * (float(Balance.BOSS_RULES["enrage_cd_mul"]) if enraged else 1.0)
	if run != null:
		run.boss_fired(self, tele_name)
	Sfx.play("boss_fire")

func _pattern_color(pat: Dictionary) -> Color:
	match String(pat.get("color", "boss")):
		"enemy":
			return Balance.BULLET["enemy_color"]
		"fast":
			return Balance.BULLET["boss_fast"]
		_:
			return Balance.BULLET["boss_color"]

func _aim_dir() -> Vector2:
	if run != null:
		return (run.player_position() - global_position).normalized()
	return Vector2.DOWN

func _boss_bullet(local_pos: Vector2, vel: Vector2, pat: Dictionary, homing := 0.0) -> void:
	if run == null:
		return
	if tele_active:
		bullets_during_telegraph += 1   # không bao giờ được > 0
	run.spawn_boss_bullet(global_position + local_pos, vel * bullet_mul, _pattern_color(pat), float(pat.get("radius", 8)), homing)

## Thi triển 16 kind — mỗi boss chọn bộ pattern riêng trong Balance.BOSSES.
func _execute_pattern(pat: Dictionary) -> void:
	var kind := String(pat["kind"])
	var aim := _aim_dir()
	match kind:
		"aimed":
			var n: int = int(pat.get("count", 3))
			var sp: float = float(pat.get("spread", 0.16))
			for i in n:
				var off := (float(i) - float(n - 1) * 0.5) * sp
				_boss_bullet(Vector2.ZERO, aim.rotated(off) * float(pat["speed"]), pat)
		"fan":
			var n: int = int(pat["count"])
			var arc := deg_to_rad(float(pat["arc"]))
			for i in n:
				var off := lerpf(-arc * 0.5, arc * 0.5, float(i) / float(maxi(1, n - 1)))
				_boss_bullet(Vector2.ZERO, aim.rotated(off) * float(pat["speed"]), pat)
		"ring":
			var n: int = int(pat["count"])
			var base := float(shots_fired) * 0.31
			for i in n:
				var a := base + TAU * float(i) / float(n)
				_boss_bullet(Vector2.ZERO, Vector2.RIGHT.rotated(a) * float(pat["speed"]), pat)
		"ring2":
			var n: int = int(pat["count"])
			var off2 := float(pat.get("offset2", 0.17))
			var spin2 := float(pat.get("spin2", 1.0))
			for i in n:
				var a := TAU * float(i) / float(n)
				_boss_bullet(Vector2.ZERO, Vector2.RIGHT.rotated(a) * float(pat["speed"]), pat)
				_boss_bullet(Vector2.ZERO, Vector2.RIGHT.rotated(a + off2) * float(pat["speed"]) * spin2, pat)
		"spiral":
			var arms: int = int(pat["arms"])
			var rings: int = int(pat["rings"])
			for j in rings:
				for i in arms:
					var a := float(shots_fired) * 0.55 + TAU * float(i) / float(arms) + float(j) * 0.42
					_boss_bullet(Vector2.ZERO, Vector2.RIGHT.rotated(a) * (float(pat["speed"]) - float(j) * 18.0), pat)
		"sweep":
			var n: int = int(pat["count"])
			var arc := deg_to_rad(float(pat["arc"]))
			var speeds: Array = pat["speeds"]
			var dir := 1.0 if shots_fired % 2 == 0 else -1.0
			for s_i in speeds.size():
				for i in n:
					var off := lerpf(-arc * 0.5, arc * 0.5, float(i) / float(maxi(1, n - 1))) * dir
					_boss_bullet(Vector2.ZERO, aim.rotated(off) * float(speeds[s_i]), pat)
		"dash":
			_boss_bullet(rig.call("muzzle", "stinger"), aim * float(pat["speed"]), pat)
			var orbs: int = int(pat.get("orbs", 0))
			for i in orbs:
				var a := TAU * float(i) / float(maxi(1, orbs))
				_boss_bullet(Vector2.ZERO, Vector2.RIGHT.rotated(a) * 150.0, pat, 1.4)
		"summon":
			var n: int = int(pat.get("summon_count", 2))
			for i in n:
				if run != null:
					run.spawn_enemy(String(pat["summon"]), Balance.VIEW.x * (float(i) + 1.0) / float(n + 1), position.y + 40.0)
			if pat.has("ring"):
				var m: int = int(pat["ring"])
				for i in m:
					var a := TAU * float(i) / float(m) + 0.2
					_boss_bullet(Vector2.ZERO, Vector2.RIGHT.rotated(a) * float(pat["speed"]), pat)
			if pat.has("fan"):
				var m: int = int(pat["fan"])
				for i in m:
					var off := lerpf(-0.6, 0.6, float(i) / float(maxi(1, m - 1)))
					_boss_bullet(Vector2.ZERO, aim.rotated(off) * float(pat["speed"]), pat)
			if pat.has("aimed"):
				var m: int = int(pat["aimed"])
				for i in m:
					var off := (float(i) - float(m - 1) * 0.5) * 0.18
					_boss_bullet(Vector2.ZERO, aim.rotated(off) * float(pat["speed"]), pat)
		"broadside":
			var n: int = int(pat["count"])
			var arc := deg_to_rad(float(pat["arc"]))
			for side in [-1.0, 1.0]:
				var mz: Vector2 = rig.call("muzzle", "wing_l" if side < 0.0 else "wing_r")
				if mz == Vector2.ZERO:
					mz = Vector2(side * float(data["radius"]), 0)
				var center := Vector2(side * 0.5, 1.0).normalized()
				for i in n:
					var off := lerpf(-arc * 0.5, arc * 0.5, float(i) / float(maxi(1, n - 1)))
					_boss_bullet(mz, center.rotated(off) * float(pat["speed"]), pat)
		"beam_row":
			var n: int = int(pat["count"])
			var dir := aim if bool(pat.get("aim", false)) else Vector2.DOWN.rotated(sin(float(shots_fired) * 1.3) * 0.7)
			for i in n:
				_boss_bullet(dir * float(i) * 26.0, dir * float(pat["speed"]), pat)
		"wall":
			var n: int = int(pat["count"])
			var gap: int = int(pat.get("gap", 1))
			var px: float = float(run.player_position().x - global_position.x) if run != null else 0.0
			var gap_i := clampi(int((px + Balance.VIEW.x * 0.5) / Balance.VIEW.x * float(n)), gap, n - 1 - gap)
			for i in n:
				if absi(i - gap_i) < gap:
					continue
				var x := (float(i) + 0.5) / float(n) * Balance.VIEW.x - position.x
				_boss_bullet(Vector2(x, -20.0), Vector2.DOWN * float(pat["speed"]), pat)
		"slam":
			var n: int = int(pat["count"])
			var px: float = float(run.player_position().x - global_position.x) if run != null else 0.0
			for i in n:
				var x := px + (float(i) - float(n - 1) * 0.5) * 86.0
				_boss_bullet(Vector2(x, 0), Vector2.DOWN.rotated(clampf(x * 0.0004, -0.2, 0.2)) * float(pat["speed"]), pat)
		"spikes":
			var n: int = int(pat["count"])
			for i in n:
				var a := TAU * float(i) / float(n) + 0.4
				_boss_bullet(Vector2.ZERO, Vector2.RIGHT.rotated(a) * float(pat["speed"]), pat, float(pat.get("homing", 1.6)))
		"twin":
			var n: int = int(pat["count"])
			var sp: float = float(pat.get("spread", 0.1))
			for side in [-1.0, 1.0]:
				var mz: Vector2 = rig.call("muzzle", "cannon_l" if side < 0.0 else "cannon_r")
				if mz == Vector2.ZERO:
					mz = Vector2(side * float(data["radius"]) * 0.8, 30.0)
				for i in n:
					var off := (float(i) - float(n - 1) * 0.5) * sp
					_boss_bullet(mz, aim.rotated(off) * float(pat["speed"]), pat)
		"homing":
			var n: int = int(pat["count"])
			for i in n:
				var a := TAU * float(i) / float(n)
				_boss_bullet(Vector2.ZERO, Vector2.RIGHT.rotated(a) * float(pat["speed"]), pat, float(pat.get("homing", 2.0)))
		"core":
			var m: int = int(pat["ring"])
			for i in m:
				var a := TAU * float(i) / float(m) + float(shots_fired) * 0.2
				_boss_bullet(Vector2.ZERO, Vector2.RIGHT.rotated(a) * float(pat["speed"]), pat)
			var l: int = int(pat.get("lance", 3))
			for i in l:
				var off := (float(i) - float(l - 1) * 0.5) * 0.1
				_boss_bullet(Vector2.ZERO, aim.rotated(off) * float(pat.get("lance_speed", 700.0)), pat)
		"hell":
			var n: int = int(pat["count"])
			var rings: int = int(pat["rings"])
			for j in rings:
				for i in n:
					var a := TAU * float(i) / float(n) + float(j) * 0.21 + float(shots_fired) * 0.37
					_boss_bullet(Vector2.ZERO, Vector2.RIGHT.rotated(a) * (float(pat["speed"]) + float(j) * 40.0), pat)
		_:
			push_error("BossBase: unknown pattern kind " + kind)

# ---------------------------------------------------------------- chịu đòn
func take_damage(dmg: float) -> void:
	if state == "dying" or state == "dead":
		return
	hp -= dmg
	if hurt_t <= 0.0:
		hurt_t = R_HURT_CD
		rig.call("play", "hurt")
	if run != null:
		run.boss_hp_changed(self)
	if hp <= 0.0:
		hp = 0.0
		_die()

const R_HURT_CD := 0.2

func _die() -> void:
	state = "dying"
	death_t = float(Balance.BOSS_RULES["death_time"])
	if tele_active:
		tele_active = false
		telegraph_fx.call("finish")
	rig.call("play", "death")
	Sfx.play("explosion_big")
	if run != null:
		run.fx_slow_mo(0.25, 0.9)
		run.fx_shake(16.0, 0.9)
		run.fx_flash(Color(1, 0.95, 0.85), 0.55, 0.5)

func radius() -> float:
	return float(data["radius"]) * float(Balance.BOSS_RULES["contact_radius_mul"])

func is_alive() -> bool:
	return state != "dead" and state != "dying"
