extends SceneTree

## Reports which ART SLOT CONTRACT slots ship real art and which still fall back
## to the vector drawing. CI appends the output to BUILD_INFO.txt.
##
## Run: godot --headless --path game --script res://tools/art_report.gd
## Exit code 0 when the contract loads and every slot has a status line.

const ArtLibraryScript = preload("res://scripts/art_library.gd")


func _initialize() -> void:
	var library: ArtLibrary = ArtLibraryScript.new()
	var problems := library.validate()
	if not library.contract_ready():
		printerr("ART_ERROR %s" % library.error)
		quit(1)
		return
	for problem: Variant in problems:
		printerr("ART_CONTRACT_PROBLEM %s" % str(problem))
	print("ART_CONTRACT_SOURCE %s" % str(library.contract.get("sources", {})))
	var lines := library.report_lines()
	for line: Variant in lines:
		print(str(line))
	var missing := library.missing_ids()
	if not missing.is_empty():
		print("ART_MISSING_SLOTS %s" % ",".join(PackedStringArray(missing)))
	print("ART_REPORT_END")
	if not problems.is_empty():
		quit(1)
		return
	quit(0)
