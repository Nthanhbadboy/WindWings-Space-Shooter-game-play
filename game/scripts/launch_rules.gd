class_name LaunchRules
extends RefCounted

## Source-pinned rules for the M2 launch slice.
##
## COORDINATE CONVENTION: every number here that comes from the decoded data uses
## the SOURCE convention (x right, y up, playfield top = +10, bottom = -15).
## Godot's screen convention is y-down, so gameplay nodes convert with
## source_to_world(): world = (x, -y). The launcher never mixes the two.
##
## Anything that is not a source fact is marked INFERRED or NEW_DESIGN.

# STATIC_CONFIRMED — docs/spec/ENEMY_BEHAVIOUR.md §1.3-§1.4 (Enemy_Movement
# border w/x/y/z = 15.0 / -10.0 / 10.0 / -15.0) and START_HERE.md rows 2 and 5.
# Playfield is 20 units wide (-10..10) and 25 units tall (-15..10).
const PLAYFIELD_WIDTH_UNITS := 20.0
const PLAYFIELD_HEIGHT_UNITS := 25.0
const PLAYFIELD_MIN_X := -10.0
const PLAYFIELD_MAX_X := 10.0
const PLAYFIELD_MIN_Y := -15.0
const PLAYFIELD_MAX_Y := 10.0

# STATIC_CONFIRMED — spawner y edge and median spawner rate (START_HERE row 5).
const SPAWN_Y := 9.6
const SPAWN_MEDIAN_RATE := 1.0
# STATIC_CONFIRMED distribution over the 10.807 active spawner rows of
# datas/waves.json: y=9.6 on 66.1%, y=12.0 on 15.7%, y=0.0 on 6.3%, y=15.0 on
# 1.1%, the rest between 8.0/5.0/6.0/4.0/2.0/10.0/7.0/3.0/9.0 and a few
# fractional values (minimum -0.25). Spawning above the visible top is normal:
# those enemies fly in, so the value is kept, not clamped.
const SPAWN_Y_MIN := -0.25
const SPAWN_Y_MAX := 15.0
# INFERRED NEW_DESIGN — one unit of margin above the highest spawn height so an
# enemy that spawns at source y=15 is not despawned on its first frame.
const DESPAWN_TOP_MARGIN := 1.0

# STATIC_CONFIRMED — the prefab collision/border radius is 15 units for 799/800
# Enemy_Movement rows and for Bullet_Linearly.border.w.
const SOURCE_COLLIDER_UNITS := 15.0
# INFERRED NEW_DESIGN — the source never states how a prefab unit maps onto the
# 20x25 playfield; a literal 15-unit collider would cover 75% of its width. The
# slice renders the projectile collider at 15 * 0.01 = 0.15 world units.
const SOURCE_COLLIDER_SCALE := 0.01

# STATIC_CONFIRMED — BALANCE §0.6 / OPEN_ISSUES A1:
# HPmax = StartHp * (1 + 0,18 * TechStatPoints(0) + ability7 * GetNumberAbility(7)).
const START_HP := 2500.0
const STEP_COMMON := 0.18
const HIT_INVULNERABILITY_SECONDS := 3.0

# STATIC_CONFIRMED — START_HERE row 6 / DIFFICULTY_MODES §5: levelDelta scales
# the reward only. It never scales HP and never scales the enemy count.
const LEVEL_DELTA := [1.0, 2.0, 3.6, 3.6]
const MAX_MODE_INDEX := 4

# STATIC_CONFIRMED — datas/camera_scaler_contract.json: ortho size is
# max((h / w) * 5.4, 9.6); 9.6 is a floor, not a fixed value.
const CAMERA_ASPECT_FACTOR := 5.4
const CAMERA_MIN_HALF_HEIGHT := 9.6

# INFERRED NEW_DESIGN — slice scoring and screen margins.
const SCORE_PER_KILL := 10
const SCORE_PER_WAVE := 250
const SCORE_VICTORY := 1000
const PLAYER_SIDE_MARGIN := 0.6
const PLAYER_TOP_MARGIN := 1.2
const PLAYER_BOTTOM_MARGIN := 0.9

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


static func is_inside_playfield(source_point: Vector2) -> bool:
	return playfield_rect().has_point(source_point)


static func source_to_world(source_point: Vector2) -> Vector2:
	return Vector2(source_point.x, -source_point.y)


static func world_to_source(world_point: Vector2) -> Vector2:
	return Vector2(world_point.x, -world_point.y)


static func world_playfield_rect() -> Rect2:
	# x -10..10, world y -10..15 (source top +10 becomes world -10).
	return Rect2(PLAYFIELD_MIN_X, -PLAYFIELD_MAX_Y, PLAYFIELD_WIDTH_UNITS, PLAYFIELD_HEIGHT_UNITS)


static func world_border_rect() -> Rect2:
	# STATIC_CONFIRMED border.w/x/y/z plus the documented off-screen spawn
	# heights: horizontal -15..15, world bottom (source -15) = +15, world top
	# (source 15 + margin) = -16.
	var top := -(SPAWN_Y_MAX + DESPAWN_TOP_MARGIN)
	var bottom := -PLAYFIELD_MIN_Y
	return Rect2(-SOURCE_COLLIDER_UNITS, top, SOURCE_COLLIDER_UNITS * 2.0, bottom - top)


static func is_outside_world_border(world_point: Vector2) -> bool:
	return not world_border_rect().has_point(world_point)


static func is_spawn_y_documented(source_y: float) -> bool:
	return source_y >= SPAWN_Y_MIN and source_y <= SPAWN_Y_MAX


static func is_spawn_offscreen(source_y: float) -> bool:
	# Above the playfield top but still a documented spawn height.
	return source_y > PLAYFIELD_MAX_Y and source_y <= SPAWN_Y_MAX


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
	return 1.0


static func enemy_hp(source_hp: float, mode: int) -> float:
	return source_hp * hp_multiplier(mode)


static func kill_score(mode: int) -> int:
	return int(round(float(SCORE_PER_KILL) * reward_multiplier(mode)))


static func wave_score(mode: int) -> int:
	return int(round(float(SCORE_PER_WAVE) * reward_multiplier(mode)))


static func boss_score(mode: int) -> int:
	return int(round(float(SCORE_VICTORY) * reward_multiplier(mode)))


static func camera_half_height(viewport_size: Vector2) -> float:
	if viewport_size.x <= 0.0 or viewport_size.y <= 0.0:
		return CAMERA_MIN_HALF_HEIGHT
	return maxf((viewport_size.y / viewport_size.x) * CAMERA_ASPECT_FACTOR, CAMERA_MIN_HALF_HEIGHT)


static func camera_half_width(viewport_size: Vector2) -> float:
	var half_height := camera_half_height(viewport_size)
	if viewport_size.y <= 0.0:
		return half_height * 0.5625
	return half_height * (viewport_size.x / viewport_size.y)


static func player_bounds(half_height: float, half_width: float) -> Rect2:
	var playfield := world_playfield_rect()
	var left := maxf(-half_width + PLAYER_SIDE_MARGIN, playfield.position.x + PLAYER_SIDE_MARGIN)
	var right := minf(half_width - PLAYER_SIDE_MARGIN, playfield.end.x - PLAYER_SIDE_MARGIN)
	var top := maxf(-half_height + PLAYER_TOP_MARGIN, playfield.position.y + 1.0)
	var bottom := minf(half_height - PLAYER_BOTTOM_MARGIN, playfield.end.y - 1.0)
	return Rect2(left, top, maxf(right - left, 0.2), maxf(bottom - top, 0.2))


static func enemy_spawn_x_limit(half_width: float) -> float:
	return minf(half_width - 0.75, PLAYFIELD_MAX_X - 0.75)


static func boss_station_world(slot: int, copies: int) -> Vector2:
	# INFERRED NEW_DESIGN: bosses hold a station in the upper half of the view,
	# side by side when the row keeps copies=2.
	var spread := 2.6
	var offset := (float(slot) - float(maxi(copies - 1, 0)) * 0.5) * spread
	return Vector2(offset, -5.4)
