extends Node2D

## Launch-slice run: five real campaign waves, then the Wave_7001 boss, then
## victory or game over. Menu, ship select, settings, pause and results live in
## their own scenes; this scene only owns the run.

const WaveCatalogScript = preload("res://scripts/wave_catalog.gd")
const BossPatternScript = preload("res://scripts/boss_pattern.gd")
const PauseMenuScript = preload("res://scripts/pause_menu.gd")
const PROJECTILE_SCENE := preload("res://scenes/projectile.tscn")

var catalog: WaveCatalog
var boss_data: BossPattern
var stage_index := 0
var kills := 0
var score := 0
var boss_started := false

var _finished := false
var _pause_menu: SlicePauseMenu

# INFERRED NEW_DESIGN — a bullet-hell cap. The decoded cadences can put hundreds
# of 400-damage bullets on screen; the slice keeps at most this many live enemy
# projectiles and drops the rest instead of shipping an unplayable frame rate.
const MAX_LIVE_ENEMY_SHOTS := 40
var _live_enemy_shots := 0

# Headless CI harness. Enabled only by `godot ... -- --slice-autoplay`: it keeps
# the hull full, kills live enemies each frame and removes the spawner waits, so
# the whole wave -> boss -> results -> save path runs inside one CI step. It is
# not a gameplay mode and the exported game never enables it by itself.
var _autoplay := false

# Motion-capture driver (tools/motion_capture.gd). Empty in normal play. The
# capture scene sets this before the node enters the tree.
var capture_stage := ""
var _capture_time := 0.0
var _shake_elapsed := 999.0
var _shake_strength := 0.0

@onready var camera: Camera2D = $Camera2D
@onready var world: Node2D = $World
@onready var player: Player = $World/Player
@onready var director: WaveDirector = $WaveDirector
@onready var hud: GameHUD = $CanvasLayer/HUD


func _ready() -> void:
	_autoplay = OS.get_cmdline_user_args().has("--slice-autoplay")
	get_tree().paused = false
	Session.apply_audio(false)
	catalog = WaveCatalogScript.new()
	if not catalog.load_default() or not catalog.errors.is_empty():
		hud.show_fatal("DATA ERROR: %s" % ", ".join(PackedStringArray(catalog.errors)))
		return
	boss_data = BossPatternScript.new()
	if not boss_data.load_default():
		hud.show_fatal("BOSS DATA ERROR: %s" % boss_data.error)
		return

	_configure_camera()
	get_viewport().size_changed.connect(_configure_camera)

	player.configure_ship(Session.selected_ship)
	player.configure_weapon(Session.ship_damage(), 0.24)
	player.configure_health(Session.player_max_hp())
	player.died.connect(_on_player_died)
	player.impact.connect(_on_player_impact)
	player.shot_requested.connect(_on_player_shot)
	player.health_changed.connect(_on_player_health_changed)

	director.configure(world, player, catalog, boss_data, Session.mode_index)
	director.fast_forward = _autoplay
	director.wave_started.connect(_on_wave_started)
	director.spawn_progress_changed.connect(_on_spawn_progress)
	director.wave_cleared.connect(_on_wave_cleared)
	director.enemy_spawned.connect(_on_enemy_spawned)
	director.enemy_defeated.connect(_on_enemy_defeated)
	director.enemy_escaped.connect(_on_enemy_escaped)
	director.boss_spawned.connect(_on_boss_spawned)
	director.boss_defeated.connect(_on_boss_defeated)

	hud.pause_requested.connect(_toggle_pause)
	_pause_menu = PauseMenuScript.new()
	$CanvasLayer.add_child(_pause_menu)
	_pause_menu.resume_requested.connect(_resume)
	_pause_menu.restart_requested.connect(_restart)
	_pause_menu.quit_requested.connect(_quit_to_menu)

	Session.start_music()
	hud.set_score(score)
	if Session.art != null:
		print("ART_USAGE %s" % Session.art.summary_line())
	print(
		"SLICE_RUN_START ship=%d hull=%d waves=%d entries=%d boss_hp=%.0f"
		% [
			Session.selected_ship,
			int(round(player.maximum_health)),
			catalog.stage_count(),
			catalog.total_entries,
			boss_data.hp_max,
		]
	)
	if capture_stage == "boss" or capture_stage == "turret":
		_skip_to_boss_for_capture()
		if capture_stage == "turret":
			for child in world.get_children():
				if child.is_in_group("bosses"):
					child.set("capture_turret_sweep", true)
	else:
		director.start_stage_wave(0)


func _process(delta: float) -> void:
	if not capture_stage.is_empty():
		_capture_time += delta
		_drive_capture(delta)
	_update_shake(delta)
	if _autoplay and not _finished:
		player.current_health = player.maximum_health
		for child in world.get_children():
			if child.is_in_group("enemies") and child.has_method("take_damage"):
				child.take_damage(1000000000.0)
	if boss_started and not _finished:
		var status := director.boss_hp_status()
		if status.y > 0.0:
			hud.set_boss("%s  ·  BOSS" % boss_data.prefab, status.x, status.y)


func capture_time() -> float:
	return _capture_time


func _skip_to_boss_for_capture() -> void:
	if not catalog.boss_rows.is_empty():
		boss_started = true
		hud.show_banner("WARNING · BOSS INCOMING", MotionTuning.BOSS_WARNING_SECONDS)
		hud.set_warning(1.0)
		director.start_boss()
		hud.set_wave("BOSS  ·  %s" % boss_data.prefab)


func _drive_capture(delta: float) -> void:
	# Capture only: glide the ship left and right so the banking and engine
	# animation are visible, and keep the hull full so the run never ends.
	if not is_instance_valid(player):
		return
	player.current_health = player.maximum_health
	if capture_stage == "flight":
		var bounds := LaunchRules.player_bounds(
			LaunchRules.camera_half_height(get_viewport_rect().size),
			LaunchRules.camera_half_width(get_viewport_rect().size)
		)
		var span := bounds.size.x * 0.5
		player.global_position.x = sin(_capture_time * 1.35) * span
		player.global_position.y = lerpf(bounds.end.y, bounds.position.y + 1.2, 0.5 + 0.35 * sin(_capture_time * 0.9))
	elif capture_stage == "boss":
		# Capture only: line the ship up under the nearest boss so the volley hits
		# and the frame sequence shows the flash, the shake and the core telegraph.
		var aim := sin(_capture_time * 0.8) * 1.8
		var nearest := 999.0
		for child in world.get_children():
			if not child.is_in_group("bosses"):
				continue
			var distance := absf(child.global_position.x - player.global_position.x)
			if distance < nearest:
				nearest = distance
				aim = child.global_position.x + 0.25 * sin(_capture_time * 3.0)
		player.global_position.x = aim


func _update_shake(delta: float) -> void:
	if _shake_elapsed >= MotionTuning.shake_seconds():
		if camera.offset != Vector2.ZERO:
			camera.offset = Vector2.ZERO
		return
	_shake_elapsed += delta
	camera.offset = MotionTuning.shake_offset(_shake_elapsed, _shake_strength)


func _start_shake(strength: float) -> void:
	_shake_strength = MotionTuning.SHAKE_AMPLITUDE * clampf(strength, 0.2, 1.6)
	_shake_elapsed = 0.0


func _on_player_impact(strength: float) -> void:
	_start_shake(1.0 + strength)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		_toggle_pause()
		get_viewport().set_input_as_handled()
	elif event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_P:
		_toggle_pause()
		get_viewport().set_input_as_handled()


func _configure_camera() -> void:
	var viewport_size := get_viewport_rect().size
	if viewport_size.x <= 0.0 or viewport_size.y <= 0.0:
		return
	var half_height := LaunchRules.camera_half_height(viewport_size)
	var pixels_per_unit := viewport_size.y / (half_height * 2.0)
	camera.zoom = Vector2(pixels_per_unit, pixels_per_unit)
	camera.position = Vector2(0.0, 0.0)
	var half_width := LaunchRules.camera_half_width(viewport_size)
	player.set_movement_bounds(LaunchRules.player_bounds(half_height, half_width))


func _on_wave_started(wave_name: String, entries: int) -> void:
	hud.set_wave("%s  ·  %d ENTRIES" % [wave_name, entries])


func _on_spawn_progress(spawned: int, total: int) -> void:
	hud.set_wave(
		"%s  ·  %d / %d SPAWNED" % [catalog.stage_name(stage_index), spawned, total]
	)


func _on_enemy_spawned(enemy: Node2D) -> void:
	if enemy.has_signal("projectile_requested"):
		enemy.projectile_requested.connect(_on_enemy_projectile)


func _on_enemy_defeated(_enemy_id: int) -> void:
	kills += 1
	score += LaunchRules.kill_score(Session.mode_index)
	hud.set_score(score)
	Session.play_sfx("destroy")


func _on_enemy_escaped(_enemy_id: int) -> void:
	pass


func _on_wave_cleared(wave_name: String) -> void:
	if _finished:
		return
	score += LaunchRules.wave_score(Session.mode_index)
	hud.set_score(score)
	print("SLICE_WAVE_CLEAR %s kills=%d score=%d" % [wave_name, kills, score])
	hud.show_banner("%s CLEAR" % wave_name, 1.6)
	stage_index += 1
	if stage_index < catalog.stage_count():
		await get_tree().create_timer(1.8).timeout
		while get_tree().paused:
			await get_tree().process_frame
		if _finished:
			return
		director.start_stage_wave(stage_index)
	else:
		hud.show_banner("WARNING · BOSS INCOMING", 2.0)
		await get_tree().create_timer(2.2).timeout
		while get_tree().paused:
			await get_tree().process_frame
		if _finished:
			return
		boss_started = true
		director.start_boss()


func _on_boss_spawned(boss: Node2D) -> void:
	if boss.has_signal("projectile_requested"):
		boss.projectile_requested.connect(_on_enemy_projectile)
	if boss.has_signal("shake_requested"):
		boss.shake_requested.connect(_start_shake)
	if boss.has_signal("entrance_progress"):
		boss.entrance_progress.connect(_on_boss_entrance_progress)
	hud.set_boss("%s  ·  BOSS" % boss_data.prefab, boss_data.hp_max, boss_data.hp_max)


func _on_boss_entrance_progress(progress: float) -> void:
	hud.set_warning(1.0 - clampf(progress, 0.0, 1.0))


func _on_boss_defeated() -> void:
	if _finished:
		return
	hud.clear_boss()
	hud.set_warning(0.0)
	hud.show_banner("STAGE CLEAR", 2.0)
	score += LaunchRules.boss_score(Session.mode_index)
	hud.set_score(score)
	_finish(true)


func _on_player_shot(origin: Vector2, damage: float) -> void:
	var shot := PROJECTILE_SCENE.instantiate() as Projectile
	shot.faction = Projectile.Faction.PLAYER
	shot.position = origin
	shot.direction = Vector2.UP
	shot.speed = 18.0
	shot.damage = damage
	shot.lifetime_seconds = 3.0
	world.add_child(shot)
	Session.play_sfx("shot")


func _on_enemy_projectile(
	origin: Vector2, direction: Vector2, damage: float, speed: float, lifetime_seconds: float
) -> void:
	if _live_enemy_shots >= MAX_LIVE_ENEMY_SHOTS:
		return
	var shot := PROJECTILE_SCENE.instantiate() as Projectile
	shot.faction = Projectile.Faction.ENEMY
	shot.position = origin
	shot.direction = direction
	shot.speed = maxf(speed, 1.0)
	shot.damage = damage
	shot.lifetime_seconds = maxf(lifetime_seconds, 0.5)
	shot.target = player
	_live_enemy_shots += 1
	shot.tree_exited.connect(_on_enemy_shot_freed)
	world.add_child(shot)


func _on_enemy_shot_freed() -> void:
	_live_enemy_shots = maxi(_live_enemy_shots - 1, 0)


func _on_player_health_changed(current: float, maximum: float) -> void:
	hud.set_hp(current, maximum)


func _on_player_died() -> void:
	if _finished:
		return
	hud.show_banner("HULL LOST", 1.2)
	_finish(false)


func _finish(victory: bool) -> void:
	if _finished:
		return
	_finished = true
	get_tree().paused = false
	Session.apply_audio(false)
	Session.clear_boss_music()
	var entries := catalog.total_entries + catalog.boss_entries()
	var summary := Session.record_run(
		victory, kills, entries, score, stage_index + (1 if boss_started else 0)
	)
	print(
		"SLICE_RUN_END victory=%s kills=%d entries=%d score=%d stars=%d best=%d total=%d autoplay=%s"
		% [
			str(victory),
			kills,
			entries,
			score,
			int(summary.get("stars", 0)),
			int(summary.get("best_after", 0)),
			int(summary.get("star_total", 0)),
			str(_autoplay),
		]
	)
	await get_tree().create_timer(0.7).timeout
	get_tree().change_scene_to_file("res://scenes/results.tscn")


func _toggle_pause() -> void:
	if _finished:
		return
	var should_pause := not get_tree().paused
	get_tree().paused = should_pause
	hud.set_paused(should_pause)
	Session.apply_audio(should_pause)
	if should_pause:
		_pause_menu.open()
	else:
		_pause_menu.close()


func _resume() -> void:
	if not get_tree().paused:
		return
	get_tree().paused = false
	hud.set_paused(false)
	Session.apply_audio(false)
	_pause_menu.close()


func _restart() -> void:
	get_tree().paused = false
	Session.apply_audio(false)
	get_tree().reload_current_scene()


func _quit_to_menu() -> void:
	get_tree().paused = false
	Session.apply_audio(false)
	get_tree().change_scene_to_file("res://scenes/menu.tscn")
