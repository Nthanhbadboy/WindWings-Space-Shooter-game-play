extends Control

## Main menu of the launch slice.

const SettingsPanelScript = preload("res://scripts/settings_panel.gd")

var _settings: SliceSettingsPanel


func _ready() -> void:
	Session.start_music()
	_build()
	var variant := Session.variant
	if variant != null:
		for line: Variant in variant.report_lines():
			print(str(line))
	print(
		"SLICE_MENU_READY stars=%d variant=%s"
		% [Session.star_total_for_display(), Session.variant_label()]
	)


func _art_source_label() -> String:
	if Session.variant == null:
		return "A placeholder"
	var mode := "layered" if Session.variant.is_layered() else "whole image"
	if Session.variant.is_placeholder():
		return "%s build, placeholder" % mode
	return "%s build, %s" % [mode, Session.variant.art_package_commit]


func _build() -> void:
	UIKit.background(self)
	if Session.art != null and Session.art.has_art("UI-MENU-FRAME"):
		var frame := TextureRect.new()
		frame.texture = Session.art.texture_for("UI-MENU-FRAME")
		frame.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		frame.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
		frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
		frame.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		add_child(frame)
	var margin := UIKit.full_margin(self, 28)
	var center := CenterContainer.new()
	margin.add_child(center)

	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation", 16)
	column.custom_minimum_size = Vector2(360, 0)
	center.add_child(column)

	column.add_child(UIKit.title("WINDWINGS", 46))
	column.add_child(UIKit.body("SPACE SHOOTER · LAUNCH SLICE", 16, UIKit.ACCENT))
	column.add_child(
		UIKit.body(
			"Vertical slice: 5 real campaign waves + boss, portrait layout on any window",
			13
		)
	)
	column.add_child(UIKit.spacer(8))
	column.add_child(
		UIKit.body(
			"%s · %s art" % [Session.variant_label(), _art_source_label()],
			12,
			UIKit.ACCENT
		)
	)
	if not Session.modifier_tag().is_empty():
		column.add_child(
			UIKit.body("%s MODE · hull takes no damage" % Session.modifier_tag(), 12, UIKit.ACCENT)
		)
	column.add_child(UIKit.body("BEST STARS · STAGE 1", 13))
	column.add_child(UIKit.star_row(Session.best_stars(), 3, 30))
	column.add_child(UIKit.body("TOTAL STARS  %d" % Session.star_total_for_display(), 14, UIKit.INK))
	column.add_child(UIKit.spacer(10))

	var play := UIKit.button("LAUNCH", 64)
	play.pressed.connect(_on_play)
	column.add_child(play)

	var settings := UIKit.button("SETTINGS", 56)
	settings.pressed.connect(_on_settings)
	column.add_child(settings)

	var quit := UIKit.button("QUIT", 48)
	quit.pressed.connect(_on_quit)
	column.add_child(quit)

	column.add_child(UIKit.spacer(12))
	column.add_child(
		UIKit.body("Drag with the mouse or use the arrow keys · auto-fire · P / Esc pauses", 12)
	)
	column.add_child(
		UIKit.body(
			"Placeholder art and placeholder tones are generated in-project; no original asset is shipped.",
			11
		)
	)

	_settings = SettingsPanelScript.new()
	add_child(_settings)


func _on_play() -> void:
	Session.play_sfx("click")
	get_tree().change_scene_to_file("res://scenes/ship_select.tscn")


func _on_settings() -> void:
	Session.play_sfx("click")
	_settings.open()


func _on_quit() -> void:
	get_tree().quit()
