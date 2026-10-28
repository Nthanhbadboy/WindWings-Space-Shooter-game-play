extends Control

## Ship select. The three ships come from the decoded 24-entry arrays; the
## ship-to-combat-index mapping is the STATIC_CONFIRMED BALANCE §1.1b rule.

const SHIP_SCENE := preload("res://scenes/hangar_ship.tscn")

var _start_button: Button
var _cards: Dictionary = {}
var _hangar: HangarShip
var _hangar_wrap: Control


func _ready() -> void:
	Session.start_music()
	_build()
	_refresh()


func _build() -> void:
	UIKit.background(self)
	_build_hangar()
	var margin := UIKit.full_margin(self, 24)
	var center := CenterContainer.new()
	margin.add_child(center)

	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation", 14)
	column.custom_minimum_size = Vector2(430, 0)
	center.add_child(column)

	column.add_child(UIKit.title("SELECT SHIP", 34))
	column.add_child(
		UIKit.body(
			"Damage from StartMainCannonDamages[]; combat index per BALANCE §1.1b (10001→2, 10003→0, 10004+→id−10001)",
			12
		)
	)

	for ship_id: int in Session.roster.roster_ships():
		var card := UIKit.button("", 74, 430)
		card.alignment = HORIZONTAL_ALIGNMENT_LEFT
		card.pressed.connect(_on_ship_pressed.bind(ship_id))
		column.add_child(card)
		_cards[ship_id] = card

	column.add_child(
		UIKit.body(
			"Ship 10002 (combat index 1, damage 220) is outside this slice roster: the slice tuning would make the boss unbeatable.",
			11
		)
	)
	column.add_child(UIKit.spacer(6))

	_start_button = UIKit.button("START RUN", 62)
	_start_button.pressed.connect(_on_start)
	column.add_child(_start_button)

	var back := UIKit.button("BACK", 46)
	back.pressed.connect(_on_back)
	column.add_child(back)


func _build_hangar() -> void:
	_hangar_wrap = Control.new()
	_hangar_wrap.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_hangar_wrap.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_hangar_wrap)
	_hangar = SHIP_SCENE.instantiate() as HangarShip
	_hangar_wrap.add_child(_hangar)
	_hangar_wrap.resized.connect(_layout_hangar)
	_layout_hangar()


func _layout_hangar() -> void:
	if _hangar == null or _hangar_wrap == null:
		return
	var size := _hangar_wrap.size
	if size.y <= 0.0:
		return
	var pixels_per_unit := size.y / 11.0
	_hangar.position = Vector2(size.x * 0.5, size.y * 0.30)
	_hangar.scale = Vector2(pixels_per_unit, pixels_per_unit)


func _refresh() -> void:
	for ship_id: int in _cards.keys():
		var card: Button = _cards[ship_id]
		var unlocked: bool = Session.ship_unlocked(ship_id)
		var cost: int = Session.roster.cost_for_ship(ship_id)
		var cost_text := "FREE" if cost == 0 else ("SENTINEL -1" if cost < 0 else str(cost))
		var marker := "▶ " if ship_id == Session.selected_ship else "   "
		card.text = (
			"%sSHIP %d   ·   combat index %d\n"
			+ "damage %.0f   ·   cost %s   ·   rank %d   ·   level %d"
		) % [
			marker,
			ship_id,
			ShipRoster.combat_index_for_ship(ship_id),
			Session.roster.damage_for_ship(ship_id),
			cost_text,
			Session.store.player_rank(ship_id),
			Session.store.player_level(ship_id),
		]
		card.disabled = not unlocked
	if _hangar != null:
		_hangar.set_ship(Session.selected_ship)
	_start_button.disabled = not Session.ship_unlocked(Session.selected_ship)
	_start_button.text = "START RUN  ·  SHIP %d" % Session.selected_ship


func _on_ship_pressed(ship_id: int) -> void:
	Session.play_sfx("click")
	if Session.select_ship(ship_id):
		_refresh()


func _on_start() -> void:
	Session.play_sfx("click")
	get_tree().change_scene_to_file("res://scenes/main.tscn")


func _on_back() -> void:
	Session.play_sfx("click")
	get_tree().change_scene_to_file("res://scenes/menu.tscn")
