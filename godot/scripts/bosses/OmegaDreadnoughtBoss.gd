extends "res://scripts/bosses/BossBase.gd"
## B6 — OMEGA DREADNOUGHT: siêu chiến hạm cuối cùng (chương 6). Art
## dreadnought + 2 pháo tay cơ khí ngắm-người-chơi với giật lùi, 4 tấm cánh
## XOÈ RỘNG dần theo pha, lõi phản lực rực sáng tích tụ theo telegraph.

func _make_rig() -> Node2D:
	return preload("res://scripts/bosses/rigs/OmegaDreadnoughtRig.gd").new()
