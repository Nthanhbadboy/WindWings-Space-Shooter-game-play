extends "res://scripts/ui/ScreenBase.gd"
## TechScreen.gd — cây công nghệ 5 nhánh (pháo/giáp/khiên/drone/từ trường):
## cấp hiện tại, hiệu ứng mỗi cấp, giá leo thang Balance.tech_cost, mua bằng
## xu. Mua xong cập nhật ngay thanh tài nguyên.

const TECH_ICONS := {
	"cannon": "res://assets/icons/ic_cannon.png",
	"armor": "res://assets/icons/ic_shield.png",
	"shield": "res://assets/icons/ic_shield.png",
	"drone": "res://assets/icons/ic_drone.png",
	"magnet": "res://assets/icons/ic_magnet.png",
}

var list_box: VBoxContainer

func attach(main_ref: Node, _args: Dictionary) -> void:
	main = main_ref
	build_base(5, "CÔNG NGHỆ")
	var ui := content_root()
	var hint := ThemeWW.label("Nâng cấp vĩnh viễn — áp dụng cho MỌI tàu", 22, Balance.UI["text_dim"])
	hint.position = Vector2(0, 92)
	hint.size = Vector2(Balance.VIEW.x, 32)
	hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	ui.add_child(hint)
	var scroll := ScrollContainer.new()
	scroll.position = Vector2(16, 136)
	scroll.size = Vector2(Balance.VIEW.x - 32, Balance.VIEW.y - 162)
	ui.add_child(scroll)
	list_box = VBoxContainer.new()
	list_box.add_theme_constant_override("separation", 14)
	list_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(list_box)
	_rebuild()

func _rebuild() -> void:
	for c in list_box.get_children():
		list_box.remove_child(c)
		c.queue_free()
	var levels := Game.tech_levels()
	for key in Balance.TECH:
		var t: Dictionary = Balance.TECH[key]
		var lvl := int(levels.get(key, 0))
		var maxed := lvl >= int(t["max"])
		var row := ThemeWW.panel_box(14)
		row.custom_minimum_size = Vector2(0, 150)
		var h: HBoxContainer = row.get_child(0)
		h.add_theme_constant_override("separation", 14)
		var ic := ThemeWW.icon(String(TECH_ICONS.get(key, "")), 72)
		ic.modulate = Balance.UI["rim_cyan"] if not maxed else Balance.UI["gold_a"]
		h.add_child(ic)
		var v := VBoxContainer.new()
		v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		v.alignment = BoxContainer.ALIGNMENT_CENTER
		v.add_theme_constant_override("separation", 4)
		h.add_child(v)
		v.add_child(ThemeWW.label(String(t["name"]), 28, Balance.UI["gold_a"], true))
		v.add_child(ThemeWW.label(String(t["desc"]), 20, Balance.UI["text_dim"]))
		# thanh cấp
		var bar := Control.new()
		bar.set_script(preload("res://scripts/ui/SlantedBar.gd"))
		bar.call("set", "fill_a", Balance.UI["energy_a"])
		bar.call("set", "fill_b", Balance.UI["energy_c"])
		bar.custom_minimum_size = Vector2(300, 16)
		bar.size = Vector2(300, 16)
		bar.call("set_ratio", float(lvl) / float(t["max"]))
		v.add_child(bar)
		var lv := ThemeWW.label("Cấp %d / %d" % [lvl, int(t["max"])], 20, Balance.UI["text"])
		v.add_child(lv)
		var right := VBoxContainer.new()
		right.alignment = BoxContainer.ALIGNMENT_CENTER
		h.add_child(right)
		var b: Button
		if maxed:
			b = ThemeWW.button("TỐI ĐA", "green", Vector2(180, 62))
			b.disabled = true
		else:
			var cost := Balance.tech_cost(String(key), lvl)
			b = ThemeWW.button("NÂNG\n%d ⛃" % cost, "gold", Vector2(180, 84))
			b.add_theme_font_size_override("font_size", 22)
			b.disabled = Game.data["coins"] < cost
			b.pressed.connect(_buy.bind(String(key)))
		right.add_child(b)
		list_box.add_child(row)
	refresh_resources()

func _buy(key: String) -> void:
	if Game.buy_tech(key):
		Sfx.play("coin")
		_rebuild()
