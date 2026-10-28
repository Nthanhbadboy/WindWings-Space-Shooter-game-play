extends Node

## Session singleton for the launch slice (autoload name: Session).
##
## It owns the save document, the selected ship, the audio settings and the
## result of the last run. Playfield and combat numbers stay in LaunchRules.

const SaveStoreScript = preload("res://scripts/save_store.gd")
const ShipRosterScript = preload("res://scripts/ship_roster.gd")
const AudioMixerScript = preload("res://scripts/audio_mixer.gd")
const StarRulesScript = preload("res://scripts/star_rules.gd")

const DEFAULT_SHIP := 10003

var store: SaveStore
var roster: ShipRoster
var mixer: AudioMixer

var selected_ship := DEFAULT_SHIP
var ability7 := 0
var stage_index := 1
var mode_index := 0
var last_result: Dictionary = {}
var startup_notes: Array = []


func _ready() -> void:
	store = SaveStoreScript.new()
	if not store.contract_ready():
		startup_notes.append("save contract failed: %s" % store.last_error())
	var load_error := store.load_from()
	if load_error != OK:
		startup_notes.append("no existing save (%s)" % error_string(load_error))
	roster = ShipRosterScript.new()
	if not roster.load_default():
		startup_notes.append("roster failed: %s" % roster.error)
	mixer = AudioMixerScript.new()
	if not mixer.load_default():
		startup_notes.append("audio defaults failed")
	var used_ship := store.player_used(0)
	selected_ship = used_ship if roster.roster_ships().has(used_ship) else DEFAULT_SHIP
	apply_audio(false)


func ship_damage() -> float:
	return roster.damage_for_ship(selected_ship)


func ship_cost() -> int:
	return roster.cost_for_ship(selected_ship)


func player_max_hp() -> float:
	return roster.max_hp(store, ability7)


func ship_unlocked(ship_id: int) -> bool:
	return store.player_unlocked(ship_id)


func select_ship(ship_id: int) -> bool:
	if not roster.roster_ships().has(ship_id):
		return false
	if not ship_unlocked(ship_id):
		return false
	selected_ship = ship_id
	store.set_int("PlayerUsed%s", [0], ship_id)
	store.save_to()
	return true


func apply_audio(paused: bool) -> void:
	if store == null:
		return
	AudioMixer.apply_to_buses(
		store.audio_muted(), store.sound_volume(), store.music_volume(), paused
	)


func save_audio(muted: bool, sound: float, music: float) -> void:
	store.set_audio(muted, sound, music)
	apply_audio(false)
	var write_error := store.save_to()
	if write_error != OK:
		startup_notes.append("audio save failed: %s" % error_string(write_error))


func record_run(victory: bool, kills: int, entries: int, score: int, wave_reached: int) -> Dictionary:
	var stars := StarRulesScript.stars_for(kills, entries, mode_index) if victory else 0
	var best_before := store.star_for_stage(stage_index, mode_index)
	if victory:
		store.record_stars(stage_index, mode_index, stars)
	store.save_to()
	last_result = {
		"victory": victory,
		"kills": kills,
		"entries": entries,
		"stars": stars,
		"best_before": best_before,
		"best_after": store.star_for_stage(stage_index, mode_index),
		"star_total": maxi(store.get_int("StarCount", []), store.star_total()),
		"score": score,
		"wave_reached": wave_reached,
		"stage_index": stage_index,
		"mode_index": mode_index,
	}
	return last_result


func star_total_for_display() -> int:
	return maxi(store.get_int("StarCount", []), store.star_total())


func best_stars() -> int:
	return store.star_for_stage(stage_index, mode_index)
