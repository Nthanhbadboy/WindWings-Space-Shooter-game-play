extends Node
## Sfx.gd — placeholder âm thanh (silent). Asset audio sẽ thêm sau.
## TODO: add sound — thay bằng AudioStreamPlayer khi có asset (nhạc + SFX).

var muted := false
var _players: Array[AudioStreamPlayer] = []

func _ready() -> void:
	for i in range(4):
		var p := AudioStreamPlayer.new()
		p.bus = "Master"
		add_child(p)
		_players.append(p)

func play(_sfx_name: String) -> void:
	# TODO: add sound — map _sfx_name -> AudioStream và phát qua _players
	if muted:
		return

func music(_track: String) -> void:
	# TODO: add sound — nhạc nền theo chương/boss
	if muted:
		return

func set_muted(v: bool) -> void:
	muted = v
