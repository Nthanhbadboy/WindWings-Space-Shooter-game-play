extends CanvasLayer
## ResultPanel.gd — bảng kết quả trận: sao hiện LẦN LƯỢT (delta-timer, không
## await), tiền/thưởng/điểm đếm dồn, nút màn tiếp / chơi lại / bản đồ.


var run: Node = null
var dim: ColorRect
var center: CenterContainer
var box: PanelContainer
var col: VBoxContainer
var title_lbl: Label
var stars_box: HBoxContainer
var reward_lbl: Label
var score_lbl: Label
var extra_lbl: Label
var buttons: HBoxContainer
var res: Dictionary = {}
var win := false
var reveal_t := 0.0
var revealed := 0
var target_stars := 0
var counting := false
var count_t := 0.0
var shown_coins := 0
var shown_score := 0

func attach_run(r: Node) -> void:
	run = r
	layer = 80
	dim = ColorRect.new()
	dim.color = Color(0.01, 0.04, 0.1, 0.78)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	center = CenterContainer.new()
	center.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(center)
	box = ThemeWW.panel_box(34)
	box.custom_minimum_size = Vector2(600, 0)
	center.add_child(box)
	col = box.get_child(0)
	col.add_theme_constant_override("separation", 16)
	col.alignment = BoxContainer.ALIGNMENT_CENTER
	title_lbl = ThemeWW.label("", 56, Balance.UI["gold_a"], true)
	title_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	col.add_child(title_lbl)
	stars_box = HBoxContainer.new()
	stars_box.alignment = BoxContainer.ALIGNMENT_CENTER
	col.add_child(stars_box)
	reward_lbl = ThemeWW.label("", 34, Balance.UI["gold_a"], true)
	reward_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	col.add_child(reward_lbl)
	score_lbl = ThemeWW.label("", 28, Color.WHITE, true)
	score_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	col.add_child(score_lbl)
	extra_lbl = ThemeWW.label("", 22, Balance.UI["text_dim"])
	extra_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	col.add_child(extra_lbl)
	buttons = HBoxContainer.new()
	buttons.alignment = BoxContainer.ALIGNMENT_CENTER
	buttons.add_theme_constant_override("separation", 14)
	col.add_child(buttons)

func show_result(is_win: bool, r: Dictionary) -> void:
	win = is_win
	res = r
	reveal_t = 0.0
	revealed = 0
	target_stars = int(r.get("stars", 0)) if win else 0
	shown_coins = 0
	shown_score = 0
	counting = true
	count_t = 0.0
	_clear_children(stars_box)
	_clear_children(buttons)
	title_lbl.text = "CHIẾN THẮNG!" if win else "THẤT BẠI"
	title_lbl.add_theme_color_override("font_color", Balance.UI["gold_a"] if win else Balance.UI["red"])
	if win:
		for i in 3:
			var t := ThemeWW.icon("res://assets/icons/ic_star.png", 92)
			t.modulate = Balance.UI["star_off"]
			stars_box.add_child(t)
	reward_lbl.text = "+0"
	score_lbl.text = "ĐIỂM 0"
	var mins := int(float(r.get("time", 0.0))) / 60
	var secs := int(float(r.get("time", 0.0))) % 60
	extra_lbl.text = "Hạ %d địch · %02d:%02d" % [int(r.get("kills", 0)), mins, secs]
	if r.has("daily") and not (r["daily"] as Dictionary).is_empty():
		var d: Dictionary = r["daily"]
		extra_lbl.text += " · Thưởng ngày: +%d xu (chuỗi %d)" % [int(d.get("coins", 0)), int(d.get("streak", 1))]
	if int(r.get("new_gems", 0)) > 0:
		extra_lbl.text += " · +%d ngọc" % int(r["new_gems"])
	# nút
	if win and run.mode == "campaign" and run.level < Balance.TOTAL_LEVELS:
		_add_btn("MÀN TIẾP ▶", "green", func(): run.next_level())
	_add_btn("CHƠI LẠI", "gold", func(): run.restart())
	_add_btn("BẢN ĐỒ", "dark", func(): run.quit_to_menu())

func _add_btn(text: String, kind: String, cb: Callable) -> void:
	var b := ThemeWW.button(text, kind, Vector2(210, 70))
	b.pressed.connect(cb)
	buttons.add_child(b)

func _clear_children(c: Node) -> void:
	for ch in c.get_children():
		c.remove_child(ch)
		ch.queue_free()

func _process(delta: float) -> void:
	if not visible:
		return
	# sao hiện lần lượt mỗi 0.45s
	if win and revealed < target_stars:
		reveal_t += delta
		if reveal_t >= 0.45:
			reveal_t = 0.0
			var star: TextureRect = stars_box.get_child(revealed)
			star.modulate = Balance.UI["star"]
			revealed += 1
			Sfx.play("star")
			if run != null:
				run.fx_shake(3.0, 0.12)
	# đếm dồn tiền + điểm
	if counting:
		count_t += delta
		var coins: int = int(res.get("coins", 0))
		var total: int = int(res.get("score", 0))
		var k := clampf(count_t / 1.2, 0.0, 1.0)
		shown_coins = int(float(coins) * k)
		shown_score = int(float(total) * k)
		reward_lbl.text = "+%d XU" % shown_coins
		score_lbl.text = "ĐIỂM %d" % shown_score
		if k >= 1.0:
			counting = false
