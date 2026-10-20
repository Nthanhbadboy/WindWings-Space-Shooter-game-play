extends Node2D
## Vẽ vòng hitbox thật (8px) để người chơi/test THẤY hitbox nhỏ hơn sprite.

func _draw() -> void:
	var r: float = Balance.PLAYER["hitbox_radius"]
	draw_arc(Vector2.ZERO, r, 0, TAU, 24, Color(1, 1, 1, 0.9), 2.0)
	draw_circle(Vector2.ZERO, 2.0, Color(1, 0.3, 0.3, 0.9))
