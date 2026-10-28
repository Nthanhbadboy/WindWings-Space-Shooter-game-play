extends Node

## Session singleton for the launch slice (autoload name: Session).
##
## It owns the save document, the selected ship, the audio settings and the
## result of the last run. Playfield and combat numbers stay in LaunchRules.

const SaveStoreScript = preload("res://scripts/save_store.gd")
const ShipRosterScript = preload("res://scripts/ship_roster.gd")
const AudioMixerScript = preload("res://scripts/audio_mixer.gd")
const StarRulesScript = preload("res://scripts/star_rules.gd")
const ArtLibraryScript = preload("res://scripts/art_library.gd")
const AnimationVariantScript = preload("res://scripts/animation_variant.gd")

const DEFAULT_SHIP := 10003

var store: SaveStore
var roster: ShipRoster
var mixer: AudioMixer
var art: ArtLibrary
## A / B / C build parameter: which art package folder loads and how it animates.
var variant: AnimationVariant

var selected_ship := DEFAULT_SHIP
var ability7 := 0
var stage_index := 1
var mode_index := 0
var last_result: Dictionary = {}
var startup_notes: Array = []

const SFX_STREAMS := {
	"shot": "res://audio/sfx_shot.wav",
	"hit": "res://audio/sfx_hit.wav",
	"destroy": "res://audio/sfx_destroy.wav",
	"click": "res://audio/sfx_click.wav",
}
const MUSIC_STREAM := "res://audio/music_game.wav"
const SFX_VOICES := 8

var _sfx_players: Array = []
var _sfx_cache: Dictionary = {}
var _music_player: AudioStreamPlayer
var _sfx_cursor := 0


## Menu/build label, e.g. "ANIM-B", so nobody runs the wrong package by mistake.
func variant_label() -> String:
	return variant.label() if variant != null else "ANIM-A"


func variant_is_layered() -> bool:
	return variant == null or variant.is_layered()


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
	variant = AnimationVariantScript.load_default()
	if not variant.error.is_empty():
		startup_notes.append("animation variant: %s" % variant.error)
	art = ArtLibraryScript.new(ArtLibraryScript.CONTRACT_PATH, variant.art_roots())
	if not art.contract_ready():
		startup_notes.append("art slot contract failed: %s" % art.error)
	for problem: Variant in art.validate():
		startup_notes.append("art contract: %s" % str(problem))
	_setup_audio_nodes()
	var used_ship := store.player_used(0)
	selected_ship = used_ship if roster.roster_ships().has(used_ship) else DEFAULT_SHIP
	apply_audio(false)


func _setup_audio_nodes() -> void:
	for _index in range(SFX_VOICES):
		var player := AudioStreamPlayer.new()
		player.bus = "SFX"
		add_child(player)
		_sfx_players.append(player)
	_music_player = AudioStreamPlayer.new()
	_music_player.bus = "Music"
	add_child(_music_player)
	_music_player.finished.connect(_on_music_finished)


func play_sfx(name: String) -> void:
	if _sfx_players.is_empty() or not SFX_STREAMS.has(name):
		return
	var path: String = SFX_STREAMS[name]
	if not ResourceLoader.exists(path):
		return
	if not _sfx_cache.has(path):
		_sfx_cache[path] = load(path)
	var player: AudioStreamPlayer = _sfx_players[_sfx_cursor % _sfx_players.size()]
	_sfx_cursor += 1
	player.stream = _sfx_cache[path]
	player.play()


func start_music() -> void:
	if _music_player == null or _music_player.playing:
		return
	if not ResourceLoader.exists(MUSIC_STREAM):
		return
	_music_player.stream = load(MUSIC_STREAM)
	_music_player.play()


func stop_music() -> void:
	if _music_player != null:
		_music_player.stop()


func clear_boss_music() -> void:
	# The slice has no separate boss track: the source boss_warning rule (PlayMusic
	# enum 0 then 31) is a coroutine sequence that is out of slice scope.
	pass


func _on_music_finished() -> void:
	if _music_player != null and _music_player.stream != null:
		_music_player.play()


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
