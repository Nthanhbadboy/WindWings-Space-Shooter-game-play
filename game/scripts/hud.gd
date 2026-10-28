class_name GameHUD
extends Control

## In-run HUD: hull bar, wave/score readouts, boss bar, banner and pause button.

signal pause_requested

var _hp_bar: ProgressBar
var _hp_label: Label
var _wave_label: Label
var _score_label: Label
var _banner: Label
var _boss_box: VBoxContainer
var _boss_bar: ProgressBar
var _boss_label: Label
var _fatal_label: Label
var _warning_box: VBoxContainer
var _warning_bar: ProgressBar
var _wave_text := ""


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_build()


func _build() -> void:
	var margin := UIKit.full_margin(self, 14)
	margin.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation", 6)
	margin.add_child(column)

	var top := HBoxContainer.new()
	top.add_theme_constant_override("separation", 10)
	column.add_child(top)

	var hull_box := VBoxContainer.new()
	hull_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hull_box.add_theme_constant_override("separation", 2)
	top.add_child(hull_box)

	_hp_label = UIKit.body("HULL 2500 / 2500", 14, UIKit.INK)
	_hp_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	hull_box.add_child(_hp_label)

	_hp_bar = ProgressBar.new()
	_hp_bar.min_value = 0.0
	_hp_bar.max_value = 1.0
	_hp_bar.step = 0.0
	_hp_bar.value = 1.0
	_hp_bar.show_percentage = false
	_hp_bar.custom_minimum_size = Vector2(0, 18)
	hull_box.add_child(_hp_bar)

	var pause := UIKit.button("II", 44, 60)
	pause.focus_mode = Control.FOCUS_NONE
	pause.pressed.connect(_on_pause_pressed)
	top.add_child(pause)

	var info := HBoxContainer.new()
	info.add_theme_constant_override("separation", 12)
	column.add_child(info)
	_wave_label = UIKit.body("WAVE", 15, UIKit.ACCENT)
	_wave_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	_wave_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	info.add_child(_wave_label)
	_score_label = UIKit.body("SCORE 0", 15, UIKit.GOLD)
	_score_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	info.add_child(_score_label)

	_warning_box = VBoxContainer.new()
	_warning_box.add_theme_constant_override("separation", 2)
	_warning_box.visible = false
	column.add_child(_warning_box)
	var warning_label := UIKit.body("!! BOSS APPROACHING !!", 15, UIKit.DANGER)
	_warning_box.add_child(warning_label)
	_warning_bar = ProgressBar.new()
	_warning_bar.min_value = 0.0
	_warning_bar.max_value = 1.0
	_warning_bar.step = 0.0
	_warning_bar.value = 0.0
	_warning_bar.show_percentage = false
	_warning_bar.custom_minimum_size = Vector2(0, 12)
	_warning_box.add_child(_warning_bar)

	_boss_box = VBoxContainer.new()
	_boss_box.add_theme_constant_override("separation", 2)
	_boss_box.visible = false
	column.add_child(_boss_box)
	_boss_label = UIKit.body("BOSS", 13, UIKit.DANGER)
	_boss_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	_boss_box.add_child(_boss_label)
	_boss_bar = ProgressBar.new()
	_boss_bar.min_value = 0.0
	_boss_bar.max_value = 1.0
	_boss_bar.step = 0.0
	_boss_bar.value = 1.0
	_boss_bar.show_percentage = false
	_boss_bar.custom_minimum_size = Vector2(0, 14)
	_boss_box.add_child(_boss_bar)

	var spacer := Control.new()
	spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
	spacer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	column.add_child(spacer)

	_banner = UIKit.title("", 26)
	_banner.visible = false
	column.add_child(_banner)

	_fatal_label = UIKit.body("", 14, UIKit.DANGER)
	_fatal_label.visible = false
	column.add_child(_fatal_label)


func _on_pause_pressed() -> void:
	Session.play_sfx("click")
	pause_requested.emit()


func set_hp(current: float, maximum: float) -> void:
	var ratio := 0.0 if maximum <= 0.0 else clampf(current / maximum, 0.0, 1.0)
	_hp_bar.value = ratio
	_hp_label.text = "HULL %d / %d" % [int(round(maxf(current, 0.0))), int(round(maximum))]
	if not Session.modifier_tag().is_empty():
		_hp_label.text += "  ·  %s (NO DAMAGE)" % Session.modifier_tag()
	var color := UIKit.ACCENT if ratio > 0.4 else UIKit.DANGER
	_hp_label.add_theme_color_override("font_color", color)


func set_wave(text: String) -> void:
	_wave_text = text
	if not get_tree().paused:
		_wave_label.text = text


func set_score(value: int) -> void:
	_score_label.text = "SCORE %d" % value


func show_banner(text: String, seconds := 1.4) -> void:
	_banner.text = text
	_banner.visible = true
	_hide_banner_later(seconds)


func _hide_banner_later(seconds: float) -> void:
	await get_tree().create_timer(seconds).timeout
	_banner.visible = false


func set_boss(name: String, current: float, maximum: float) -> void:
	_boss_box.visible = true
	_boss_label.text = name
	_boss_bar.value = 0.0 if maximum <= 0.0 else clampf(current / maximum, 0.0, 1.0)


func clear_boss() -> void:
	_boss_box.visible = false


func set_warning(remaining: float) -> void:
	var clamped := clampf(remaining, 0.0, 1.0)
	_warning_box.visible = clamped > 0.001
	_warning_bar.value = clamped


func set_paused(paused: bool) -> void:
	_wave_label.text = "PAUSED" if paused else _wave_text


func show_fatal(text: String) -> void:
	_fatal_label.text = text
	_fatal_label.visible = true
	push_error(text)
