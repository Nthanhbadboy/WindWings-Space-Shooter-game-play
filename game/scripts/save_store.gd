class_name SaveStore
extends RefCounted

## Save/load for the M2 launch slice.
##
## Key names, types and defaults come from docs/spec/MISSING_FOR_NEW_GAME.md
## §2.3 / §2.3b and are enumerated in res://data/save_contract.json. The Godot
## JSON file, the atomic write and the pure getters are NEW_DESIGN; the source
## contract proves neither atomicity nor side-effect-free reads.

const CONTRACT_PATH := "res://data/save_contract.json"
const SAVE_PATH := "user://launch_slice_save.json"
const SAVE_SCHEMA := "windwings.launch_slice.save/1"
const SAVE_VERSION := 1

var _keys: Dictionary = {}
var _values: Dictionary = {}
var _contract: Dictionary = {}
var _contract_ok := false
var _last_error := ""


func _init() -> void:
	_contract_ok = _load_contract()


func _load_contract() -> bool:
	if not FileAccess.file_exists(CONTRACT_PATH):
		_last_error = "missing %s" % CONTRACT_PATH
		return false
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT_PATH))
	if not parsed is Dictionary:
		_last_error = "contract is not a JSON object"
		return false
	_contract = parsed
	for entry_value: Variant in _contract.get("keys", []):
		if not entry_value is Dictionary:
			continue
		var entry: Dictionary = entry_value
		var template := str(entry.get("template", ""))
		if template.is_empty():
			continue
		_keys[template] = entry
	return not _keys.is_empty()


func contract_ready() -> bool:
	return _contract_ok


func last_error() -> String:
	return _last_error


func contract() -> Dictionary:
	return _contract


func resolve(template: String, args: Array = []) -> String:
	if args.is_empty():
		return template
	return template % args


func _definition(template: String) -> Dictionary:
	return _keys.get(template, {})


func has_definition(template: String) -> bool:
	return _keys.has(template)


func default_value(template: String, args: Array = []) -> Variant:
	var definition := _definition(template)
	if definition.is_empty():
		return null
	var by_index: Dictionary = definition.get("default_by_index", {})
	if not by_index.is_empty() and not args.is_empty():
		var index_key := str(args[0])
		if by_index.has(index_key):
			return by_index[index_key]
		if by_index.has("*"):
			return by_index["*"]
	return definition.get("default", null)


func value_of(template: String, args: Array = []) -> Variant:
	var key := resolve(template, args)
	if _values.has(key):
		return _values[key]
	return default_value(template, args)


func get_int(template: String, args: Array = []) -> int:
	var value: Variant = value_of(template, args)
	if value == null:
		_last_error = "unknown key template %s" % template
		return 0
	return int(value)


func get_float(template: String, args: Array = []) -> float:
	var value: Variant = value_of(template, args)
	if value == null:
		_last_error = "unknown key template %s" % template
		return 0.0
	return float(value)


func get_bool(template: String, args: Array = []) -> bool:
	return get_int(template, args) == 1


func set_int(template: String, args: Array, value: int) -> void:
	if not has_definition(template):
		_last_error = "unknown key template %s" % template
		return
	_values[resolve(template, args)] = int(value)


func set_float(template: String, args: Array, value: float) -> void:
	if not has_definition(template):
		_last_error = "unknown key template %s" % template
		return
	_values[resolve(template, args)] = float(value)


func has_stored(template: String, args: Array = []) -> bool:
	return _values.has(resolve(template, args))


func stored_keys() -> Array:
	var keys := _values.keys()
	keys.sort()
	return keys


# --- §2.3 / §2.3b repair rules -------------------------------------------------

func player_used(slot: int) -> int:
	var stored := get_int("PlayerUsed%s", [slot])
	if stored > 0:
		return stored
	set_int("PlayerUsed%s", [0], 10001)
	set_int("PlayerUsed%s", [1], 10002)
	return get_int("PlayerUsed%s", [slot])


func player_unlocked(ship_id: int) -> bool:
	if ship_id < 10003:
		return true
	return get_int("PlayerUnlocked%s", [ship_id]) == 1


func player_rank(ship_id: int) -> int:
	var rank_value := get_int("PLAYER_RANK%s", [ship_id])
	if rank_value <= 1:
		set_int("PLAYER_RANK%s", [ship_id], 2)
		rank_value = 2
	if get_int("TRIAL_ID_%s", [ship_id]) == 1:
		return get_int("TRIAL_RANK_%s", [ship_id])
	return rank_value


func player_level(ship_id: int) -> int:
	if get_int("TRIAL_ID_%s", [ship_id]) == 1:
		return get_int("TRIAL_LEVEL_%s", [ship_id])
	return get_int("PLAYER_LEVEL%s", [ship_id])


func drone_used(slot: int) -> int:
	var stored := get_int("DroneUsed%s", [slot])
	if stored < 0:
		set_int("DroneUsed%s", [slot], 0)
		return 0
	return stored


# --- stars ---------------------------------------------------------------------

func star_for_stage(stage_index: int, mode_index: int) -> int:
	return maxi(get_int("StarStageMaster%s_%s", [stage_index, mode_index]), 0)


func star_total() -> int:
	var total := 0
	for key: String in _values.keys():
		if not key.begins_with("StarStageMaster"):
			continue
		total += maxi(int(_values[key]), 0)
	return total


func record_stars(stage_index: int, mode_index: int, stars: int) -> int:
	var previous := star_for_stage(stage_index, mode_index)
	var best := maxi(previous, clampi(stars, 0, 3))
	set_int("StarStageMaster%s_%s", [stage_index, mode_index], best)
	set_int("StarCount", [], star_total())
	return best


# --- audio settings ------------------------------------------------------------

func audio_muted() -> bool:
	return get_int("MUTE_AUDIO", []) == 1


func sound_volume() -> float:
	return clampf(get_float("VolumeSound", []), 0.0, 1.0)


func music_volume() -> float:
	return clampf(get_float("VolumeMusic", []), 0.0, 1.0)


func set_audio(muted: bool, sound: float, music: float) -> void:
	set_int("MUTE_AUDIO", [], 1 if muted else 0)
	set_float("VolumeSound", [], clampf(sound, 0.0, 1.0))
	set_float("VolumeMusic", [], clampf(music, 0.0, 1.0))


# --- disk ----------------------------------------------------------------------

func save_to(path: String = SAVE_PATH) -> Error:
	var document := {
		"schema": SAVE_SCHEMA,
		"version": SAVE_VERSION,
		"values": _values,
	}
	var temp_path := path + ".tmp"
	var handle := FileAccess.open(temp_path, FileAccess.WRITE)
	if handle == null:
		_last_error = "cannot write %s" % temp_path
		return FileAccess.get_open_error()
	handle.store_string(JSON.stringify(document, "\t", false))
	handle.flush()
	handle.close()
	var absolute_temp := ProjectSettings.globalize_path(temp_path)
	var absolute_target := ProjectSettings.globalize_path(path)
	var rename_error := DirAccess.rename_absolute(absolute_temp, absolute_target)
	if rename_error != OK:
		_last_error = "cannot rename temp save (error %d)" % rename_error
		return rename_error
	return OK


func load_from(path: String = SAVE_PATH) -> Error:
	_last_loaded_path = path
	if not FileAccess.file_exists(path):
		_last_error = "no save at %s" % path
		return ERR_FILE_NOT_FOUND
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not parsed is Dictionary:
		_last_error = "save is not a JSON object"
		return ERR_PARSE_ERROR
	var document: Dictionary = parsed
	if str(document.get("schema", "")) != SAVE_SCHEMA:
		_last_error = "unexpected save schema %s" % str(document.get("schema", ""))
		return ERR_FILE_UNRECOGNIZED
	var values: Variant = document.get("values", {})
	if not values is Dictionary:
		_last_error = "save values are not an object"
		return ERR_PARSE_ERROR
	for key_value: Variant in (values as Dictionary).keys():
		_values[str(key_value)] = (values as Dictionary)[key_value]
	return OK


var _last_loaded_path := ""


func last_loaded_path() -> String:
	return _last_loaded_path


func snapshot() -> Dictionary:
	return _values.duplicate(true)


func static_defaults() -> Dictionary:
	var defaults := {}
	for template: String in _keys.keys():
		var args: Array = []
		if template.contains("%s"):
			if template.count("%s") == 2:
				args = [0, 0]
			else:
				args = [0]
		defaults[resolve(template, args)] = default_value(template, args)
	return defaults
