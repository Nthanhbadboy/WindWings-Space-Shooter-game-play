extends RefCounted
## Loot.gd — kinh tế trận đánh: điểm + combo khi hạ địch, tỉ lệ rơi powerup
## (bảng cân bằng trong Balance.POWERUP.kinds), hiệu ứng nhặt vật phẩm.

static func on_enemy_killed(run: Node, e: Node2D, by_player: bool) -> void:
	run.fx_burst(e.global_position, Color("#ffc46a"), 14)
	Sfx.play("explosion")
	if not by_player:
		return
	run.kills += 1
	run.combo += 1
	run.combo_t = float(Balance.PLAYER["combo_time"])
	var mult := 1.0 + minf(float(run.combo) * 0.02, float(Balance.ECONOMY["combo_max"]) - 1.0)
	var gained := int(float(e.score_value) * mult)
	run.score += gained
	run.coins_earned += e.coin_value
	run.fx.call("popup", e.global_position, "+%d" % gained, Color("#ffec22") if run.combo < 8 else Color("#ff9d3d"))
	run.hud.set_score(run.score, run.combo)
	drop_roll(run, e.global_position)

static func drop_roll(run: Node, pos: Vector2) -> void:
	if randf() >= float(Balance.POWERUP["drop_chance"]):
		return
	var table: Array = Balance.POWERUP["kinds"]
	var acc := 0.0
	var pick := String(table[0][0])
	var r := randf()
	for row in table:
		acc += float(row[1])
		if r <= acc:
			pick = String(row[0])
			break
	var pu := Node2D.new()
	pu.set_script(preload("res://scripts/core/Powerup.gd"))
	pu.kind = pick
	pu.run = run
	run.powerups_node.add_child(pu)
	pu.global_position = pos

static func apply_powerup(run: Node, kind: String, pos: Vector2) -> void:
	match kind:
		"weapon":
			run.player.raise_weapon()
			run.fx.call("popup", pos, "SỨC MẠNH +1", Color("#ffb700"))
		"shield":
			run.player.add_shield()
			run.fx.call("popup", pos, "KHIÊN +1", Color("#46c6f4"))
		"bomb":
			run.player.bombs += 1
			run.player.bombs_changed.emit(run.player.bombs)
			run.fx.call("popup", pos, "BOM +1", Color("#e23a2e"))
		"heal":
			run.player.heal(int(Balance.PLAYER["heal_amount"]))
			run.fx.call("popup", pos, "HỒI PHỤC", Color("#7df05a"))
		"drone":
			run.temp_drone_t = float(Balance.PLAYER["temp_drone_time"])
			run.drones.refresh(int(run.player.stats["drones"]) + 1)
			run.fx.call("popup", pos, "VỆ TINH!", Color("#c890ff"))
		"magnet":
			run.magnet_t = float(Balance.POWERUP["magnet_duration"])
			run.fx.call("popup", pos, "NAM CHÂM!", Color("#ff5db1"))

static func magnet_radius(run: Node) -> float:
	var base: float = float(run.player.stats["magnet"])
	return base * (1.6 if run.magnet_t > 0.0 else 1.0)
