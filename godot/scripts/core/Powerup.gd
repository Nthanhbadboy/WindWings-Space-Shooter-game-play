extends Node2D
## Powerup.gd — huy hiệu rơi xuống, rung rinh sine; NAM CHÂM hút khi vào
## tầm (magnet_duration từ tech). Nhặt → run.apply_powerup(kind).

const KIND_COLORS := {
	"weapon": Color("#ffb700"),
	"shield": Color("#46c6f4"),
	"bomb": Color("#e23a2e"),
	"heal": Color("#7df05a"),
	"drone": Color("#c890ff"),
	"magnet": Color("#ff5db1"),
}
const KIND_ICONS := {
	"weapon": "res://assets/icons/ic_cannon.png",
	"shield": "res://assets/icons/ic_shield.png",
	"bomb": "res://assets/icons/ic_skull.png",
	"heal": "res://assets/icons/ic_star.png",
	"drone": "res://assets/icons/ic_drone.png",
	"magnet": "res://assets/icons/ic_magnet.png",
}

var kind := "weapon"
var run: Node = null
var t := 0.0
var vel := Vector2(0, float(Balance.POWERUP["fall_speed"]))
var magnet := false
var collected := false

var sprite: Sprite2D

func _ready() -> void:
	z_index = 12
	sprite = Sprite2D.new()
	var path: String = KIND_ICONS.get(kind, "")
	if path != "" and ResourceLoader.exists(path):
		sprite.texture = load(path)
		var s := 52.0 / maxf(sprite.texture.get_width(), sprite.texture.get_height())
		sprite.scale = Vector2(s, s)
	add_child(sprite)

func _physics_process(delta: float) -> void:
	if collected:
		return
	t += delta
	if magnet and run != null:
		var p: Vector2 = run.player_position()
		var d := p - global_position
		if d.length() < 26.0:
			_collect()
			return
		vel = d.normalized() * 560.0
	else:
		vel.y = float(Balance.POWERUP["fall_speed"])
		vel.x = sin(t * 2.2) * 36.0
	position += vel * delta
	sprite.rotation = sin(t * 3.0) * 0.16
	# nam châm tự kích hoạt khi player đủ gần (kể cả chưa nhặt magnet)
	if run != null:
		var pr: float = run.player_position().distance_to(global_position)
		if pr < 40.0:
			_collect()
			return
		if run.has_magnet() and pr < run.magnet_radius():
			magnet = true
	if position.y > Balance.VIEW.y + 60.0:
		queue_free()

func _collect() -> void:
	collected = true
	if run != null:
		run.apply_powerup(kind, position)
	if kind in KIND_COLORS and run != null:
		run.fx_burst(position, KIND_COLORS[kind], 10)
	Sfx.play("powerup")
	queue_free()

func _draw() -> void:
	var c: Color = KIND_COLORS.get(kind, Color.WHITE)
	draw_arc(Vector2.ZERO, 30.0, 0, TAU, 28, Color(c, 0.85), 3.0)
	draw_arc(Vector2.ZERO, 34.0 + sin(t * 5.0) * 3.0, 0, TAU, 28, Color(c, 0.3), 2.0)
