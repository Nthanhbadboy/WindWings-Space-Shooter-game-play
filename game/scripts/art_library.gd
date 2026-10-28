class_name ArtLibrary
extends RefCounted

## Resolves the ART SLOT CONTRACT (res://data/art_slot_contract.json) and hands
## textures to the gameplay nodes.
##
## Contract rules implemented here:
##   - a slot is looked up in res://art/<folder>/<file> first, then user://art/…
##   - a slot with no file returns null, the node keeps drawing its vector shape,
##     and the slot is recorded as a fallback (never a crash)
##   - pivots are the canvas centre; sizes come from the contract display block
##
## The loader is deliberately dependency-free: it works headless, before any
## scene is loaded, and in an exported build.

const CONTRACT_PATH := "res://data/art_slot_contract.json"
const DEFAULT_ROOTS := ["res://art", "user://art"]

var contract: Dictionary = {}
var slots: Dictionary = {}
var slot_order: Array = []
var roots: Array = DEFAULT_ROOTS.duplicate()
var error := ""
var verbose := false

var _textures: Dictionary = {}
var _white_textures: Dictionary = {}
var _resolved: Dictionary = {}
var _missing: Array = []
var _present: Array = []


func _init(contract_path := CONTRACT_PATH, art_roots: Array = []) -> void:
	if not art_roots.is_empty():
		roots = art_roots.duplicate()
	load_contract(contract_path)


func load_contract(contract_path := CONTRACT_PATH) -> bool:
	slots.clear()
	slot_order.clear()
	error = ""
	if not FileAccess.file_exists(contract_path):
		error = "missing art slot contract: %s" % contract_path
		return false
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(contract_path))
	if not parsed is Dictionary:
		error = "art slot contract is not a JSON object"
		return false
	contract = parsed
	for entry_value: Variant in contract.get("slots", []):
		if not entry_value is Dictionary:
			continue
		var entry: Dictionary = entry_value
		var slot_id := str(entry.get("slot", ""))
		if slot_id.is_empty():
			continue
		slots[slot_id] = entry
		slot_order.append(slot_id)
	if slots.is_empty():
		error = "art slot contract lists no slots"
		return false
	return true


func contract_ready() -> bool:
	return error.is_empty() and not slots.is_empty()


func slot_ids() -> Array:
	return slot_order.duplicate()


func slot(slot_id: String) -> Dictionary:
	return slots.get(slot_id, {})


func slot_count() -> int:
	return slot_order.size()


func validate() -> Array:
	var problems: Array = []
	if not contract_ready():
		problems.append(error)
		return problems
	var seen_files := {}
	for slot_id: String in slot_order:
		var entry: Dictionary = slots[slot_id]
		var relative := str(entry.get("file", ""))
		if relative.is_empty():
			problems.append("%s has no file" % slot_id)
			continue
		if not relative.ends_with(".png"):
			problems.append("%s must be a .png" % slot_id)
		if seen_files.has(relative):
			problems.append("%s shares its file with %s" % [slot_id, seen_files[relative]])
		seen_files[relative] = slot_id
		var canvas: Dictionary = entry.get("canvas", {})
		if int(canvas.get("width", 0)) <= 0 or int(canvas.get("height", 0)) <= 0:
			problems.append("%s has an invalid canvas" % slot_id)
		var pivot: Array = entry.get("pivot", [])
		if pivot.size() != 2 or not is_equal_approx(float(pivot[0]), 0.5):
			problems.append("%s must use a centred pivot" % slot_id)
		if not entry.has("display"):
			problems.append("%s has no display rule" % slot_id)
	var required := ["PLAYER-10001", "BG-FIELD", "BULLET-PLAYER", "BULLET-ENEMY", "FX-HIT", "FX-EXPLOSION", "UI-MENU-FRAME"]
	for slot_id: String in required:
		if not slots.has(slot_id):
			problems.append("required slot %s is missing from the contract" % slot_id)
	return problems


func required_slot_ids() -> Array:
	var required: Array = []
	for slot_id: String in slot_order:
		if bool((slots[slot_id] as Dictionary).get("required", false)):
			required.append(slot_id)
	return required


func path_for(slot_id: String) -> String:
	if not slots.has(slot_id):
		return ""
	return "%s/%s" % [roots[0] if not roots.is_empty() else "res://art", str(slots[slot_id].get("file", ""))]


func candidate_paths(slot_id: String) -> Array:
	if not slots.has(slot_id):
		return []
	var relative := str(slots[slot_id].get("file", ""))
	var candidates: Array = []
	for root: String in roots:
		candidates.append("%s/%s" % [root.trim_suffix("/"), relative])
	return candidates


func _load_texture(path: String) -> Texture2D:
	if path.begins_with("res://"):
		if not ResourceLoader.exists(path, "Texture2D"):
			return null
		var resource: Resource = load(path)
		return resource as Texture2D
	if not FileAccess.file_exists(path):
		return null
	var absolute := ProjectSettings.globalize_path(path)
	var image := Image.load_from_file(absolute)
	if image == null:
		return null
	return ImageTexture.create_from_image(image)


func texture_for(slot_id: String) -> Texture2D:
	if _resolved.has(slot_id):
		return _textures.get(slot_id)
	_resolved[slot_id] = true
	_textures[slot_id] = null
	for path: String in candidate_paths(slot_id):
		var texture := _load_texture(path)
		if texture != null:
			_textures[slot_id] = texture
			_present.append(slot_id)
			if verbose:
				print("ART_SLOT %s present %s" % [slot_id, path])
			return texture
	_missing.append(slot_id)
	if verbose:
		print("ART_SLOT %s fallback vector" % slot_id)
	return null


## A white silhouette of the slot texture, used for the 0.05 s hit flash.
func white_texture_for(slot_id: String) -> Texture2D:
	if _white_textures.has(slot_id):
		return _white_textures.get(slot_id)
	var texture := texture_for(slot_id)
	if texture == null:
		return null
	var image := texture.get_image()
	if image == null:
		return null
	var white := image.duplicate() as Image
	if white.is_compressed():
		white.decompress()
	white.convert(Image.FORMAT_RGBA8)
	for y in range(white.get_height()):
		for x in range(white.get_width()):
			var pixel := white.get_pixel(x, y)
			white.set_pixel(x, y, Color(1.0, 1.0, 1.0, pixel.a))
	var result := ImageTexture.create_from_image(white)
	_white_textures[slot_id] = result
	return result


func draw_flash(canvas_item: CanvasItem, slot_id: String, center: Vector2, strength: float) -> bool:
	if strength <= 0.0:
		return false
	var texture := white_texture_for(slot_id)
	if texture == null:
		return false
	var draw_size := display_size(slot_id)
	canvas_item.draw_texture_rect(
		texture, Rect2(center - draw_size * 0.5, draw_size), false, Color(1, 1, 1, clampf(strength, 0.0, 1.0))
	)
	return true


func has_art(slot_id: String) -> bool:
	return texture_for(slot_id) != null


func status(slot_id: String) -> String:
	return "present" if has_art(slot_id) else "fallback"


func _resolve_all() -> void:
	for slot_id: String in slot_order:
		texture_for(slot_id)


func present_ids() -> Array:
	_resolve_all()
	return _present.duplicate()


func missing_ids() -> Array:
	_resolve_all()
	return _missing.duplicate()


func display_size(slot_id: String) -> Vector2:
	var entry: Dictionary = slots.get(slot_id, {})
	var display: Dictionary = entry.get("display", {})
	if display.get("unit") == "screen":
		return Vector2.ZERO
	var width := float(display.get("width", 0.0))
	var height := float(display.get("height", 0.0))
	if width <= 0.0 or height <= 0.0:
		var canvas: Dictionary = entry.get("canvas", {})
		width = float(canvas.get("width", 1))
		height = float(canvas.get("height", 1))
	return Vector2(width, height)


## Draw a slot centred on `center` inside a CanvasItem's _draw(). Returns false
## (and draws nothing) when the slot has no art, so callers can fall back.
func draw_slot(
	canvas_item: CanvasItem,
	slot_id: String,
	center: Vector2,
	size := Vector2.ZERO,
	tint := Color.WHITE,
	additive_hint := false,
	rotation := 0.0
) -> bool:
	var texture := texture_for(slot_id)
	if texture == null:
		return false
	var draw_size := size
	if draw_size == Vector2.ZERO:
		draw_size = display_size(slot_id)
	if draw_size.x <= 0.0 or draw_size.y <= 0.0:
		return false
	# `additive_hint` is accepted so callers can tag glow/flash passes; the
	# compatibility renderer keeps plain alpha blending, which stays readable.
	canvas_item.draw_set_transform(center, rotation, Vector2.ONE)
	canvas_item.draw_texture_rect(texture, Rect2(-draw_size * 0.5, draw_size), false, tint)
	canvas_item.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	return true


## Draw a slot so that its declared pivot lands on `mount`, rotated by `rotation`.
## Used for the boss gun mounts and any other layer with a non-centred pivot.
func draw_slot_pivoted(
	canvas_item: CanvasItem,
	slot_id: String,
	mount: Vector2,
	size := Vector2.ZERO,
	tint := Color.WHITE,
	rotation := 0.0
) -> bool:
	var texture := texture_for(slot_id)
	if texture == null:
		return false
	var draw_size := size
	if draw_size == Vector2.ZERO:
		draw_size = display_size(slot_id)
	if draw_size.x <= 0.0 or draw_size.y <= 0.0:
		return false
	var pivot: Array = slots.get(slot_id, {}).get("pivot", [0.5, 0.5])
	var offset := -Vector2(float(pivot[0]), float(pivot[1])) * draw_size
	canvas_item.draw_set_transform(mount, rotation, Vector2.ONE)
	canvas_item.draw_texture_rect(texture, Rect2(offset, draw_size), false, tint)
	canvas_item.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	return true


## True when every listed slot has art (used for all-or-nothing layer sets).
func all_present(slot_ids: Array) -> bool:
	if slot_ids.is_empty():
		return false
	for slot_id: Variant in slot_ids:
		if not has_art(str(slot_id)):
			return false
	return true


## True when at least one slot of the list has art.
func any_present(slot_ids: Array) -> bool:
	for slot_id: Variant in slot_ids:
		if has_art(str(slot_id)):
			return true
	return false


func pivot_of(slot_id: String) -> Vector2:
	var pivot: Array = slots.get(slot_id, {}).get("pivot", [0.5, 0.5])
	if pivot.size() != 2:
		return Vector2(0.5, 0.5)
	return Vector2(float(pivot[0]), float(pivot[1]))


## Cover-fit a slot into a rect (background / full-screen art).
func draw_cover(canvas_item: CanvasItem, slot_id: String, rect: Rect2, tint := Color.WHITE) -> bool:
	var texture := texture_for(slot_id)
	if texture == null:
		return false
	var texture_size := texture.get_size()
	if texture_size.x <= 0.0 or texture_size.y <= 0.0:
		return false
	var target := rect
	var texture_aspect := texture_size.x / texture_size.y
	var rect_aspect := rect.size.x / rect.size.y
	if texture_aspect > rect_aspect:
		var width := rect.size.y * texture_aspect
		target = Rect2(rect.get_center() - Vector2(width, rect.size.y) * 0.5, Vector2(width, rect.size.y))
	else:
		var height := rect.size.x / texture_aspect
		target = Rect2(rect.get_center() - Vector2(rect.size.x, height) * 0.5, Vector2(rect.size.x, height))
	canvas_item.draw_texture_rect(texture, target, false, tint)
	return true


func report_lines() -> Array:
	var lines: Array = []
	lines.append(
		"ART_CONTRACT slots=%d art_root=%s" % [slot_order.size(), roots[0] if not roots.is_empty() else "?"]
	)
	for slot_id: String in slot_order:
		var entry: Dictionary = slots[slot_id]
		var candidate: String = candidate_paths(slot_id)[0] if not candidate_paths(slot_id).is_empty() else ""
		if has_art(slot_id):
			lines.append("ART_SLOT %s present %s" % [slot_id, candidate])
		else:
			lines.append(
				"ART_SLOT %s fallback vector (%s missing)" % [slot_id, str(entry.get("file", ""))]
			)
	lines.append(summary_line())
	return lines


func summary_line() -> String:
	_resolve_all()
	var present_count := 0
	for slot_id: String in slot_order:
		if has_art(slot_id):
			present_count += 1
	return "ART_SUMMARY total=%d present=%d fallback=%d" % [
		slot_order.size(), present_count, slot_order.size() - present_count
	]
