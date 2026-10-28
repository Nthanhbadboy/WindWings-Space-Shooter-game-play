class_name LaunchRules
extends RefCounted

## Source-pinned rules for the M2 launch slice.
##
## Every constant below cites where it comes from. Anything that is not a source
## fact is marked INFERRED or NEW_DESIGN and is repeated in the slice report.

# STATIC_CONFIRMED — docs/spec/ENEMY_BEHAVIOUR.md §1.3–§1.4 (border w/x/y/z =
# 15.0 / -10.0 / 10.0 / -15.0) and docs/spec/START_HERE.md rows 2 and 5.
# Playfield is 20 units wide (-10..10) and 25 units tall (-15..10).
const PLAYFIELD_WIDTH_UNITS := 20.0
const PLAYFIELD_HEIGHT_UNITS := 25.0
const PLAYFIELD_MIN_X := -10.0
const PLAYFIELD_MAX_X := 10.0
const PLAYFIELD_MIN_Y := -15.0
const PLAYFIELD_MAX_Y := 10.0

# STATIC_CONFIRMED — spawner y edge and median spawner rate (START_HERE row 5,
# DONE.md "ví dụ test cụ thể": rate default 1.0 on 16.173 spawners, y_spawn 9.6
# on 15.485 spawners).
const SPAWN_Y := 9.6
const SPAWN_MEDIAN_RATE := 1.0

# STATIC_CONFIRMED — prefab collision/border radius is 15 units for 799/800
# Enemy_Movement rows and for Bullet_Linearly.border.w.
const SOURCE_COLLIDER_UNITS := 15.0
# INFERRED NEW_DESIGN — the source never states how a prefab unit maps to the
# 20x25 playfield; a literal 15-unit collider would cover 75% of the playfield
# width. The slice therefore renders colliders at 15 * 0.01 = 0.15 world units.
# This conversion is a slice decision and is not claimed as reconstructed.
const SOURCE_COLLIDER_SCALE := 0.01

# STATIC_CONFIRMED — docs/spec/BALANCE.md §0.6, docs/spec/OPEN_ISSUES.md A1:
# HPmax = StartHp * (1 + 0,18 * TechStatPoints(0) + ability7 * GetNumberAbility(7)).
const START_HP := 2500.0
const STEP_COMMON := 0.18
const HIT_INVULNERABILITY_SECONDS := 3.0

# STATIC_CONFIRMED — docs/spec/START_HERE.md row 6, DIFFICULTY_MODES §5:
# levelDelta scales the reward, never enemy HP, and never the enemy count.
const LEVEL_DELTA := [1.0, 2.0, 3.6, 3.6]
const MAX_MODE_INDEX := 4

# STATIC_CONFIRMED — datas/camera_scaler_contract.json: ortho size is
# max((h / w) * 5.4, 9.6); 9.6 is a floor, not a fixed value.
const CAMERA_ASPECT_FACTOR := 5.4
const CAMERA_MIN_HALF_HEIGHT := 9.6

# INFERRED NEW_DESIGN — slice scoring and safety margins. The source does not
# expose a per-kill score, so the slice scores below and multiplies only the
# score by levelDelta[mode].
const SCORE_PER_KILL := 10
const SCORE_PER_WAVE := 250
const SCORE_VICTORY := 1000
const PLAYER_BOTTOM_MARGIN := 0.9
const PLAYER_TOP_LIMIT := 8.6
const PLAYER_SIDE_MARGIN := 0.6

# INFERRED NEW_DESIGN — contact damage is not decoded; the slice reuses the
# documented Gun_Attack median damage (400) so ramming is survivable but not free.
const CONTACT_DAMAGE := 400.0


static func playfield_rect() -> Rect2:
	return Rect2(
		PLAYFIELD_MIN_X,
		PLAYFIELD_MIN_Y,
		PLAYFIELD_WIDTH_UNITS,
		PLAYFIELD_HEIGHT_UNITS
	)


static func collider_radius_world() -> float:
	return SOURCE_COLLIDER_UNITS * SOURCE_COLLIDER_SCALE


static func max_hp(start_hp: float, tech_stat_points: int, ability7_count: int) -> float:
	var tech := float(maxi(tech_stat_points, 0))
	var ability := float(maxi(ability7_count, 0))
	return start_hp * (1.0 + STEP_COMMON * tech + ability)


static func level_delta(mode: int) -> float:
	if mode < 0 or mode >= LEVEL_DELTA.size():
		return 1.0
	return float(LEVEL_DELTA[mode])


static func reward_multiplier(mode: int) -> float:
	return level_delta(mode)


static func hp_multiplier(_mode: int) -> float:
	# Mode never scales HP (kHp does not exist; only levelDelta scales rewards).
	return 1.0


static func enemy_hp(source_hp: float, mode: int) -> float:
	return source_hp * hp_multiplier(mode)


static func kill_score(mode: int) -> int:
	return int(round(float(SCORE_PER_KILL) * reward_multiplier(mode)))


static func wave_score(mode: int) -> int:
	return int(round(float(SCORE_PER_WAVE) * reward_multiplier(mode)))


static func camera_half_height(viewport_size: Vector2) -> float:
	if viewport_size.x <= 0.0 or viewport_size.y <= 0.0:
		return CAMERA_MIN_HALF_HEIGHT
	var aspect := viewport_size.y / viewport_size.x
	return maxf(aspect * CAMERA_ASPECT_FACTOR, CAMERA_MIN_HALF_HEIGHT)


static func player_bounds(half_height: float) -> Rect2:
	var bottom := maxf(-half_height + PLAYER_BOTTOM_MARGIN, PLAYFIELD_MIN_Y + PLAYER_BOTTOM_MARGIN)
	var top := minf(PLAYER_TOP_LIMIT, PLAYFIELD_MAX_Y - 1.4)
	var left := PLAYFIELD_MIN_X + PLAYER_SIDE_MARGIN
	var right := PLAYFIELD_MAX_X - PLAYER_SIDE_MARGIN
	return Rect2(left, bottom, right - left, top - bottom)


static func enemy_spawn_x_limit(half_width: float) -> float:
	return minf(half_width - 0.75, PLAYFIELD_MAX_X - 0.75)


static func is_inside_playfield(point: Vector2) -> bool:
	return (
		point.x >= PLAYFIELD_MIN_X
		and point.x <= PLAYFIELD_MAX_X
		and point.y >= PLAYFIELD_MIN_Y
		and point.y <= PLAYFIELD_MAX_Y
	)


static func is_outside_despawn_border(point: Vector2) -> bool:
	# STATIC_CONFIRMED border.w / border.z: horizontal wrap radius 15, vertical 15.
	return absf(point.x) > SOURCE_COLLIDER_UNITS or point.y < -SOURCE_COLLIDER_UNITS or point.y > PLAYFIELD_MAX_Y + 2.0
