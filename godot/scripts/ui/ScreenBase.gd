extends Control
## ScreenBase.gd — nền dùng chung cho các màn hình ngoài trận đánh: parallax
## không gian, thanh tài nguyên (xu/ngọc/sao) trên cùng, nút quay lui, tiêu
## đề. Các màn con gọi build_base() trong attach().

const U := Balance.UI

var main: Node = null
var coin_lbl: Label
var gem_lbl: Label
var star_lbl: Label
var parallax: ParallaxBackground

func build_base(chapter: int, title: String) -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	parallax = preload("res://scripts/core/ParallaxSpace.gd").new()
	add_child(parallax)
	parallax.call("set_theme", chapter)
	var canvas := CanvasLayer.new()
	canvas.layer = 5
	add_child(canvas)
	var ui_root := Control.new()
	ui_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	ui_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	canvas.add_child(ui_root)
	# thanh tài nguyên
	var bar := ThemeWW.grad_rect(Color(U["hud_top"], 0.95), Color(U["hud_bottom"], 0.75))
	bar.position = Vector2.ZERO
	bar.size = Vector2(Balance.VIEW.x, 76)
	ui_root.add_child(bar)
	var back := ThemeWW.icon_button("", 56.0, "dark")
	back.text = "◀"
	back.add_theme_font_size_override("font_size", 30)
	back.position = Vector2(12, 10)
	back.pressed.connect(_on_back)
	ui_root.add_child(back)
	var t := ThemeWW.label(title, 30, U["gold_a"], true)
	t.position = Vector2(84, 20)
	ui_root.add_child(t)
	coin_lbl = _res_label("res://assets/icons/ic_coin.png", Vector2(400, 18), U["gold_a"])
	gem_lbl = _res_label("res://assets/icons/ic_gem.png", Vector2(536, 18), Color("#8fe8ff"))
	star_lbl = _res_label("res://assets/icons/ic_star.png", Vector2(650, 18), U["star"])
	ui_root.add_child(coin_lbl.get_parent())
	ui_root.add_child(gem_lbl.get_parent())
	ui_root.add_child(star_lbl.get_parent())
	refresh_resources()
	_content_root = ui_root

var _content_root: Control = null

func content_root() -> Control:
	return _content_root

func _res_label(icon_path: String, pos: Vector2, color: Color) -> Label:
	var h := HBoxContainer.new()
	h.position = pos
	h.mouse_filter = Control.MOUSE_FILTER_IGNORE
	h.add_child(ThemeWW.icon(icon_path, 38))
	var l := ThemeWW.label("0", 26, color, true)
	h.add_child(l)
	return l

func refresh_resources() -> void:
	if coin_lbl != null:
		coin_lbl.text = str(Game.data["coins"])
		gem_lbl.text = str(Game.data["gems"])
		star_lbl.text = "%d/%d" % [Game.total_stars(), Balance.TOTAL_LEVELS * 3]

func _on_back() -> void:
	if main != null:
		main.show_screen("home")
