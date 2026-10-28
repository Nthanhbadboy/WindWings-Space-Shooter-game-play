class_name RunModifiers
extends RefCounted

## Build-time run modifiers for the launch slice.
##
## Read from `res://data/run_modifiers.json` at startup. The file ships with
## `player_invincible = true` for the three art-review builds: the USER needs to
## watch all five waves and the boss without the hull dying mid-clip. A missing
## or broken file is not fatal - it just means the normal damage rules apply,
## and `error` says why.

const PATH := "res://data/run_modifiers.json"

var player_invincible := false
var label := ""
var error := ""


func load_default() -> bool:
	return load_from_path(PATH)


func load_from_path(path: String) -> bool:
	player_invincible = false
	label = ""
	error = ""
	if not FileAccess.file_exists(path):
		error = "missing %s" % path
		return false
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if parsed is not Dictionary:
		error = "unreadable %s" % path
		return false
	return load_from_document(parsed)


## Split out so the rule can be tested without touching the shipped file.
func load_from_document(document: Dictionary) -> bool:
	player_invincible = bool(document.get("player_invincible", false))
	label = str(document.get("label", ""))
	error = ""
	return true


## True when the player's hull must not lose HP in this build.
func blocks_player_damage() -> bool:
	return player_invincible


## Short tag for the menu/HUD ("GOD"), or "" when damage rules are normal.
func tag() -> String:
	return label if player_invincible and not label.is_empty() else ""


func report_line() -> String:
	return (
		"RUN_MODIFIERS player_invincible=%s label=%s"
		% ["true" if player_invincible else "false", label if not label.is_empty() else "none"]
	)
