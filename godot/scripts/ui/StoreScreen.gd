extends "res://scripts/ui/ScreenBase.gd"
## StoreScreen.gd — cửa hàng: quà ngày (xu + ngọc theo chuỗi đăng nhập),
## đổi ngọc lấy xu theo tỉ lệ ECONOMY, gói tiếp viện mua bằng ngọc (bom +
## khiên cho trận kế tiếp — buff đầu trận). Không IAP thật: toàn bộ nền
## kinh tế trong game.

const SUPPLY_GEM_COST := 6

var list_box: VBoxContainer
var supply_active_lbl: Label

func attach(main_ref: Node, _args: Dictionary) -> void:
	main = main_ref
	build_base(6, "CỬA HÀNG")
	var ui := content_root()
	var scroll := ScrollContainer.new()
	scroll.position = Vector2(16, 96)
	scroll.size = Vector2(Balance.VIEW.x - 32, Balance.VIEW.y - 122)
	ui.add_child(scroll)
	list_box = VBoxContainer.new()
	list_box.add_theme_constant_override("separation", 16)
	list_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(list_box)
	_rebuild()

func _rebuild() -> void:
	for c in list_box.get_children():
		list_box.remove_child(c)
		c.queue_free()
	# quà ngày
	var claimed := str(Game.data["last_daily"]) == Game.daily_key()
	var streak := int(Game.data["daily_streak"])
	list_box.add_child(_card(
		"QUÀ NGÀY",
		"Chuỗi %d ngày — nhận %d xu + ngọc. Chuỗi càng dài quà càng to!" % [streak, Balance.ECONOMY["daily_coins"] + ((streak % 7) + 1) * Balance.ECONOMY["daily_streak_step"]],
		"ĐÃ NHẬN HÔM NAY" if claimed else "NHẬN NGAY",
		"green" if not claimed else "dark",
		claimed, _claim))
	# đổi ngọc → xu
	var rate := 400
	list_box.add_child(_card(
		"ĐỔI NGỌC → XU",
		"1 ngọc = %d xu. Ngọc kiếm từ sao màn chơi (%d sao = 1 ngọc)." % [rate, Balance.ECONOMY["star_gem"]],
		"ĐỔI 1 NGỌC",
		"gold",
		Game.data["gems"] < 1, _exchange.bind(rate)))
	# gói tiếp viện
	var has_supply := bool(Game.data.get("supply", false))
	list_box.add_child(_card(
		"GÓI TIẾP VIỆN",
		"Trận kế tiếp: +1 bom, +1 khiên, súng khởi động LV2." + ("  (ĐANG CÓ HIỆU LỰC)" if has_supply else ""),
		"ĐANG CÓ" if has_supply else "MUA · %d ◆" % SUPPLY_GEM_COST,
		"dark" if has_supply else "gold",
		has_supply or Game.data["gems"] < SUPPLY_GEM_COST, _buy_supply))
	# ghi chú kinh tế
	var note := ThemeWW.label("Mẹo CEO: giữ chuỗi đăng nhập 7 ngày để tối đa quà; ngọc chỉ đổi khi kẹt nâng cấp cuối game.", 20, U["text_dim"])
	note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	note.custom_minimum_size = Vector2(Balance.VIEW.x - 80, 0)
	list_box.add_child(note)
	refresh_resources()

func _card(title: String, desc: String, btn_text: String, kind: String, disabled: bool, cb: Callable) -> Control:
	var row := ThemeWW.panel_box(18)
	row.custom_minimum_size = Vector2(0, 170)
	var v: VBoxContainer = row.get_child(0)
	v.add_theme_constant_override("separation", 8)
	v.add_child(ThemeWW.label(title, 30, U["gold_a"], true))
	var d := ThemeWW.label(desc, 21, U["text_dim"])
	d.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	d.custom_minimum_size = Vector2(Balance.VIEW.x - 130, 0)
	v.add_child(d)
	var b := ThemeWW.button(btn_text, kind, Vector2(320, 62))
	b.disabled = disabled
	if not disabled:
		b.pressed.connect(cb)
	v.add_child(b)
	return row

func _claim() -> void:
	if not Game.claim_daily().is_empty():
		Sfx.play("coin")
		_rebuild()

func _exchange(rate: int) -> void:
	if Game.spend_gems(1):
		Game.add_coins(rate)
		Game.save_game()
		Sfx.play("coin")
		_rebuild()

func _buy_supply() -> void:
	if Game.spend_gems(SUPPLY_GEM_COST):
		Game.data["supply"] = true
		Game.save_game()
		Sfx.play("powerup")
		_rebuild()
