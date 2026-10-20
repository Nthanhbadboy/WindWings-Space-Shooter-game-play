extends Node2D
## Bullet.gd — đạn vẽ bằng code (màu ngôn ngữ đạn: người chơi cyan, địch
## đỏ/hồng, boss tím/cam). Va chạm vòng tròn do RunScene xử lý tập trung.

enum Side { PLAYER, ENEMY }

var side: int = Side.PLAYER
var vel := Vector2.ZERO
var radius := 6.0
var damage := 1.0
var color := Color("#58e6ff")
var glow := true
var homing := 0.0          # rad/s tối đa (0 = không đuổi)
var pierce := 0
var t := 0.0
var dead := false
var run: Node = null

func _ready() -> void:
	z_index = 15 if side == Side.PLAYER else 14

func _process(delta: float) -> void:
	t += delta
	position += vel * delta
	if homing > 0.0 and run != null:
		var to: Vector2 = run.player_position() - global_position
		var d := wrapf(vel.angle_to(to), -PI, PI)
		vel = vel.rotated(clampf(d, -homing * delta, homing * delta))
	queue_redraw()
	var m := 80.0
	if position.x < -m or position.x > Balance.VIEW.x + m or position.y < -m or position.y > Balance.VIEW.y + m:
		dead = true

func _draw() -> void:
	if side == Side.PLAYER:
		# đạn người chơi: viên nang cyan nhỏ, sáng
		if glow:
			draw_circle(Vector2.ZERO, radius * 2.2, Color(color, 0.18))
		draw_circle(Vector2.ZERO, radius, color)
		draw_circle(Vector2.ZERO, radius * 0.5, Color(1, 1, 1, 0.9))
	else:
		# đạn địch/boss: tròn hồng-tím + viền sáng (bullet-hell đọc rõ)
		if glow:
			draw_circle(Vector2.ZERO, radius * 2.0, Color(color, 0.22))
		draw_circle(Vector2.ZERO, radius, color)
		draw_arc(Vector2.ZERO, radius, 0, TAU, 16, Color(1, 1, 1, 0.85), 2.0)
		draw_circle(Vector2.ZERO, radius * 0.35, Color(1, 1, 1, 0.95))
