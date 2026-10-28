class_name FXBurst
extends Node2D

## Short-lived hit / explosion effect. Uses the contract slot when art exists and
## a vector ring otherwise, so gameplay never depends on art being present.

var kind := "hit"
var lifetime := 0.28
var radius := 0.5
var _age := 0.0
var _tint := Color.WHITE
var _size_multiplier := 1.0


static func spawn(parent: Node, fx_kind: String, at: Vector2, size_multiplier := 1.0) -> FXBurst:
	if parent == null or not parent.is_inside_tree():
		return null
	var burst := FXBurst.new()
	burst.kind = fx_kind
	burst.position = at
	if fx_kind == "explosion":
		burst.lifetime = 0.42
	burst.radius = (0.55 if fx_kind == "hit" else 1.0) * size_multiplier
	burst.lifetime *= clampf(size_multiplier, 0.5, 2.5)
	burst._size_multiplier = size_multiplier
	parent.add_child(burst)
	return burst


func _ready() -> void:
	z_index = 6
	queue_redraw()


func _process(delta: float) -> void:
	_age += delta
	if _age >= lifetime:
		queue_free()
		return
	queue_redraw()


func _draw() -> void:
	var progress := clampf(_age / maxf(lifetime, 0.001), 0.0, 1.0)
	var alpha := 1.0 - progress
	var slot_id := "FX-HIT" if kind == "hit" else "FX-EXPLOSION"
	var slot_size := Vector2.ZERO
	if Session.art != null and not is_equal_approx(_size_multiplier, 1.0):
		slot_size = Session.art.display_size(slot_id) * _size_multiplier
	if Session.art != null and Session.art.draw_slot(
		self, slot_id, Vector2.ZERO, slot_size, Color(_tint.r, _tint.g, _tint.b, alpha)
	):
		return
	var color := (
		Color(0.55, 0.95, 1.0, alpha)
		if kind == "hit"
		else Color(1.0, 0.72, 0.32, alpha)
	)
	draw_arc(Vector2.ZERO, radius * (0.35 + 0.85 * progress), 0.0, TAU, 24, color, 0.06, true)
	if kind == "explosion":
		draw_arc(
			Vector2.ZERO,
			radius * (0.15 + 0.55 * progress),
			0.0,
			TAU,
			18,
			Color(color.r, color.g, color.b, alpha * 0.6),
			0.05,
			true
		)
