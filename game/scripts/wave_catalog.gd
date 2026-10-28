class_name WaveCatalog
extends RefCounted

## Runtime view of res://data/launch_slice_waves.json plus its derived data.
##
## Rows are STATIC_CONFIRMED copies of datas/waves.json spawner rows (see the
## generator in game/tools/build_launch_slice_data.py). Anything the runtime adds
## on top (x placement, spawn ordering) is documented as new design in
## wave_director.gd.

const WAVES_PATH := "res://data/launch_slice_waves.json"
const MOVEMENT_PATH := "res://data/enemy_movement_slice.json"
const GUNS_PATH := "res://data/enemy_guns_slice.json"
const HP_PATH := "res://data/enemy_hp_by_id.json"

var stages: Array = []
var boss_rows: Array = []
var boss_prefab := ""
var errors: Array = []
var warnings: Array = []
var ready := false
var total_entries := 0
var median_rate := 0.0
var rate_statistics: Dictionary = {}
var source: Dictionary = {}
var design_decisions: Array = []

var _hp_by_id: Dictionary = {}
var _movement_by_prefab: Dictionary = {}
var _guns_by_prefab: Dictionary = {}
var _fallback_profile: Dictionary = {}


func load_default() -> bool:
	return load_all(WAVES_PATH, MOVEMENT_PATH, GUNS_PATH, HP_PATH)


func load_all(waves_path: String, movement_path: String, guns_path: String, hp_path: String) -> bool:
	errors.clear()
	warnings.clear()
	var waves := _read_object(waves_path)
	if waves.is_empty():
		errors.append("cannot read %s" % waves_path)
		return false
	var movement := _read_object(movement_path)
	if movement.is_empty():
		errors.append("cannot read %s" % movement_path)
		return false
	var guns := _read_object(guns_path)
	if guns.is_empty():
		errors.append("cannot read %s" % guns_path)
		return false
	var hp_document := _read_object(hp_path)
	if hp_document.is_empty():
		errors.append("cannot read %s" % hp_path)
		return false

	source = waves.get("source", {})
	design_decisions = waves.get("design_decisions", [])
	stages = waves.get("stages", [])
	var boss: Dictionary = waves.get("boss", {})
	boss_rows = boss.get("rows", [])
	boss_prefab = str(boss.get("prefab", ""))
	_hp_by_id = hp_document.get("hp_by_id", {})
	_movement_by_prefab = movement.get("by_prefab", {})
	_guns_by_prefab = guns.get("by_prefab", {})
	_fallback_profile = guns.get("slice_fallback", {})
	rate_statistics = waves.get("rate_statistics", {})
	median_rate = float(rate_statistics.get("median_positive_rate", 0.0))

	total_entries = 0
	for stage_value: Variant in stages:
		if not stage_value is Dictionary:
			errors.append("stage entry is not an object")
			continue
		var stage: Dictionary = stage_value
		total_entries += int(stage.get("entries", 0))
		var declared := int(stage.get("entries", -1))
		var counted := 0
		for row_value: Variant in stage.get("rows", []):
			var row: Dictionary = row_value
			var enemies: Array = row.get("enemies", [])
			counted += enemies.size() * int(row.get("copies", 0))
		if declared != counted:
			errors.append(
				"%s declares %d entries but rows hold %d"
				% [str(stage.get("wave", "?")), declared, counted]
			)

	var declared_total := int(waves.get("stage_total_entries", -1))
	if declared_total != total_entries:
		errors.append("stage_total_entries %d != counted %d" % [declared_total, total_entries])

	_validate_prefabs()
	ready = errors.is_empty() and not stages.is_empty() and total_entries > 0
	return ready


func _read_object(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		return {}
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not parsed is Dictionary:
		return {}
	return parsed


func _validate_prefabs() -> void:
	for prefab: String in used_prefabs():
		if prefab == boss_prefab:
			continue
		if not has_hp(prefab):
			errors.append("%s has no STATIC_CONFIRMED HP row" % prefab)
		if not has_movement(prefab):
			errors.append("%s has no source movement row" % prefab)
		if gun_profile_for(prefab).is_empty():
			errors.append("%s has neither a decoded gun row nor the fallback" % prefab)


func used_prefabs() -> Array:
	var prefabs: Array = []
	for stage_value: Variant in stages:
		var stage: Dictionary = stage_value
		for row_value: Variant in stage.get("rows", []):
			var row: Dictionary = row_value
			for enemy_value: Variant in row.get("enemies", []):
				var prefab := str(enemy_value)
				if not prefabs.has(prefab):
					prefabs.append(prefab)
	for row_value: Variant in boss_rows:
		var row: Dictionary = row_value
		for enemy_value: Variant in row.get("enemies", []):
			var prefab := str(enemy_value)
			if not prefabs.has(prefab):
				prefabs.append(prefab)
	return prefabs


static func id_from_prefab(prefab: String) -> String:
	var parts := prefab.split("-")
	return parts[parts.size() - 1] if parts.size() > 1 else prefab


func has_hp(prefab: String) -> bool:
	return _hp_by_id.has(id_from_prefab(prefab))


func hp_for(prefab: String) -> float:
	return float(_hp_by_id.get(id_from_prefab(prefab), 0.0))


func has_movement(prefab: String) -> bool:
	return _movement_by_prefab.has(prefab)


func movement_for(prefab: String) -> Dictionary:
	return _movement_by_prefab.get(prefab, {})


func has_decoded_gun(prefab: String) -> bool:
	var entry: Dictionary = _guns_by_prefab.get(prefab, {})
	return entry.get("runtime_profile") != null


func gun_profile_for(prefab: String) -> Dictionary:
	var entry: Dictionary = _guns_by_prefab.get(prefab, {})
	var profile: Variant = entry.get("runtime_profile")
	if profile is Dictionary:
		var chosen: Dictionary = (profile as Dictionary).duplicate(true)
		chosen["evidence"] = "STATIC_CONFIRMED"
		chosen["selection"] = str(entry.get("selection", "source_agreement"))
		return chosen
	if _fallback_profile.is_empty():
		return {}
	var fallback := _fallback_profile.duplicate(true)
	fallback["evidence"] = "INFERRED_FALLBACK"
	fallback["selection"] = "INFERRED_FALLBACK_corpus_median"
	return fallback


func stage_count() -> int:
	return stages.size()


func stage_name(index: int) -> String:
	if index < 0 or index >= stages.size():
		return ""
	return str((stages[index] as Dictionary).get("wave", ""))


func stage_rows(index: int) -> Array:
	if index < 0 or index >= stages.size():
		return []
	return (stages[index] as Dictionary).get("rows", [])


func stage_entries(index: int) -> int:
	if index < 0 or index >= stages.size():
		return 0
	return int((stages[index] as Dictionary).get("entries", 0))


func boss_entries() -> int:
	var entries := 0
	for row_value: Variant in boss_rows:
		var row: Dictionary = row_value
		entries += (row.get("enemies", []) as Array).size() * int(row.get("copies", 0))
	return entries


func spawn_y_values() -> Array:
	var values: Array = []
	for stage_value: Variant in stages:
		var stage: Dictionary = stage_value
		for row_value: Variant in stage.get("rows", []):
			var row: Dictionary = row_value
			var y := float(row.get("y_spawn", 0.0))
			if not values.has(y):
				values.append(y)
	values.sort()
	return values
