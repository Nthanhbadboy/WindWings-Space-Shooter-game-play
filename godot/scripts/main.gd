extends Node
## Main.gd — điều phối luồng màn hình. Mọi màn dựng bằng code (không phụ thuộc
## .tscn phức tạp): home Ramus -> bản đồ 60 màn -> trận đánh -> kết quả.

const HomeScreen := preload("res://scripts/ui/HomeScreen.gd")
const LevelMap := preload("res://scripts/ui/LevelMap.gd")
const HangarScreen := preload("res://scripts/ui/HangarScreen.gd")
const TechScreen := preload("res://scripts/ui/TechScreen.gd")
const StoreScreen := preload("res://scripts/ui/StoreScreen.gd")
const RunScene := preload("res://scripts/core/RunScene.gd")

var current: Node = null
var current_name := ""

func _ready() -> void:
	show_screen("home")

## Chuyển màn. args: {"level": int} cho "run", {"chapter": int} cho "map".
func show_screen(screen: String, args: Dictionary = {}) -> void:
	if current != null:
		current.queue_free()
	current_name = screen
	match screen:
		"map":
			current = LevelMap.new()
		"hangar":
			current = HangarScreen.new()
		"tech":
			current = TechScreen.new()
		"store":
			current = StoreScreen.new()
		"run":
			current = RunScene.new()
		_:
			current = HomeScreen.new()
	if current.has_method("attach"):
		current.call("attach", self, args)
	add_child(current)

func restart_run(level: int) -> void:
	show_screen("run", {"level": level})
