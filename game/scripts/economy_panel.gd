class_name EconomyPanel
extends Control

signal close_requested
signal purchase_requested(player_index: int, quantity: int)

var _player_costs: Array = []
var _pvp_arrays: Dictionary = {}
var _shop_contract: Dictionary = {}
var _monetization_service: MonetizationService
var _wallet := 0
var _purchased: Dictionary = {}
var _player_grid: GridContainer
var _balance_label: Label
var _status_label: Label
var _player_cards: Dictionary = {}
var _pvp_list: VBoxContainer
var _shop_text: RichTextLabel
var _store_provider_select: OptionButton
var _store_provider_ids: Array = []
var _store_product_input: LineEdit
var _store_status_label: Label
var _tabs: TabContainer


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	mouse_filter = Control.MOUSE_FILTER_STOP
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_build_interface()
	visible = false


func configure(
	player_costs: Array,
	pvp_document: Dictionary,
	shop_contract: Dictionary,
	monetization_service: MonetizationService
) -> void:
	_player_costs = player_costs.duplicate()
	_pvp_arrays = pvp_document.get("arrays", {})
	_shop_contract = shop_contract
	_monetization_service = monetization_service
	_monetization_service.provider_selected.connect(_on_store_provider_selected)
	_monetization_service.provider_status.connect(_on_store_provider_status)
	_monetization_service.product_query_result.connect(_on_store_product_query_result)
	_monetization_service.purchase_result.connect(_on_store_purchase_result)
	_monetization_service.restore_result.connect(_on_store_restore_result)
	_monetization_service.rewarded_ad_result.connect(_on_store_rewarded_ad_result)
	_refresh_player_cards()
	_refresh_pvp_table()
	_refresh_shop_contract()
	_refresh_store_page()


func open_panel(wallet: int, purchased: Dictionary) -> void:
	_wallet = wallet
	_purchased = purchased.duplicate()
	visible = true
	_tabs.current_tab = 0
	_status_label.text = "Prototype ledger only; displayed costs come from decoded PlayerCosts[]."
	_refresh_player_states()


func set_economy_state(wallet: int, purchased: Dictionary) -> void:
	_wallet = wallet
	_purchased = purchased.duplicate()
	_refresh_player_states()


func report_result(message: String) -> void:
	_status_label.text = message


func _build_interface() -> void:
	var backdrop := ColorRect.new()
	backdrop.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	backdrop.color = Color(0.003, 0.009, 0.032, 0.93)
	backdrop.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(backdrop)

	var panel := PanelContainer.new()
	panel.anchor_left = 0.035
	panel.anchor_top = 0.045
	panel.anchor_right = 0.965
	panel.anchor_bottom = 0.955
	panel.add_theme_stylebox_override("panel", _panel_style(Color(0.022, 0.044, 0.105, 0.99)))
	add_child(panel)

	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation", 8)
	panel.add_child(column)

	var header := HBoxContainer.new()
	header.add_theme_constant_override("separation", 8)
	column.add_child(header)

	var title := Label.new()
	title.text = "ECONOMY  /  DECODED DATA"
	title.add_theme_font_size_override("font_size", 20)
	title.add_theme_color_override("font_color", Color(0.62, 0.92, 1.0))
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(title)

	_balance_label = Label.new()
	_balance_label.add_theme_font_size_override("font_size", 15)
	_balance_label.add_theme_color_override("font_color", Color(1.0, 0.80, 0.43))
	header.add_child(_balance_label)

	var close_button := Button.new()
	close_button.text = "CLOSE"
	close_button.custom_minimum_size = Vector2(88, 44)
	close_button.focus_mode = Control.FOCUS_NONE
	close_button.pressed.connect(_on_close_pressed)
	header.add_child(close_button)

	_status_label = Label.new()
	_status_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_status_label.add_theme_font_size_override("font_size", 13)
	_status_label.add_theme_color_override("font_color", Color(0.76, 0.84, 0.98))
	column.add_child(_status_label)

	_tabs = TabContainer.new()
	_tabs.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_tabs.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	column.add_child(_tabs)

	_build_player_page()
	_build_pvp_page()
	_build_shop_page()
	_build_store_page()


func _build_player_page() -> void:
	var scroll := ScrollContainer.new()
	scroll.name = "PLAYER COSTS"
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_tabs.add_child(scroll)

	var page := VBoxContainer.new()
	page.add_theme_constant_override("separation", 8)
	scroll.add_child(page)

	var note := Label.new()
	note.text = (
		"24 decoded playerIndex rows · coin cost only. Index-to-ship-ID mapping is UNKNOWN; "
		+ "this panel does not assign ship identities."
	)
	note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	note.add_theme_font_size_override("font_size", 13)
	note.add_theme_color_override("font_color", Color(0.69, 0.82, 0.96))
	page.add_child(note)

	_player_grid = GridContainer.new()
	_player_grid.columns = 2
	_player_grid.add_theme_constant_override("h_separation", 8)
	_player_grid.add_theme_constant_override("v_separation", 8)
	_player_grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	page.add_child(_player_grid)


func _build_pvp_page() -> void:
	var scroll := ScrollContainer.new()
	scroll.name = "PVP ARRAYS"
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_tabs.add_child(scroll)

	_pvp_list = VBoxContainer.new()
	_pvp_list.add_theme_constant_override("separation", 8)
	_pvp_list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(_pvp_list)


func _build_shop_page() -> void:
	var scroll := ScrollContainer.new()
	scroll.name = "SHOP RULES"
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_tabs.add_child(scroll)

	_shop_text = RichTextLabel.new()
	_shop_text.bbcode_enabled = true
	_shop_text.fit_content = true
	_shop_text.scroll_active = false
	_shop_text.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_shop_text.add_theme_font_size_override("normal_font_size", 15)
	_shop_text.add_theme_color_override("default_color", Color(0.81, 0.89, 1.0))
	scroll.add_child(_shop_text)


func _build_store_page() -> void:
	var scroll := ScrollContainer.new()
	scroll.name = "STORE STUBS"
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_tabs.add_child(scroll)

	var page := VBoxContainer.new()
	page.add_theme_constant_override("separation", 9)
	page.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(page)

	var note := Label.new()
	note.text = (
		"STUB_ONLY · No SDK, network, receipt, entitlement, payment, or ad reward is active. "
		+ "The source manifest has product IDs only; prices are UNKNOWN."
	)
	note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	note.add_theme_font_size_override("font_size", 13)
	note.add_theme_color_override("font_color", Color(1.0, 0.79, 0.47))
	page.add_child(note)

	var provider_row := HBoxContainer.new()
	provider_row.add_theme_constant_override("separation", 8)
	page.add_child(provider_row)
	_store_provider_select = OptionButton.new()
	_store_provider_select.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	provider_row.add_child(_store_provider_select)
	var select_button := Button.new()
	select_button.text = "SELECT STUB"
	select_button.custom_minimum_size = Vector2(130, 44)
	select_button.focus_mode = Control.FOCUS_NONE
	select_button.pressed.connect(_on_store_select_pressed)
	provider_row.add_child(select_button)

	var product_row := HBoxContainer.new()
	product_row.add_theme_constant_override("separation", 8)
	page.add_child(product_row)
	var product_label := Label.new()
	product_label.text = "PRODUCT ID"
	product_label.add_theme_font_size_override("font_size", 13)
	product_row.add_child(product_label)
	_store_product_input = LineEdit.new()
	_store_product_input.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_store_product_input.placeholder_text = "Source product ID; no price data"
	product_row.add_child(_store_product_input)

	var action_row_one := HBoxContainer.new()
	action_row_one.add_theme_constant_override("separation", 8)
	page.add_child(action_row_one)
	var query_button := Button.new()
	query_button.text = "QUERY PRODUCTS"
	query_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	query_button.focus_mode = Control.FOCUS_NONE
	query_button.pressed.connect(_on_store_query_pressed)
	action_row_one.add_child(query_button)
	var purchase_button := Button.new()
	purchase_button.text = "TEST PURCHASE"
	purchase_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	purchase_button.focus_mode = Control.FOCUS_NONE
	purchase_button.pressed.connect(_on_store_purchase_pressed)
	action_row_one.add_child(purchase_button)

	var action_row_two := HBoxContainer.new()
	action_row_two.add_theme_constant_override("separation", 8)
	page.add_child(action_row_two)
	var restore_button := Button.new()
	restore_button.text = "RESTORE"
	restore_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	restore_button.focus_mode = Control.FOCUS_NONE
	restore_button.pressed.connect(_on_store_restore_pressed)
	action_row_two.add_child(restore_button)
	var ad_button := Button.new()
	ad_button.text = "TEST REWARDED AD"
	ad_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	ad_button.focus_mode = Control.FOCUS_NONE
	ad_button.pressed.connect(_on_store_ad_pressed)
	action_row_two.add_child(ad_button)

	_store_status_label = Label.new()
	_store_status_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_store_status_label.add_theme_font_size_override("font_size", 13)
	_store_status_label.add_theme_color_override("font_color", Color(0.72, 0.86, 1.0))
	page.add_child(_store_status_label)


func _refresh_store_page() -> void:
	if not is_instance_valid(_store_provider_select) or not is_instance_valid(_store_status_label):
		return
	_store_provider_ids.clear()
	_store_provider_select.clear()
	if not is_instance_valid(_monetization_service):
		_store_status_label.text = "Monetization service is not configured."
		return
	for summary_value: Variant in _monetization_service.get_provider_summaries():
		if summary_value is Dictionary:
			var summary: Dictionary = summary_value
			var provider_id := str(summary.get("provider_id", ""))
			_store_provider_ids.append(provider_id)
			_store_provider_select.add_item(
				"%s  ·  STUB ONLY" % str(summary.get("display_name", provider_id))
			)
	if not _store_provider_ids.is_empty():
		_store_provider_select.select(0)
	var product_ids := _monetization_service.get_product_ids()
	if not product_ids.is_empty() and _store_product_input.text.is_empty():
		_store_product_input.text = str(product_ids[0])
	_store_status_label.text = (
		"%d source product IDs loaded. No provider is active until selected; " % product_ids.size()
		+ "all adapter calls fail closed."
	)


func _refresh_player_cards() -> void:
	if not is_instance_valid(_player_grid):
		return
	for child in _player_grid.get_children():
		child.queue_free()
	_player_cards.clear()
	for index in range(_player_costs.size()):
		var cost := int(_player_costs[index])
		var card := PanelContainer.new()
		card.custom_minimum_size = Vector2(0, 106)
		card.add_theme_stylebox_override("panel", _panel_style(Color(0.04, 0.073, 0.14, 0.96)))
		_player_grid.add_child(card)

		var stack := VBoxContainer.new()
		stack.add_theme_constant_override("separation", 4)
		card.add_child(stack)

		var heading := Label.new()
		heading.text = "PLAYER INDEX %02d" % index
		heading.add_theme_font_size_override("font_size", 15)
		heading.add_theme_color_override("font_color", Color(0.62, 0.91, 1.0))
		stack.add_child(heading)

		var price_label := Label.new()
		price_label.text = "COIN PRICE  %d" % cost if cost >= 0 else "COIN PRICE  -1 SENTINEL"
		price_label.add_theme_font_size_override("font_size", 14)
		price_label.add_theme_color_override("font_color", Color(1.0, 0.80, 0.43))
		stack.add_child(price_label)

		var bottom := HBoxContainer.new()
		bottom.add_theme_constant_override("separation", 6)
		stack.add_child(bottom)

		var state_label := Label.new()
		state_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		state_label.add_theme_font_size_override("font_size", 12)
		state_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		bottom.add_child(state_label)

		var buy_button := Button.new()
		buy_button.custom_minimum_size = Vector2(92, 42)
		buy_button.focus_mode = Control.FOCUS_NONE
		buy_button.pressed.connect(_on_player_buy_pressed.bind(index))
		bottom.add_child(buy_button)
		_player_cards[index] = {"cost": cost, "state": state_label, "button": buy_button}
	_refresh_player_states()


func _refresh_player_states() -> void:
	if not is_instance_valid(_balance_label):
		return
	_balance_label.text = "PROTO COINS  %d" % _wallet
	for index_value: Variant in _player_cards.keys():
		var index := int(index_value)
		var card: Dictionary = _player_cards[index]
		var cost := int(card["cost"])
		var state: Label = card["state"]
		var button: Button = card["button"]
		if cost < 0:
			state.text = "Sentinel retained; not treated as a negative price."
			state.add_theme_color_override("font_color", Color(0.72, 0.77, 0.89))
			button.text = "UNAVAILABLE"
			button.disabled = true
		elif _purchased.has(index):
			state.text = "Claimed in this local prototype."
			state.add_theme_color_override("font_color", Color(0.43, 0.91, 0.74))
			button.text = "CLAIMED"
			button.disabled = true
		elif _wallet < cost:
			state.text = "Insufficient prototype balance."
			state.add_theme_color_override("font_color", Color(0.94, 0.67, 0.52))
			button.text = "BUY %d" % cost if cost > 0 else "CLAIM FREE"
			button.disabled = cost > 0
		else:
			state.text = "Exact decoded PlayerCosts entry."
			state.add_theme_color_override("font_color", Color(0.62, 0.88, 1.0))
			button.text = "BUY %d" % cost if cost > 0 else "CLAIM FREE"
			button.disabled = false


func _refresh_pvp_table() -> void:
	if not is_instance_valid(_pvp_list):
		return
	for child in _pvp_list.get_children():
		child.queue_free()
	var keys := [
		"rewardIndexs",
		"rewardValues",
		"rewardScales",
		"allBetCoinValues",
		"allBetGemValues",
		"allBetMedalValues"
	]
	var invalid_arrays := false
	for key: String in keys:
		var values: Array = _pvp_arrays.get(key, [])
		if values.size() != 6:
			var warning := Label.new()
			warning.text = "%s: expected six decoded values." % key
			_pvp_list.add_child(warning)
			invalid_arrays = true
	if invalid_arrays:
		return
	var intro := Label.new()
	intro.text = (
		"STATIC_CONFIRMED build-time arrays · six tiers · award behavior RUNTIME_UNVERIFIED. "
		+ "Reward type indexes are shown raw; no currency mapping or match payout is inferred."
	)
	intro.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	intro.add_theme_font_size_override("font_size", 13)
	intro.add_theme_color_override("font_color", Color(0.69, 0.82, 0.96))
	_pvp_list.add_child(intro)
	var indexs: Array = _pvp_arrays.get("rewardIndexs", [])
	var values: Array = _pvp_arrays.get("rewardValues", [])
	var scales: Array = _pvp_arrays.get("rewardScales", [])
	var coins: Array = _pvp_arrays.get("allBetCoinValues", [])
	var gems: Array = _pvp_arrays.get("allBetGemValues", [])
	var medals: Array = _pvp_arrays.get("allBetMedalValues", [])
	if indexs.size() != 6 or values.size() != 6 or scales.size() != 6:
		return
	for tier in range(6):
		var card := PanelContainer.new()
		card.add_theme_stylebox_override("panel", _panel_style(Color(0.04, 0.073, 0.14, 0.96)))
		_pvp_list.add_child(card)
		var stack := VBoxContainer.new()
		stack.add_theme_constant_override("separation", 3)
		card.add_child(stack)
		var title := Label.new()
		title.text = "TIER %d" % (tier + 1)
		title.add_theme_color_override("font_color", Color(0.62, 0.91, 1.0))
		stack.add_child(title)
		var bets := Label.new()
		bets.text = "BET  COIN %d  ·  GEM %d  ·  MEDAL %d" % [coins[tier], gems[tier], medals[tier]]
		bets.add_theme_color_override("font_color", Color(1.0, 0.80, 0.43))
		stack.add_child(bets)
		var reward := Label.new()
		reward.text = (
			"RAW REWARD  index %d  ·  value %d  ·  scale %.16f"
			% [indexs[tier], values[tier], float(scales[tier])]
		)
		reward.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		stack.add_child(reward)


func _refresh_shop_contract() -> void:
	if not is_instance_valid(_shop_text):
		return
	var families: Array = _shop_contract.get("families", [])
	var lines: Array[String] = [
		"[b]Decoded shop contract — structure only where numeric runtime values are absent.[/b]",
		"Shop names: %s" % str(_shop_contract.get("shop_names", [])),
		""
	]
	for family_value: Variant in families:
		if family_value is Dictionary:
			var family: Dictionary = family_value
			lines.append(
				(
					"• %s: five slots, base %d, stored as %s"
					% [
						family.get("name", "?"),
						family.get("slot_base", 0),
						family.get("stored_value", "?")
					]
				)
			)
	var stock: Dictionary = _shop_contract.get("stock_preferences", {})
	var quantity: Dictionary = _shop_contract.get("popup_quantity", {})
	lines.append("")
	lines.append(
		(
			"Stock getter default %d; reset writes %d."
			% [stock.get("getter_default", 0), stock.get("reset_value", 0)]
		)
	)
	lines.append(
		(
			"Popup count starts at %d; slider step %d; maximum rule: %s."
			% [
				quantity.get("initial_count", 1),
				quantity.get("slider_step", 1),
				quantity.get("maximum_rule", "UNKNOWN")
			]
		)
	)
	lines.append(
		(
			"MaxStockCount offset %s; numeric cap: %s."
			% [
				quantity.get("max_stock_count_field_offset_hex", "UNKNOWN"),
				quantity.get("max_stock_count_numeric", "UNKNOWN")
			]
		)
	)
	lines.append("")
	for limitation: Variant in _shop_contract.get("limitations", []):
		lines.append("• %s" % str(limitation))
	lines.append("")
	lines.append(
		"Price table used by the first tab: exact decoded PlayerCosts[24], not Shop_Cell prices."
	)
	_shop_text.text = "\n".join(lines)


func _on_player_buy_pressed(index: int) -> void:
	purchase_requested.emit(index, 1)


func _on_store_select_pressed() -> void:
	if not is_instance_valid(_monetization_service):
		_store_status_label.text = "STUB_ONLY · Monetization service is not configured."
		return
	var selected_index := _store_provider_select.selected
	if selected_index < 0 or selected_index >= _store_provider_ids.size():
		_store_status_label.text = "Choose one local provider stub first."
		return
	_monetization_service.select_provider(str(_store_provider_ids[selected_index]))


func _on_store_query_pressed() -> void:
	_monetization_service.query_products()


func _on_store_purchase_pressed() -> void:
	_monetization_service.request_purchase(_store_product_input.text.strip_edges())


func _on_store_restore_pressed() -> void:
	_monetization_service.request_restore()


func _on_store_ad_pressed() -> void:
	_monetization_service.request_rewarded_ad("prototype-test-placement")


func _on_store_provider_selected(provider_id: String, display_name: String) -> void:
	_store_status_label.text = (
		"STUB_ONLY · selected %s (%s). No live store is called." % [display_name, provider_id]
	)


func _on_store_provider_status(provider_id: String, available: bool, message: String) -> void:
	_store_status_label.text = (
		"STUB_ONLY · %s · available=%s · %s" % [provider_id, str(available), message]
	)


func _on_store_product_query_result(
	provider_id: String, _products: Array, success: bool, message: String
) -> void:
	_store_status_label.text = (
		"STUB_ONLY · product query %s · success=%s · %s" % [provider_id, str(success), message]
	)


func _on_store_purchase_result(
	provider_id: String, product_id: String, success: bool, transaction_id: String, message: String
) -> void:
	_store_status_label.text = (
		"STUB_ONLY · purchase %s/%s · success=%s · tx=%s · %s"
		% [provider_id, product_id, str(success), transaction_id, message]
	)


func _on_store_restore_result(
	provider_id: String, success: bool, _product_ids: Array, message: String
) -> void:
	_store_status_label.text = (
		"STUB_ONLY · restore %s · success=%s · %s" % [provider_id, str(success), message]
	)


func _on_store_rewarded_ad_result(
	provider_id: String, placement_id: String, success: bool, reward_granted: bool, message: String
) -> void:
	_store_status_label.text = (
		"STUB_ONLY · ad %s/%s · success=%s · reward=%s · %s"
		% [provider_id, placement_id, str(success), str(reward_granted), message]
	)


func _on_close_pressed() -> void:
	visible = false
	close_requested.emit()


func _panel_style(background: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = background
	style.border_color = Color(0.26, 0.73, 0.92, 0.42)
	style.set_border_width_all(1)
	style.set_corner_radius_all(10)
	style.content_margin_left = 10.0
	style.content_margin_top = 8.0
	style.content_margin_right = 10.0
	style.content_margin_bottom = 8.0
	return style
