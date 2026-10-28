class_name BossPattern
extends RefCounted

## Boss timeline for the launch slice, read from res://data/boss_slice.json.
##
## STATIC_CONFIRMED — datas/boss_hp.json (Boss-37001 hp_max) and
## datas/boss_anim_events.csv (Attack2 Shoot events). The flight path and the
## projectile ballistics are INFERRED new design and are flagged in the data file.

const DATA_PATH := "res://data/boss_slice.json"

var prefab := ""
var hp_max := 0.0
var clip := ""
var loop_seconds := 1.0
var shot_times: Array = []
var source: Dictionary = {}
var design_decisions: Array = []
var ready := false
var error := ""


func load_default() -> bool:
	return load_from_path(DATA_PATH)


func load_from_path(path: String) -> bool:
	if not FileAccess.file_exists(path):
		error = "missing %s" % path
		return false
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not parsed is Dictionary:
		error = "boss data is not a JSON object"
		return false
	var document: Dictionary = parsed
	prefab = str(document.get("prefab", ""))
	hp_max = float(document.get("hp_max", 0.0))
	clip = str(document.get("clip", ""))
	loop_seconds = maxf(float(document.get("clip_loop_seconds", 0.0)), 0.001)
	shot_times = []
	for time_value: Variant in document.get("shot_times", []):
		shot_times.append(float(time_value))
	shot_times.sort()
	source = document.get("source", {})
	design_decisions = document.get("design_decisions", [])
	ready = not prefab.is_empty() and hp_max > 0.0 and not shot_times.is_empty()
	if not ready:
		error = "boss data incomplete"
	return ready


static func shots_crossed(times: Array, loop: float, previous_elapsed: float, current_elapsed: float) -> int:
	if times.is_empty() or loop <= 0.0 or current_elapsed <= previous_elapsed:
		return 0
	var count := 0
	for time_value: Variant in times:
		var event_time := float(time_value)
		var cycle := floori(previous_elapsed / loop)
		while true:
			var absolute := float(cycle) * loop + event_time
			if absolute > previous_elapsed and absolute <= current_elapsed:
				count += 1
			if absolute > current_elapsed:
				break
			cycle += 1
	return count


func shots_in_interval(previous_elapsed: float, current_elapsed: float) -> int:
	return shots_crossed(shot_times, loop_seconds, previous_elapsed, current_elapsed)


func loop_progress(elapsed: float) -> float:
	return fposmod(elapsed, loop_seconds)
