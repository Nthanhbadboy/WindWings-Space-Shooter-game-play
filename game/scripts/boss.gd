class_name SliceBoss
extends Area2D

## Wave boss for the slice.
##
## Data: HP and the 14 Attack2 shot times (datas/boss_hp.json,
## datas/boss_anim_events.csv via data/boss_slice.json).
## Animation (all rhythms in MotionTuning):
##   - descends from above, then bobs gently in place
##   - both gun mounts rotate to aim at the player ship
##   - the core brightens for the last 0.42 s before each scheduled shot
##   - 0.05 s white flash + a short shake on every hit
##   - death: layers fade one after another, then the explosion FX chain
##
## Art: body / gun_left / gun_right / core slots when present, the single
## Boss-37001.png otherwise, and the vector boss when no art exists at all.

signal defeated(boss: Node)
signal projectile_requested(
	origin: Vector2, direction: Vector2, damage: float, speed: float, lifetime_seconds: float
)
signal shake_requested(strength: float)
signal entrance_progress(progress: float)

const INTRO_SECONDS := MotionTuning.BOSS_DESCENT_SECONDS

var max_hp := 0.0
var current_hp := 0.0
var contact_damage := 0.0

var _pattern: BossPattern
var _target: Node2D
var _station := Vector2.ZERO
var _spawn_point := Vector2.ZERO
var _slot := 0
var _gun: Dictionary = {}
var _elapsed := 0.0
var _shot_elapsed := 0.0
var _dead := false
var _dying := false
var _death_elapsed := 0.0
var _hit_flash_elapsed := 999.0
var _gun_angles := [0.0, 0.0]
var _bob := 0.0
var _aura: GPUParticles2D


func configure(data: Dictionary) -> void:
	_pattern = data.get("pattern")
	max_hp = float(data.get("hp", 0.0))
	current_hp = max_hp
	contact_damage = float(data.get("contact_damage", 0.0))
	_station = data.get("station", Vector2.ZERO)
	_spawn_point = data.get("spawn_position", _station)
	_slot = int(data.get("slot", 0))
	var target_value: Variant = data.get("target")
	if target_value is Node2D:
		_target = target_value
	var gun_value: Variant = data.get("gun_profile", {})
	if gun_value is Dictionary:
		_gun = gun_value
	position = _spawn_point


func _guns_track_target() -> bool:
	return Session.variant == null or Session.variant.guns_track_target()


func _whole_image_mode() -> bool:
	return Session.variant != null and Session.variant.is_whole()


## Variant C has no separate core layer, so the telegraph reads as an ember aura
## emitted on top of the flat image instead of a brightening core sprite.
func _build_aura() -> void:
	_aura = GPUParticles2D.new()
	_aura.amount = 26
	_aura.lifetime = 0.8
	_aura.local_coords = true
	_aura.position = Vector2(0.0, -0.1)
	_aura.z_index = 1
	var image := Image.create(12, 12, false, Image.FORMAT_RGBA8)
	for y in range(12):
		for x in range(12):
			var offset := Vector2(float(x) - 5.5, float(y) - 5.5) / 5.5
			image.set_pixel(x, y, Color(1.0, 0.7, 0.5, pow(1.0 - clampf(offset.length(), 0.0, 1.0), 2.0)))
	_aura.texture = ImageTexture.create_from_image(image)
	var material := ParticleProcessMaterial.new()
	material.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
	material.emission_sphere_radius = 0.7
	material.direction = Vector3(0.0, -1.0, 0.0)
	material.spread = 60.0
	material.gravity = Vector3.ZERO
	material.initial_velocity_min = 0.2
	material.initial_velocity_max = 0.6
	material.scale_min = MotionTuning.BOSS_AURA_SCALE_MIN
	material.scale_max = MotionTuning.BOSS_AURA_SCALE_MAX
	material.color = Color(1.0, 0.6, 0.42, 0.6)
	_aura.process_material = material
	add_child(_aura)


func _ready() -> void:
	add_to_group("enemies")
	add_to_group("shootable")
	add_to_group("bosses")
	collision_layer = 4
	collision_mask = 3
	var shape := CircleShape2D.new()
	shape.radius = 1.15
	var collider := get_node_or_null("CollisionShape2D") as CollisionShape2D
	if collider != null:
		collider.shape = shape
	if _whole_image_mode():
		_build_aura()
	queue_redraw()


func _physics_process(delta: float) -> void:
	if _dead or _dying:
		if _dying:
			_death_elapsed += delta
			queue_redraw()
			if _death_elapsed >= MotionTuning.death_total_seconds():
				_finish_death()
		return
	_elapsed += delta
	var progress := clampf(_elapsed / INTRO_SECONDS, 0.0, 1.0)
	position.y = lerpf(_spawn_point.y, _station.y, _ease_out(progress))
	position.x = _station.x + sin(_elapsed * 0.75 + float(_slot) * 1.7) * 1.35 * progress
	entrance_progress.emit(progress)
	_bob = sin(_elapsed * TAU / MotionTuning.BOSS_BOB_PERIOD) * MotionTuning.BOSS_BOB_AMPLITUDE
	if progress < 1.0:
		return

	_update_guns(delta)
	var previous := _shot_elapsed
	_shot_elapsed += delta
	if _pattern == null:
		return
	for _shot in range(_pattern.shots_in_interval(previous, _shot_elapsed)):
		_fire()
	queue_redraw()


static func _ease_out(value: float) -> float:
	return 1.0 - pow(1.0 - clampf(value, 0.0, 1.0), 3.0)


func _mount_world(index: int) -> Vector2:
	# Gun mount anchors inside the 2.4-unit body; the pivot in the contract sits
	# at (0.5, 0.22) of the 0.95-unit gun canvas.
	var side := -1.0 if index == 0 else 1.0
	return global_position + Vector2(side * 0.62, _bob + 0.42)


func _update_guns(delta: float) -> void:
	# Variant C animates one rigid flat image: its guns are painted on, so the
	# mounts stay at their rest pose instead of swinging independently.
	if not _guns_track_target():
		_gun_angles = [0.0, 0.0]
		return
	if not is_instance_valid(_target):
		return
	for index in range(2):
		var mount := _mount_world(index)
		var aim := (_target.global_position - mount).angle()
		# Canvas gun art points down, so a downward rest pose is 0 radians.
		var desired := aim - PI * 0.5
		var step := deg_to_rad(MotionTuning.BOSS_GUN_TURN_DEGREES_PER_SECOND) * delta
		_gun_angles[index] = move_toward(_gun_angles[index], desired, step)


func _seconds_until_next_shot() -> float:
	if _pattern == null or _pattern.shot_times.is_empty():
		return 999.0
	var progress := _pattern.loop_progress(_shot_elapsed)
	var best := 999.0
	for time_value: Variant in _pattern.shot_times:
		var delta := float(time_value) - progress
		if delta <= 0.0001:
			delta += _pattern.loop_seconds
		best = minf(best, delta)
	return best


func _current_core_glow() -> float:
	if _dying:
		return 0.0
	return MotionTuning.core_glow(_seconds_until_next_shot())


func _fire() -> void:
	if not is_instance_valid(_target) or _gun.is_empty() or _dying:
		return
	for index in range(2):
		var mount := _mount_world(index)
		var origin := mount + Vector2(0.0, 0.35)
		var direction := (_target.global_position - origin).normalized()
		projectile_requested.emit(
			origin,
			direction,
			float(_gun.get("damage", 400.0)),
			float(_gun.get("speed", 8.0)),
			float(_gun.get("lifetime_seconds", 6.0))
		)
	Session.play_sfx("hit")
	queue_redraw()


func take_damage(amount: float) -> void:
	if _dead or _dying or amount <= 0.0:
		return
	current_hp = maxf(current_hp - amount, 0.0)
	_hit_flash_elapsed = 0.0
	shake_requested.emit(0.35)
	queue_redraw()
	if current_hp <= 0.0:
		_begin_death()


func _process(delta: float) -> void:
	if _hit_flash_elapsed < MotionTuning.BOSS_HIT_FLASH_SECONDS:
		_hit_flash_elapsed += delta
		queue_redraw()


func _begin_death() -> void:
	_dying = true
	_death_elapsed = 0.0
	queue_redraw()


func _finish_death() -> void:
	if _dead:
		return
	_dead = true
	var parent := get_parent()
	for index in range(3):
		var burst := FXBurst.spawn(parent, "explosion", global_position + Vector2(float(index - 1) * 0.5, float(index) * 0.3), 1.6 + float(index) * 0.4)
		if burst != null:
			burst.delay = float(index) * 0.08
	defeated.emit(self)
	queue_free()


func is_defeated() -> bool:
	return _dead or _dying


func _draw() -> void:
	var art := Session.art
	var slot := _art_slot()
	var body_slot := "%s-BODY" % slot
	var core_slot := "%s-CORE" % slot
	var flash_strength := MotionTuning.flash_alpha(_hit_flash_elapsed) / MotionTuning.FLASH_ALPHA

	var layered := (
		art != null
		and (Session.variant == null or Session.variant.uses_layers())
		and art.has_art(body_slot)
		and art.has_art(core_slot)
	)
	if layered:
		_draw_layered(art, slot, flash_strength)
		_draw_health_bar()
		return
	if art != null and art.draw_slot(self, slot, Vector2(0.0, _bob)):
		if flash_strength > 0.0:
			art.draw_flash(self, slot, Vector2(0.0, _bob), flash_strength)
		_draw_whole_image_telegraph()
		_draw_health_bar()
		return
	_draw_vector(flash_strength)
	_draw_whole_image_telegraph()
	_draw_health_bar()


## Only used by variant C: a halo that grows for the 0.42 s before a shot, so the
## rhythm stays readable without a separate core sprite.
func _draw_whole_image_telegraph() -> void:
	if not _whole_image_mode() or _dying:
		return
	var strength := MotionTuning.telegraph_strength(_seconds_until_next_shot())
	if strength <= 0.0:
		return
	var death_alpha := 1.0
	var radius := 0.95 + 0.55 * strength
	draw_circle(
		Vector2(0.0, _bob), radius, Color(1.0, 0.45, 0.3, 0.22 * strength * death_alpha)
	)
	draw_arc(
		Vector2(0.0, _bob),
		radius,
		0.0,
		TAU,
		48,
		Color(1.0, 0.7, 0.4, 0.55 * strength),
		0.08
	)


func _draw_layered(art: ArtLibrary, slot: String, flash_strength: float) -> void:
	var death_alpha := 1.0
	if _dying:
		death_alpha = MotionTuning.death_layer_alpha(3, _death_elapsed)
	art.draw_slot(
		self, "%s-BODY" % slot, Vector2(0.0, _bob), Vector2.ZERO, Color(1, 1, 1, death_alpha)
	)
	for index in range(2):
		var gun_slot := "%s-%s" % [slot, "GUN-L" if index == 0 else "GUN-R"]
		if not art.has_art(gun_slot):
			continue
		var gun_alpha := death_alpha
		if _dying:
			gun_alpha = MotionTuning.death_layer_alpha(index, _death_elapsed)
		art.draw_slot_pivoted(
			self,
			gun_slot,
			_mount_world(index) - global_position,
			Vector2.ZERO,
			Color(1, 1, 1, gun_alpha),
			_gun_angles[index]
		)
	var glow := _current_core_glow()
	var core_alpha := clampf(glow * death_alpha, 0.0, 1.0)
	art.draw_slot(
		self, "%s-CORE" % slot, Vector2(0.0, _bob), Vector2.ZERO, Color(1, 1, 1, core_alpha)
	)
	if flash_strength > 0.0:
		art.draw_flash(self, "%s-BODY" % slot, Vector2(0.0, _bob), flash_strength)


func _draw_vector(flash_strength: float) -> void:
	var death_alpha := 1.0 if not _dying else MotionTuning.death_layer_alpha(3, _death_elapsed)
	# The hit flash lightens the shapes that were hit (a silhouette flash); an
	# opaque disc on top would just hide the boss and read as a pale ball.
	var flash := clampf(flash_strength, 0.0, 1.0) * MotionTuning.FLASH_ALPHA
	var hull := Color(0.62, 0.30, 0.86, death_alpha).lerp(Color(1, 1, 1, death_alpha), flash)
	var glow := Color(1.0, 0.55, 0.42, death_alpha)
	draw_circle(
		Vector2(0.0, _bob),
		1.05,
		Color(0.16, 0.06, 0.24, 0.9 * death_alpha).lerp(Color(1, 1, 1, death_alpha), flash)
	)
	draw_colored_polygon(
		PackedVector2Array(
			[
				Vector2(0.0, -1.0 + _bob),
				Vector2(1.05, -0.25 + _bob),
				Vector2(0.78, 0.72 + _bob),
				Vector2(0.0, 0.45 + _bob),
				Vector2(-0.78, 0.72 + _bob),
				Vector2(-1.05, -0.25 + _bob),
			]
		),
		hull
	)
	# Two rotatable vector guns mirroring the contract gun mounts.
	for index in range(2):
		var mount := _mount_world(index) - global_position
		var gun_alpha := death_alpha
		if _dying:
			gun_alpha = MotionTuning.death_layer_alpha(index, _death_elapsed)
		draw_set_transform(mount, _gun_angles[index], Vector2.ONE)
		draw_rect(
			Rect2(-0.13, 0.0, 0.26, 0.82),
			Color(0.45, 0.20, 0.62, gun_alpha).lerp(Color(1, 1, 1, gun_alpha), flash)
		)
		draw_rect(Rect2(-0.06, 0.10, 0.12, 0.6), Color(0.9, 0.5, 0.4, gun_alpha))
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	var core_alpha := clampf(_current_core_glow(), 0.0, 1.0) * death_alpha
	var core_radius := 0.34 + 0.22 * core_alpha
	draw_circle(Vector2(0.0, -0.15 + _bob), core_radius, Color(1.0, 0.55, 0.42, 0.55 * core_alpha))
	draw_circle(Vector2(0.0, -0.15 + _bob), 0.16, Color(1.0, 0.95, 0.75, core_alpha))



func _art_slot() -> String:
	if _pattern != null and not _pattern.prefab.is_empty():
		return _pattern.prefab
	return "Boss-37001"


func _draw_health_bar() -> void:
	if max_hp > 0.0:
		var ratio := clampf(current_hp / max_hp, 0.0, 1.0)
		draw_rect(Rect2(-1.1, -1.45, 2.2, 0.16), Color(0.06, 0.05, 0.1, 0.9))
		draw_rect(Rect2(-1.08, -1.43, 2.16 * ratio, 0.12), Color(1.0, 0.42, 0.34, 0.95))
