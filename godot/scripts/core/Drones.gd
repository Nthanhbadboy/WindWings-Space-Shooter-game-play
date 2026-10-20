extends Node2D
## Drones.gd — vệ tinh bay quanh tàu (tech drone + pickup tạm thời), tự bắn
## theo nhịp volley của tàu. Quỹ đạo tròn, làm mượt delta-time.

var run: Node = null
var count := 0
var t := 0.0
var nodes: Array[Node2D] = []

func refresh(n: int) -> void:
	if n == count:
		return
	count = n
	for d in nodes:
		d.queue_free()
	nodes.clear()
	for i in count:
		var d := Node2D.new()
		d.set_script(preload("res://scripts/core/DroneDraw.gd"))
		add_child(d)
		nodes.append(d)

func update(delta: float, player: Node2D) -> void:
	t += delta
	if count == 0:
		return
	global_position = player.global_position
	var r: float = Balance.PLAYER["drone_orbit_r"]
	var w: float = Balance.PLAYER["drone_orbit_w"]
	for i in nodes.size():
		var a := t * w + TAU * float(i) / float(nodes.size())
		nodes[i].position = Vector2(cos(a), sin(a) * 0.55) * r

func fire(dmg: float) -> void:
	for d in nodes:
		if run != null:
			run.spawn_player_bullet(d.global_position + Vector2(0, -14), Vector2(0, -Balance.BULLET["player_speed"] * 0.92), dmg * Balance.PLAYER["drone_dmg_mul"], 4.0, Color("#9be8ff"))
