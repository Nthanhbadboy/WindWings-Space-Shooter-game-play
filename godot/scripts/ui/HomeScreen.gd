extends "res://scripts/ui/ScreenBase.gd"
## HomeScreen.gd — trang chủ theo ảnh Ramus: logo vàng lớn giữa nền tinh vân,
## tàu hiện hành bay lơ lửng thở theo sine, nút VÀO GAME vàng kim, hàng nút
## chế độ (chiến dịch / vô tận / săn boss / nhiệm vụ ngày), hangar–tech–store,
## quà ngày, điểm cao nhất, tắt tiếng.

var ship_sprite: TextureRect
var pt := 0.0
var daily_btn: Button

func attach(main_ref: Node, _args: Dictionary) -> void:
	main = main_ref
	build_base(randi_range(1, Balance.CHAPTER_COUNT), "")
	var ui := content_root()
	# logo
	var logo := ThemeWW.label("WINDWINGS", 84, Balance.UI["gold_a"], true)
	logo.add_theme_color_override("font_outline_color", Color("#7a4a00"))
	logo.add_theme_constant_override("outline_size", 14)
	logo.position = Vector2(0, 120)
	logo.size = Vector2(Balance.VIEW.x, 110)
	logo.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	ui.add_child(logo)
	var sub := ThemeWW.label("G A L A X Y   A C E", 30, Balance.UI["rim_cyan"], true)
	sub.position = Vector2(0, 226)
	sub.size = Vector2(Balance.VIEW.x, 44)
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	ui.add_child(sub)
	# tàu hiện hành lơ lửng
	ship_sprite = TextureRect.new()
	var spath := "res://assets/ships/%s.png" % Game.current_ship()
	if ResourceLoader.exists(spath):
		ship_sprite.texture = load(spath)
	ship_sprite.position = Vector2(Balance.VIEW.x * 0.5 - 90, 290)
	ship_sprite.size = Vector2(180, 180)
	ship_sprite.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	ship_sprite.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	ship_sprite.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ui.add_child(ship_sprite)
	var ship_name := ThemeWW.label(String(Balance.SHIPS[Game.current_ship()]["name"]), 24, Balance.UI["text_dim"])
	ship_name.position = Vector2(0, 470)
	ship_name.size = Vector2(Balance.VIEW.x, 34)
	ship_name.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	ui.add_child(ship_name)
	# nút chính
	var play := ThemeWW.button("▶  VÀO GAME", "gold", Vector2(460, 104))
	play.add_theme_font_size_override("font_size", 42)
	play.position = Vector2(Balance.VIEW.x * 0.5 - 230, 530)
	play.pressed.connect(func(): main.show_screen("map", {"chapter": Balance.chapter_of(int(Game.data["unlocked"]))}))
	ui.add_child(play)
	# 4 chế độ
	var modes := [
		["CHIẾN DỊCH", "campaign", "green"],
		["VÔ TẬN", "endless", "dark"],
		["SĂN BOSS", "bossrush", "red"],
		["NHIỆM VỤ NGÀY", "daily", "dark"],
	]
	for i in modes.size():
		var m: Array = modes[i]
		var col := i % 2
		var row := i / 2
		var b := ThemeWW.button(String(m[0]), String(m[2]), Vector2(316, 74))
		b.position = Vector2(56.0 + float(col) * 326.0, 668.0 + float(row) * 88.0)
		b.pressed.connect(_start_mode.bind(String(m[1])))
		ui.add_child(b)
	# hàng tiện ích
	var hangar := ThemeWW.button("TÀU", "dark", Vector2(200, 68))
	hangar.position = Vector2(56, 862)
	hangar.pressed.connect(func(): main.show_screen("hangar"))
	ui.add_child(hangar)
	var tech := ThemeWW.button("CÔNG NGHỆ", "dark", Vector2(240, 68))
	tech.position = Vector2(266, 862)
	tech.pressed.connect(func(): main.show_screen("tech"))
	ui.add_child(tech)
	var store := ThemeWW.button("CỬA HÀNG", "dark", Vector2(200, 68))
	store.position = Vector2(516, 862)
	store.pressed.connect(func(): main.show_screen("store"))
	ui.add_child(store)
	# quà ngày
	daily_btn = ThemeWW.button("NHẬN QUÀ NGÀY", "green", Vector2(460, 66))
	daily_btn.position = Vector2(Balance.VIEW.x * 0.5 - 230, 950)
	daily_btn.pressed.connect(_claim_daily)
	ui.add_child(daily_btn)
	if str(Game.data["last_daily"]) == Game.daily_key():
		daily_btn.text = "ĐÃ NHẬN HÔM NAY"
		daily_btn.disabled = true
	# điểm cao + âm thanh
	var best := ThemeWW.label("ĐIỂM CAO NHẤT: %d" % int(Game.data["best_score"]), 24, Balance.UI["text_dim"])
	best.position = Vector2(0, 1140)
	best.size = Vector2(Balance.VIEW.x, 34)
	best.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	ui.add_child(best)
	var ver := ThemeWW.label("v0.4 · Godot 4 · 60 màn · 6 boss chủ thể riêng", 20, Color(Balance.UI["text_dim"], 0.7))
	ver.position = Vector2(0, 1180)
	ver.size = Vector2(Balance.VIEW.x, 30)
	ver.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	ui.add_child(ver)
	var mute := ThemeWW.icon_button("", 60.0, "dark")
	mute.text = "🔊" if not Sfx.muted else "🔇"
	mute.position = Vector2(Balance.VIEW.x - 76, 92)
	mute.pressed.connect(func():
		Sfx.set_muted(not Sfx.muted)
		mute.text = "🔊" if not Sfx.muted else "🔇")
	ui.add_child(mute)

func _start_mode(m: String) -> void:
	match m:
		"campaign":
			main.show_screen("map", {"chapter": Balance.chapter_of(int(Game.data["unlocked"]))})
		"endless":
			main.show_screen("run", {"mode": "endless", "level": 6})
		"bossrush":
			main.show_screen("run", {"mode": "bossrush", "level": 60})
		"daily":
			main.show_screen("run", {"mode": "daily", "level": 30})

func _claim_daily() -> void:
	var d := Game.claim_daily()
	if not d.is_empty():
		daily_btn.text = "ĐÃ NHẬN + %d XU" % int(d.get("coins", 0))
		daily_btn.disabled = true
		refresh_resources()
		Sfx.play("coin")

func _process(delta: float) -> void:
	pt += delta
	if ship_sprite != null:
		ship_sprite.position.y = 290.0 + sin(pt * 1.6) * 12.0
		ship_sprite.rotation = sin(pt * 1.1) * 0.05
