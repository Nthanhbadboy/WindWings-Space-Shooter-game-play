extends CanvasLayer
## Hud.gd — HUD trận đánh đúng thông số DO_DAC_UI.md (portrait 16,88 74×58;
## vỏ HP 62,92 270×30 skewX−12°; 5 ô năng lượng skew −26°; coin 444,84;
## pause 640,86 60×60; đếm địch phải-20 y176) + thanh boss + nút bom.


var run: Node = null
var root: Control
var hp_bar: Control
var energy_cells: Array[Control] = []
var score_lbl: Label
var combo_lbl: Label
var wave_lbl: Label
var coin_lbl: Label
var enemy_lbl: Label
var lives_box: HBoxContainer
var weapon_lbl: Label
var bomb_btn: Button
var bomb_lbl: Label
var boss_box: VBoxContainer
var boss_name_lbl: Label
var boss_bar: Control
var boss_pips: HBoxContainer
var boss_enraged := false
var last_hp := -1.0

func attach_run(r: Node) -> void:
	run = r
	layer = 10
	root = Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)
	_build_top()
	_build_boss_bar()
	_build_bottom()

func _build_top() -> void:
	# dải HUD trên: gradient đêm xanh + viền cyan
	var top := ThemeWW.grad_rect(Balance.UI["hud_top"], Balance.UI["hud_bottom"])
	top.position = Vector2.ZERO
	top.size = Vector2(Balance.VIEW.x, 149)
	root.add_child(top)
	var rim := ColorRect.new()
	rim.color = Balance.UI["rim_cyan"]
	rim.position = Vector2(0, 149)
	rim.size = Vector2(Balance.VIEW.x, 3)
	rim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(rim)
	# portrait: khung tròn + ảnh tàu hiện tại
	var pp: Vector2 = Balance.UI["portrait_pos"]
	var ps: Vector2 = Balance.UI["portrait_size"]
	var frame := TextureRect.new()
	if ResourceLoader.exists("res://assets/ui/ring_porthole.png"):
		frame.texture = load("res://assets/ui/ring_porthole.png")
	frame.position = pp
	frame.size = ps
	frame.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	frame.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(frame)
	var ship := TextureRect.new()
	var spath := "res://assets/ships/%s.png" % Game.current_ship()
	if ResourceLoader.exists(spath):
		ship.texture = load(spath)
	ship.position = pp + Vector2(13, 13)
	ship.size = ps - Vector2(26, 26)
	ship.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	ship.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	ship.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(ship)
	# HP: vỏ nghiêng 270×30 @62,92
	hp_bar = Control.new()
	hp_bar.set_script(preload("res://scripts/ui/SlantedBar.gd"))
	hp_bar.position = Balance.UI["hp_pos"]
	hp_bar.size = Balance.UI["hp_size"]
	root.add_child(hp_bar)
	# 5 ô năng lượng (khiên) skew −26°
	for i in 5:
		var c := Control.new()
		c.set_script(preload("res://scripts/ui/SlantedBar.gd"))
		c.skew = float(Balance.UI["energy_skew"])
		c.fill_a = Balance.UI["energy_a"]
		c.fill_b = Balance.UI["energy_c"]
		c.position = Vector2(64.0 + float(i) * 50.0, 126.0)
		c.size = Vector2(44, 15)
		c.call("set_ratio", 0.0)
		root.add_child(c)
		energy_cells.append(c)
	# coin
	coin_lbl = ThemeWW.label("0", 28, Balance.UI["gold_a"], true)
	coin_lbl.position = Balance.UI["coin_pos"] + Vector2(46, 4)
	root.add_child(coin_lbl)
	root.add_child(_fixed_icon("res://assets/icons/ic_coin.png", Balance.UI["coin_pos"], 40))
	# điểm + combo (giữa)
	score_lbl = ThemeWW.label("0", 40, Color.WHITE, true)
	score_lbl.position = Vector2(Balance.VIEW.x * 0.5 - 120, 6)
	score_lbl.custom_minimum_size = Vector2(240, 0)
	score_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	root.add_child(score_lbl)
	combo_lbl = ThemeWW.label("", 24, Balance.UI["gold_b"], true)
	combo_lbl.position = Vector2(Balance.VIEW.x * 0.5 - 120, 50)
	combo_lbl.custom_minimum_size = Vector2(240, 0)
	combo_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	root.add_child(combo_lbl)
	# nút pause 60×60 @640,86
	var pb := ThemeWW.icon_button("res://assets/icons/ic_pause.png", float(Balance.UI["pause_size"]), "dark")
	pb.position = Balance.UI["pause_pos"]
	pb.mouse_filter = Control.MOUSE_FILTER_STOP
	pb.pressed.connect(func(): run.toggle_pause())
	root.add_child(pb)

func _fixed_icon(path: String, pos: Vector2, px: float) -> TextureRect:
	var t := ThemeWW.icon(path, px)
	t.position = pos
	return t

func _build_boss_bar() -> void:
	boss_box = VBoxContainer.new()
	boss_box.position = Vector2(60, 160)
	boss_box.size = Vector2(Balance.VIEW.x - 120, 92)
	boss_box.visible = false
	root.add_child(boss_box)
	boss_name_lbl = ThemeWW.label("", 26, Color("#ff8fa8"), true)
	boss_name_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	boss_box.add_child(boss_name_lbl)
	boss_bar = Control.new()
	boss_bar.set_script(preload("res://scripts/ui/SlantedBar.gd"))
	boss_bar.fill_a = Color("#ff5d7a")
	boss_bar.fill_b = Color("#7a1030")
	boss_bar.rim = Color("#ffb0c0")
	boss_bar.custom_minimum_size = Vector2(0, 22)
	boss_box.add_child(boss_bar)
	boss_pips = HBoxContainer.new()
	boss_pips.alignment = BoxContainer.ALIGNMENT_CENTER
	boss_box.add_child(boss_pips)
	for i in 3:
		var pip := ColorRect.new()
		pip.custom_minimum_size = Vector2(34, 6)
		pip.color = Balance.UI["rim_cyan"]
		pip.mouse_filter = Control.MOUSE_FILTER_IGNORE
		boss_pips.add_child(pip)

func _build_bottom() -> void:
	# đếm địch còn lại (phải, y176) — icon skull + số
	var skull := _fixed_icon("res://assets/icons/ic_skull.png", Vector2(Balance.VIEW.x - 92, float(Balance.UI["enemy_count_y"])), 34)
	root.add_child(skull)
	enemy_lbl = ThemeWW.label("0", 26, Color("#ffd0d8"), true)
	enemy_lbl.position = Vector2(Balance.VIEW.x - 54, float(Balance.UI["enemy_count_y"]) + 2)
	root.add_child(enemy_lbl)
	# mạng: tàu nhỏ góc trái dưới HUD
	lives_box = HBoxContainer.new()
	lives_box.position = Vector2(18, 1180)
	root.add_child(lives_box)
	# cấp súng
	weapon_lbl = ThemeWW.label("LV1", 24, Balance.UI["rim_cyan"], true)
	weapon_lbl.position = Vector2(18, 1226)
	root.add_child(weapon_lbl)
	# nút bom góc phải dưới
	bomb_btn = ThemeWW.icon_button("res://assets/icons/ic_skull.png", 78.0, "gold")
	bomb_btn.position = Vector2(Balance.VIEW.x - 104, 1168)
	bomb_btn.mouse_filter = Control.MOUSE_FILTER_STOP
	bomb_btn.modulate = Color(1.0, 0.55, 0.45)
	bomb_btn.pressed.connect(func(): run.use_bomb())
	root.add_child(bomb_btn)
	bomb_lbl = ThemeWW.label("×0", 24, Balance.UI["gold_a"], true)
	bomb_lbl.position = Vector2(Balance.VIEW.x - 46, 1216)
	root.add_child(bomb_lbl)

func _process(_delta: float) -> void:
	if run == null or run.player == null:
		return
	# HP poll (đổi khi hồi máu/đỡ đòn)
	var p: Node2D = run.player
	var r: float = float(p.hp) / float(p.max_hp)
	if not is_equal_approx(r, last_hp):
		last_hp = r
		hp_bar.call("set_ratio", r, true)
	set_lives(p.lives)
	coin_lbl.text = str(Game.data["coins"] + run.coins_earned)
	# năng lượng = khiên
	for i in energy_cells.size():
		energy_cells[i].call("set_ratio", 1.0 if i < p.shields else 0.0)
	# boss bar
	if boss_box.visible:
		boss_bar.call("set_ratio", clampf(run.boss.hp / run.boss.max_hp, 0.0, 1.0) if run.boss != null else 0.0)
		var kids := boss_pips.get_children()
		for i in kids.size():
			var c: Color = Balance.UI["rim_cyan"]
			if run.boss != null:
				c = Balance.UI["red"] if i + 1 <= (3 - run.boss.phase) else Balance.UI["rim_cyan"]
			kids[i].color = c

func set_lives(n: int) -> void:
	while lives_box.get_child_count() > n:
		var c := lives_box.get_child(lives_box.get_child_count() - 1)
		lives_box.remove_child(c)
		c.queue_free()
	while lives_box.get_child_count() < n:
		var t := TextureRect.new()
		if ResourceLoader.exists("res://assets/ships/%s.png" % Game.current_ship()):
			t.texture = load("res://assets/ships/%s.png" % Game.current_ship())
		t.custom_minimum_size = Vector2(44, 44)
		t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		t.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		t.mouse_filter = Control.MOUSE_FILTER_IGNORE
		lives_box.add_child(t)

func set_shields(n: int) -> void:
	for i in energy_cells.size():
		energy_cells[i].call("set_ratio", 1.0 if i < n else 0.0)

func set_weapon(n: int) -> void:
	weapon_lbl.text = "LV%d" % n

func set_bombs(n: int) -> void:
	bomb_lbl.text = "×%d" % n
	bomb_btn.modulate = Color(1.0, 0.55, 0.45) if n > 0 else Color(0.5, 0.45, 0.45, 0.7)

func set_score(s: int, combo: int) -> void:
	score_lbl.text = str(s)
	combo_lbl.text = ("COMBO ×%d" % combo) if combo >= 3 else ""

func set_wave(i: int, total: int) -> void:
	if wave_lbl == null:
		wave_lbl = ThemeWW.label("", 22, Balance.UI["text_dim"], true)
		wave_lbl.position = Vector2(Balance.VIEW.x * 0.5 - 120, 156)
		wave_lbl.custom_minimum_size = Vector2(240, 0)
		wave_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		root.add_child(wave_lbl)
	wave_lbl.text = ("SÓNG %d/%d" % [i, total]) if i > 0 else ""

func set_enemy_count(n: int) -> void:
	enemy_lbl.text = str(n)

func show_boss(boss_name: String, _max_hp: float) -> void:
	boss_name_lbl.text = boss_name
	boss_box.visible = true
	boss_enraged = false

func set_boss_hp(_hp: float) -> void:
	pass  # thanh boss poll trong _process

func set_boss_phase(p: int) -> void:
	boss_name_lbl.text = boss_name_lbl.text.get_slice("  ", 0) + ("  ◆ PHA %d" % p)

func set_boss_enraged() -> void:
	if boss_enraged:
		return
	boss_enraged = true
	boss_name_lbl.text += "  ⚠ CUỒNG NỘ"
	boss_name_lbl.add_theme_color_override("font_color", Color("#ff3c3c"))

func hide_boss() -> void:
	boss_box.visible = false
