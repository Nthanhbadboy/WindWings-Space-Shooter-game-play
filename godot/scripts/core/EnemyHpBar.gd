extends Node2D
## EnemyHpBar.gd — thanh HP nhỏ trên đầu địch (chỉ hiện khi đã mất máu).

var ratio := 1.0
var width := 44.0

func set_ratio(r: float) -> void:
	ratio = clampf(r, 0.0, 1.0)
	queue_redraw()

func _draw() -> void:
	draw_rect(Rect2(-width * 0.5, 0, width, 5), Color(0, 0, 0, 0.55))
	var c := Color("#e23a2e") if ratio < 0.34 else (Color("#ffb700") if ratio < 0.67 else Color("#7df05a"))
	draw_rect(Rect2(-width * 0.5 + 1, 1, (width - 2) * ratio, 3), c)
