extends "res://scripts/bosses/BossBase.gd"
## B2 — QUEEN WASP: ong chúa tinh vân (chương 2). Art boss_pancake + 4 cánh
## vỗ rung tần số cao, ngòi chích thò ra theo tiến trình telegraph, bụng thở.

func _make_rig() -> Node2D:
	return preload("res://scripts/bosses/rigs/QueenWaspRig.gd").new()
