extends "res://scripts/ui/ScreenBase.gd"
## LevelMap.gd — bản đồ 60 màn (6 chương × 10): 6 tab chương, lưới nút màn
## với sao đã đạt, màn 10 là BOSS (viền đỏ, icon skull), màn khoá hiện ổ
## khoá. Chạm màn mở khoá → vào trận ngay.

var chapter := 1
var tabs: Array[Button] = []
var grid: GridContainer
var title_lbl: Label

func attach(main_ref: Node, args: Dictionary) -> void:
	main = main_ref
	chapter = clampi(int(args.get("chapter", 1)), 1, Balance.CHAPTER_COUNT)
	build_base(chapter, "BẢN ĐỒ CHIẾN DỊCH")
	var ui := content_root()
	# tab chương
	var tab_row := HBoxContainer.new()
	tab_row.position = Vector2(12, 88)
	tab_row.add_theme_constant_override("separation", 6)
	ui.add_child(tab_row)
	for c in Balance.CHAPTER_COUNT:
		var b := ThemeWW.button(str(c + 1), "dark", Vector2(106, 52))
		b.add_theme_font_size_override("font_size", 26)
		b.pressed.connect(_select_chapter.bind(c + 1))
		tab_row.add_child(b)
		tabs.append(b)
	# tên chương
	title_lbl = ThemeWW.label("", 26, Balance.CHAPTERS[chapter - 1]["tint"], true)
	title_lbl.position = Vector2(0, 150)
	title_lbl.size = Vector2(Balance.VIEW.x, 36)
	title_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	ui.add_child(title_lbl)
	# lưới màn
	var scroll := ScrollContainer.new()
	scroll.position = Vector2(16, 196)
	scroll.size = Vector2(Balance.VIEW.x - 32, Balance.VIEW.y - 220)
	ui.add_child(scroll)
	grid = GridContainer.new()
	grid.columns = 2
	grid.add_theme_constant_override("h_separation", 20)
	grid.add_theme_constant_override("v_separation", 16)
	grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(grid)
	_rebuild()

func _select_chapter(c: int) -> void:
	chapter = c
	parallax.call("set_theme", c)
	_rebuild()

func _rebuild() -> void:
	var ch: Dictionary = Balance.CHAPTERS[chapter - 1]
	title_lbl.text = "CHƯƠNG %d · %s" % [chapter, String(ch["name"])]
	title_lbl.add_theme_color_override("font_color", ch["tint"])
	for i in tabs.size():
		tabs[i].text = str(i + 1)
		if i + 1 == chapter:
			tabs[i].text = "▼ " + tabs[i].text
	for c in grid.get_children():
		grid.remove_child(c)
		c.queue_free()
	var boss_id: String = ch["boss"]
	for idx in Balance.LEVELS_PER_CHAPTER:
		var level := (chapter - 1) * Balance.LEVELS_PER_CHAPTER + idx + 1
		var is_boss := idx == Balance.LEVELS_PER_CHAPTER - 1
		var unlocked := Game.is_unlocked(level)
		var node := _level_button(level, is_boss, unlocked, boss_id)
		grid.add_child(node)

func _level_button(level: int, is_boss: bool, unlocked: bool, boss_id: String) -> Control:
	var box := ThemeWW.panel_box(12)
	box.custom_minimum_size = Vector2(324, 168)
	var col: VBoxContainer = box.get_child(0)
	col.alignment = BoxContainer.ALIGNMENT_CENTER
	col.add_theme_constant_override("separation", 6)
	if is_boss:
		var skull := HBoxContainer.new()
		skull.alignment = BoxContainer.ALIGNMENT_CENTER
		skull.add_child(ThemeWW.icon("res://assets/icons/ic_skull.png", 42))
		col.add_child(skull)
		var bl := ThemeWW.label(String(Balance.BOSSES[boss_id]["name"]), 22, Color("#ff8fa8"), true)
		bl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		bl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		col.add_child(bl)
		var subj := ThemeWW.label(String(Balance.BOSSES[boss_id]["subject"]), 18, Balance.UI["text_dim"])
		subj.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		col.add_child(subj)
	else:
		var nl := ThemeWW.label("MÀN %d" % level, 34, Balance.UI["gold_a"] if unlocked else Balance.UI["text_dim"], true)
		nl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		col.add_child(nl)
		var stars := ThemeWW.star_row(Game.stars_of(level), 3, 34)
		stars.alignment = BoxContainer.ALIGNMENT_CENTER
		col.add_child(stars)
	if not unlocked:
		var lock := ThemeWW.icon("res://assets/icons/ic_lock.png", 46)
		lock.modulate = Color(1, 1, 1, 0.85)
		col.add_child(lock)
	else:
		var go := ThemeWW.button("VÀO TRẬN" if not is_boss else "ĐẤU BOSS", "green" if not is_boss else "red", Vector2(240, 52))
		go.add_theme_font_size_override("font_size", 22)
		var h := CenterContainer.new()
		h.add_child(go)
		col.add_child(h)
		go.pressed.connect(func(): main.show_screen("run", {"level": level, "mode": "campaign"}))
		if is_boss:
			box.add_theme_stylebox_override("panel", ThemeWW.style(Color("#2a0d18", 0.92), Color("#ff5d7a"), 18, 3))
	return box

func _on_back() -> void:
	if main != null:
		main.show_screen("home")
