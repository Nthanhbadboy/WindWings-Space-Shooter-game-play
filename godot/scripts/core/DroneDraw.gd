extends Node2D
## DroneDraw.gd — vệ tinh nhỏ vẽ bằng code: lõi sáng + cánh năng lượng.

var t := randf() * TAU

func _process(delta: float) -> void:
	t += delta
	rotation = sin(t * 3.0) * 0.3
	queue_redraw()

func _draw() -> void:
	draw_circle(Vector2.ZERO, 9.0, Color("#2f9fe0"))
	draw_circle(Vector2.ZERO, 5.0, Color("#9be8ff"))
	draw_circle(Vector2.ZERO, 2.0, Color.WHITE)
	draw_line(Vector2(-13, 0), Vector2(-7, 0), Color("#ffb700"), 3.0)
	draw_line(Vector2(13, 0), Vector2(7, 0), Color("#ffb700"), 3.0)
