extends RefCounted
class_name ThemeWW
## ThemeWW.gd — bộ kit UI WindWings dựng bằng code theo DO_DAC_UI.md +
## ảnh Ramus: nút bevel vàng/cam, panel xanh đêm viền cyan, chữ sáng,
## thanh nghiêng (skewX -12°/-26°). Dùng chung cho HUD và mọi màn hình.

const U := Balance.UI

static func grad_rect(c_top: Color, c_bottom: Color, vertical := true) -> TextureRect:
	var t := TextureRect.new()
	var g := Gradient.new()
	g.set_color(0, c_top)
	g.set_color(1, c_bottom)
	var gt := GradientTexture2D.new()
	gt.gradient = g
	gt.width = 8
	gt.height = 256 if vertical else 8
	gt.fill_from = Vector2.ZERO
	gt.fill_to = Vector2(0, 1) if vertical else Vector2(1, 0)
	t.texture = gt
	t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	t.stretch_mode = TextureRect.STRETCH_SCALE
	t.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return t

static func style(bg: Color, rim: Color, radius := 14, border := 3) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = bg
	s.border_color = rim
	s.set_border_width_all(border)
	s.set_corner_radius_all(radius)
	s.shadow_color = Color(0, 0, 0, 0.45)
	s.shadow_size = 6
	s.shadow_offset = Vector2(0, 4)
	return s

static func style_grad(a: Color, b: Color, rim: Color, radius := 14) -> StyleBoxFlat:
	# StyleBoxFlat một màu: lấy màu giữa của gradient + viền đậm (bevel giả)
	var s := style(a.lerp(b, 0.5), rim, radius, 3)
	s.border_color = rim
	return s

static func button(text: String, kind := "gold", min_size := Vector2(240, 72)) -> Button:
	var b := Button.new()
	b.text = text
	b.custom_minimum_size = min_size
	var dark := Color(0, 0, 0, 0.35)
	match kind:
		"gold":
			b.add_theme_stylebox_override("normal", style_grad(U["btn_a"], U["btn_b"], U["btn_c"]))
			b.add_theme_stylebox_override("hover", style_grad(U["btn_a"].lightened(0.12), U["btn_b"].lightened(0.1), U["btn_c"]))
			b.add_theme_stylebox_override("pressed", style_grad(U["btn_c"], U["btn_b"], U["btn_c"]))
			b.add_theme_color_override("font_color", Color("#4a2a00"))
			b.add_theme_color_override("font_hover_color", Color("#3a1f00"))
			b.add_theme_color_override("font_pressed_color", Color("#2a1500"))
		"green":
			b.add_theme_stylebox_override("normal", style_grad(U["green_a"], U["green_b"], Color("#1c7a10")))
			b.add_theme_stylebox_override("hover", style_grad(U["green_a"].lightened(0.1), U["green_b"].lightened(0.1), Color("#1c7a10")))
			b.add_theme_stylebox_override("pressed", style_grad(U["green_b"], U["green_a"], Color("#1c7a10")))
			b.add_theme_color_override("font_color", Color("#0c3308"))
		"red":
			b.add_theme_stylebox_override("normal", style_grad(Color("#ff7a6a"), U["red"], Color("#7a1a12")))
			b.add_theme_stylebox_override("hover", style_grad(Color("#ff9a8a"), U["red"].lightened(0.1), Color("#7a1a12")))
			b.add_theme_stylebox_override("pressed", style_grad(U["red"], Color("#ff7a6a"), Color("#7a1a12")))
			b.add_theme_color_override("font_color", Color("#3a0a06"))
		"dark":
			b.add_theme_stylebox_override("normal", style(Color("#122a4a"), U["rim_dark"]))
			b.add_theme_stylebox_override("hover", style(Color("#1a3a62"), U["rim_blue"]))
			b.add_theme_stylebox_override("pressed", style(Color("#0c1e38"), U["rim_dark"]))
			b.add_theme_color_override("font_color", U["text"])
	b.add_theme_font_size_override("font_size", 30)
	return b

static func panel_box(margin := 20) -> PanelContainer:
	var p := PanelContainer.new()
	var sb := style(U["panel"], U["panel_rim"], 18, 3)
	sb.set_content_margin_all(float(margin))
	p.add_theme_stylebox_override("panel", sb)
	var v := VBoxContainer.new()
	p.add_child(v)
	return p

static func label(text: String, size := 28, color := Color.WHITE, bold := false) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	l.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.75))
	l.add_theme_constant_override("shadow_offset_y", 2)
	if bold:
		l.add_theme_constant_override("outline_size", 6)
		l.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.55))
	return l

static func icon(path: String, size := 48) -> TextureRect:
	var t := TextureRect.new()
	if ResourceLoader.exists(path):
		t.texture = load(path)
	t.custom_minimum_size = Vector2(size, size)
	t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	t.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	t.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return t

static func coin_row(amount: int) -> HBoxContainer:
	var h := HBoxContainer.new()
	h.add_child(icon("res://assets/icons/ic_coin.png", 40))
	h.add_child(label(str(amount), 28, U["gold_a"], true))
	return h

static func gem_row(amount: int) -> HBoxContainer:
	var h := HBoxContainer.new()
	h.add_child(icon("res://assets/icons/ic_gem.png", 40))
	h.add_child(label(str(amount), 28, Color("#8fe8ff"), true))
	return h

static func star_row(count: int, max_count := 3, size := 44) -> HBoxContainer:
	var h := HBoxContainer.new()
	for i in max_count:
		var t := icon("res://assets/icons/ic_star.png", size)
		t.modulate = U["star"] if i < count else U["star_off"]
		h.add_child(t)
	return h

## Nút icon vuông (pause, bomb…) có badge số.
static func icon_button(icon_path: String, px: float, kind := "gold") -> Button:
	var b := Button.new()
	b.custom_minimum_size = Vector2(px, px)
	b.icon = load(icon_path) if ResourceLoader.exists(icon_path) else null
	b.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
	match kind:
		"gold":
			b.add_theme_stylebox_override("normal", style_grad(U["btn_a"], U["btn_b"], U["btn_c"], int(px * 0.24)))
			b.add_theme_stylebox_override("pressed", style_grad(U["btn_c"], U["btn_b"], U["btn_c"], int(px * 0.24)))
		"dark":
			b.add_theme_stylebox_override("normal", style(Color("#122a4a"), U["rim_blue"], int(px * 0.24)))
			b.add_theme_stylebox_override("pressed", style(Color("#0c1e38"), U["rim_dark"], int(px * 0.24)))
	return b
