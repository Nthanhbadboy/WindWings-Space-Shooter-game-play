class_name UIKit
extends RefCounted

## Small builder helpers so every screen shares one look without a scene theme.

const BG := Color(0.012, 0.021, 0.062)
const INK := Color(0.86, 0.94, 1.0)
const MUTED := Color(0.55, 0.68, 0.85)
const ACCENT := Color(0.30, 0.88, 1.0)
const GOLD := Color(1.0, 0.78, 0.32)
const DANGER := Color(1.0, 0.42, 0.34)


static func background(parent: Control) -> ColorRect:
	var rect := ColorRect.new()
	rect.color = BG
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	parent.add_child(rect)
	return rect


static func full_margin(parent: Control, margin_px: int) -> MarginContainer:
	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for side in ["left", "top", "right", "bottom"]:
		margin.add_theme_constant_override("margin_" + side, margin_px)
	parent.add_child(margin)
	return margin


static func title(text: String, size := 42) -> Label:
	var label := Label.new()
	label.text = text
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.add_theme_font_size_override("font_size", size)
	label.add_theme_color_override("font_color", INK)
	return label


static func body(text: String, size := 15, color := MUTED) -> Label:
	var label := Label.new()
	label.text = text
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_font_size_override("font_size", size)
	label.add_theme_color_override("font_color", color)
	return label


static func spacer(height: int) -> Control:
	var control := Control.new()
	control.custom_minimum_size = Vector2(0, height)
	return control


static func button(text: String, height := 56, width := 320) -> Button:
	var button_node := Button.new()
	button_node.text = text
	button_node.custom_minimum_size = Vector2(width, height)
	button_node.add_theme_font_size_override("font_size", 20)
	return button_node


static func star_row(stars: int, maximum := 3, size := 30) -> HBoxContainer:
	var row := HBoxContainer.new()
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override("separation", 8)
	for index in range(maximum):
		var label := Label.new()
		label.text = "★" if index < stars else "☆"
		label.add_theme_font_size_override("font_size", size)
		label.add_theme_color_override("font_color", GOLD if index < stars else MUTED)
		row.add_child(label)
	return row
