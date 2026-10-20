extends RefCounted
## Spawner.gd — nhà máy sinh thực thể cho RunScene: địch, boss (6 chủ thể),
## đạn (2 phe), và loạt bắn của người chơi theo Balance.WEAPONS L1–L5.

const BOSS_SCRIPTS := {
	"void_tyrant": preload("res://scripts/bosses/VoidTyrantBoss.gd"),
	"queen_wasp": preload("res://scripts/bosses/QueenWaspBoss.gd"),
	"imperator": preload("res://scripts/bosses/ImperatorBoss.gd"),
	"void_spider": preload("res://scripts/bosses/VoidSpiderBoss.gd"),
	"sentinel_eye": preload("res://scripts/bosses/SentinelEyeBoss.gd"),
	"omega_dreadnought": preload("res://scripts/bosses/OmegaDreadnoughtBoss.gd"),
}

static func enemy(run: Node, type: String, x: float, y: float) -> void:
	var e := Node2D.new()
	e.set_script(preload("res://scripts/core/Enemy.gd"))
	e.call("setup", type, run.hp_mul, run.speed_mul, run.bullet_mul, run, Vector2(x, y))
	run.enemies_node.add_child(e)

static func boss(run: Node, id: String) -> void:
	var script: Script = BOSS_SCRIPTS[id]
	run.boss = script.new()
	run.boss.setup(id, run.hp_mul, run.bullet_mul, run)
	run.world.add_child(run.boss)
	run.boss.boss_died.connect(run._on_boss_died)
	run.boss.phase_changed.connect(func(_b, p): run.hud.set_boss_phase(p); run.fx_shake(10.0, 0.4))
	run.boss.enraged.connect(run.boss_enraged)
	var bdata: Dictionary = Balance.BOSSES[id]
	run.hud.show_boss(String(bdata["name"]), run.boss.max_hp)
	run.fx_shake(8.0, 0.6)
	run.fx.call("popup", Vector2(Balance.VIEW.x * 0.5, Balance.VIEW.y * 0.3), String(bdata["name"]), Color("#ff5d7a"))
	Sfx.play("boss_roar")

static func bullet(run: Node, side: int, pos: Vector2, vel: Vector2, color: Color, radius: float, dmg: float, homing: float) -> void:
	var b := Node2D.new()
	b.set_script(preload("res://scripts/core/Bullet.gd"))
	run.bullets_node.add_child(b)
	b.side = side
	b.vel = vel
	b.color = color
	b.radius = radius
	b.damage = dmg
	b.homing = homing
	b.run = run
	b.global_position = pos

static func player_weapon(run: Node, p: Node2D) -> void:
	var pat: Dictionary = Balance.WEAPONS[clampi(p.weapon_level, 1, 5) - 1]
	var dmg: float = float(p.stats["dmg"]) * float(pat["dmg"])
	var spd: float = float(pat["speed"])
	var col: Color = Balance.BULLET["player_color"]
	var r: float = float(Balance.BULLET["player_radius"])
	var angles: Array = pat["angles"]
	if pat.has("offset"):
		# L2: hai nòng song song
		var o: float = float(pat["offset"])
		run.spawn_player_bullet(p.global_position + Vector2(-o, 10), Vector2.UP * spd, dmg, r, col)
		run.spawn_player_bullet(p.global_position + Vector2(o, 10), Vector2.UP * spd, dmg, r, col)
	else:
		for a in angles:
			var rot := deg_to_rad(float(a))
			var off := Vector2(-12.0 if float(a) < 0.0 else (12.0 if float(a) > 0.0 else 0.0), 6.0)
			run.spawn_player_bullet(p.global_position + off, Vector2.UP.rotated(rot) * spd, dmg, r, col)
	if pat.has("side_laser"):
		# L5: hai tia sườn chếch nhẹ
		run.spawn_player_bullet(p.global_position + Vector2(-30, 16), Vector2(-0.22, -1).normalized() * spd * 0.95, dmg * 0.6, r * 0.8, Color("#b7f3ff"))
		run.spawn_player_bullet(p.global_position + Vector2(30, 16), Vector2(0.22, -1).normalized() * spd * 0.95, dmg * 0.6, r * 0.8, Color("#b7f3ff"))
	run.drones.fire(dmg)
	Sfx.play("shoot")
