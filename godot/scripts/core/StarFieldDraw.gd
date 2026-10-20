extends Node2D
## Vẽ trường sao tất định (seed cố định) trong ô 720x1280 — lớp xa nhất,
## lặp vô tận nhờ motion_mirroring của ParallaxLayer cha.

var _stars: Array[Dictionary] = []

func _ready() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 424242
	var count: int = Balance.PARALLAX["stars_count"]
	for i in range(count):
		var tier := rng.randi_range(0, 2)
		_stars.append({
			"pos": Vector2(rng.randf_range(0, Balance.VIEW.x), rng.randf_range(0, Balance.VIEW.y)),
			"r": [1.0, 1.6, 2.4][tier],
			"a": [0.35, 0.6, 0.95][tier],
			"tw": rng.randf_range(0.0, TAU),
		})
	set_z_index(-10)

func _process(_delta: float) -> void:
	queue_redraw() # sao nhấp nháy

func _draw() -> void:
	var t := float(Time.get_ticks_msec()) / 1000.0
	for s in _stars:
		var twinkle := 0.75 + 0.25 * sin(t * 2.0 + s["tw"])
		var col := Color(0.85, 0.92, 1.0, s["a"] * twinkle)
		draw_circle(s["pos"], s["r"], col)
