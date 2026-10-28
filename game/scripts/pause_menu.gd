class_name SlicePauseMenu
extends Control

signal resume_requested
signal restart_requested
signal quit_requested

const SettingsPanelScript = preload("res://scripts/settings_panel.gd")

var _settings: SliceSettingsPanel


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_build()
	visible = false


func _build() -> void:
	var dim := ColorRect.new()
	dim.color = Color(0.0, 0.0, 0.0, 0.75)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)

	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(center)

	var panel := PanelContainer.new()
	panel.custom_minimum_size = Vector2(340, 0)
	center.add_child(panel)

	var margin := MarginContainer.new()
	for side in ["left", "top", "right", "bottom"]:
		margin.add_theme_constant_override("margin_" + side, 20)
	panel.add_child(margin)

	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation", 12)
	margin.add_child(column)
	column.add_child(UIKit.title("PAUSED", 30))
	column.add_child(UIKit.body("P / Esc resumes · music keeps playing, SFX is paused", 11))

	var resume := UIKit.button("RESUME", 54)
	resume.pressed.connect(_on_resume)
	column.add_child(resume)

	var settings := UIKit.button("AUDIO SETTINGS", 50)
	settings.pressed.connect(_on_settings)
	column.add_child(settings)

	var restart := UIKit.button("RESTART RUN", 50)
	restart.pressed.connect(_on_restart)
	column.add_child(restart)

	var quit := UIKit.button("QUIT TO MENU", 50)
	quit.pressed.connect(_on_quit)
	column.add_child(quit)

	_settings = SettingsPanelScript.new()
	add_child(_settings)


func open() -> void:
	visible = true


func close() -> void:
	if _settings != null:
		_settings.visible = false
	visible = false


func _on_resume() -> void:
	Session.play_sfx("click")
	resume_requested.emit()


func _on_settings() -> void:
	Session.play_sfx("click")
	_settings.open()


func _on_restart() -> void:
	restart_requested.emit()


func _on_quit() -> void:
	quit_requested.emit()
