class_name SliceSettingsPanel
extends Control

## Audio settings driven by datas/audio_rules.json defaults:
## MUTE_AUDIO (int, 0), VolumeSound (float, 0.73), VolumeMusic (float, 0.3).
## Values persist through Session -> SaveStore.

signal closed

var _mute_toggle: CheckButton
var _sound_slider: HSlider
var _music_slider: HSlider
var _sound_value: Label
var _music_value: Label


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_build()
	visible = false


func _build() -> void:
	var dim := ColorRect.new()
	dim.color = Color(0.0, 0.0, 0.0, 0.72)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)

	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(center)

	var panel := PanelContainer.new()
	panel.custom_minimum_size = Vector2(420, 0)
	center.add_child(panel)

	var margin := MarginContainer.new()
	for side in ["left", "top", "right", "bottom"]:
		margin.add_theme_constant_override("margin_" + side, 22)
	panel.add_child(margin)

	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation", 14)
	margin.add_child(column)

	column.add_child(UIKit.title("AUDIO SETTINGS", 26))
	column.add_child(
		UIKit.body(
			"datas/audio_rules.json · MUTE_AUDIO 0 · VolumeSound 0.73 · VolumeMusic 0.3",
			13
		)
	)

	_mute_toggle = CheckButton.new()
	_mute_toggle.text = "MUTE ALL"
	_mute_toggle.add_theme_font_size_override("font_size", 18)
	_mute_toggle.toggled.connect(_on_mute_toggled)
	column.add_child(_mute_toggle)

	column.add_child(UIKit.body("SOUND FX", 14, UIKit.INK))
	_sound_slider = _make_slider()
	_sound_slider.value_changed.connect(_on_sound_changed)
	column.add_child(_sound_slider)
	_sound_value = UIKit.body("0.73", 13)
	column.add_child(_sound_value)

	column.add_child(UIKit.body("MUSIC", 14, UIKit.INK))
	_music_slider = _make_slider()
	_music_slider.value_changed.connect(_on_music_changed)
	column.add_child(_music_slider)
	_music_value = UIKit.body("0.30", 13)
	column.add_child(_music_value)

	column.add_child(UIKit.spacer(6))
	var back := UIKit.button("BACK", 52)
	back.pressed.connect(close)
	column.add_child(back)


func _make_slider() -> HSlider:
	var slider := HSlider.new()
	slider.min_value = 0.0
	slider.max_value = 1.0
	slider.step = 0.01
	slider.custom_minimum_size = Vector2(0, 34)
	return slider


func open() -> void:
	_sync_from_session()
	visible = true


func close() -> void:
	visible = false
	Session.play_sfx("click")
	closed.emit()


func _sync_from_session() -> void:
	var muted := Session.store.audio_muted()
	var sound := Session.store.sound_volume()
	var music := Session.store.music_volume()
	_mute_toggle.set_pressed_no_signal(muted)
	_sound_slider.set_value_no_signal(sound)
	_music_slider.set_value_no_signal(music)
	_refresh_labels(sound, music)


func _refresh_labels(sound: float, music: float) -> void:
	_sound_value.text = "%.2f" % sound
	_music_value.text = "%.2f" % music


func _persist() -> void:
	Session.save_audio(
		_mute_toggle.button_pressed, _sound_slider.value, _music_slider.value
	)
	_refresh_labels(_sound_slider.value, _music_slider.value)


func _on_mute_toggled(_pressed: bool) -> void:
	_persist()


func _on_sound_changed(_value: float) -> void:
	_persist()


func _on_music_changed(_value: float) -> void:
	_persist()
