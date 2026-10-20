extends "res://scripts/bosses/BossBase.gd"
## B3 — IMPERATOR: soái hạm pháo đài đế quốc (chương 3). Art imperial +
## 2 tháp pháo xoay ngắm, cửa hangar mở thả tiêm kích, đèn cầu nhấp nháy.

func _make_rig() -> Node2D:
	return preload("res://scripts/bosses/rigs/ImperatorRig.gd").new()
