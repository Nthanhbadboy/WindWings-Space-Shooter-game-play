class_name MotionTuning
extends RefCounted

## Every rhythm and amplitude of the launch-slice animation, in one file.
##
## Source numbers (docs/spec/VISUAL_DESIGN.md §4, claims J9/AF1):
##   hit flash   : alpha 0.5 for 0.05 s (Enemy_Display.OnHit) = 3 frames at 60 fps
##   screen shake: lvVibr 0.10 · timeVibr 20 frames (185/241 prefabs)
##   boss rhythm : 0.17 / 0.33 / 1.0 / 5.0 s attack spacing
## Everything else is INFERRED NEW_DESIGN and is labelled as such per constant.
## No gameplay value (HP, damage, spawn rate) lives here.

# --- hit feedback (STATIC_CONFIRMED) ------------------------------------------
const FLASH_SECONDS := 0.05
const FLASH_ALPHA := 0.5
const SHAKE_AMPLITUDE := 0.10
const SHAKE_FRAMES := 20
const SHAKE_FPS := 60.0

# --- hangar idle (INFERRED NEW_DESIGN) ----------------------------------------
const HANGAR_BOB_AMPLITUDE := 0.28
const HANGAR_BOB_PERIOD := 2.6
const HANGAR_SHADOW_MIN_SCALE := 0.55
const HANGAR_SHADOW_MAX_SCALE := 0.9
const HANGAR_GLOW_PERIOD := 1.9
const HANGAR_GLOW_MIN := 0.35
const HANGAR_GLOW_MAX := 0.95
const HANGAR_ENGINE_IDLE := 0.8
const HANGAR_ROLL_PERIOD := 5.2
const HANGAR_ROLL_DEGREES := 2.5

# --- flight (INFERRED NEW_DESIGN) ---------------------------------------------
const BANK_MAX_DEGREES := 16.0
const BANK_RESPONSE := 7.0
const BANK_VELOCITY_FULL_SCALE := 9.0
const ENGINE_IDLE_LENGTH := 0.55
const ENGINE_FAST_LENGTH := 1.85
const ENGINE_RESPONSE := 6.0
const ENGINE_UPWARD_GAIN := 0.35

# --- particle sizes (INFERRED NEW_DESIGN) -------------------------------------
# GPUParticles2D draws its texture at pixel size in world units, so a 16 px
# flame texture must be scaled to ~0.05 to read as a sub-unit plume.
const ENGINE_PARTICLE_SCALE_MIN := 0.03
const ENGINE_PARTICLE_SCALE_MAX := 0.07
const HULL_SPARK_SCALE_MIN := 0.02
const HULL_SPARK_SCALE_MAX := 0.05
const BOSS_AURA_SCALE_MIN := 0.06
const BOSS_AURA_SCALE_MAX := 0.14

# --- boss (INFERRED NEW_DESIGN, rhythm from BOSS_ANIM_TIMELINE 0.17 s) --------
const BOSS_DESCENT_SECONDS := 2.4
const BOSS_BOB_AMPLITUDE := 0.16
const BOSS_BOB_PERIOD := 3.1
const BOSS_GUN_TURN_DEGREES_PER_SECOND := 150.0
const BOSS_TELEGRAPH_SECONDS := 0.42
const BOSS_CORE_MIN_GLOW := 0.35
const BOSS_CORE_MAX_GLOW := 1.0
const BOSS_HIT_FLASH_SECONDS := 0.05
const BOSS_DEATH_LAYERS := 4
const BOSS_DEATH_LAYER_STAGGER := 0.12
const BOSS_DEATH_LAYER_FADE := 0.45
const BOSS_WARNING_SECONDS := 1.4


static func flash_alpha(elapsed: float) -> float:
	if elapsed < 0.0 or elapsed >= FLASH_SECONDS:
		return 0.0
	return FLASH_ALPHA


static func shake_seconds() -> float:
	return SHAKE_FRAMES / SHAKE_FPS


static func shake_offset(elapsed: float, amplitude := SHAKE_AMPLITUDE) -> Vector2:
	var duration := shake_seconds()
	if elapsed < 0.0 or elapsed >= duration:
		return Vector2.ZERO
	var decay := 1.0 - (elapsed / duration)
	var phase := elapsed * 62.0
	# Both axes start at zero so the first shaken frame never jumps the camera.
	return Vector2(sin(phase) * amplitude, sin(phase * 1.37) * amplitude * 0.7) * decay


static func telegraph_strength(seconds_until_shot: float) -> float:
	if seconds_until_shot < 0.0 or seconds_until_shot > BOSS_TELEGRAPH_SECONDS:
		return 0.0
	return 1.0 - (seconds_until_shot / BOSS_TELEGRAPH_SECONDS)


static func core_glow(seconds_until_shot: float) -> float:
	# Same time domain as telegraph_strength(): the core is brightest at the shot.
	return lerpf(BOSS_CORE_MIN_GLOW, BOSS_CORE_MAX_GLOW, telegraph_strength(seconds_until_shot))


static func bank_angle(velocity_x: float) -> float:
	var normalised := clampf(velocity_x / BANK_VELOCITY_FULL_SCALE, -1.0, 1.0)
	return deg_to_rad(-BANK_MAX_DEGREES * normalised)


static func engine_length(vertical_speed: float, boosting := false) -> float:
	var base := ENGINE_FAST_LENGTH if boosting else ENGINE_IDLE_LENGTH
	return clampf(base + absf(vertical_speed) * ENGINE_UPWARD_GAIN, ENGINE_IDLE_LENGTH, ENGINE_FAST_LENGTH)


static func death_layer_alpha(layer: int, elapsed: float) -> float:
	var delay := float(layer) * BOSS_DEATH_LAYER_STAGGER
	if elapsed < delay:
		return 1.0
	return clampf(1.0 - (elapsed - delay) / BOSS_DEATH_LAYER_FADE, 0.0, 1.0)


static func death_total_seconds() -> float:
	return float(BOSS_DEATH_LAYERS - 1) * BOSS_DEATH_LAYER_STAGGER + BOSS_DEATH_LAYER_FADE
