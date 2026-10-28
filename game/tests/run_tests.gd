extends SceneTree

## Headless rule tests for the M2 launch slice.
##
## Run:  godot --headless --path game --script res://tests/run_tests.gd
## Exit code 0 = every rule check passed, 1 = at least one failed.
##
## The checks encode the rules the slice must obey (spec numbers, save contract,
## star tiers, boss timeline, audio defaults). They were written before the
## runtime code was wired up and must not be weakened to make a run green.

const LaunchRulesScript = preload("res://scripts/launch_rules.gd")
const SaveStoreScript = preload("res://scripts/save_store.gd")
const StarRulesScript = preload("res://scripts/star_rules.gd")
const WaveCatalogScript = preload("res://scripts/wave_catalog.gd")
const BossPatternScript = preload("res://scripts/boss_pattern.gd")
const AudioMixerScript = preload("res://scripts/audio_mixer.gd")
const ShipRosterScript = preload("res://scripts/ship_roster.gd")
const ArtLibraryScript = preload("res://scripts/art_library.gd")

const ART_CONTRACT_PATH := "res://data/art_slot_contract.json"
const ART_TEST_ROOT := "user://art_test_root"

const TEST_SAVE_PATH := "user://launch_slice_test_save.json"

var _checks := 0
var _failures: Array = []


func _initialize() -> void:
	_test_playfield_and_collision()
	_test_spawn_rate_and_edge()
	_test_camera_and_bounds()
	_test_hp_formula()
	_test_level_delta()
	_test_save_contract_defaults()
	_test_save_contract_repairs()
	_test_save_roundtrip()
	_test_save_rejects_foreign_document()
	_test_star_tiers()
	_test_star_recording()
	_test_wave_catalog()
	_test_boss_pattern()
	_test_audio_rules()
	_test_ship_roster()
	_test_provenance_pins()
	_test_art_slot_contract()
	_test_art_library_fallback()
	_test_art_library_drop_in()

	print("TESTS: %d checks, %d failures" % [_checks, _failures.size()])
	if _failures.is_empty():
		print("TESTS_OK")
		quit(0)
	else:
		for failure: String in _failures:
			printerr("FAIL: %s" % failure)
		print("TESTS_FAILED")
		quit(1)


func check(condition: bool, message: String) -> void:
	_checks += 1
	if not condition:
		_failures.append(message)


func check_eq(actual: Variant, expected: Variant, message: String) -> void:
	_checks += 1
	if actual != expected:
		_failures.append("%s (actual=%s expected=%s)" % [message, str(actual), str(expected)])


func check_float(actual: float, expected: float, message: String, epsilon := 0.0001) -> void:
	_checks += 1
	if absf(actual - expected) > epsilon:
		_failures.append("%s (actual=%f expected=%f)" % [message, actual, expected])


# --- spec numbers --------------------------------------------------------------

func _test_playfield_and_collision() -> void:
	check_float(LaunchRulesScript.PLAYFIELD_WIDTH_UNITS, 20.0, "playfield width is 20 units")
	check_float(LaunchRulesScript.PLAYFIELD_HEIGHT_UNITS, 25.0, "playfield height is 25 units")
	check_float(LaunchRulesScript.PLAYFIELD_MAX_X - LaunchRulesScript.PLAYFIELD_MIN_X, 20.0, "x span is 20")
	check_float(LaunchRulesScript.PLAYFIELD_MAX_Y - LaunchRulesScript.PLAYFIELD_MIN_Y, 25.0, "y span is 25")
	check_float(LaunchRulesScript.PLAYFIELD_MIN_X, -10.0, "border x is -10")
	check_float(LaunchRulesScript.PLAYFIELD_MAX_X, 10.0, "border y is 10")
	check_float(LaunchRulesScript.PLAYFIELD_MIN_Y, -15.0, "border z is -15")
	check_float(LaunchRulesScript.SOURCE_COLLIDER_UNITS, 15.0, "source collision/border radius is 15 units")
	check_float(
		LaunchRulesScript.collider_radius_world(),
		0.15,
		"collider converts to 0.15 world units at the documented 0.01 slice scale"
	)
	check(
		LaunchRulesScript.collider_radius_world() * 2.0 < LaunchRulesScript.PLAYFIELD_WIDTH_UNITS,
		"collider diameter must fit the playfield"
	)
	var field := LaunchRulesScript.playfield_rect()
	check_float(field.size.x, 20.0, "playfield rect width")
	check_float(field.size.y, 25.0, "playfield rect height")
	check(LaunchRulesScript.is_inside_playfield(Vector2(0.0, 9.6)), "spawn edge is inside the playfield")
	check(not LaunchRulesScript.is_inside_playfield(Vector2(0.0, 10.4)), "above the top border is outside")
	check(
		LaunchRulesScript.is_outside_world_border(Vector2(16.0, 0.0)),
		"world x past the 15-unit border despawns"
	)
	check(
		not LaunchRulesScript.is_outside_world_border(Vector2(0.0, -15.0)),
		"an enemy spawned at the documented y=15 height is not despawned instantly"
	)
	check(
		LaunchRulesScript.is_outside_world_border(Vector2(0.0, 15.5)),
		"an enemy below the -15 source border despawns"
	)
	check(
		LaunchRulesScript.source_to_world(Vector2(0.0, 9.6)).is_equal_approx(Vector2(0.0, -9.6)),
		"source y up maps to world y down"
	)
	check(LaunchRulesScript.is_spawn_offscreen(12.0), "y=12 is a documented off-screen spawn")
	check(LaunchRulesScript.is_spawn_offscreen(15.0), "y=15 is a documented off-screen spawn")
	check(not LaunchRulesScript.is_spawn_offscreen(9.6), "y=9.6 is the on-screen spawn edge")


func _test_spawn_rate_and_edge() -> void:
	check_float(LaunchRulesScript.SPAWN_Y, 9.6, "spawn y edge is 9.6")
	check_float(LaunchRulesScript.SPAWN_MEDIAN_RATE, 1.0, "median spawner rate is 1.0 s")


func _test_camera_and_bounds() -> void:
	# 9:16 portrait: 1280 / 720 * 5.4 = 9.6 exactly.
	check_float(
		LaunchRulesScript.camera_half_height(Vector2(720.0, 1280.0)),
		9.6,
		"9:16 portrait hits the 9.6 floor"
	)
	# 16:9 window: 600 / 720 * 5.4 = 4.5, so the 9.6 floor still wins.
	check_float(
		LaunchRulesScript.camera_half_height(Vector2(720.0, 600.0)),
		9.6,
		"16:9 window keeps the 9.6 floor"
	)
	check_float(
		LaunchRulesScript.camera_half_height(Vector2(360.0, 800.0)),
		12.0,
		"tall viewport grows the ortho half height"
	)
	var bounds := LaunchRulesScript.player_bounds(9.6, 5.4)
	check(bounds.position.y >= -9.6, "player stays inside the visible top")
	check(bounds.end.y <= 9.6, "player stays inside the visible bottom")
	check(bounds.position.x >= -10.0, "player stays inside the playfield on the left")
	check(bounds.end.x <= 10.0, "player stays inside the playfield on the right")
	check_float(bounds.position.x, -4.8, "player left bound follows the visible half width")
	check_float(bounds.end.x, 4.8, "player right bound follows the visible half width")
	var spawn_limit := LaunchRulesScript.enemy_spawn_x_limit(5.4)
	check_float(spawn_limit, 4.65, "enemy spawn x limit follows the visible half width")


func _test_hp_formula() -> void:
	check_float(
		LaunchRulesScript.max_hp(LaunchRulesScript.START_HP, 0, 0),
		2500.0,
		"base hull is 2500"
	)
	check_float(
		LaunchRulesScript.max_hp(LaunchRulesScript.START_HP, 10, 0),
		7000.0,
		"tech 10 gives 2500 * (1 + 0.18 * 10) = 7000"
	)
	check_float(
		LaunchRulesScript.max_hp(LaunchRulesScript.START_HP, 0, 1),
		5000.0,
		"ability7 adds one full StartHp"
	)
	check_float(
		LaunchRulesScript.max_hp(LaunchRulesScript.START_HP, 30, 0),
		16000.0,
		"tech 30 gives 16000"
	)
	check_float(
		LaunchRulesScript.max_hp(LaunchRulesScript.START_HP, -5, -3),
		2500.0,
		"negative tech/ability inputs clamp to zero"
	)


func _test_level_delta() -> void:
	check_eq(LaunchRulesScript.LEVEL_DELTA.size(), 4, "levelDelta has four mode entries")
	check_float(LaunchRulesScript.level_delta(0), 1.0, "mode 0 reward multiplier")
	check_float(LaunchRulesScript.level_delta(1), 2.0, "mode 1 reward multiplier")
	check_float(LaunchRulesScript.level_delta(2), 3.6, "mode 2 reward multiplier")
	check_float(LaunchRulesScript.level_delta(3), 3.6, "mode 3 reward multiplier")
	for mode in range(LaunchRulesScript.MAX_MODE_INDEX):
		check_float(LaunchRulesScript.hp_multiplier(mode), 1.0, "mode %d never scales HP" % mode)
		check_float(
			LaunchRulesScript.enemy_hp(1000.0, mode),
			1000.0,
			"enemy HP is untouched by mode %d" % mode
		)
		check_float(
			LaunchRulesScript.reward_multiplier(mode),
			LaunchRulesScript.level_delta(mode),
			"reward multiplier equals levelDelta for mode %d" % mode
		)
	check_eq(LaunchRulesScript.kill_score(2), 36, "mode 2 kill score is scaled by 3.6")
	check_eq(LaunchRulesScript.kill_score(0), 10, "mode 0 kill score is unscaled")


# --- save contract -------------------------------------------------------------

func _test_save_contract_defaults() -> void:
	var store: SaveStore = SaveStoreScript.new()
	check(store.contract_ready(), "save contract loads")
	check_eq(store.get_int("TUTORIAL", []), -1, "TUTORIAL default -1")
	check_eq(store.get_int("StageTarget", []), -1, "StageTarget default -1")
	check_eq(store.get_int("ZoneUnlocked", []), -1, "ZoneUnlocked default -1")
	check_eq(store.get_int("StarCount", []), -1, "StarCount sentinel -1")
	check_eq(store.get_int("StarStageMaster%s_%s", [1, 0]), 0, "stage star default 0")
	check_eq(store.get_int("PlayerUsed%s", [0]), 10001, "PlayerUsed slot 0 default 10001")
	check_eq(store.get_int("PlayerUsed%s", [1]), 10002, "PlayerUsed slot 1 default 10002")
	check_eq(store.get_int("PLAYER_RANK%s", [10003]), 2, "PLAYER_RANK default 2")
	check_eq(store.get_int("PLAYER_LEVEL%s", [10003]), 0, "PLAYER_LEVEL default 0")
	check_eq(store.get_int("PLAYER_DEFAULT_SKIN%s", [10003]), -1, "skin default -1 is valid")
	check_eq(store.get_int("TALENT_SELECTED", []), -1, "TALENT_SELECTED default -1")
	check_eq(store.get_int("PLAYER_DEVICE_%s_%s", [10003, 3]), -1, "device slot default -1")
	check_eq(store.get_int("TRIAL_ID_%s", [10003]), 0, "trial id default 0")
	check_eq(store.get_int("MUTE_AUDIO", []), 0, "audio mute default 0")
	check_float(store.get_float("VolumeSound", []), 0.73, "sound volume default 0.73")
	check_float(store.get_float("VolumeMusic", []), 0.3, "music volume default 0.3")
	check(not store.audio_muted(), "audio is not muted by default")


func _test_save_contract_repairs() -> void:
	var store: SaveStore = SaveStoreScript.new()
	store.set_int("PlayerUsed%s", [0], 0)
	store.set_int("PlayerUsed%s", [1], -4)
	check_eq(store.player_used(0), 10001, "PlayerUsed <= 0 rewrites slot 0 to 10001")
	check_eq(store.player_used(1), 10002, "PlayerUsed <= 0 rewrites slot 1 to 10002")

	store.set_int("PLAYER_RANK%s", [10005], 0)
	check_eq(store.player_rank(10005), 2, "rank base <= 1 is floored to 2")
	store.set_int("TRIAL_ID_%s", [10005], 1)
	store.set_int("TRIAL_RANK_%s", [10005], 7)
	check_eq(store.player_rank(10005), 7, "trial rank replaces the saved rank when TRIAL_ID == 1")
	store.set_int("TRIAL_LEVEL_%s", [10005], 4)
	check_eq(store.player_level(10005), 4, "trial level replaces the saved level when TRIAL_ID == 1")

	check(store.player_unlocked(10002), "ships below 10003 read as unlocked")
	check(not store.player_unlocked(10005), "later ships need PlayerUnlocked == 1")
	store.set_int("PlayerUnlocked%s", [10005], 1)
	check(store.player_unlocked(10005), "PlayerUnlocked == 1 unlocks the ship")

	store.set_int("DroneUsed%s", [0], -2)
	check_eq(store.drone_used(0), 0, "negative DroneUsed is rewritten as 0")

	store.set_int("StageTarget", [], 3)
	check_eq(store.get_int("StageTarget", []), 3, "pure getter does not change StageTarget")
	check_eq(store.get_int("TUTORIAL", []), -1, "pure getter does not rewrite TUTORIAL")


func _test_save_roundtrip() -> void:
	var store: SaveStore = SaveStoreScript.new()
	store.set_int("StarStageMaster%s_%s", [1, 0], 2)
	store.set_int("StarCount", [], 2)
	store.set_int("PLAYER_RANK%s", [10003], 4)
	store.set_float("VolumeSound", [], 0.5)
	store.set_int("MUTE_AUDIO", [], 1)
	var path := TEST_SAVE_PATH
	if FileAccess.file_exists(path):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
	check_eq(store.save_to(path), OK, "save writes a file")

	var reloaded: SaveStore = SaveStoreScript.new()
	check_eq(reloaded.load_from(path), OK, "save reads back")
	check_eq(reloaded.get_int("StarStageMaster%s_%s", [1, 0]), 2, "stage stars roundtrip")
	check_eq(reloaded.get_int("PLAYER_RANK%s", [10003]), 4, "rank roundtrip")
	check_float(reloaded.get_float("VolumeSound", []), 0.5, "sound volume roundtrip")
	check(reloaded.audio_muted(), "mute flag roundtrip")
	check(not FileAccess.file_exists(path + ".tmp"), "no temp save file is left behind")

	# Unknown keys from a newer build must survive a load/save cycle.
	var document := {
		"schema": "windwings.launch_slice.save/1",
		"version": 1,
		"values": {"FutureKey": 42, "StarCount": 5},
	}
	var handle := FileAccess.open(path, FileAccess.WRITE)
	handle.store_string(JSON.stringify(document))
	handle.close()
	var forwarding: SaveStore = SaveStoreScript.new()
	check_eq(forwarding.load_from(path), OK, "save with unknown key loads")
	check_eq(forwarding.get_int("StarCount", []), 5, "known key from disk wins over the default")
	check(forwarding.snapshot().has("FutureKey"), "unknown keys are preserved")
	check_eq(forwarding.save_to(path), OK, "save with unknown key writes back")
	var reread: SaveStore = SaveStoreScript.new()
	reread.load_from(path)
	check_eq(int(reread.snapshot().get("FutureKey", 0)), 42, "unknown key survives a rewrite")
	DirAccess.remove_absolute(ProjectSettings.globalize_path(path))


func _test_save_rejects_foreign_document() -> void:
	var path := "user://launch_slice_foreign_save.json"
	var handle := FileAccess.open(path, FileAccess.WRITE)
	handle.store_string(JSON.stringify({"schema": "something.else/1", "values": {}}))
	handle.close()
	var store: SaveStore = SaveStoreScript.new()
	check_eq(store.load_from(path), ERR_FILE_UNRECOGNIZED, "foreign save schema is rejected")
	DirAccess.remove_absolute(ProjectSettings.globalize_path(path))


# --- stars ---------------------------------------------------------------------

func _test_star_tiers() -> void:
	check_eq(StarRulesScript.tiers_for(0), [0.20, 0.45, 0.80], "mode 0 tiers")
	check_eq(StarRulesScript.tiers_for(1), [0.35, 0.60, 0.98], "mode 1 tiers")
	check_eq(StarRulesScript.tiers_for(2), [0.50, 0.80, 1.00], "mode 2 tiers")
	check_eq(StarRulesScript.stars_for(0, 100, 0), 0, "no kills means no stars")
	check_eq(StarRulesScript.stars_for(19, 100, 0), 0, "19% is below the 20% tier")
	check_eq(StarRulesScript.stars_for(20, 100, 0), 1, "20% earns one star")
	check_eq(StarRulesScript.stars_for(45, 100, 0), 2, "45% earns two stars")
	check_eq(StarRulesScript.stars_for(80, 100, 0), 3, "80% earns three stars")
	check_eq(StarRulesScript.stars_for(100, 100, 0), 3, "100% never exceeds three stars")
	check_eq(StarRulesScript.stars_for(50, 100, 1), 1, "mode 1 has a 35% first tier")
	check_eq(StarRulesScript.stars_for(50, 100, 2), 1, "mode 2 needs 50% for one star")
	check_eq(StarRulesScript.stars_for(10, 0, 0), 0, "an empty stage awards nothing")
	check_eq(StarRulesScript.MAX_STARS, 3, "maximum stars is three")
	check_float(StarRulesScript.next_tier_ratio(1, 0), 0.45, "next tier after one star")


func _test_star_recording() -> void:
	var store: SaveStore = SaveStoreScript.new()
	check_eq(store.record_stars(1, 0, 2), 2, "first clear records two stars")
	check_eq(store.get_int("StarCount", []), 2, "total star count follows the stage record")
	check_eq(store.record_stars(1, 0, 1), 2, "a worse run never removes stars")
	check_eq(store.get_int("StarCount", []), 2, "total stays at the best result")
	check_eq(store.record_stars(2, 0, 3), 3, "second stage records three stars")
	check_eq(store.get_int("StarCount", []), 5, "total star count sums the stages")
	check_eq(store.record_stars(1, 0, 9), 3, "stars are capped at three")
	check_eq(store.star_for_stage(1, 0), 3, "stage star accessor")


# --- data-driven checks --------------------------------------------------------

func _test_wave_catalog() -> void:
	var catalog: WaveCatalog = WaveCatalogScript.new()
	var loaded := catalog.load_default()
	check(loaded, "wave catalog loads: %s" % str(catalog.errors))
	check_eq(catalog.errors.size(), 0, "catalog reports no data errors: %s" % str(catalog.errors))
	check_eq(catalog.stage_count(), 5, "slice has five stage waves")
	check_eq(catalog.total_entries, 343, "slice spawns 343 stage entries")
	check_eq(catalog.stage_name(0), "Wave_0016", "first wave is a real campaign wave")
	check_eq(catalog.stage_name(4), "Wave_0020", "last stage wave is a real campaign wave")
	check_float(catalog.median_rate, 1.0, "median positive spawner rate comes from the real rows")
	var total_check := 0
	for index in range(catalog.stage_count()):
		total_check += catalog.stage_entries(index)
		check(catalog.stage_entries(index) > 0, "wave %d has enemies" % index)
	check_eq(total_check, catalog.total_entries, "per-wave entries add up")
	var y_values := catalog.spawn_y_values()
	check(y_values.has(9.6), "spawn rows use the documented 9.6 top edge")
	var offscreen_rows := 0
	for y_value: Variant in y_values:
		check(
			LaunchRulesScript.is_spawn_y_documented(float(y_value)),
			"spawn y %s is a documented spawn height (-0.25..15)" % str(y_value)
		)
		if LaunchRulesScript.is_spawn_offscreen(float(y_value)):
			offscreen_rows += 1
	check(
		offscreen_rows > 0,
		"the slice keeps the real off-screen spawn heights (12.0 / 15.0) instead of clamping them"
	)
	var prefabs := catalog.used_prefabs()
	check(prefabs.size() >= 10, "slice uses a varied set of real prefabs")
	for prefab: String in prefabs:
		if prefab == catalog.boss_prefab:
			continue
		check(catalog.has_hp(prefab), "%s has a STATIC_CONFIRMED HP row" % prefab)
		check(catalog.hp_for(prefab) > 0.0, "%s HP is positive" % prefab)
		check(catalog.has_movement(prefab), "%s has a movement row" % prefab)
		var profile := catalog.gun_profile_for(prefab)
		check(not profile.is_empty(), "%s has a gun profile" % prefab)
		check(
			profile.get("evidence") in ["STATIC_CONFIRMED", "INFERRED_FALLBACK"],
			"%s gun profile carries an evidence label" % prefab
		)
	check(catalog.boss_rows.size() == 1, "boss wave keeps exactly one boss row")
	check_eq(catalog.boss_prefab, "Boss-37001", "boss prefab is a real boss")
	check_eq(catalog.boss_entries(), 2, "Wave_7001 boss row keeps its decoded copies=2")
	check_eq(catalog.stage_rows(0).size() > 0, true, "first wave has spawner rows")


func _test_boss_pattern() -> void:
	var boss: BossPattern = BossPatternScript.new()
	check(boss.load_default(), "boss data loads: %s" % boss.error)
	check_eq(boss.prefab, "Boss-37001", "boss prefab")
	check_float(boss.hp_max, 225000.0, "boss HP matches datas/boss_hp.json")
	check_eq(boss.clip, "Attack2", "boss attack clip")
	check_float(boss.loop_seconds, 7.0, "clip loop is the last event time")
	check_eq(boss.shot_times.size(), 14, "Attack2 carries 14 Shoot events")
	check_float(float(boss.shot_times[0]), 0.467, "first shot time")
	check_float(float(boss.shot_times[13]), 6.6, "last shot time")
	check_eq(boss.shots_in_interval(0.0, 7.0), 14, "one clip loop fires 14 shots")
	check_eq(boss.shots_in_interval(7.0, 14.0), 14, "the next loop fires 14 shots again")
	check_eq(boss.shots_in_interval(0.0, 0.5), 1, "0.467 fires inside the first half second")
	check_eq(boss.shots_in_interval(0.5, 0.9), 0, "no event between 0.5 and 0.9")
	check_eq(boss.shots_in_interval(0.5, 1.0), 1, "0.933 fires before 1.0")
	check_eq(boss.shots_in_interval(3.0, 3.0), 0, "empty interval fires nothing")
	check(boss.source.has("hp_sha256"), "boss data pins the HP source hash")


func _test_audio_rules() -> void:
	var mixer: AudioMixer = AudioMixerScript.new()
	check(mixer.load_default(), "audio defaults load")
	check(not mixer.default_muted(), "source mute default is 0")
	check_float(mixer.default_sound_volume(), 0.73, "source sound volume default")
	check_float(mixer.default_music_volume(), 0.3, "source music volume default")
	check_float(AudioMixerScript.effective_volume(0.73, false), 0.73, "unmuted volume passes through")
	check_float(AudioMixerScript.effective_volume(0.73, true), 0.0, "mute forces 0 regardless of stored volume")
	check_float(AudioMixerScript.effective_volume(1.7, false), 1.0, "volume clamps at 1")
	check_float(AudioMixerScript.effective_volume(-2.0, false), 0.0, "volume clamps at 0")


func _test_ship_roster() -> void:
	var roster: ShipRoster = ShipRosterScript.new()
	check(roster.load_default(), "player stats load: %s" % roster.error)
	check_eq(roster.damage_values.size(), 24, "damage array keeps 24 decoded entries")
	check_eq(roster.cost_values.size(), 24, "cost array keeps 24 decoded entries")
	check_eq(ShipRosterScript.combat_index_for_ship(10001), 2, "ship 10001 maps to index 2")
	check_eq(ShipRosterScript.combat_index_for_ship(10003), 0, "ship 10003 maps to index 0")
	check_eq(ShipRosterScript.combat_index_for_ship(10004), 3, "ship 10004 maps to index 3")
	check_float(roster.damage_for_ship(10003), 4500.0, "ship 10003 damage is index 0 = 4500")
	check_float(roster.damage_for_ship(10001), 2680.0, "ship 10001 damage is index 2 = 2680")
	check_float(roster.damage_for_ship(10004), 8000.0, "ship 10004 damage is index 3 = 8000")
	check_eq(roster.cost_for_ship(10003), 0, "ship 10003 cost row is index 0 = 0")
	check_eq(roster.roster_ships().size(), 3, "slice roster offers three ships")
	check(roster.damage_values.size() > 1 and float(roster.damage_values[23]) == 3300.0, "last damage entry is 3300")

	var store: SaveStore = SaveStoreScript.new()
	check_float(roster.max_hp(store, 0), 2500.0, "fresh save yields 2500 hull")
	store.set_int("PlayerStatPoints%s", [0], 10)
	check_float(roster.max_hp(store, 0), 7000.0, "tech points feed the HP formula")
	check_float(roster.max_hp(store, 1), 9500.0, "ability7 adds 2500 on top of tech 10")


func _test_provenance_pins() -> void:
	var path := "res://data/slice_provenance.json"
	check(FileAccess.file_exists(path), "slice provenance file exists")
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	check(parsed is Dictionary, "provenance is a JSON object")
	if parsed is Dictionary:
		var document: Dictionary = parsed
		var sources: Dictionary = document.get("sources", {})
		check_eq(sources.size(), 7, "seven source files are pinned")
		for source_name: String in sources.keys():
			check_eq(str(sources[source_name]).length(), 64, "%s pins a sha256" % source_name)
		check_eq(document.get("problems", [1]).size(), 0, "generator reported no problems")
		check(FileAccess.file_exists("res://tools/build_launch_slice_data.py"), "generator is shipped")
	var save_contract: Variant = JSON.parse_string(
		FileAccess.get_file_as_string("res://data/save_contract.json")
	)
	check(save_contract is Dictionary, "save contract is a JSON object")
	if save_contract is Dictionary:
		check_eq((save_contract as Dictionary).get("keys", []).size(), 26, "save contract lists 26 keys")


# --- art slot contract ---------------------------------------------------------

func _test_art_slot_contract() -> void:
	check(FileAccess.file_exists(ART_CONTRACT_PATH), "art slot contract exists")
	var library: ArtLibrary = ArtLibraryScript.new()
	check(library.contract_ready(), "art slot contract loads: %s" % library.error)
	check_eq(library.validate().size(), 0, "art slot contract validates: %s" % str(library.validate()))
	check_eq(library.slot_count(), 23, "contract lists 23 slots")
	check_eq(
		library.contract.get("art_root", ""), "res://art", "contract names the integrated art root"
	)

	# Required slots the slice cannot ship without.
	for slot_id: String in ["PLAYER-10001", "Boss-37001", "BG-FIELD", "BULLET-PLAYER", "BULLET-ENEMY", "FX-HIT", "FX-EXPLOSION", "UI-MENU-FRAME"]:
		check(library.slot(slot_id).size() > 0, "contract has slot %s" % slot_id)
	check(library.slot("PLAYER-10001").get("required", false), "PLAYER-10001 is a required slot")

	# Every enemy prefab the slice spawns must have a slot, derived from the same data.
	var catalog: WaveCatalog = WaveCatalogScript.new()
	check(catalog.load_default(), "wave catalog loads for the art cross-check")
	var stage_prefabs: Array = []
	for prefab: String in catalog.used_prefabs():
		if prefab == catalog.boss_prefab:
			continue
		stage_prefabs.append(prefab)
	check_eq(stage_prefabs.size(), 13, "the slice spawns 13 distinct enemy prefabs")
	for prefab: String in stage_prefabs:
		check(library.slot(prefab).size() > 0, "contract has an enemy slot for %s" % prefab)
	check_eq(
		library.contract.get("counts", {}).get("enemies", -1),
		stage_prefabs.size(),
		"contract enemy count matches the spawned prefabs"
	)
	check_eq(
		library.contract.get("counts", {}).get("total", -1),
		library.slot_count(),
		"contract total matches the slot list"
	)

	# Canvas sizes and orientation from the brief.
	var canvas_expectations := {
		"PLAYER-10001": [256, 256],
		"PLAYER-10003": [256, 256],
		"PLAYER-10004": [256, 256],
		"CD-31002": [128, 128],
		"CB-30001": [128, 128],
		"Boss-37001": [512, 512],
		"BG-FIELD": [1024, 1024],
		"BULLET-PLAYER": [64, 128],
		"BULLET-ENEMY": [64, 64],
		"FX-HIT": [256, 256],
		"FX-EXPLOSION": [256, 256],
		"UI-MENU-FRAME": [1080, 1920],
	}
	for slot_id: String in canvas_expectations.keys():
		var canvas: Dictionary = library.slot(slot_id).get("canvas", {})
		var expected: Array = canvas_expectations[slot_id]
		check_eq(int(canvas.get("width", 0)), int(expected[0]), "%s canvas width" % slot_id)
		check_eq(int(canvas.get("height", 0)), int(expected[1]), "%s canvas height" % slot_id)

	check_eq(library.slot("PLAYER-10001").get("facing", ""), "up", "ships face up")
	check_eq(library.slot("CD-31002").get("facing", ""), "down", "enemies face down")
	check_eq(library.slot("Boss-37001").get("facing", ""), "down", "the boss faces down")

	# File names, folders and pivots.
	var files := {}
	for slot_id: String in library.slot_ids():
		var entry: Dictionary = library.slot(slot_id)
		var file := str(entry.get("file", ""))
		check(file.ends_with(".png"), "%s uses a .png file" % slot_id)
		check(not files.has(file), "%s has a unique file path" % slot_id)
		files[file] = slot_id
		var pivot: Array = entry.get("pivot", [])
		check_eq(pivot.size(), 2, "%s declares a pivot" % slot_id)
		if pivot.size() == 2:
			check_float(float(pivot[0]), 0.5, "%s pivot x is centred" % slot_id)
			check_float(float(pivot[1]), 0.5, "%s pivot y is centred" % slot_id)
		var display: Dictionary = entry.get("display", {})
		check(not display.is_empty(), "%s declares how it is displayed" % slot_id)
	check_eq(
		library.slot("CD-31002").get("file", ""),
		"enemies/CD-31002.png",
		"enemy files live under enemies/"
	)
	check_eq(
		library.slot("Boss-37001").get("file", ""), "bosses/Boss-37001.png", "boss file path"
	)
	check_eq(
		library.slot("PLAYER-10001").get("file", ""),
		"ships/PLAYER-10001.png",
		"ship file path"
	)
	# Display sizes stay inside the playfield and match the vector silhouettes.
	check_float(library.display_size("PLAYER-10001").y, 1.4, "ship display height")
	check_float(library.display_size("CD-31002").y, 0.78, "enemy display height")
	check_float(library.display_size("Boss-37001").y, 2.4, "boss display height")
	check(
		library.display_size("Boss-37001").y < LaunchRulesScript.PLAYFIELD_HEIGHT_UNITS,
		"the boss sprite fits the 25-unit playfield"
	)


func _test_art_library_fallback() -> void:
	# The repository ships no art yet: every slot must fall back without crashing.
	var library: ArtLibrary = ArtLibraryScript.new(ART_CONTRACT_PATH, ["res://art"])
	check(library.contract_ready(), "fallback library loads the contract")
	check_eq(library.present_ids().size(), 0, "no art is integrated yet")
	check_eq(library.missing_ids().size(), library.slot_count(), "every slot is a fallback")
	check_eq(library.summary_line(), "ART_SUMMARY total=23 present=0 fallback=23", "summary line counts fallbacks")
	for slot_id: String in library.slot_ids():
		check(not library.has_art(slot_id), "%s falls back to vector art" % slot_id)
		check_eq(library.status(slot_id), "fallback", "%s reports fallback status" % slot_id)
	check(library.texture_for("PLAYER-10001") == null, "a missing texture returns null")
	# draw_slot must return false instead of drawing (and must not crash headless).
	var probe := Node2D.new()
	var drew := library.draw_slot(probe, "PLAYER-10001", Vector2.ZERO)
	check(not drew, "draw_slot reports false when the slot has no art")
	check(
		not library.draw_cover(probe, "BG-FIELD", Rect2(0, 0, 10, 10)),
		"draw_cover reports false when the background has no art"
	)
	probe.free()
	var unknown := library.draw_slot(null, "NOT-A-SLOT", Vector2.ZERO)
	check(not unknown, "an unknown slot never draws and never crashes")


func _test_art_library_drop_in() -> void:
	# Dropping a contract-named PNG into an art root must switch that slot to art
	# and leave the other slots on the fallback.
	_clear_dir(ART_TEST_ROOT)
	var png_path := ART_TEST_ROOT + "/ships/PLAYER-10001.png"
	var directory_error := DirAccess.make_dir_recursive_absolute(
		ProjectSettings.globalize_path(ART_TEST_ROOT + "/ships")
	)
	check_eq(directory_error, OK, "art test folder is writable")
	var image := Image.create(8, 8, false, Image.FORMAT_RGBA8)
	image.fill(Color(0.2, 0.8, 1.0, 1.0))
	check_eq(image.save_png(ProjectSettings.globalize_path(png_path)), OK, "a test PNG is written")
	check(FileAccess.file_exists(png_path), "the test PNG exists")

	var library: ArtLibrary = ArtLibraryScript.new(ART_CONTRACT_PATH, [ART_TEST_ROOT])
	check(library.has_art("PLAYER-10001"), "a dropped PNG is picked up for its slot")
	check(library.texture_for("PLAYER-10001") is Texture2D, "the dropped PNG becomes a texture")
	check_eq(library.status("PLAYER-10001"), "present", "the slot reports present")
	check(library.texture_for("PLAYER-10001").get_width() == 8, "the texture has the PNG size")
	check(not library.has_art("PLAYER-10003"), "other slots stay on the fallback")
	check(not library.has_art("CD-31002"), "enemies stay on the fallback")
	check_eq(library.summary_line(), "ART_SUMMARY total=23 present=1 fallback=22", "summary counts one slot of art")
	var report := library.report_lines()
	check(report.size() == library.slot_count() + 2, "the report lists every slot plus two summary lines")
	check(
		report.has("ART_SLOT PLAYER-10001 present %s/%s" % [ART_TEST_ROOT, "ships/PLAYER-10001.png"]),
		"the report names the present slot and its path"
	)
	_clear_dir(ART_TEST_ROOT)


func _clear_dir(root: String) -> void:
	var absolute := ProjectSettings.globalize_path(root)
	var directory := DirAccess.open(absolute)
	if directory == null:
		return
	for sub_path: String in directory.get_files():
		DirAccess.remove_absolute(absolute + "/" + sub_path)
	for sub_dir: String in directory.get_directories():
		_clear_dir(root + "/" + sub_dir)
	DirAccess.remove_absolute(absolute)
