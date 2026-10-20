extends "res://scripts/bosses/BossBase.gd"
## B1 — VOID TYRANT: sứa hư không khổng lồ (chương 1). 100% procedural:
## chuông sứa thở, 6 xúc tu sine IK, 2 mắt đuổi theo người chơi.

func _make_rig() -> Node2D:
	return preload("res://scripts/bosses/rigs/VoidTyrantRig.gd").new()
