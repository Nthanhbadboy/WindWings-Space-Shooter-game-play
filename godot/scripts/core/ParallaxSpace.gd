extends ParallaxBackground
## ParallaxSpace.gd — nền không gian dọc 3 lớp ParallaxLayer theo yêu cầu:
##   1. sao xa   (motion_scale nhỏ nhất, loop bằng motion_mirroring)
##   2. tinh vân (NoiseTexture2D seamless, trôi giữa)
##   3. hành tinh gần (motion_scale lớn nhất, chu kỳ loop 2560px)
## Cuộn vô tận: scroll_offset chạy trong _process, mỗi lớp tự lặp nhờ
## motion_mirroring — không bao giờ hết nền.

var speed: float = Balance.PARALLAX["scroll_speed"]
var chapter := 1
var stars_layer: ParallaxLayer
var nebula_layer: ParallaxLayer
var planet_layer: ParallaxLayer
var _nebula_sprite: Sprite2D
var _planet_nodes: Array[Node2D] = []

func _ready() -> void:
	_build_stars()
	_build_nebula()
	_build_planets()
	set_theme(chapter)

func _process(delta: float) -> void:
	# nền trôi XUỐNG (tàu đang bay lên): scroll_offset.y giảm dần
	scroll_offset = scroll_offset - Vector2(0, speed * delta)

## Đổi bảng màu nền theo chương (1..6).
func set_theme(new_chapter: int) -> void:
	chapter = clampi(new_chapter, 1, Balance.CHAPTER_COUNT)
	var c: Dictionary = Balance.CHAPTERS[chapter - 1]
	if _nebula_sprite == null:
		return   # chưa vào tree — _ready sẽ áp lại đúng chương đã nhớ
	var tex := _nebula_sprite.texture as NoiseTexture2D
	if tex != null and tex.color_ramp != null:
		var ramp := tex.color_ramp
		ramp.set_color(0, Color(c["nebula_a"], 0.0))
		ramp.set_color(1, Color(c["nebula_b"], 0.55))
	for p in _planet_nodes:
		if p.has_method("set_palette"):
			p.call("set_palette", c["planet"], c["tint"])

# ---------------------------------------------------------------- lớp 1: sao
func _build_stars() -> void:
	stars_layer = ParallaxLayer.new()
	stars_layer.motion_scale = Balance.PARALLAX["stars_scale"]
	stars_layer.motion_mirroring = Balance.PARALLAX["stars_mirror"]
	add_child(stars_layer)
	var field := Node2D.new()
	field.set_script(preload("res://scripts/core/StarFieldDraw.gd"))
	stars_layer.add_child(field)

# ------------------------------------------------------------ lớp 2: tinh vân
func _build_nebula() -> void:
	nebula_layer = ParallaxLayer.new()
	nebula_layer.motion_scale = Balance.PARALLAX["nebula_scale"]
	nebula_layer.motion_mirroring = Balance.PARALLAX["nebula_mirror"]
	add_child(nebula_layer)
	_nebula_sprite = Sprite2D.new()
	var noise := FastNoiseLite.new()
	noise.seed = 1337
	noise.frequency = 0.0035
	noise.fractal_octaves = 5
	var tex := NoiseTexture2D.new()
	tex.width = Balance.VIEW.x
	tex.height = Balance.VIEW.y
	tex.seamless = true
	tex.as_normal_map = false
	var ramp := Gradient.new()
	ramp.set_color(0, Color(0.2, 0.1, 0.5, 0.0))
	ramp.set_color(1, Color(0.1, 0.4, 0.8, 0.55))
	tex.color_ramp = ramp
	tex.noise = noise
	_nebula_sprite.texture = tex
	_nebula_sprite.centered = false
	_nebula_sprite.modulate = Color(1, 1, 1, 0.85)
	nebula_layer.add_child(_nebula_sprite)

# --------------------------------------------------------- lớp 3: hành tinh
func _build_planets() -> void:
	planet_layer = ParallaxLayer.new()
	planet_layer.motion_scale = Balance.PARALLAX["planet_scale"]
	planet_layer.motion_mirroring = Balance.PARALLAX["planet_mirror"]
	add_child(planet_layer)
	var rng := RandomNumberGenerator.new()
	rng.seed = 9081
	var planet_script := preload("res://scripts/core/PlanetDraw.gd")
	for i in range(3):
		var p := Node2D.new()
		p.set_script(planet_script)
		p.position = Vector2(rng.randf_range(80, 640), 200 + i * 820)
		planet_layer.add_child(p)
		_planet_nodes.append(p)
