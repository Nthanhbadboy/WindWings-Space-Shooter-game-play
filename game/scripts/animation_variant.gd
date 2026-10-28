class_name AnimationVariant
extends RefCounted

## One build parameter decides which art package a Windows build loads and which
## animation mode it runs:
##
##   A  clean generated layer package   -> layered animation (body + glow, boss
##                                         body/gun-l/gun-r/core, guns track the ship)
##   B  inpainted flat package          -> layered animation, same rules as A
##   C  single flat image               -> whole-image animation (bob, bank, flash,
##                                         shake, particle overlay outside the hull,
##                                         guns do not turn, flame sticks to the hull)
##
## The file is written at build time by game/tools/build_variant.py from the
## `--variant` CI matrix entry, so an exported .exe always knows its own variant.
## Everything is optional: a missing or broken file falls back to variant A so
## the game never fails to boot because of packaging metadata.

const PATH := "res://data/animation_variant.json"
const VARIANTS: Array[String] = ["A", "B", "C"]
const FALLBACK_VARIANT := "A"

const MODE_LAYERED := "layered"
const MODE_WHOLE := "whole"

const SOURCE_PLACEHOLDER := "placeholder"
const SOURCE_PACKAGE := "package"

var variant := FALLBACK_VARIANT
var mode := MODE_LAYERED
var art_source := SOURCE_PLACEHOLDER
var art_package_commit := ""
var error := ""


static func load_default(path := PATH) -> AnimationVariant:
	if not FileAccess.file_exists(path):
		var missing := AnimationVariant.new()
		missing.error = "no variant file at %s, using %s" % [path, FALLBACK_VARIANT]
		return missing
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not parsed is Dictionary:
		var broken := AnimationVariant.new()
		broken.error = "variant file %s is not a JSON object, using %s" % [path, FALLBACK_VARIANT]
		return broken
	return from_dictionary(parsed as Dictionary)


## Build a variant from already parsed JSON. Unknown/invalid values fall back to A
## with an error note instead of throwing, so a bad CI input cannot break a build.
static func from_dictionary(data: Dictionary) -> AnimationVariant:
	var result := AnimationVariant.new()
	var requested := str(data.get("variant", FALLBACK_VARIANT)).strip_edges().to_upper()
	if VARIANTS.has(requested):
		result.variant = requested
	else:
		result.error = "unknown variant '%s', using %s" % [requested, FALLBACK_VARIANT]
		result.variant = FALLBACK_VARIANT
	result.mode = MODE_LAYERED if result.variant != "C" else MODE_WHOLE
	var declared_mode := str(data.get("mode", result.mode))
	if declared_mode != result.mode:
		result.error = "%s must run mode '%s', file said '%s'" % [result.variant, result.mode, declared_mode]
	result.art_source = str(data.get("art_source", SOURCE_PLACEHOLDER))
	if result.art_source != SOURCE_PACKAGE:
		result.art_source = SOURCE_PLACEHOLDER
	result.art_package_commit = str(data.get("art_package_commit", "")).strip_edges()
	return result


func is_layered() -> bool:
	return mode == MODE_LAYERED


func is_whole() -> bool:
	return mode == MODE_WHOLE


## Ship glow layer and boss part layers only exist in the generated/inpainted
## packages; the flat package animates one whole image instead.
func uses_layers() -> bool:
	return is_layered()


## In the flat package the boss keeps one rigid silhouette, so its guns must not
## swing around the contract mounts.
func guns_track_target() -> bool:
	return is_layered()


## In the flat package the flame belongs to the hull and follows every bank,
## where the layered builds let it trail in world space.
func flame_sticks_to_hull() -> bool:
	return is_whole()


func label() -> String:
	return "ANIM-%s" % variant


func art_root() -> String:
	return "art/%s" % variant


## Variant package first, then the shared art folder, then the user drop-in
## folders, so an artist can test one package without copying files around.
func art_roots() -> Array:
	return [
		"res://%s" % art_root(),
		"user://%s" % art_root(),
		"res://art",
		"user://art",
	]


func is_placeholder() -> bool:
	return art_source != SOURCE_PACKAGE


func describe() -> String:
	var commit := art_package_commit if not art_package_commit.is_empty() else "none"
	return "ANIM_VARIANT variant=%s mode=%s art=res://%s source=%s package_commit=%s" % [
		variant, mode, art_root(), art_source, commit
	]


func report_lines() -> Array:
	var lines: Array = [describe()]
	lines.append("ANIM_VARIANT_LABEL %s" % label())
	if is_placeholder():
		lines.append(
			"ANIM_VARIANT_PLACEHOLDER %s package not delivered yet; the build runs the variant rules on fallback art" % label()
		)
	if not error.is_empty():
		lines.append("ANIM_VARIANT_NOTE %s" % error)
	return lines
