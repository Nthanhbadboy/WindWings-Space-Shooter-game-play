extends CanvasLayer
## PauseMenu.gd — overlay tạm dừng: làm mờ nền, panel WindWings, nút tiếp
## tục / chơi lại / về bản đồ, bật tắt hitbox debug + âm thanh.

var run: Node = null
var dim: ColorRect
var box: PanelContainer
var hitbox_on := false
var sound_btn: Button
var hitbox_btn: Button

func attach_run(r: Node) -> void:
	run = r
	layer = 70
	dim = ColorRect.new()
	dim.color = Color(0.02, 0.05, 0.12, 0.68)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	box = ThemeWW.panel_box(30)
	box.custom_minimum_size = Vector2(520, 0)
	var center := CenterContainer.new()
	center.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(center)
	center.add_child(box)
	var col: VBoxContainer = box.get_child(0)
	col.add_theme_constant_override("separation", 18)
	col.alignment = BoxContainer.ALIGNMENT_CENTER
	var title := ThemeWW.label("TẠM DỪNG", 48, Balance.UI["gold_a"], true)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	col.add_child(title)
	var info := ThemeWW.label("Màn %d · %s" % [run.level, run.info["chapter_name"]], 24, Balance.UI["text_dim"])
	info.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	col.add_child(info)
	var b1 := ThemeWW.button("TIẾP TỤC", "green", Vector2(400, 76))
	b1.pressed.connect(func(): run.toggle_pause())
	col.add_child(b1)
	var b2 := ThemeWW.button("CHƠI LẠI", "gold", Vector2(400, 76))
	b2.pressed.connect(func(): run.restart())
	col.add_child(b2)
	var b3 := ThemeWW.button("VỀ BẢN ĐỒ", "dark", Vector2(400, 76))
	b3.pressed.connect(func(): run.quit_to_menu())
	col.add_child(b3)
	hitbox_btn = ThemeWW.button("HITBOX: TẮT", "dark", Vector2(400, 60))
	hitbox_btn.pressed.connect(_toggle_hitbox)
	col.add_child(hitbox_btn)
	sound_btn = ThemeWW.button("ÂM THANH: BẬT", "dark", Vector2(400, 60))
	sound_btn.pressed.connect(_toggle_sound)
	col.add_child(sound_btn)

func open() -> void:
	visible = true

func _toggle_hitbox() -> void:
	hitbox_on = not hitbox_on
	hitbox_btn.text = "HITBOX: BẬT" if hitbox_on else "HITBOX: TẮT"
	if run != null and run.player != null:
		run.player.show_hitbox(hitbox_on)

func _toggle_sound() -> void:
	Sfx.set_muted(not Sfx.muted)
	sound_btn.text = "ÂM THANH: TẮT" if Sfx.muted else "ÂM THANH: BẬT"
