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
const AnimationVariantScript = preload("res://scripts/animation_variant.gd")

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
	_test_art_layer_slots()
	_test_motion_tuning()
	_test_animation_variants()

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
	check_eq(library.slot_count(), 32, "contract lists 32 slots including the animation layers")
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
	# Per roster ship: a canopy glow layer and an optional nozzle glow layer.
	check_eq(library.contract.get("counts", {}).get("ship_layers", -1), 6, "six ship layer slots")
	check_eq(library.contract.get("counts", {}).get("boss_parts", -1), 3, "three boss layer slots")
	check_eq(library.contract.get("counts", {}).get("total", -1), 32, "contract total is 32")
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
			# The contract stays centred for every slot; the art package manifest
			# owns the turret mounts (pinned in the layer test), so the engine can
			# never hardcode a mount that contradicts the delivered art.
			check_float(float(pivot[0]), 0.5, "%s pivot x is centred" % slot_id)
			check_float(float(pivot[1]), 0.5, "%s pivot y is centred" % slot_id)
		if entry.get("layer_role", "") != "":
			# Every sub-layer must be a full-canvas layer registered on its parent.
			var parent: Dictionary = library.slot(str(entry.get("parent", "")))
			check_eq(entry.get("canvas", {}), parent.get("canvas", {}), "%s uses its parent's canvas" % slot_id)
			check_eq(entry.get("display", {}), parent.get("display", {}), "%s uses its parent's display size" % slot_id)
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
	check_eq(library.summary_line(), "ART_SUMMARY total=32 present=0 fallback=32", "summary line counts fallbacks")
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
	check_eq(library.summary_line(), "ART_SUMMARY total=32 present=1 fallback=31", "summary counts one slot of art")
	var report := library.report_lines()
	check(report.size() == library.slot_count() + 2, "the report lists every slot plus the summary line")
	check(
		report.has("ART_SLOT PLAYER-10001 present %s/%s" % [ART_TEST_ROOT, "ships/PLAYER-10001.png"]),
		"the report names the present slot and its path"
	)
	_clear_dir(ART_TEST_ROOT)


func _canvas_of(library: ArtLibrary, slot_id: String) -> Array:
	var canvas: Dictionary = library.slot(slot_id).get("canvas", {})
	return [int(canvas.get("width", 0)), int(canvas.get("height", 0))]


func _test_art_layer_slots() -> void:
	var library: ArtLibrary = ArtLibraryScript.new()
	check(library.contract_ready(), "layer test library loads")

	# Ship layers: canopy glow (all packages) and nozzle glow (A only), both
	# full-canvas layers drawn exactly over the body.
	for ship_id: int in [10001, 10003, 10004]:
		var body_slot := "PLAYER-%d" % ship_id
		var glow_slot := "PLAYER-%d-GLOW" % ship_id
		var body: Dictionary = library.slot(body_slot)
		var glow: Dictionary = library.slot(glow_slot)
		check(not glow.is_empty(), "%s has a glow layer slot" % body_slot)
		check_eq(glow.get("parent", ""), body_slot, "%s glow belongs to the ship body" % body_slot)
		check_eq(glow.get("layer_role", ""), "glow", "%s glow is tagged as a glow layer" % body_slot)
		check_eq(
			glow.get("file", ""),
			"layers/ships/%s-canopy-glow.png" % body_slot,
			"%s glow file matches the delivered package layout" % body_slot
		)
		check_eq(_canvas_of(library, glow_slot), _canvas_of(library, body_slot), "%s glow canvas" % body_slot)
		check_eq(glow.get("display", {}), body.get("display", {}), "%s glow display size" % body_slot)
		check(not glow.get("required", true), "%s glow is optional" % body_slot)

		var nozzle_slot := "PLAYER-%d-NOZZLE" % ship_id
		var nozzle: Dictionary = library.slot(nozzle_slot)
		check(not nozzle.is_empty(), "%s has a nozzle layer slot" % body_slot)
		check_eq(
			nozzle.get("file", ""),
			"layers/ships/%s-nozzle-glow.png" % body_slot,
			"%s nozzle file matches the package layout" % body_slot
		)
		check(not nozzle.get("required", true), "%s nozzle layer is optional" % body_slot)

	# Boss layers: the single image is the body, plus two full-canvas turret pods
	# and a full-canvas core glow.
	var boss_slot := library.slot("Boss-37001")
	check(not boss_slot.is_empty(), "single-image boss slot still exists")
	for part: String in ["TURRET-L", "TURRET-R", "CORE"]:
		var slot_id := "Boss-37001-%s" % part
		var entry: Dictionary = library.slot(slot_id)
		check(not entry.is_empty(), "boss layer %s exists" % part)
		check_eq(entry.get("parent", ""), "Boss-37001", "%s belongs to the boss" % slot_id)
		check(not entry.get("required", true), "%s is optional" % slot_id)
		check_eq(_canvas_of(library, slot_id), [512, 512], "%s is a full 512 canvas layer" % slot_id)
		check_eq(entry.get("display", {}), boss_slot.get("display", {}), "%s display matches the body" % slot_id)
	check_eq(library.slot("Boss-37001-TURRET-L").get("layer_role", ""), "gun_left", "left turret role")
	check_eq(library.slot("Boss-37001-TURRET-R").get("layer_role", ""), "gun_right", "right turret role")
	check_eq(library.slot("Boss-37001-CORE").get("layer_role", ""), "core", "core role")
	check_eq(
		library.slot("Boss-37001-TURRET-L").get("file", ""),
		"layers/bosses/Boss-37001-turret-left.png",
		"left turret file matches the package layout"
	)
	check_eq(
		library.slot("Boss-37001-CORE").get("file", ""),
		"layers/bosses/Boss-37001-core-glow.png",
		"core file matches the package layout"
	)

	# Package manifests own the rotating mounts; the contract stays centred.
	for package: String in ["A", "B"]:
		var packaged: ArtLibrary = ArtLibraryScript.new(
			ART_CONTRACT_PATH, ["res://art/%s" % package, "res://art"]
		)
		check(packaged.has_manifest(), "package %s ships a manifest" % package)
		var left: Vector2 = packaged.pivot_of("Boss-37001-TURRET-L")
		var right: Vector2 = packaged.pivot_of("Boss-37001-TURRET-R")
		check(left.x > 0.0 and left.x < 0.5, "%s left turret mount is on the left half" % package)
		check(right.x > 0.5 and right.x < 1.0, "%s right turret mount is on the right half" % package)
		check(left.y > 0.0 and left.y < 1.0, "%s left turret mount is inside the canvas" % package)
		check(left.y > 0.15 and left.y < 0.6, "%s left turret mount sits on the pod" % package)
		check_float(left.y, right.y, "%s turret mounts share one height" % package)
		# Full-canvas layers drawn centred: the draw pivot must stay at the centre
		# for the body and the core, so nothing shifts when a package is swapped.
		check(packaged.pivot_of("Boss-37001").is_equal_approx(Vector2(0.5, 0.5)), "%s body is centred" % package)
		check(packaged.pivot_of("PLAYER-10001").is_equal_approx(Vector2(0.5, 0.5)), "%s ship is centred" % package)

	# The two delivered packages must not silently claim the same mounts.
	var package_a: ArtLibrary = ArtLibraryScript.new(ART_CONTRACT_PATH, ["res://art/A"])
	var package_b: ArtLibrary = ArtLibraryScript.new(ART_CONTRACT_PATH, ["res://art/B"])
	check(
		not package_a.pivot_of("Boss-37001-TURRET-L").is_equal_approx(
			package_b.pivot_of("Boss-37001-TURRET-L")
		),
		"each package keeps its own left turret mount"
	)

	# Everything is optional, so a zero-art build must still use the fallbacks.
	var empty_library: ArtLibrary = ArtLibraryScript.new(
		ART_CONTRACT_PATH, ["user://art_missing_%d" % Time.get_ticks_usec()]
	)
	check(not empty_library.any_present(["Boss-37001-TURRET-L", "Boss-37001-CORE"]), "turret art is absent")
	check(not empty_library.has_art("PLAYER-10001-GLOW"), "the glow layer is absent before art arrives")
	check_float(empty_library.pivot_of("Boss-37001-TURRET-L").x, 0.5, "no manifest means a centred pivot")


func _test_motion_tuning() -> void:
	# STATIC_CONFIRMED feel numbers from docs/spec/VISUAL_DESIGN.md §4 (J9/AF1).
	check_float(MotionTuning.FLASH_SECONDS, 0.05, "hit flash lasts 0.05 s")
	check_float(MotionTuning.FLASH_ALPHA, 0.5, "hit flash alpha is 0.5")
	check_float(MotionTuning.SHAKE_AMPLITUDE, 0.10, "shake amplitude is 0.10")
	check_eq(MotionTuning.SHAKE_FRAMES, 20, "shake lasts 20 frames")
	check_float(MotionTuning.shake_seconds(), 20.0 / 60.0, "20 frames at 60 fps is 0.333 s")

	check_float(MotionTuning.flash_alpha(0.0), 0.5, "flash is visible on the hit frame")
	check_float(MotionTuning.flash_alpha(0.049), 0.5, "flash is visible just before 0.05 s")
	check_float(MotionTuning.flash_alpha(0.05), 0.0, "flash is gone at 0.05 s")
	check_float(MotionTuning.flash_alpha(0.2), 0.0, "flash stays gone")

	# The flash must lighten the shape that was hit, never paint a white disc
	# over it: the vector fallback uses the same 0.5 alpha for its tint.
	check_float(MotionTuning.FLASH_ALPHA, 0.5, "the vector hit flash tints shapes at 0.5")

	check(MotionTuning.shake_offset(0.0).length() == 0.0, "shake starts at zero offset")
	var peak := 0.0
	for step in range(20):
		var offset := MotionTuning.shake_offset(float(step) * 0.01)
		peak = maxf(peak, offset.length())
	check(peak <= MotionTuning.SHAKE_AMPLITUDE * 1.25, "shake never exceeds the tuned amplitude")
	check(
		MotionTuning.shake_offset(MotionTuning.shake_seconds() + 0.01) == Vector2.ZERO,
		"shake ends after 20 frames"
	)
	var early := MotionTuning.shake_offset(0.01)
	var late := MotionTuning.shake_offset(MotionTuning.shake_seconds() - 0.02)
	check(early.length() > late.length(), "shake decays over time")

	# Telegraph ramps for the last 0.42 s before a scheduled shot.
	check_float(MotionTuning.telegraph_strength(0.5), 0.0, "no telegraph far from the shot")
	check_float(MotionTuning.telegraph_strength(MotionTuning.BOSS_TELEGRAPH_SECONDS), 0.0, "telegraph starts at 0.42 s")
	check_float(MotionTuning.telegraph_strength(0.0), 1.0, "telegraph is full at the shot")
	check(
		MotionTuning.core_glow(0.0) > MotionTuning.core_glow(1.0),
		"the core is brightest right before a shot"
	)

	# Ship animation mapping.
	check_float(MotionTuning.bank_angle(0.0), 0.0, "no banking when not moving sideways")
	check(MotionTuning.bank_angle(50.0) < 0.0, "moving right banks the ship clockwise")
	check(MotionTuning.bank_angle(-50.0) > 0.0, "moving left banks the other way")
	check(
		absf(rad_to_deg(MotionTuning.bank_angle(50.0))) <= MotionTuning.BANK_MAX_DEGREES + 0.001,
		"banking is capped by the tuned maximum"
	)
	check(
		MotionTuning.engine_length(0.0) < MotionTuning.engine_length(9.0),
		"the engine flame lengthens with speed"
	)
	check(
		MotionTuning.engine_length(0.0, true) >= MotionTuning.engine_length(0.0, false),
		"the engine is longer while boosting"
	)
	check(
		MotionTuning.engine_length(99.0) <= MotionTuning.ENGINE_FAST_LENGTH,
		"the engine flame is clamped"
	)

	# Particle sizes: the flame texture is 16 px, drawn at pixel size in world
	# units, so a scale near 1 would paint a 16 unit sheet over the playfield.
	check(
		MotionTuning.ENGINE_PARTICLE_SCALE_MAX * 16.0 < 1.5,
		"the engine plume stays under 1.5 world units"
	)
	check(
		MotionTuning.ENGINE_PARTICLE_SCALE_MIN > 0.0
			and MotionTuning.ENGINE_PARTICLE_SCALE_MIN < MotionTuning.ENGINE_PARTICLE_SCALE_MAX,
		"the engine plume scale range is ordered"
	)
	check(
		MotionTuning.BOSS_AURA_SCALE_MAX * 12.0 < 2.0,
		"the boss aura stays under 2 world units"
	)
	check(
		MotionTuning.HULL_SPARK_SCALE_MAX * 16.0 < 1.0,
		"the whole-image hull sparkle stays under a unit"
	)

	# Boss death chain: layers fade in order and the total is bounded.
	check_float(MotionTuning.death_layer_alpha(0, 0.0), 1.0, "the first layer is opaque at t=0")
	check(
		MotionTuning.death_layer_alpha(0, 0.2) < MotionTuning.death_layer_alpha(2, 0.2),
		"later layers fade after the earlier ones"
	)
	check_float(
		MotionTuning.death_layer_alpha(MotionTuning.BOSS_DEATH_LAYERS - 1, MotionTuning.death_total_seconds()),
		0.0,
		"every layer is gone at the end of the chain"
	)
	check(MotionTuning.death_total_seconds() < 1.5, "the death chain stays under 1.5 s")


func _test_animation_variants() -> void:
	# The shipped default file must describe a real, bootable build.
	var shipped: AnimationVariant = AnimationVariantScript.load_default(
		"res://data/animation_variant.json"
	)
	# CI rewrites this file per matrix build, so the rule is that the build runs
	# exactly the mode its own variant letter declares - C must be whole-image.
	check(AnimationVariantScript.VARIANTS.has(shipped.variant), "the built variant is A, B or C")
	check(shipped.error.is_empty(), "the built variant file parses cleanly")
	var built_layered := shipped.variant != "C"
	check_eq(shipped.mode, "layered" if built_layered else "whole", "the mode matches the variant letter")
	check_eq(shipped.uses_layers(), built_layered, "A/B animate layers, C animates a whole image")
	check_eq(
		shipped.guns_track_target(), built_layered, "A/B turn the boss guns, C keeps them fixed"
	)

	# A and B are layered; C animates one whole image.
	for variant: String in ["A", "B"]:
		var layered: AnimationVariant = AnimationVariantScript.from_dictionary(
			{"variant": variant, "art_source": "package", "art_package_commit": "215aa58f"}
		)
		check_eq(layered.mode, "layered", "variant %s uses the layered animation" % variant)
		check(layered.uses_layers(), "variant %s animates layer slots" % variant)
		check(layered.guns_track_target(), "variant %s turns the boss guns" % variant)
		check(not layered.flame_sticks_to_hull(), "variant %s lets the flame trail" % variant)
		check(not layered.is_placeholder(), "variant %s is a real package build" % variant)
		check_eq(layered.label(), "ANIM-%s" % variant, "variant %s menu label" % variant)
		check_eq(
			layered.art_roots()[0], "res://art/%s" % variant, "variant %s loads its own folder" % variant
		)

	var whole: AnimationVariant = AnimationVariantScript.from_dictionary({"variant": "C"})
	check_eq(whole.mode, "whole", "variant C animates whole images")
	check(not whole.uses_layers(), "variant C ignores the layer slots")
	check(not whole.guns_track_target(), "variant C keeps the boss guns fixed")
	check(whole.flame_sticks_to_hull(), "variant C keeps the flame on the hull")
	check(whole.is_placeholder(), "variant C without a package is a placeholder build")
	check_eq(whole.art_roots()[0], "res://art/C", "variant C loads its own folder")

	# Every variant searches its own package first and the shared folder after.
	for variant: String in ["A", "B", "C"]:
		var roots: Array = AnimationVariantScript.from_dictionary({"variant": variant}).art_roots()
		check_eq(roots.size(), 4, "variant %s declares four art roots" % variant)
		check_eq(roots[0], "res://art/%s" % variant, "variant %s res root" % variant)
		check_eq(roots[1], "user://art/%s" % variant, "variant %s user root" % variant)
		check_eq(roots[2], "res://art", "variant %s falls back to the shared res folder" % variant)
		check_eq(roots[3], "user://art", "variant %s falls back to the shared user folder" % variant)

	# Bad input never blocks a build: it degrades to A with a note.
	var fallback: AnimationVariant = AnimationVariantScript.from_dictionary({"variant": "Z"})
	check_eq(fallback.variant, "A", "an unknown variant falls back to A")
	check(not fallback.error.is_empty(), "an unknown variant reports why it fell back")
	var wrong_mode: AnimationVariant = AnimationVariantScript.from_dictionary(
		{"variant": "C", "mode": "layered"}
	)
	check_eq(wrong_mode.mode, "whole", "the variant decides the mode, not the file")
	check(not wrong_mode.error.is_empty(), "a contradicting mode is reported")
	var unknown_source: AnimationVariant = AnimationVariantScript.from_dictionary(
		{"variant": "B", "art_source": "guessed"}
	)
	check_eq(unknown_source.art_source, "placeholder", "an unknown art source is a placeholder")
	var described := whole.describe()
	check(described.begins_with("ANIM_VARIANT "), "the variant prints a machine-readable line")
	check(described.contains("mode=whole"), "the variant line states the animation mode")

	# The art lookup really is variant-aware and still falls back to vector art.
	var library: ArtLibrary = ArtLibraryScript.new(
		ART_CONTRACT_PATH, AnimationVariantScript.from_dictionary({"variant": "B"}).art_roots()
	)
	check(library.contract_ready(), "a variant library loads the contract")
	check_eq(
		library.candidate_paths("PLAYER-10001")[0],
		"res://art/B/ships/PLAYER-10001.png",
		"slot files resolve inside the variant folder first"
	)
	check_eq(
		library.candidate_paths("PLAYER-10001")[2],
		"res://art/ships/PLAYER-10001.png",
		"slot files also resolve in the shared folder"
	)
	check(library.validate().is_empty(), "the contract still validates with variant roots")


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
