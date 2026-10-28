extends Control

## Victory (stars + save) and game over (retry) screen.


func _ready() -> void:
	if get_tree().paused:
		get_tree().paused = false
	Session.apply_audio(false)
	Session.start_music()
	_build()


func _build() -> void:
	UIKit.background(self)
	var margin := UIKit.full_margin(self, 26)
	var center := CenterContainer.new()
	margin.add_child(center)

	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation", 14)
	column.custom_minimum_size = Vector2(400, 0)
	center.add_child(column)

	var result: Dictionary = Session.last_result
	var victory := bool(result.get("victory", false))
	var stars := int(result.get("stars", 0))
	var kills := int(result.get("kills", 0))
	var entries := int(result.get("entries", 0))
	var score := int(result.get("score", 0))

	if victory:
		column.add_child(UIKit.title("STAGE CLEAR", 40))
	else:
		column.add_child(UIKit.body("GAME OVER", 40, UIKit.DANGER))
	column.add_child(
		UIKit.body(
			"Victory" if victory else "The hull is lost. Stars are only awarded on a clear.",
			13
		)
	)
	column.add_child(UIKit.star_row(stars, 3, 46))
	column.add_child(
		UIKit.body(
			"BEST  %d ★   ·   SAVED TOTAL  %d ★"
			% [int(result.get("best_after", 0)), int(result.get("star_total", 0))],
			14,
			UIKit.INK
		)
	)
	column.add_child(UIKit.spacer(6))
	column.add_child(UIKit.body("SCORE  %d" % score, 22, UIKit.GOLD))
	column.add_child(UIKit.body("KILLS  %d / %d entries" % [kills, entries], 13))
	column.add_child(
		UIKit.body(
			"Stage %d · mode %d (levelDelta reward x%.1f, HP x1.0)"
			% [
				int(result.get("stage_index", 1)),
				int(result.get("mode_index", 0)),
				LaunchRules.level_delta(int(result.get("mode_index", 0))),
			],
			12
		)
	)
	column.add_child(UIKit.spacer(10))

	var retry := UIKit.button("PLAY AGAIN", 60)
	retry.pressed.connect(_on_retry)
	column.add_child(retry)

	var ships := UIKit.button("SHIP SELECT", 48)
	ships.pressed.connect(_on_ships)
	column.add_child(ships)

	var menu := UIKit.button("MAIN MENU", 48)
	menu.pressed.connect(_on_menu)
	column.add_child(menu)


func _on_retry() -> void:
	Session.play_sfx("click")
	get_tree().paused = false
	get_tree().reload_current_scene()


func _on_ships() -> void:
	Session.play_sfx("click")
	get_tree().change_scene_to_file("res://scenes/ship_select.tscn")


func _on_menu() -> void:
	Session.play_sfx("click")
	get_tree().change_scene_to_file("res://scenes/menu.tscn")
