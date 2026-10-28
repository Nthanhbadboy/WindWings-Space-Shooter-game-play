class_name WaveDirector
extends Node

signal wave_started(wave_name: String, total_enemy_entries: int)
signal enemy_spawned(enemy: WaveEnemy)
signal spawn_progress_changed(spawned: int, total: int)
signal spawns_finished(wave_name: String)

const ENEMY_SCENE := preload("res://scenes/enemy.tscn")

var _world: Node2D
var _target: Node2D
var _wave: Dictionary = {}
var _hp_by_id: Dictionary = {}
var _movement_by_id: Dictionary = {}
var _guns_by_id: Dictionary = {}
var _active_spawners := 0
var _spawned := 0
var _total_to_spawn := 0
var _started := false


func configure(
	world_root: Node2D,
	wave_document: Dictionary,
	hp_document: Dictionary,
	movement_document: Dictionary,
	guns_document: Dictionary,
	target: Node2D
) -> void:
	_world = world_root
	_target = target
	_wave = wave_document.get("wave", {})
	_hp_by_id = hp_document.get("hp_by_id", {})
	_movement_by_id = movement_document.get("enemy_by_id", {})
	_guns_by_id = guns_document.get("enemy_by_id", {})


func start_wave() -> void:
	if _started:
		return
	_started = true
	var rows: Array = _wave.get("spawners", [])
	var active_rows: Array[Dictionary] = []
	for row_value: Variant in rows:
		if not row_value is Dictionary:
			continue
		var row: Dictionary = row_value
		var enemies: Array = row.get("enemies", [])
		var copies := maxi(int(row.get("copies", 0)), 0)
		if enemies.is_empty() or copies == 0:
			continue
		active_rows.append(row)
		_total_to_spawn += enemies.size() * copies
	_active_spawners = active_rows.size()
	var wave_name := str(_wave.get("wave", "Wave_0000"))
	wave_started.emit(wave_name, _total_to_spawn)
	if _active_spawners == 0:
		spawns_finished.emit(wave_name)
		return
	for row_index in range(active_rows.size()):
		_spawn_spawner.call_deferred(active_rows[row_index], row_index)


func _spawn_spawner(row: Dictionary, row_index: int) -> void:
	var enemy_names: Array = row.get("enemies", [])
	var copies := maxi(int(row.get("copies", 0)), 0)
	var interval := maxf(float(row.get("rate", 0.0)), 0.0)
	var entries_in_row := enemy_names.size() * copies
	var emitted_in_row := 0
	for copy_index in range(copies):
		for enemy_index in range(enemy_names.size()):
			var prefab_name := str(enemy_names[enemy_index])
			_spawn_enemy(row, row_index, copy_index, enemy_index, prefab_name)
			_spawned += 1
			emitted_in_row += 1
			spawn_progress_changed.emit(_spawned, _total_to_spawn)
			if emitted_in_row < entries_in_row:
				if interval > 0.0:
					await get_tree().create_timer(interval).timeout
				else:
					await get_tree().process_frame
	_active_spawners -= 1
	if _active_spawners == 0:
		spawns_finished.emit(str(_wave.get("wave", "Wave_0000")))


func _spawn_enemy(
	row: Dictionary, row_index: int, copy_index: int, enemy_index: int, prefab_name: String
) -> void:
	var id_text := prefab_name.get_slice("-", 1)
	var enemy_id := int(id_text)
	var id_key := str(enemy_id)
	var health_known := _hp_by_id.has(id_key)
	var movement: Dictionary = _movement_by_id.get(id_key, {})
	var gun_data: Dictionary = _guns_by_id.get(id_key, {})
	var gun_profile: Dictionary = {}
	if bool(gun_data.get("same_ballistics_and_schedule", false)):
		var selected_profile: Variant = gun_data.get("runtime_profile")
		if selected_profile is Dictionary:
			gun_profile = selected_profile
	var enemy := ENEMY_SCENE.instantiate() as WaveEnemy
	enemy.configure(
		{
			"enemy_id": enemy_id,
			"prefab_name": prefab_name,
			"health_known": health_known,
			"health": float(_hp_by_id.get(id_key, 0.0)),
			"movement_speed": float(movement.get("speed", 0.0)),
			"is_turret": bool(movement.get("is_turret", false)),
			"formation_kind": _formation_kind(row),
			"formation_phase": float(row_index) * 0.61 + float(copy_index) * 0.83,
			"spawner_speed_hint": float(row.get("speed", 0.0)),
			"spawn_position": _formation_position(row, copy_index, enemy_index),
			"gun_profile": gun_profile,
			"target": _target
		}
	)
	_world.add_child(enemy)
	enemy_spawned.emit(enemy)


func _formation_kind(row: Dictionary) -> String:
	var spawner_name := str(row.get("spawner", ""))
	# The serialized boss/special labels also identify boundary markers, not enemy roles.
	if spawner_name == "EndPoint" or spawner_name == "StartPoint":
		return "point"
	return str(row.get("spawn_type", "point"))


func _formation_position(row: Dictionary, copy_index: int, enemy_index: int) -> Vector2:
	var spawner_name := str(row.get("spawner", ""))
	var kind := _formation_kind(row)
	var enemy_names: Array = row.get("enemies", [])
	var enemy_count := maxi(enemy_names.size(), 1)
	var copies := maxi(int(row.get("copies", 1)), 1)
	var x := 0.0
	var vertical_slot := 0
	match kind:
		"path":
			var progress := float(enemy_index) / maxf(float(enemy_count - 1), 1.0)
			x = sin(progress * PI * 2.0 + float(copy_index) * PI) * 3.15
			vertical_slot = floori(float(enemy_index) / 8.0)
		"point_range":
			var column := (enemy_index + copy_index * 3) % 9
			x = -4.0 + float(column) * 1.0
			vertical_slot = floori(float(enemy_index) / 9.0)
		"point":
			var column := enemy_index % 5 - 2
			var copy_offset := (float(copy_index) - float(copies - 1) * 0.5) * 0.34
			x = float(column) * 0.68 + copy_offset
			vertical_slot = floori(float(enemy_index) / 5.0)
		_:
			x = (float(copy_index) - float(copies - 1) * 0.5) * 0.65
			vertical_slot = enemy_index
	if spawner_name == "EndPoint":
		x = 0.0
	return Vector2(
		clampf(x, -4.65, 4.65), -float(row.get("y_spawn", 9.6)) + float(vertical_slot) * 0.42
	)
