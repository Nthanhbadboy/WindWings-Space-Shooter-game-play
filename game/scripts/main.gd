extends Node2D

const PLAYER_INDEX := 0
const FALLBACK_PLAYER_HP := 2500.0
const PROJECTILE_SCENE := preload("res://scenes/projectile.tscn")
const PICKUP_SCENE := preload("res://scenes/pickup.tscn")

var _rng := RandomNumberGenerator.new()
var _player_shots := 0
var _near_misses := 0
var _player_bullet_speed := 18.0
var _wave_spawned := 0
var _wave_spawn_total := 0
var _live_enemies := 0
var _kills := 0
var _items_collected := 0
var _coins := 0
var _spawns_finished := false
var _wave_clear := false
var _game_over := false
var _drop_elapsed := 0.0
var _drop_period := 18.0
var _drop_item_cycle: Array = [1]
var _drop_cycle_index := 0
var _items_by_index: Dictionary = {}
var _player_costs: Array = []
var _purchased_player_indices: Dictionary = {}
var _economy_paused := false

@onready var camera: Camera2D = $Camera2D
@onready var world: Node2D = $World
@onready var player: Player = $World/Player
@onready var wave_director: WaveDirector = $WaveDirector
@onready var hud: GameHUD = $CanvasLayer/HUD
@onready var economy_panel: EconomyPanel = $CanvasLayer/EconomyPanel
@onready var monetization: MonetizationService = $MonetizationService


func _ready() -> void:
	_rng.seed = 0x20330D0E
	_configure_camera()
	get_viewport().size_changed.connect(_configure_camera)
	player.shot_requested.connect(_on_player_shot_requested)
	player.health_changed.connect(_on_health_changed)
	player.died.connect(_on_player_died)
	hud.pause_requested.connect(_on_pause_requested)
	hud.retry_requested.connect(_on_retry_requested)
	hud.economy_requested.connect(_on_economy_requested)
	economy_panel.close_requested.connect(_on_economy_closed)
	economy_panel.purchase_requested.connect(_on_player_purchase_requested)
	var player_stats := _read_json("res://data/player_start_stats.json")
	var damage_values := _get_field_values(player_stats, "StartMainCannonDamages")
	_player_costs = _get_field_values(player_stats, "PlayerCosts")
	if damage_values.size() != 24 or _player_costs.size() != 24:
		push_error(
			"Expected decoded 24-entry player damage/cost arrays; see game/data/player_start_stats.json"
		)
		return
	var baseline := _read_json("res://data/player_baseline.json")
	var tuning := _read_json("res://data/prototype_tuning.json")
	var wave_document := _read_json("res://data/wave_0000.json")
	var hp_document := _read_json("res://data/enemy_hp_by_id.json")
	var movement_document := _read_json("res://data/enemy_movement_wave_0000.json")
	var guns_document := _read_json("res://data/enemy_guns_wave_0000.json")
	var items_document := _read_json("res://data/items.json")
	var drop_policy := _read_json("res://data/drop_policy.json")
	var pvp_document := _read_json("res://data/pvp_reward_arrays.json")
	var shop_contract := _read_json("res://data/shop_contract.json")
	var iap_products := _read_json("res://data/iap_products.json")
	var monetization_config := _read_json("res://data/monetization_config.json")
	if (
		wave_document.is_empty()
		or hp_document.is_empty()
		or movement_document.is_empty()
		or pvp_document.is_empty()
		or shop_contract.is_empty()
		or iap_products.is_empty()
		or monetization_config.is_empty()
	):
		return
	var wave: Dictionary = wave_document.get("wave", {})
	if not _validate_wave_data(wave, hp_document, movement_document):
		return
	var base_hp := float(baseline.get("base_hp", FALLBACK_PLAYER_HP))
	var fire_period := float(tuning.get("player_fire_period_seconds", 0.24))
	_player_bullet_speed = float(tuning.get("player_projectile_speed_units_per_second", 18.0))
	# STATIC_CONFIRMED: index 0 is 4500; index-to-ship-ID mapping is not asserted.
	player.configure_weapon(float(damage_values[PLAYER_INDEX]), fire_period)
	player.configure_health(base_hp)
	_load_item_catalog(items_document)
	monetization.configure(iap_products, monetization_config)
	economy_panel.configure(_player_costs, pvp_document, shop_contract, monetization)
	economy_panel.set_economy_state(_coins, _purchased_player_indices)
	_drop_period = maxf(float(drop_policy.get("period_seconds", 18.0)), 1.0)
	_drop_item_cycle = drop_policy.get("item_index_cycle", [1])
	wave_director.configure(
		world, wave_document, hp_document, movement_document, guns_document, player
	)
	wave_director.wave_started.connect(_on_wave_started)
	wave_director.enemy_spawned.connect(_on_enemy_spawned)
	wave_director.spawn_progress_changed.connect(_on_spawn_progress_changed)
	wave_director.spawns_finished.connect(_on_spawns_finished)
	_update_hud()
	wave_director.start_wave()


func _process(delta: float) -> void:
	if _game_over or _wave_clear or get_tree().paused or _drop_item_cycle.is_empty():
		return
	_drop_elapsed += delta
	if _drop_elapsed >= _drop_period:
		_drop_elapsed = fposmod(_drop_elapsed, _drop_period)
		_spawn_item_drop()


func _configure_camera() -> void:
	var viewport_size := get_viewport_rect().size
	if viewport_size.x <= 0.0 or viewport_size.y <= 0.0:
		return
	# Reference camera contract: half-height = max((h / w) * 5.4, 9.6).
	var half_height := maxf((viewport_size.y / viewport_size.x) * 5.4, 9.6)
	var pixels_per_world_unit := viewport_size.y / (half_height * 2.0)
	camera.zoom = Vector2(pixels_per_world_unit, pixels_per_world_unit)
	var half_width := viewport_size.x / pixels_per_world_unit * 0.5
	player.set_movement_bounds(
		Rect2(
			-half_width + 0.48,
			-half_height + 0.82,
			(half_width - 0.48) * 2.0,
			(half_height - 0.82) * 2.0
		)
	)


func _on_wave_started(wave_name: String, total_enemy_entries: int) -> void:
	_wave_spawn_total = total_enemy_entries
	hud.update_status({"wave": "WAVE 0000  ·  %s" % wave_name.to_upper()})
	_update_hud()


func _on_enemy_spawned(enemy: WaveEnemy) -> void:
	_live_enemies += 1
	enemy.defeated.connect(_on_enemy_defeated)
	enemy.escaped.connect(_on_enemy_escaped)
	enemy.projectile_requested.connect(_on_enemy_projectile_requested)
	_update_hud()


func _on_spawn_progress_changed(spawned: int, total: int) -> void:
	_wave_spawned = spawned
	_wave_spawn_total = total
	_update_hud()


func _on_spawns_finished(_wave_name: String) -> void:
	_spawns_finished = true
	_check_wave_clear()


func _on_enemy_defeated(_enemy_id: int) -> void:
	_live_enemies = maxi(_live_enemies - 1, 0)
	_kills += 1
	_update_hud()
	_check_wave_clear()


func _on_enemy_escaped(_enemy_id: int) -> void:
	_live_enemies = maxi(_live_enemies - 1, 0)
	_update_hud()
	_check_wave_clear()


func _check_wave_clear() -> void:
	if _spawns_finished and _live_enemies == 0 and not _wave_clear and not _game_over:
		_wave_clear = true
		hud.show_wave_clear()


func _on_player_shot_requested(origin: Vector2, damage: float) -> void:
	_player_shots += 1
	var shot := PROJECTILE_SCENE.instantiate() as Projectile
	shot.faction = Projectile.Faction.PLAYER
	shot.position = origin
	shot.direction = Vector2.UP
	shot.speed = _player_bullet_speed
	shot.damage = damage
	shot.lifetime_seconds = 3.0
	world.add_child(shot)
	_update_hud()


func _on_enemy_projectile_requested(
	origin: Vector2, direction: Vector2, damage: float, speed: float, lifetime_seconds: float
) -> void:
	var shot := PROJECTILE_SCENE.instantiate() as Projectile
	shot.faction = Projectile.Faction.ENEMY
	shot.position = origin
	shot.direction = direction
	shot.speed = speed
	shot.damage = damage
	shot.lifetime_seconds = lifetime_seconds
	shot.target = player
	shot.near_miss.connect(_on_near_miss)
	world.add_child(shot)


func _on_near_miss() -> void:
	_near_misses += 1
	_update_hud()


func _spawn_item_drop() -> void:
	var item_index := int(_drop_item_cycle[_drop_cycle_index % _drop_item_cycle.size()])
	_drop_cycle_index += 1
	var item_data: Dictionary = _items_by_index.get(item_index, {})
	if item_data.is_empty():
		push_warning("Drop policy references missing catalog item %d" % item_index)
		return
	var spawn_x := clampf(player.global_position.x + _rng.randf_range(-2.0, 2.0), -4.3, 4.3)
	var spawn_y := minf(player.global_position.y - 2.4, 6.0)
	var pickup := PICKUP_SCENE.instantiate() as WavePickup
	pickup.configure(
		item_index, str(item_data.get("icon_sprite_name", "ITEM")), Vector2(spawn_x, spawn_y)
	)
	pickup.collected.connect(_on_item_collected)
	world.add_child(pickup)


func _on_item_collected(_item_index: int) -> void:
	_items_collected += 1
	_update_hud()


func _on_health_changed(_current: float, _maximum: float) -> void:
	_update_hud()


func _on_player_died() -> void:
	_game_over = true
	hud.show_game_over()
	get_tree().paused = true


func _on_pause_requested() -> void:
	if _game_over or _wave_clear or _economy_paused:
		return
	var should_pause := not get_tree().paused
	get_tree().paused = should_pause
	hud.set_paused(should_pause)


func _on_economy_requested() -> void:
	if _game_over or _wave_clear or _economy_paused:
		return
	_economy_paused = true
	get_tree().paused = true
	hud.set_paused(true)
	economy_panel.open_panel(_coins, _purchased_player_indices)


func _on_economy_closed() -> void:
	if not _economy_paused:
		return
	_economy_paused = false
	get_tree().paused = false
	hud.set_paused(false)


func _on_player_purchase_requested(player_index: int, quantity: int) -> void:
	if player_index < 0 or player_index >= _player_costs.size():
		economy_panel.report_result("Unknown playerIndex row; purchase rejected.")
		return
	if quantity != 1:
		economy_panel.report_result("One roster entry per action; stock cap is not decoded.")
		return
	var cost := int(_player_costs[player_index])
	if cost < 0:
		economy_panel.report_result(
			"PlayerCosts sentinel -1 retained; no negative-price transaction was made."
		)
		return
	if _purchased_player_indices.has(player_index):
		economy_panel.report_result("This row is already claimed in the local prototype ledger.")
		return
	if _coins < cost:
		economy_panel.report_result("Insufficient prototype coin balance; no transaction was made.")
		return
	_coins -= cost
	_purchased_player_indices[player_index] = true
	economy_panel.set_economy_state(_coins, _purchased_player_indices)
	economy_panel.report_result(
		(
			"Local ledger updated for playerIndex %d; ship identity/equip mapping remains UNKNOWN."
			% player_index
		)
	)
	_update_hud()


func _on_retry_requested() -> void:
	get_tree().paused = false
	get_tree().reload_current_scene()


func _update_hud() -> void:
	if not is_instance_valid(hud) or not is_instance_valid(player):
		return
	hud.update_status(
		{
			"wave": "WAVE 0000  ·  FIRST ENCOUNTER",
			"hp": player.current_health,
			"max_hp": player.maximum_health,
			"kills": _kills,
			"shots": _player_shots,
			"coins": _coins,
			"spawned": _wave_spawned,
			"spawn_total": _wave_spawn_total,
			"items": _items_collected,
			"near_misses": _near_misses
		}
	)


func _load_item_catalog(items_document: Dictionary) -> void:
	for item_value: Variant in items_document.get("items", []):
		if item_value is Dictionary:
			var item: Dictionary = item_value
			_items_by_index[int(item.get("index", 0))] = item


func _validate_wave_data(
	wave: Dictionary, hp_document: Dictionary, movement_document: Dictionary
) -> bool:
	var hp_by_id: Dictionary = hp_document.get("hp_by_id", {})
	var movement_by_id: Dictionary = movement_document.get("enemy_by_id", {})
	for row_value: Variant in wave.get("spawners", []):
		if not row_value is Dictionary:
			continue
		var row: Dictionary = row_value
		for prefab_value: Variant in row.get("enemies", []):
			var enemy_name := str(prefab_value)
			var enemy_id := int(enemy_name.get_slice("-", 1))
			var id_key := str(enemy_id)
			if not hp_by_id.has(id_key):
				push_error("Wave_0000 enemy %s has no STATIC_CONFIRMED HP row" % enemy_name)
				return false
			if not movement_by_id.has(id_key):
				push_error("Wave_0000 enemy %s has no source movement row" % enemy_name)
				return false
	return true


func _read_json(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		push_error("Missing runtime data file: %s" % path)
		return {}
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not parsed is Dictionary:
		push_error("Expected a JSON object in %s" % path)
		return {}
	return parsed


func _get_field_values(data: Dictionary, field_name: String) -> Array:
	for row: Dictionary in data.get("fields", []):
		if row.get("field", "") == field_name:
			return row.get("values", [])
	return []
