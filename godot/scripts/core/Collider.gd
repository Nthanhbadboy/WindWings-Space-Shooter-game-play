extends RefCounted
## Collider.gd — va chạm vòng tròn tự viết (không physics engine): đạn người
## chơi vs địch/boss; đạn địch vs hitbox 8px; thân địch/boss vs người chơi.
## Toạ độ global nhất quán; khoảng cách bình phương để khỏi sqrt thừa.

static func process(run: Node) -> void:
	var pr: float = float(Balance.PLAYER["hitbox_radius"])
	var pp: Vector2 = run.player.global_position
	for b in run.bullets_node.get_children():
		if b.dead:
			continue
		if b.side == 0:
			_hit_player_bullet(run, b)
		elif run.player.alive:
			var dist: float = b.global_position.distance_to(pp)
			if dist < pr + b.radius:
				var res: int = run.player.hit()
				if res > 0:
					b.dead = true
					run.fx_shake(9.0, 0.3)
					if res == 2:
						run.lives_lost += 1
						run.fx_flash(Color(1, 0.2, 0.15), 0.5, 0.35)
						run.fx_slow_mo(0.3, 0.3)
	_bodies_vs_player(run, pp, pr)

static func _hit_player_bullet(run: Node, b: Node) -> void:
	if run.boss != null and run.boss.is_alive():
		if b.global_position.distance_to(run.boss.global_position) < run.boss.radius() + b.radius:
			run.boss.take_damage(b.damage)
			b.dead = true
			run.fx_burst(b.global_position, Color("#ffd9a0"), 3)
			return
	for e in run.enemies_node.get_children():
		if e.dead:
			continue
		if b.global_position.distance_to(e.global_position) < e.radius() * 0.85 + b.radius:
			e.damage(b.damage, true)
			b.dead = true
			run.fx_burst(b.global_position, Color("#bff0ff"), 2)
			break

static func _bodies_vs_player(run: Node, pp: Vector2, pr: float) -> void:
	if not run.player.alive:
		return
	for e in run.enemies_node.get_children():
		if e.dead:
			continue
		if e.global_position.distance_to(pp) < e.radius() * 0.7 + pr + 2.0:
			var res: int = run.player.hit()
			if res > 0:
				e.damage(e.hp, true)   # kamikaze nổ tung
				if res == 2:
					run.lives_lost += 1
	if run.boss != null and run.boss.is_alive():
		if run.boss.global_position.distance_to(pp) < run.boss.radius() + pr:
			var res: int = run.player.hit()
			if res == 2:
				run.lives_lost += 1

static func cull(run: Node) -> void:
	for b in run.bullets_node.get_children():
		if b.dead:
			b.queue_free()
