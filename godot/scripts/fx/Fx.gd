extends Node
## Fx.gd — "game feel": rung màn hình, loé sáng, hitstop/slow-mo, popup điểm,
## particle burst, coin burst. Tất cả theo delta-time, không await/sleep.

signal slowmo_finished

var world: Node2D = null            # container bị rung
var flash_rect: ColorRect = null    # phủ toàn màn
var _shake_amp := 0.0
var _shake_dur := 0.0
var _shake_t := 0.0
var _flash_a := 0.0
var _flash_dur := 0.0
var _flash_t := 0.0
var _slowmo_scale := 1.0
var _slowmo_left := 0.0
var _popups: Array[Node] = []
var _popup_layer: CanvasLayer
var _particles: Array[CPUParticles2D] = []

func _ready() -> void:
	_popup_layer = CanvasLayer.new()
	_popup_layer.layer = 60
	add_child(_popup_layer)

func _process(delta: float) -> void:
	# slow-mo đếm bằng GIÂY THẬT (delta đang bị scale)
	if _slowmo_left > 0.0:
		var real := delta / maxf(Engine.time_scale, 0.0001)
		_slowmo_left -= real
		if _slowmo_left <= 0.0:
			Engine.time_scale = 1.0
			slowmo_finished.emit()
	# rung
	if _shake_t < _shake_dur and world != null:
		_shake_t += delta
		var k := maxf(0.0, 1.0 - _shake_t / _shake_dur)
		var a := _shake_amp * k
		world.position = Vector2(randf_range(-a, a), randf_range(-a, a))
	elif world != null and world.position != Vector2.ZERO:
		world.position = Vector2.ZERO
	# loé
	if _flash_t < _flash_dur and flash_rect != null:
		_flash_t += delta
		flash_rect.modulate.a = _flash_a * maxf(0.0, 1.0 - _flash_t / _flash_dur)

func shake(amp: float, dur: float) -> void:
	if amp >= _shake_amp or _shake_t >= _shake_dur:
		_shake_amp = amp
		_shake_dur = dur
		_shake_t = 0.0

func flash(color: Color, alpha: float, dur: float) -> void:
	if flash_rect == null:
		return
	flash_rect.color = color
	flash_rect.modulate.a = alpha
	_flash_a = alpha
	_flash_dur = dur
	_flash_t = 0.0

func slow_mo(scale: float, dur_real: float) -> void:
	Engine.time_scale = scale
	_slowmo_scale = scale
	_slowmo_left = dur_real

## Dừng cứng 1 nhịp khi boss đổi pha / trúng bom (hitstop).
func hitstop(dur_real: float) -> void:
	slow_mo(0.05, dur_real)

func popup(pos: Vector2, text: String, color: Color) -> void:
	if _popups.size() > 24:
		return
	var l := Label.new()
	l.text = text
	l.add_theme_color_override("font_color", color)
	l.add_theme_font_size_override("font_size", 30)
	l.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.8))
	l.add_theme_constant_override("shadow_offset_y", 3)
	l.position = pos
	_popup_layer.add_child(l)
	_popups.append(l)
	var tween := create_tween()
	tween.set_parallel(true)
	tween.tween_property(l, "position:y", pos.y - 90.0, 0.8)
	tween.tween_property(l, "modulate:a", 0.0, 0.8)
	tween.chain().tween_callback(l.queue_free)
	tween.chain().tween_callback(_popups.erase.bind(l))

func burst(pos: Vector2, color: Color, count: int, spread := 240.0) -> void:
	var p := _get_particle()
	if p == null:
		return
	p.position = pos
	p.color = color
	p.amount = count
	p.initial_velocity_min = spread * 0.3
	p.initial_velocity_max = spread
	p.lifetime = 0.6
	p.one_shot = true
	p.emitting = true
	p.restart()

func _get_particle() -> CPUParticles2D:
	for p in _particles:
		if not p.emitting:
			return p
	if _particles.size() >= 16:
		return null
	var p := CPUParticles2D.new()
	p.explosiveness = 1.0
	p.gravity = Vector2(0, 60)
	p.scale_amount_min = 2.0
	p.scale_amount_max = 5.0
	p.spread = 180.0
	add_child(p)
	_particles.append(p)
	return p
