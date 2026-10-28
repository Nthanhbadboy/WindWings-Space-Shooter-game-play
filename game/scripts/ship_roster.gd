class_name ShipRoster
extends RefCounted

## Ship roster for the launch slice.
##
## STATIC_CONFIRMED — docs/spec/BALANCE.md §1.1b and START_HERE row 9:
## combat resolves implementation N to array index N-1, ship 10001 -> index 2,
## ship 10003 -> index 0 and ships 10004+ -> id - 10001. The same section states
## that the index order is NOT the ship order 1..25 and that no ship-id table is
## decoded; the ships offered here are therefore an explicit slice roster.
##
## STATIC_CONFIRMED — StartMainCannonDamages / PlayerCosts / StartMainCannonRate
## are decoded 24-entry arrays in res://data/player_start_stats.json.
##
## INFERRED NEW_DESIGN — the slice offers three ships whose decoded damage keeps
## a run winnable; player index 1 (ship 10002, 220 damage) is excluded from the
## roster because the slice tuning would make the boss unbeatable. Exclusion is a
## slice decision, not a claim that the ship is locked in the source game.

const STATS_PATH := "res://data/player_start_stats.json"
const ROSTER := [10003, 10001, 10004]
const EXCLUDED_SHIP_IDS := [10002]

var damage_values: Array = []
var cost_values: Array = []
var rate_values: Array = []
var ready := false
var error := ""


func load_default() -> bool:
	if not FileAccess.file_exists(STATS_PATH):
		error = "missing %s" % STATS_PATH
		return false
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(STATS_PATH))
	if not parsed is Dictionary:
		error = "player stats is not a JSON object"
		return false
	damage_values = _field_values(parsed, "StartMainCannonDamages")
	cost_values = _field_values(parsed, "PlayerCosts")
	rate_values = _field_values(parsed, "StartMainCannonRate")
	ready = damage_values.size() == 24 and cost_values.size() == 24
	if not ready:
		error = "expected 24-entry decoded arrays"
	return ready


func _field_values(document: Dictionary, field_name: String) -> Array:
	for row_value: Variant in document.get("fields", []):
		var row: Dictionary = row_value
		if str(row.get("field", "")) == field_name:
			return row.get("values", [])
	return []


static func combat_index_for_ship(ship_id: int) -> int:
	if ship_id == 10001:
		return 2
	if ship_id == 10003:
		return 0
	if ship_id >= 10004:
		return ship_id - 10001
	return -1


func roster_ships() -> Array:
	return ROSTER.duplicate()


func damage_for_ship(ship_id: int) -> float:
	var index := combat_index_for_ship(ship_id)
	if index < 0 or index >= damage_values.size():
		return 0.0
	return float(damage_values[index])


func cost_for_ship(ship_id: int) -> int:
	var index := combat_index_for_ship(ship_id)
	if index < 0 or index >= cost_values.size():
		return -1
	return int(cost_values[index])


func decoded_rate_for_ship(ship_id: int) -> float:
	var index := combat_index_for_ship(ship_id)
	if index < 0 or index >= rate_values.size():
		return 0.0
	return float(rate_values[index])


func max_hp(store: SaveStore, ability7_count: int) -> float:
	if store == null:
		return LaunchRules.max_hp(LaunchRules.START_HP, 0, ability7_count)
	var tech_points := store.get_int("PlayerStatPoints%s", [0])
	return LaunchRules.max_hp(LaunchRules.START_HP, tech_points, ability7_count)
