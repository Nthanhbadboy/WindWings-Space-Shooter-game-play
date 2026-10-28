class_name AudioMixer
extends RefCounted

## Audio settings for the launch slice.
##
## STATIC_CONFIRMED rules — datas/audio_rules.json:
##   mute:          MUTE_AUDIO int32, missing default 0, predicate "stored == 1"
##   sound_volume:  VolumeSound float32, missing default ~0.73, "mute -> 0 else saved float"
##   music_volume:  VolumeMusic float32, missing default ~0.3, same predicate
##   pause:         AudioListener.pause, separate from Time.timeScale
## The mapping to a Godot bus layout, and the placeholder tones, are NEW_DESIGN.

const DATA_PATH := "res://data/audio_defaults.json"
const SFX_BUS := "SFX"
const MUSIC_BUS := "Music"

var defaults := {}
var source: Dictionary = {}
var ready := false


static func effective_volume(stored_volume: float, muted: bool) -> float:
	if muted:
		return 0.0
	return clampf(stored_volume, 0.0, 1.0)


static func linear_to_gain(volume: float) -> float:
	return clampf(volume, 0.0, 1.0)


func load_default() -> bool:
	if not FileAccess.file_exists(DATA_PATH):
		return false
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if not parsed is Dictionary:
		return false
	var document: Dictionary = parsed
	defaults = document.get("keys", {})
	source = document.get("source", {})
	ready = defaults.has("mute") and defaults.has("sound_volume") and defaults.has("music_volume")
	return ready


func default_muted() -> bool:
	return int(defaults.get("mute", {}).get("default", 0)) == 1


func default_sound_volume() -> float:
	return float(defaults.get("sound_volume", {}).get("default", 0.73))


func default_music_volume() -> float:
	return float(defaults.get("music_volume", {}).get("default", 0.3))


static func apply_to_buses(muted: bool, sound_volume: float, music_volume: float, paused: bool) -> bool:
	var applied := false
	var sfx_index := AudioServer.get_bus_index(SFX_BUS)
	if sfx_index >= 0:
		# AudioListener.pause analogue: SFX is silenced while the tree is paused,
		# music keeps playing because the source sets ignoreListenerPause.
		var sfx_volume := 0.0 if paused else effective_volume(sound_volume, muted)
		AudioServer.set_bus_mute(sfx_index, sfx_volume <= 0.001)
		AudioServer.set_bus_volume_db(sfx_index, linear_to_db(maxf(sfx_volume, 0.0001)))
		applied = true
	var music_index := AudioServer.get_bus_index(MUSIC_BUS)
	if music_index >= 0:
		var music := effective_volume(music_volume, muted)
		AudioServer.set_bus_mute(music_index, music <= 0.001)
		AudioServer.set_bus_volume_db(music_index, linear_to_db(maxf(music, 0.0001)))
		applied = true
	return applied
