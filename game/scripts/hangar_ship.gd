class_name HangarShip
extends Node2D

## Hangar idle animation: the ship floats up and down, its shadow breathes
## underneath, the glow layer pulses and the engine flame idles.
##
## Every amplitude/period comes from MotionTuning. The ship art uses the same
## contract slots as the run (PLAYER-<id> + optional -GLOW), so whatever art is
## dropped in shows up in the hangar too.

@export var ship_id := 10001

var _age := 0.0
var _engine: GPUParticles2D
var _engine_core: Polygon2D


func _ready() -> void:
	z_index = 2
	_build_engine()


func set_ship(id: int) -> void:
	ship_id = id
	queue_redraw()


func _build_engine() -> void:
	_engine = GPUParticles2D.new()
	_engine.amount = 20
	_engine.lifetime = 0.5
	_engine.local_coords = false
	_engine.z_index = -1
	_engine.texture = _flame_texture()
	var material := ParticleProcessMaterial.new()
	material.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
	material.emission_sphere_radius = 0.05
	material.direction = Vector3(0.0, 1.0, 0.0)
	material.spread = 12.0
	material.gravity = Vector3.ZERO
	material.initial_velocity_min = 1.0
	material.initial_velocity_max = 2.2
	# Same pixel-vs-world rule as the in-run engine: keep the idle plume under a
	# unit so the hangar ship stays visible on top of its own flame.
	material.scale_min = MotionTuning.ENGINE_PARTICLE_SCALE_MIN
	material.scale_max = MotionTuning.ENGINE_PARTICLE_SCALE_MAX
	material.color = Color(0.5, 0.85, 1.0, 0.8)
	var ramp := Gradient.new()
	ramp.set_color(0, Color(0.8, 0.95, 1.0, 0.9))
	ramp.set_color(1, Color(0.25, 0.55, 1.0, 0.0))
	var ramp_texture := GradientTexture1D.new()
	ramp_texture.gradient = ramp
	material.color_ramp = ramp_texture
	_engine.process_material = material
	add_child(_engine)

	_engine_core = Polygon2D.new()
	_engine_core.polygon = PackedVector2Array(
		[Vector2(-0.08, 0.40), Vector2(0.08, 0.40), Vector2(0.0, 0.78)]
	)
	_engine_core.color = Color(0.55, 0.9, 1.0, 0.7)
	_engine_core.z_index = -2
	add_child(_engine_core)


func _flame_texture() -> Texture2D:
	var image := Image.create(16, 16, false, Image.FORMAT_RGBA8)
	for y in range(16):
		for x in range(16):
			var offset := Vector2(float(x) - 7.5, float(y) - 7.5) / 7.5
			var alpha := pow(1.0 - clampf(offset.length(), 0.0, 1.0), 2.0)
			image.set_pixel(x, y, Color(1.0, 1.0, 1.0, alpha))
	return ImageTexture.create_from_image(image)


func _process(delta: float) -> void:
	_age += delta
	var bob := sin(_age * TAU / MotionTuning.HANGAR_BOB_PERIOD) * MotionTuning.HANGAR_BOB_AMPLITUDE
	position.y = bob
	rotation = deg_to_rad(
		sin(_age * TAU / MotionTuning.HANGAR_ROLL_PERIOD) * MotionTuning.HANGAR_ROLL_DEGREES
	)
	if _engine != null:
		_engine.position = Vector2(0.0, 0.42 + bob * 0.15)
		_engine.speed_scale = 0.7 + 0.15 * sin(_age * 3.1)
	if _engine_core != null:
		_engine_core.position = Vector2(0.0, bob * 0.1)
	queue_redraw()


func _draw() -> void:
	var art := Session.art
	var body_slot := "PLAYER-%d" % ship_id
	var glow_slot := "PLAYER-%d-GLOW" % ship_id

	# Shadow: a soft ellipse that shrinks while the ship floats up.
	var lift := clampf(
		0.5 + 0.5 * sin(_age * TAU / MotionTuning.HANGAR_BOB_PERIOD), 0.0, 1.0
	)
	var shadow_scale := lerpf(
		MotionTuning.HANGAR_SHADOW_MAX_SCALE, MotionTuning.HANGAR_SHADOW_MIN_SCALE, lift
	)
	draw_set_transform(Vector2(0.0, 1.45 - position.y * 0.25), 0.0, Vector2.ONE)
	draw_colored_polygon(
		_ellipse(1.05 * shadow_scale, 0.26 * shadow_scale, 28),
		Color(0.02, 0.05, 0.12, 0.45)
	)
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)

	var drew_art := false
	if art != null and art.draw_slot(self, body_slot, Vector2.ZERO):
		drew_art = true
		var pulse := lerpf(
			MotionTuning.HANGAR_GLOW_MIN,
			MotionTuning.HANGAR_GLOW_MAX,
			0.5 + 0.5 * sin(_age * TAU / MotionTuning.HANGAR_GLOW_PERIOD)
		)
		if art.has_art(glow_slot):
			art.draw_slot(self, glow_slot, Vector2.ZERO, Vector2.ZERO, Color(1, 1, 1, pulse))
	if not drew_art:
		_draw_vector_ship(
			lerpf(
				MotionTuning.HANGAR_GLOW_MIN,
				MotionTuning.HANGAR_GLOW_MAX,
				0.5 + 0.5 * sin(_age * TAU / MotionTuning.HANGAR_GLOW_PERIOD)
			)
		)


func _draw_vector_ship(glow: float) -> void:
	# Same silhouette family as the in-run vector ship, drawn brighter here.
	var hull := Color(0.30, 0.88, 1.0)
	draw_colored_polygon(
		PackedVector2Array(
			[
				Vector2(0.0, -0.62),
				Vector2(0.46, 0.30),
				Vector2(0.16, 0.19),
				Vector2(0.0, 0.42),
				Vector2(-0.16, 0.19),
				Vector2(-0.46, 0.30),
			]
		),
		hull
	)
	draw_circle(Vector2(0.0, -0.05), 0.34, Color(0.55, 0.95, 1.0, 0.18 * glow))
	draw_circle(Vector2(0.0, -0.05), 0.18, Color(0.75, 0.98, 1.0, 0.30 * glow))
	draw_colored_polygon(
		PackedVector2Array([Vector2(0.0, -0.43), Vector2(0.105, 0.10), Vector2(-0.105, 0.10)]),
		Color(0.90, 0.98, 1.0)
	)


func _ellipse(radius_x: float, radius_y: float, segments: int) -> PackedVector2Array:
	var points := PackedVector2Array()
	for index in range(segments):
		var angle := TAU * float(index) / float(segments)
		points.append(Vector2(cos(angle) * radius_x, sin(angle) * radius_y))
	return points
