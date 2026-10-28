class_name Player
extends Area2D

signal shot_requested(origin: Vector2, damage: float)
signal health_changed(current: float, maximum: float)
signal damage_taken(amount: float, remaining: float)
signal impact(strength: float)
signal died

const CONFIRMED_BASE_HP := 2500.0
const CONFIRMED_HIT_INVULNERABILITY_SECONDS := 3.0

@export var move_speed := 9.0
@export var smoothing_rate := 14.0

var ship_id := 10003
var current_health := CONFIRMED_BASE_HP
var maximum_health := CONFIRMED_BASE_HP
var shot_damage := 0.0
var fire_period_seconds := 0.24
var movement_bounds := Rect2(-4.8, -8.4, 9.6, 16.5)

var _dragging := false
var _move_target := Vector2.ZERO
var _fire_elapsed := 0.0
var _invulnerability_elapsed := 0.0
var _is_dead := false

# Animation state. All rhythms live in MotionTuning; this node only integrates them.
var _last_x := 0.0
var _velocity_x := 0.0
var _velocity_y := 0.0
var _bank_angle := 0.0
var _engine_length := MotionTuning.ENGINE_IDLE_LENGTH
var _hit_flash_elapsed := 999.0
var _age := 0.0
var _engine: GPUParticles2D
var _engine_core: Polygon2D
var _hull_fx: GPUParticles2D


func _ready() -> void:
	add_to_group("player")
	collision_layer = 1
	collision_mask = 28
	area_entered.connect(_on_area_entered)
	_move_target = global_position
	_last_x = global_position.x
	_build_engine()
	health_changed.emit(current_health, maximum_health)
	queue_redraw()


## Engine flame: GPUParticles2D (required by the animation brief) plus a vector
## core so the ship still reads as "thrusting" if particles are unavailable.
func _build_engine() -> void:
	_engine = GPUParticles2D.new()
	_engine.amount = 24
	_engine.lifetime = 0.42
	# Variant C animates one flat image, so its flame must move with the hull
	# instead of trailing behind it in world space.
	_engine.local_coords = _whole_image_mode()
	_engine.position = Vector2(0.0, 0.46)
	_engine.z_index = -1
	_engine.texture = _flame_texture()
	var material := ParticleProcessMaterial.new()
	material.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
	material.emission_sphere_radius = 0.06
	material.direction = Vector3(0.0, 1.0, 0.0)
	material.spread = 9.0
	material.gravity = Vector3.ZERO
	material.initial_velocity_min = 1.6
	material.initial_velocity_max = 3.4
	# A GPUParticles2D texture is drawn at its pixel size in world units, so the
	# 16 px flame needs a scale around 0.05 to become a ~0.8 unit plume instead
	# of a 16 unit sheet covering the screen.
	material.scale_min = MotionTuning.ENGINE_PARTICLE_SCALE_MIN
	material.scale_max = MotionTuning.ENGINE_PARTICLE_SCALE_MAX
	material.color = Color(0.45, 0.82, 1.0, 0.85)
	var ramp := Gradient.new()
	ramp.set_color(0, Color(0.85, 0.97, 1.0, 0.95))
	ramp.set_color(1, Color(0.25, 0.55, 1.0, 0.0))
	var ramp_texture := GradientTexture1D.new()
	ramp_texture.gradient = ramp
	material.color_ramp = ramp_texture
	_engine.process_material = material
	add_child(_engine)

	_engine_core = Polygon2D.new()
	_engine_core.polygon = PackedVector2Array(
		[
			Vector2(-0.09, 0.42),
			Vector2(0.09, 0.42),
			Vector2(0.0, 0.92),
		]
	)
	_engine_core.color = Color(0.55, 0.9, 1.0, 0.75)
	_engine_core.z_index = -2
	add_child(_engine_core)
	if _whole_image_mode():
		_build_hull_overlay()


## Variant C cannot separate the hull from its glow layer, so the animated
## "shine" is emitted as particles on top of the whole image instead.
func _build_hull_overlay() -> void:
	_hull_fx = GPUParticles2D.new()
	_hull_fx.amount = 18
	_hull_fx.lifetime = 0.55
	_hull_fx.local_coords = true
	_hull_fx.position = Vector2.ZERO
	# Behind the flat image, never over it: the C package already has its flame
	# baked in, so an overlay on top would smear the sprite.
	_hull_fx.z_index = -2
	_hull_fx.texture = _flame_texture()
	var material := ParticleProcessMaterial.new()
	material.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
	material.emission_sphere_radius = 0.34
	material.direction = Vector3(0.0, -1.0, 0.0)
	material.spread = 180.0
	material.gravity = Vector3.ZERO
	material.initial_velocity_min = 0.12
	material.initial_velocity_max = 0.42
	material.scale_min = MotionTuning.HULL_SPARK_SCALE_MIN
	material.scale_max = MotionTuning.HULL_SPARK_SCALE_MAX
	material.color = Color(1.0, 0.86, 0.55, 0.55)
	var ramp := Gradient.new()
	ramp.set_color(0, Color(1.0, 0.95, 0.75, 0.7))
	ramp.set_color(1, Color(0.4, 0.7, 1.0, 0.0))
	var ramp_texture := GradientTexture1D.new()
	ramp_texture.gradient = ramp
	material.color_ramp = ramp_texture
	_hull_fx.process_material = material
	add_child(_hull_fx)


func _whole_image_mode() -> bool:
	return Session.variant != null and Session.variant.is_whole()


func _flame_texture() -> Texture2D:
	var image := Image.create(16, 16, false, Image.FORMAT_RGBA8)
	for y in range(16):
		for x in range(16):
			var offset := Vector2(float(x) - 7.5, float(y) - 7.5) / 7.5
			var distance := clampf(offset.length(), 0.0, 1.0)
			var alpha := pow(1.0 - distance, 2.0)
			image.set_pixel(x, y, Color(1.0, 1.0, 1.0, alpha))
	return ImageTexture.create_from_image(image)


func configure_ship(ship: int) -> void:
	ship_id = ship
	queue_redraw()


func flash() -> void:
	_hit_flash_elapsed = 0.0
	queue_redraw()


func banking_angle() -> float:
	return _bank_angle


func engine_length() -> float:
	return _engine_length


func configure_weapon(damage: float, fire_period: float) -> void:
	shot_damage = maxf(damage, 0.0)
	fire_period_seconds = maxf(fire_period, 0.05)


func configure_health(base_hp: float) -> void:
	maximum_health = maxf(base_hp, 1.0)
	current_health = maximum_health
	health_changed.emit(current_health, maximum_health)
	queue_redraw()


func set_movement_bounds(bounds: Rect2) -> void:
	movement_bounds = bounds
	global_position = _clamp_to_bounds(global_position)
	_last_x = global_position.x
	_move_target = _clamp_to_bounds(_move_target)


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventScreenTouch:
		if event.pressed:
			_dragging = true
			_set_drag_target(event.position)
		else:
			_dragging = false
	elif event is InputEventScreenDrag:
		_set_drag_target(event.position)
	elif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		_dragging = event.pressed
		if event.pressed:
			_set_drag_target(event.position)
	elif event is InputEventMouseMotion and (event.button_mask & MOUSE_BUTTON_MASK_LEFT) != 0:
		_set_drag_target(event.position)


func _physics_process(delta: float) -> void:
	var keyboard_direction := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	if keyboard_direction.length_squared() > 0.0:
		_dragging = false
		global_position += keyboard_direction * move_speed * delta
	elif _dragging:
		var blend := 1.0 - exp(-smoothing_rate * delta)
		global_position = global_position.lerp(_move_target, blend)
	global_position = _clamp_to_bounds(global_position)
	var delta_safe := maxf(delta, 0.0001)
	_velocity_x = (global_position.x - _last_x) / delta_safe
	_last_x = global_position.x


func _process(delta: float) -> void:
	_age += delta
	_update_animation(delta)
	if _invulnerability_elapsed > 0.0:
		_invulnerability_elapsed = maxf(_invulnerability_elapsed - delta, 0.0)
		queue_redraw()
	if _is_dead:
		return
	_fire_elapsed += delta
	if _fire_elapsed >= fire_period_seconds:
		# Do not backfill missed shots after a stall; one input tick produces at most one shot.
		_fire_elapsed = fposmod(_fire_elapsed, fire_period_seconds)
		shot_requested.emit(global_position + Vector2(0.0, -0.58), shot_damage)


func _update_animation(delta: float) -> void:
	var previous_y := _velocity_y
	_velocity_y = _velocity_y + (0.0 - _velocity_y) * clampf(delta * 6.0, 0.0, 1.0)
	if previous_y == 0.0:
		_velocity_y = 0.0
	var target_bank := MotionTuning.bank_angle(_velocity_x)
	_bank_angle = lerpf(
		_bank_angle, target_bank, clampf(delta * MotionTuning.BANK_RESPONSE, 0.0, 1.0)
	)
	rotation = _bank_angle
	var vertical_speed := absf(_velocity_y) + absf(_velocity_x) * 0.25
	var target_length := MotionTuning.engine_length(vertical_speed, _dragging)
	_engine_length = lerpf(
		_engine_length, target_length, clampf(delta * MotionTuning.ENGINE_RESPONSE, 0.0, 1.0)
	)
	if _engine != null:
		_engine.speed_scale = clampf(_engine_length / MotionTuning.ENGINE_IDLE_LENGTH, 0.4, 2.4)
		_engine.amount_ratio = clampf(_engine_length / MotionTuning.ENGINE_FAST_LENGTH, 0.25, 1.0)
		_engine.position = Vector2(0.0, 0.46 + 0.4 * _engine_length * 0.35)
	if _engine_core != null:
		_engine_core.scale = Vector2(1.0, _engine_length / MotionTuning.ENGINE_IDLE_LENGTH)
	if _hull_fx != null:
		_hull_fx.amount_ratio = clampf(_engine_length / MotionTuning.ENGINE_FAST_LENGTH, 0.3, 1.0)
	if _hit_flash_elapsed < MotionTuning.FLASH_SECONDS:
		_hit_flash_elapsed += delta
		queue_redraw()


func take_damage(amount: float) -> bool:
	if _is_dead or _invulnerability_elapsed > 0.0:
		return false
	var applied := maxf(amount, 0.0)
	current_health = maxf(current_health - applied, 0.0)
	flash()
	impact.emit(clampf(applied / maxf(maximum_health, 1.0), 0.05, 1.0))
	FXBurst.spawn(get_parent(), "hit", global_position)
	_invulnerability_elapsed = CONFIRMED_HIT_INVULNERABILITY_SECONDS
	damage_taken.emit(applied, current_health)
	health_changed.emit(current_health, maximum_health)
	queue_redraw()
	if current_health <= 0.0:
		_is_dead = true
		died.emit()
	return true


func _set_drag_target(screen_position: Vector2) -> void:
	var world_position := get_viewport().get_canvas_transform().affine_inverse() * screen_position
	_move_target = _clamp_to_bounds(world_position)


func _clamp_to_bounds(point: Vector2) -> Vector2:
	return Vector2(
		clampf(point.x, movement_bounds.position.x, movement_bounds.end.x),
		clampf(point.y, movement_bounds.position.y, movement_bounds.end.y)
	)


func _on_area_entered(area: Area2D) -> void:
	if area.is_in_group("enemies"):
		var contact_damage := float(area.get("contact_damage"))
		if contact_damage > 0.0:
			take_damage(contact_damage)


func _layered_mode() -> bool:
	return not _whole_image_mode()


func _draw() -> void:
	var art_tint := Color(1.0, 1.0, 1.0, 1.0)
	if _invulnerability_elapsed > 0.0 and int(Time.get_ticks_msec() / 90) % 2 == 0:
		art_tint.a = 0.5
	var flash_strength := MotionTuning.flash_alpha(_hit_flash_elapsed) / MotionTuning.FLASH_ALPHA
	var body_slot := "PLAYER-%d" % ship_id
	var glow_slot := "PLAYER-%d-GLOW" % ship_id
	var nozzle_slot := "PLAYER-%d-NOZZLE" % ship_id
	# The optional nozzle glow sits behind the hull, so it reads as engine light
	# escaping from under the ship rather than a wash over the sprite.
	if _layered_mode() and Session.art != null and Session.art.has_art(nozzle_slot):
		var thrust := clampf(
			(_engine_length - MotionTuning.ENGINE_IDLE_LENGTH)
			/ maxf(MotionTuning.ENGINE_FAST_LENGTH - MotionTuning.ENGINE_IDLE_LENGTH, 0.001),
			0.0,
			1.0,
		)
		Session.art.draw_slot(
			self,
			nozzle_slot,
			Vector2.ZERO,
			Vector2.ZERO,
			Color(1.0, 1.0, 1.0, (0.45 + 0.55 * thrust) * art_tint.a)
		)
	if Session.art != null and Session.art.draw_slot(self, body_slot, Vector2.ZERO, Vector2.ZERO, art_tint):
		# Sub-layer: the glow sheet is optional and pulses on its own rhythm.
		# Variant C ships one flat image, so it must not switch to a glow layer
		# even if a stray file shows up in its folder.
		if _layered_mode() and Session.art.has_art(glow_slot):
			var pulse := lerpf(
				MotionTuning.HANGAR_GLOW_MIN,
				MotionTuning.HANGAR_GLOW_MAX,
				0.5 + 0.5 * sin(_age * TAU / MotionTuning.HANGAR_GLOW_PERIOD)
			)
			Session.art.draw_slot(
				self,
				glow_slot,
				Vector2.ZERO,
				Vector2.ZERO,
				Color(1.0, 1.0, 1.0, pulse * art_tint.a)
			)
		if flash_strength > 0.0:
			Session.art.draw_flash(self, body_slot, Vector2.ZERO, flash_strength)
		return
	var flicker := 1.0
	if _invulnerability_elapsed > 0.0 and int(Time.get_ticks_msec() / 90) % 2 == 0:
		flicker = 0.42
	# A hit flashes the shape that was hit: lerp the hull toward white instead of
	# painting over it, so the 0.05 s flash still reads as this ship.
	var flash_tint := clampf(flash_strength, 0.0, 1.0) * MotionTuning.FLASH_ALPHA
	var hull := Color(0.30, 0.88, 1.0, flicker).lerp(Color(1, 1, 1, flicker), flash_tint)
	var highlight := Color(0.90, 0.98, 1.0, flicker).lerp(Color(1, 1, 1, flicker), flash_tint)
	var accent := Color(1.0, 0.72, 0.31, flicker)

	# All ship shapes are original vector artwork created in GDScript.
	draw_colored_polygon(
		PackedVector2Array(
			[
				Vector2(0.0, -0.62),
				Vector2(0.46, 0.30),
				Vector2(0.16, 0.19),
				Vector2(0.0, 0.42),
				Vector2(-0.16, 0.19),
				Vector2(-0.46, 0.30)
			]
		),
		hull
	)
	draw_colored_polygon(
		PackedVector2Array([Vector2(0.0, -0.43), Vector2(0.105, 0.10), Vector2(-0.105, 0.10)]),
		highlight
	)
	draw_colored_polygon(
		PackedVector2Array([Vector2(-0.31, 0.25), Vector2(-0.20, 0.57), Vector2(-0.08, 0.32)]),
		accent
	)
	draw_colored_polygon(
		PackedVector2Array([Vector2(0.31, 0.25), Vector2(0.20, 0.57), Vector2(0.08, 0.32)]), accent
	)
	draw_line(
		Vector2(-0.10, 0.50), Vector2(0.0, 0.72), Color(0.28, 0.74, 1.0, flicker * 0.75), 0.075
	)
	draw_line(
		Vector2(0.10, 0.50), Vector2(0.0, 0.72), Color(0.28, 0.74, 1.0, flicker * 0.75), 0.075
	)
