extends "res://scripts/bosses/BossBase.gd"
## B4 — VOID SPIDER: nhện cơ khí 6 chân (chương 4). Procedural toàn phần:
## 6 chân IK 2 khớp bước theo nhịp, nanh thò khi charge, cụm 6 mắt đỏ rực
## theo tiến trình telegraph.

func _make_rig() -> Node2D:
	return preload("res://scripts/bosses/rigs/VoidSpiderRig.gd").new()
