extends "res://scripts/ui/ScreenBase.gd"
## HangarScreen.gd — xưởng tàu: xem trước tàu bay lơ lửng, thanh chỉ số
## (MÁU/SÁT THƯƠNG/TỐC/BẮN), perk, nâng cấp bằng xu (giá theo
## Balance.ship_level_cost), lưới 8 tàu: chọn / mua / nâng cấp.

var selected := ""
var preview: TextureRect
var name_lbl: Label
var perk_lbl: Label
var stat_bars: Array[HBoxContainer] = []
var lvl_lbl: Label
var action_btn: Button
var list_box: VBoxContainer
var pt := 0.0

func attach(main_ref: Node, args: Dictionary) -> void:
	main = main_ref
	selected = String(args.get("ship", Game.current_ship()))
	build_base(2, "HANGAR")
	var ui := content_root()
	# khung xem trước
	preview = TextureRect.new()
	preview.position = Vector2(Balance.VIEW.x * 0.5 - 130, 96)
	preview.size = Vector2(260, 220)
	preview.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	preview.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	preview.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ui.add_child(preview)
	name_lbl = ThemeWW.label("", 40, Balance.UI["gold_a"], true)
	name_lbl.position = Vector2(0, 320)
	name_lbl.size = Vector2(Balance.VIEW.x, 52)
	name_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	ui.add_child(name_lbl)
	perk_lbl = ThemeWW.label("", 22, Balance.UI["rim_cyan"])
	perk_lbl.position = Vector2(0, 372)
	perk_lbl.size = Vector2(Balance.VIEW.x, 32)
	perk_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	ui.add_child(perk_lbl)
	# thanh chỉ số
	var stat_names := [["hp", "MÁU", 160.0], ["dmg", "SÁT THƯƠNG", 22.0], ["speed", "TỐC ĐỘ", 700.0], ["fire_rate", "TỐC BẮN", 7.0]]
	for i in 4:
		var row := HBoxContainer.new()
		row.position = Vector2(60, 416 + i * 40)
		row.add_theme_constant_override("separation", 10)
		var l := ThemeWW.label(String(stat_names[i][1]), 22, Balance.UI["text"])
		l.custom_minimum_size = Vector2(190, 0)
		row.add_child(l)
		var bar := Control.new()
		bar.set_script(preload("res://scripts/ui/SlantedBar.gd"))
		bar.call("set", "fill_a", Balance.UI["energy_a"])
		bar.call("set", "fill_b", Balance.UI["energy_c"])
		bar.custom_minimum_size = Vector2(330, 22)
		bar.size = Vector2(330, 22)
		row.add_child(bar)
		ui.add_child(row)
		stat_bars.append(row)
	# cấp + nút hành động
	lvl_lbl = ThemeWW.label("", 26, Color.WHITE, true)
	lvl_lbl.position = Vector2(60, 590)
	ui.add_child(lvl_lbl)
	action_btn = ThemeWW.button("", "gold", Vector2(Balance.VIEW.x - 120, 66))
	action_btn.position = Vector2(60, 622)
	action_btn.pressed.connect(_on_action)
	ui.add_child(action_btn)
	# danh sách 8 tàu
	var scroll := ScrollContainer.new()
	scroll.position = Vector2(16, 710)
	scroll.size = Vector2(Balance.VIEW.x - 32, Balance.VIEW.y - 736)
	ui.add_child(scroll)
	list_box = VBoxContainer.new()
	list_box.add_theme_constant_override("separation", 10)
	list_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(list_box)
	_rebuild()

func _rebuild() -> void:
	var s: Dictionary = Balance.SHIPS[selected]
	var rec := Game.ship_record(selected)
	var owned := bool(rec["owned"])
	var lvl := int(rec["lvl"])
	var path := "res://assets/ships/%s.png" % selected
	if ResourceLoader.exists(path):
		preview.texture = load(path)
	preview.modulate = Color.WHITE if owned else Color(0.45, 0.5, 0.62)
	name_lbl.text = String(s["name"]) + ("" if owned else "  (CHƯA SỞ HỮU)")
	perk_lbl.text = "✦ " + String(s["perk"]).replace("_", " ").to_upper()
	var stats := Balance.ship_stats(selected, lvl, Game.tech_levels())
	var defs := [["hp", 160.0], ["dmg", 22.0], ["speed", 700.0], ["fire_rate", 7.0]]
	for i in stat_bars.size():
		var bar: Control = stat_bars[i].get_child(1)
		bar.call("set_ratio", clampf(float(stats[defs[i][0]]) / float(defs[i][1]), 0.04, 1.0))
	if owned:
		lvl_lbl.text = "CẤP %d / %d" % [lvl, Balance.SHIP_MAX_LEVEL]
		if lvl < Balance.SHIP_MAX_LEVEL:
			var cost := Balance.ship_level_cost(int(s["price"]), lvl)
			action_btn.text = "NÂNG CẤP · %d ⛃" % cost
			action_btn.disabled = Game.data["coins"] < cost
		else:
			action_btn.text = "ĐANG DÙNG" if Game.current_ship() == selected else "CHỌN TÀU NÀY"
			action_btn.disabled = Game.current_ship() == selected
	else:
		lvl_lbl.text = "GIÁ MUA"
		action_btn.text = "MUA · %d ⛃" % int(s["price"])
		action_btn.disabled = Game.data["coins"] < int(s["price"])
	for c in list_box.get_children():
		list_box.remove_child(c)
		c.queue_free()
	for id in Balance.SHIP_ORDER:
		list_box.add_child(_ship_row(String(id)))
	refresh_resources()

func _ship_row(id: String) -> Control:
	var s: Dictionary = Balance.SHIPS[id]
	var rec := Game.ship_record(id)
	var owned := bool(rec["owned"])
	var row := ThemeWW.panel_box(10)
	row.custom_minimum_size = Vector2(0, 96)
	var h: HBoxContainer = row.get_child(0)
	h.add_theme_constant_override("separation", 12)
	var ic := ThemeWW.icon("res://assets/ships/%s.png" % id, 76)
	if not owned:
		ic.modulate = Color(0.4, 0.45, 0.6)
	h.add_child(ic)
	var v := VBoxContainer.new()
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	v.alignment = BoxContainer.ALIGNMENT_CENTER
	h.add_child(v)
	var nm := ThemeWW.label(String(s["name"]) + (" · LV%d" % int(rec["lvl"]) if owned else ""), 26, s["color"] if owned else Balance.UI["text_dim"], true)
	v.add_child(nm)
	var pk := ThemeWW.label(String(s["perk"]).replace("_", " "), 18, Balance.UI["text_dim"])
	v.add_child(pk)
	var b: Button
	if not owned:
		b = ThemeWW.button("%d ⛃" % int(s["price"]), "gold", Vector2(150, 56))
		b.add_theme_font_size_override("font_size", 22)
	else:
		b = ThemeWW.button("CHỌN" if Game.current_ship() != id else "ĐANG DÙNG", "green" if Game.current_ship() != id else "dark", Vector2(150, 56))
		b.add_theme_font_size_override("font_size", 22)
		b.disabled = Game.current_ship() == id
	b.pressed.connect(_row_action.bind(id))
	h.add_child(b)
	return row

func _row_action(id: String) -> void:
	var rec := Game.ship_record(id)
	if bool(rec["owned"]):
		Game.select_ship(id)
	else:
		Game.buy_ship(id)
	selected = id
	Sfx.play("ui_click")
	_rebuild()

func _on_action() -> void:
	var rec := Game.ship_record(selected)
	if not bool(rec["owned"]):
		if Game.buy_ship(selected):
			Game.select_ship(selected)
	elif int(rec["lvl"]) < Balance.SHIP_MAX_LEVEL:
		Game.level_up_ship(selected)
	elif Game.current_ship() != selected:
		Game.select_ship(selected)
	Sfx.play("coin")
	_rebuild()

func _process(delta: float) -> void:
	pt += delta
	if preview != null:
		preview.position.y = 96.0 + sin(pt * 1.7) * 9.0
		preview.rotation = sin(pt * 1.2) * 0.04
