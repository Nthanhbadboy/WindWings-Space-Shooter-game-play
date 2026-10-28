extends Node

## Motion acceptance harness: renders the real scenes and writes PNG frames.
##
## Run (needs a renderer, CI uses xvfb + llvmpipe):
##   godot --path game --rendering-driver opengl3 --fixed-fps 60 \
##         res://tools/motion_capture.tscn -- --out=/abs/frames --capture-fps=12
##
## Segments:
##   hangar : scenes/hangar.tscn for 3.0 s (float, shadow, glow, engine idle)
##   flight : scenes/main.tscn, ship glides and auto-fires for 2.5 s
##   boss   : scenes/main.tscn jumped to the boss, entrance + one Attack2 volley
##   turret : the same boss with both turrets sweeping +-45 deg (art seam check)
##
## Every capture writes `<out>/<segment>/frame_0000.png` and a `frames.txt`
## manifest with the simulated time of each frame, so the report can state
## exactly what was captured instead of "looks fine".

const AnimationVariantScript = preload("res://scripts/animation_variant.gd")

const HANGAR_SCENE := preload("res://scenes/hangar.tscn")
const MAIN_SCENE := preload("res://scenes/main.tscn")

const SEGMENTS := {
	"hangar": {"seconds": 3.0, "stage": "hangar"},
	"flight": {"seconds": 2.6, "stage": "flight"},
	"boss": {"seconds": 7.6, "stage": "boss"},
	# Art QA: both boss turrets sweep +-45 deg so the pod seam can be judged at
	# every angle, which is what the delivered packages ask to be checked.
	"turret": {"seconds": 3.4, "stage": "turret"},
}

var out_dir := "user://motion"
var capture_fps := 12.0
var only_segment := ""
var _current: Node = null


func _ready() -> void:
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--out="):
			out_dir = argument.trim_prefix("--out=")
		elif argument.begins_with("--capture-fps="):
			capture_fps = float(argument.trim_prefix("--capture-fps="))
		elif argument.begins_with("--only="):
			only_segment = argument.trim_prefix("--only=")
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out_dir))
	var variant: AnimationVariant = AnimationVariantScript.load_default()
	print("MOTION_VARIANT %s" % variant.describe())
	print("MOTION_CAPTURE_START out=%s fps=%s" % [out_dir, str(capture_fps)])
	await _run_all()


func _run_all() -> void:
	var total := 0
	for segment: String in SEGMENTS.keys():
		if not only_segment.is_empty() and segment != only_segment:
			continue
		total += await _capture_segment(segment)
	print("MOTION_CAPTURE_END frames=%d" % total)
	get_tree().quit(0 if total > 0 else 1)


func _capture_segment(segment: String) -> int:
	var config: Dictionary = SEGMENTS[segment]
	var folder := "%s/%s" % [out_dir, segment]
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(folder))
	if _current != null and is_instance_valid(_current):
		_current.queue_free()
		await get_tree().process_frame
	_current = _build_stage(config["stage"], segment)
	add_child(_current)
	await get_tree().process_frame
	await get_tree().process_frame

	var interval := 1.0 / maxf(capture_fps, 1.0)
	var elapsed := 0.0
	var next_capture := 0.0
	var index := 0
	var manifest: Array = []
	var limit := int(float(config["seconds"]) * 240.0)
	var steps := 0
	while elapsed < float(config["seconds"]) and steps < limit:
		await get_tree().process_frame
		elapsed = _simulated_time(_current)
		steps += 1
		if elapsed + 0.0001 < next_capture:
			continue
		next_capture += interval
		await RenderingServer.frame_post_draw
		var image := get_viewport().get_texture().get_image()
		if image == null:
			continue
		var file_name := "%s/frame_%04d.png" % [folder, index]
		image.save_png(ProjectSettings.globalize_path(file_name))
		manifest.append("%s\t%.4f" % [file_name, elapsed])
		index += 1
	var manifest_file := FileAccess.open("%s/frames.txt" % folder, FileAccess.WRITE)
	if manifest_file != null:
		manifest_file.store_string("\n".join(PackedStringArray(manifest)) + "\n")
		manifest_file.close()
	print("MOTION_SEGMENT %s frames=%d seconds=%.2f" % [segment, index, elapsed])
	return index


func _simulated_time(node: Node) -> float:
	if node == null or not is_instance_valid(node):
		return 0.0
	if node.has_method("capture_time"):
		return float(node.call("capture_time"))
	return 0.0


func _build_stage(stage: String, segment: String) -> Node:
	if stage == "hangar":
		var hangar := HANGAR_SCENE.instantiate()
		return hangar
	var main := MAIN_SCENE.instantiate()
	main.set("capture_stage", "boss" if stage == "boss" else "flight")
	if stage == "flight":
		main.set("_autoplay", false)
	return main
