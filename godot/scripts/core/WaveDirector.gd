extends RefCounted
## WaveDirector.gd — chạy kịch bản sóng Balance.wave_script(level) bằng bộ
## đếm delta-time thuần (không await/sleep). Mỗi wave: {"duration", "spawns":
## [{"t","type","x"}...]}. Hết duration → sang sóng; sóng cuối xong → all_done.

signal wave_started(index: int)
signal all_done

var script: Array = []
var run: Node = null
var idx := -1
var t_wave := 0.0
var next_spawn := 0
var active := false
var finished := false
var spawned_total := 0

const WAVE_GAP := 1.2

func _init(run_ref: Node, script_arr: Array) -> void:
	run = run_ref
	script = script_arr

func start() -> void:
	_advance()

func tick(delta: float) -> void:
	if finished or not active:
		return
	t_wave += delta
	var spawns: Array = script[idx]["spawns"]
	while next_spawn < spawns.size() and float(spawns[next_spawn]["t"]) <= t_wave:
		var s: Dictionary = spawns[next_spawn]
		run.spawn_enemy(String(s["type"]), float(s["x"]))
		next_spawn += 1
		spawned_total += 1
	if t_wave >= float(script[idx]["duration"]) + WAVE_GAP and next_spawn >= spawns.size():
		_advance()

func _advance() -> void:
	idx += 1
	if idx >= script.size():
		active = false
		finished = true
		all_done.emit()
		return
	t_wave = 0.0
	next_spawn = 0
	active = true
	wave_started.emit(idx)

func remaining_spawns() -> int:
	var n := 0
	for i in range(idx, script.size()):
		var spawns: Array = script[i]["spawns"]
		n += spawns.size() - (next_spawn if i == idx else 0)
	return n

func expected_total() -> int:
	var n := 0
	for w in script:
		n += (w["spawns"] as Array).size()
	return n
