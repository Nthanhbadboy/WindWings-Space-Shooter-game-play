class_name GameHUD
extends Control

signal pause_requested
signal retry_requested

var _health_bar: ProgressBar
var _health_label: Label
var _wave_label: Label
var _score_label: Label
var _action_label: Label
var _pause_button: Button
var _overlay: ColorRect
var _overlay_title: Label
var _retry_button: Button
var _paused := false


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_build_interface()


func update_status(data: Dictionary) -> void:
	var hp := float(data.get("hp", 0.0))
	var max_hp := maxf(float(data.get("max_hp", 1.0)), 1.0)
	_health_bar.max_value = max_hp
	_health_bar.value = hp
	_health_label.text = "HULL  %d / %d" % [roundi(hp), roundi(max_hp)]
	_wave_label.text = str(data.get("wave", "TRAINING"))
	_score_label.text = (
		"COINS  %d   ·   TARGET HITS  %d" % [int(data.get("coins", 0)), int(data.get("hits", 0))]
	)
	_action_label.text = (
		"NEAR MISSES  %d   ·   SHOTS  %d"
		% [int(data.get("near_misses", 0)), int(data.get("shots", 0))]
	)


func set_paused(paused: bool) -> void:
	_paused = paused
	_pause_button.text = "RESUME" if paused else "PAUSE"
	_overlay.visible = paused
	_retry_button.visible = false
	_overlay_title.text = "PAUSED" if paused else ""


func show_game_over() -> void:
	_overlay.visible = true
	_overlay_title.text = "SIGNAL LOST"
	_retry_button.visible = true
	_pause_button.disabled = true


func _build_interface() -> void:
	var margins := MarginContainer.new()
	margins.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	margins.add_theme_constant_override("margin_left", 22)
	margins.add_theme_constant_override("margin_top", 22)
	margins.add_theme_constant_override("margin_right", 22)
	margins.add_theme_constant_override("margin_bottom", 22)
	add_child(margins)

	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation", 12)
	margins.add_child(column)

	var top_panel := PanelContainer.new()
	top_panel.add_theme_stylebox_override("panel", _panel_style(Color(0.025, 0.052, 0.12, 0.90)))
	column.add_child(top_panel)

	var top_stack := VBoxContainer.new()
	top_stack.add_theme_constant_override("separation", 7)
	top_panel.add_child(top_stack)

	var title_row := HBoxContainer.new()
	title_row.add_theme_constant_override("separation", 10)
	top_stack.add_child(title_row)

	var title := Label.new()
	title.text = "STARFALL  /  TRAINING"
	title.add_theme_font_size_override("font_size", 23)
	title.add_theme_color_override("font_color", Color(0.61, 0.91, 1.0))
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	title_row.add_child(title)

	_pause_button = Button.new()
	_pause_button.text = "PAUSE"
	_pause_button.custom_minimum_size = Vector2(118, 52)
	_pause_button.focus_mode = Control.FOCUS_NONE
	_pause_button.pressed.connect(_on_pause_pressed)
	title_row.add_child(_pause_button)

	_wave_label = Label.new()
	_wave_label.text = "WAVE 00  ·  TARGET RANGE"
	_wave_label.add_theme_font_size_override("font_size", 16)
	_wave_label.add_theme_color_override("font_color", Color(0.77, 0.85, 0.98))
	top_stack.add_child(_wave_label)

	_health_label = Label.new()
	_health_label.text = "HULL  2500 / 2500"
	_health_label.add_theme_font_size_override("font_size", 15)
	_health_label.add_theme_color_override("font_color", Color(0.82, 0.94, 1.0))
	top_stack.add_child(_health_label)

	_health_bar = ProgressBar.new()
	_health_bar.custom_minimum_size = Vector2(0, 16)
	_health_bar.max_value = 2500.0
	_health_bar.value = 2500.0
	_health_bar.show_percentage = false
	_health_bar.add_theme_stylebox_override("background", _bar_style(Color(0.08, 0.12, 0.22, 0.95)))
	_health_bar.add_theme_stylebox_override("fill", _bar_style(Color(0.17, 0.83, 0.91, 0.98)))
	top_stack.add_child(_health_bar)

	_score_label = Label.new()
	_score_label.text = "COINS  0   ·   TARGET HITS  0"
	_score_label.add_theme_font_size_override("font_size", 15)
	_score_label.add_theme_color_override("font_color", Color(1.0, 0.79, 0.43))
	top_stack.add_child(_score_label)

	var spacer := Control.new()
	spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
	column.add_child(spacer)

	var footer := PanelContainer.new()
	footer.add_theme_stylebox_override("panel", _panel_style(Color(0.025, 0.052, 0.12, 0.82)))
	column.add_child(footer)

	var footer_stack := VBoxContainer.new()
	footer_stack.add_theme_constant_override("separation", 5)
	footer.add_child(footer_stack)

	_action_label = Label.new()
	_action_label.text = "NEAR MISSES  0   ·   SHOTS  0"
	_action_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_action_label.add_theme_font_size_override("font_size", 15)
	_action_label.add_theme_color_override("font_color", Color(0.60, 0.88, 1.0))
	footer_stack.add_child(_action_label)

	var hint := Label.new()
	hint.text = "DRAG TO FLY  ·  AUTO-FIRE  ·  ARROWS ALSO WORK"
	hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hint.add_theme_font_size_override("font_size", 13)
	hint.add_theme_color_override("font_color", Color(0.69, 0.77, 0.93))
	footer_stack.add_child(hint)

	_overlay = ColorRect.new()
	_overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_overlay.color = Color(0.006, 0.015, 0.045, 0.76)
	_overlay.visible = false
	_overlay.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(_overlay)

	var overlay_panel := PanelContainer.new()
	overlay_panel.anchor_left = 0.12
	overlay_panel.anchor_top = 0.40
	overlay_panel.anchor_right = 0.88
	overlay_panel.anchor_bottom = 0.60
	overlay_panel.add_theme_stylebox_override(
		"panel", _panel_style(Color(0.035, 0.075, 0.15, 0.98))
	)
	_overlay.add_child(overlay_panel)

	var overlay_stack := VBoxContainer.new()
	overlay_stack.alignment = BoxContainer.ALIGNMENT_CENTER
	overlay_stack.add_theme_constant_override("separation", 12)
	overlay_panel.add_child(overlay_stack)

	_overlay_title = Label.new()
	_overlay_title.text = "PAUSED"
	_overlay_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_overlay_title.add_theme_font_size_override("font_size", 30)
	_overlay_title.add_theme_color_override("font_color", Color(0.68, 0.93, 1.0))
	overlay_stack.add_child(_overlay_title)

	_retry_button = Button.new()
	_retry_button.text = "RESTART RUN"
	_retry_button.custom_minimum_size = Vector2(0, 54)
	_retry_button.focus_mode = Control.FOCUS_NONE
	_retry_button.visible = false
	_retry_button.pressed.connect(func() -> void: retry_requested.emit())
	overlay_stack.add_child(_retry_button)


func _panel_style(background: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = background
	style.border_color = Color(0.26, 0.73, 0.92, 0.32)
	style.set_border_width_all(1)
	style.set_corner_radius_all(15)
	style.content_margin_left = 14.0
	style.content_margin_top = 12.0
	style.content_margin_right = 14.0
	style.content_margin_bottom = 12.0
	return style


func _bar_style(background: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = background
	style.set_corner_radius_all(6)
	return style


func _on_pause_pressed() -> void:
	pause_requested.emit()
