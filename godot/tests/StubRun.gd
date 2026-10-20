extends Node
## StubRun.gd — "RunScene giả" cho smoke test headless: đếm đạn/địch sinh ra,
## cung cấp player_position() cố định, nuốt mọi callback fx/hud.

class StubDrones:
	func fire(_dmg: float) -> void:
		pass

var boss_bullets := 0
var enemy_bullets := 0
var player_bullets := 0
var enemies_spawned := 0
var weapon_volleys := 0
var player_pos := Vector2(360.0, 1000.0)
var drones := StubDrones.new()

func player_position() -> Vector2:
	return player_pos

func spawn_boss_bullet(_pos: Vector2, _vel: Vector2, _color: Color, _radius: float, _homing := 0.0) -> void:
	boss_bullets += 1

func spawn_enemy_bullet(_pos: Vector2, _vel: Vector2, _color: Color, _radius: float, _homing := 0.0) -> void:
	enemy_bullets += 1

func spawn_player_bullet(_pos: Vector2, _vel: Vector2, _dmg: float, _radius: float, _color: Color) -> void:
	player_bullets += 1

func spawn_enemy(_type: String, _x: float, _y := -60.0) -> void:
	enemies_spawned += 1

func fire_player_weapon(_p: Node2D) -> void:
	weapon_volleys += 1

func fx_shake(_a: float, _d: float) -> void:
	pass

func fx_flash(_c: Color, _a: float, _d: float) -> void:
	pass

func fx_slow_mo(_s: float, _d: float) -> void:
	pass

func fx_burst(_pos: Vector2, _c: Color, _n: int) -> void:
	pass

func boss_hp_changed(_b: Node2D) -> void:
	pass

func boss_phase_changed(_b: Node2D, _p: int) -> void:
	pass

func boss_enraged(_b: Node2D) -> void:
	pass

func boss_fired(_b: Node2D, _pattern: String) -> void:
	pass

func on_enemy_killed(_e: Node2D, _by_player: bool) -> void:
	pass

func apply_powerup(_kind: String, _pos: Vector2) -> void:
	pass

func has_magnet() -> bool:
	return true

func magnet_radius() -> float:
	return float(Balance.POWERUP["magnet_radius"])
