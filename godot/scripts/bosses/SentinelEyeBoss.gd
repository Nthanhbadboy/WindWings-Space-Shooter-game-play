extends "res://scripts/bosses/BossBase.gd"
## B5 — SENTINEL EYE: nhãn cầu vệ tinh cổ (chương 5). Procedural: vành quỹ
## đạo kép xoay ngược, mống mắt đuổi người chơi, mi mắt ĐÓNG khi charge và
## MỞ TOÁC khi fire, tia quét ngắm trước đòn beam.

func _make_rig() -> Node2D:
	return preload("res://scripts/bosses/rigs/SentinelEyeRig.gd").new()
