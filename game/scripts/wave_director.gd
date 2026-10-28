class_name WaveDirector
extends Node

## Spawns the slice waves from the pinned data.
##
## Spawner rows, enemy names, copies, rate and y_spawn are copied verbatim from
## datas/waves.json. The x placement and the vertical stacking of multi-enemy
## rows are INFERRED new design because the source rows carry no coordinates
## (ENEMY_BEHAVIOUR §2: PathCreator has no point data).

signal wave_started(wave_name: String, entries: int)
signal enemy_spawned(enemy: Node2D)
signal enemy_defeated(enemy_id: int)
signal enemy_escaped(enemy_id: int)
signal spawn_progress_changed(spawned: int, total: int)
signal wave_spawns_finished(wave_name: String)
signal wave_cleared(wave_name: String)
signal boss_spawned(boss: Node2D)
signal boss_defeated

const ENEMY_SCENE := preload("res://scenes/enemy.tscn")
const BOSS_SCENE := preload("res://scenes/boss.tscn")

var _world: Node2D
var _target: Node2D
var _catalog: WaveCatalog
var _boss_data: BossPattern
var _mode_index := 0

var _current_wave := ""
var _spawned := 0
var _total := 0
var _live := 0
var _active_rows := 0
var _spawns_done := false
var _cleared := false
var _boss_alive := 0
var _boss_max_total := 0.0


func configure(
	world_root: Node2D, target: Node2D, catalog: WaveCatalog, boss_data: BossPattern, mode_index: int
) -> void:
	_world = world_root
	_target = target
	_catalog = catalog
	_boss_data = boss_data
	_mode_index = mode_index


func start_stage_wave(index: int) -> void:
	if _catalog == null or _world == null:
		return
	_current_wave = _catalog.stage_name(index)
	_spawned = 0
	_total = _catalog.stage_entries(index)
	_live = 0
	_spawns_done = false
	_cleared = false
	var rows: Array = _catalog.stage_rows(index)
	_active_rows = rows.size()
	wave_started.emit(_current_wave, _total)
	spawn_progress_changed.emit(0, _total)
	if _active_rows == 0:
		_spawns_done = true
		wave_spawns_finished.emit(_current_wave)
		_check_cleared()
		return
	for row_index in range(rows.size()):
		_spawn_row.call_deferred(rows[row_index], row_index)


func _spawn_row(row: Dictionary, row_index: int) -> void:
	var enemies: Array = row.get("enemies", [])
	var copies := maxi(int(row.get("copies", 0)), 0)
	var interval := maxf(float(row.get("rate", 0.0)), 0.0)
	var entries := enemies.size() * copies
	var emitted := 0
	for copy_index in range(copies):
		for enemy_index in range(enemies.size()):
			_spawn_enemy(row, row_index, copy_index, enemy_index, str(enemies[enemy_index]))
			_spawned += 1
			emitted += 1
			spawn_progress_changed.emit(_spawned, _total)
			if emitted < entries and is_inside_tree():
				if interval > 0.0:
					await get_tree().create_timer(interval).timeout
				else:
					await get_tree().process_frame
	_active_rows -= 1
	if _active_rows <= 0:
		_spawns_done = true
		wave_spawns_finished.emit(_current_wave)
		_check_cleared()


func _spawn_enemy(
	row: Dictionary, row_index: int, copy_index: int, enemy_index: int, prefab_name: String
) -> void:
	var enemy := ENEMY_SCENE.instantiate() as WaveEnemy
	var movement: Dictionary = _catalog.movement_for(prefab_name)
	enemy.configure(
		{
			"enemy_id": int(_catalog.id_from_prefab(prefab_name)),
			"prefab_name": prefab_name,
			"health": LaunchRules.enemy_hp(_catalog.hp_for(prefab_name), _mode_index),
			"health_known": _catalog.has_hp(prefab_name),
			"movement_speed": float(movement.get("speed", 0.0)),
			"is_turret": bool(movement.get("is_turret", false)),
			"formation_kind": str(row.get("spawn_type", "point")),
			"formation_phase": float(row_index) * 0.61 + float(copy_index) * 0.83,
			"spawn_position": _spawn_position(row, row_index, copy_index, enemy_index),
			"gun_profile": _catalog.gun_profile_for(prefab_name),
			"contact_damage": LaunchRules.CONTACT_DAMAGE,
			"target": _target,
		}
	)
	_world.add_child(enemy)
	_live += 1
	enemy.defeated.connect(_on_enemy_defeated)
	enemy.escaped.connect(_on_enemy_escaped)
	enemy_spawned.emit(enemy)


func _spawn_position(
	row: Dictionary, row_index: int, copy_index: int, enemy_index: int
) -> Vector2:
	var enemies: Array = row.get("enemies", [])
	var enemy_count := maxi(enemies.size(), 1)
	var copies := maxi(int(row.get("copies", 1)), 1)
	var half_width := LaunchRules.camera_half_width(get_viewport().get_visible_rect().size)
	var limit := LaunchRules.enemy_spawn_x_limit(half_width)
	var x := 0.0
	var vertical_slot := 0
	match str(row.get("spawn_type", "point")):
		"path":
			var progress := float(enemy_index) / maxf(float(enemy_count - 1), 1.0)
			x = sin(progress * PI * 2.0 + float(copy_index) * PI) * 3.15
			vertical_slot = int(floor(float(enemy_index) / 8.0))
		"point_range":
			var column := (enemy_index + copy_index * 3) % 9
			x = -4.0 + float(column) * 1.0
			vertical_slot = int(floor(float(enemy_index) / 9.0))
		"point":
			var point_column := enemy_index % 5 - 2
			var copy_offset := (float(copy_index) - float(copies - 1) * 0.5) * 0.34
			x = float(point_column) * 0.68 + copy_offset
			vertical_slot = int(floor(float(enemy_index) / 5.0))
		_:
			x = (float(copy_index) - float(copies - 1) * 0.5) * 0.65
			vertical_slot = enemy_index
	x = clampf(x, -limit, limit)
	var source_y := float(row.get("y_spawn", LaunchRules.SPAWN_Y)) - float(vertical_slot) * 0.42
	return LaunchRules.source_to_world(Vector2(x, source_y))


func _on_enemy_defeated(enemy_id: int) -> void:
	_live = maxi(_live - 1, 0)
	enemy_defeated.emit(enemy_id)
	_check_cleared()


func _on_enemy_escaped(enemy_id: int) -> void:
	_live = maxi(_live - 1, 0)
	enemy_escaped.emit(enemy_id)
	_check_cleared()


func _check_cleared() -> void:
	if _cleared or not _spawns_done or _live > 0:
		return
	_cleared = true
	wave_cleared.emit(_current_wave)


func start_boss() -> void:
	if _catalog == null or _boss_data == null or not _boss_data.ready:
		return
	var copies := 0
	for row_value: Variant in _catalog.boss_rows:
		var row: Dictionary = row_value
		copies += int(row.get("copies", 0))
	copies = maxi(copies, 1)
	_boss_alive = copies
	_boss_max_total = _boss_data.hp_max * float(copies)
	var gun_profile: Dictionary = _catalog.gun_profile_for(_catalog.boss_prefab)
	for slot in range(copies):
		var boss := BOSS_SCENE.instantiate() as SliceBoss
		var station := LaunchRules.boss_station_world(slot, copies)
		boss.configure(
			{
				"pattern": _boss_data,
				"hp": _boss_data.hp_max,
				"target": _target,
				"station": station,
				"spawn_position": station + Vector2(0.0, -4.2),
				"slot": slot,
				"gun_profile": gun_profile,
				"contact_damage": LaunchRules.CONTACT_DAMAGE,
			}
		)
		_world.add_child(boss)
		boss.defeated.connect(_on_boss_down)
		boss_spawned.emit(boss)


func _on_boss_down(_boss: Node) -> void:
	_boss_alive = maxi(_boss_alive - 1, 0)
	if _boss_alive == 0:
		boss_defeated.emit()


func boss_hp_status() -> Vector2:
	var current := 0.0
	var maximum := 0.0
	if _world == null:
		return Vector2.ZERO
	for child in _world.get_children():
		if child is SliceBoss and is_instance_valid(child):
			var boss := child as SliceBoss
			if not boss.is_defeated():
				current += boss.current_hp
				maximum += boss.max_hp
	return Vector2(current, maximum)


func live_enemies() -> int:
	return _live
