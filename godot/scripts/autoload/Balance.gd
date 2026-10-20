extends Node
## Balance.gd — MỌI hằng số của game (không magic number trong code chạy).
## Dữ liệu: 6 chương x 10 màn = 60 màn, 6 boss chủ thể riêng, 8 tàu, 5 nhánh tech.

const VIEW := Vector2i(720, 1280)
const LEVELS_PER_CHAPTER := 10
const CHAPTER_COUNT := 6
const TOTAL_LEVELS := LEVELS_PER_CHAPTER * CHAPTER_COUNT

# ---------------------------------------------------------------- chương
const CHAPTERS := [
	{
		"name": "VÀNH ĐAI SAO MỘC", "tint": Color("#59d8ff"),
		"nebula_a": Color("#3a2a7e"), "nebula_b": Color("#123a6e"),
		"planet": Color("#c98a4b"), "boss": "void_tyrant",
		"pool": ["wasp", "wasp", "hornet", "meteor"],
	},
	{
		"name": "TINH VÂN XANH", "tint": Color("#5dffa8"),
		"nebula_a": Color("#1f6fa8"), "nebula_b": Color("#2fc6a0"),
		"planet": Color("#4bd0c9"), "boss": "queen_wasp",
		"pool": ["wasp", "hornet", "interceptor", "meteor"],
	},
	{
		"name": "VÙNG TỐI", "tint": Color("#ff8f6a"),
		"nebula_a": Color("#6a1030"), "nebula_b": Color("#3a1a6e"),
		"planet": Color("#8a5ac9"), "boss": "imperator",
		"pool": ["hornet", "tank", "bomber", "wasp"],
	},
	{
		"name": "BIỂN TIỂU HÀNH TINH", "tint": Color("#ffc46a"),
		"nebula_a": Color("#8c4a1f"), "nebula_b": Color("#5e2a12"),
		"planet": Color("#d0a06a"), "boss": "void_spider",
		"pool": ["meteor", "wasp", "tank", "interceptor"],
	},
	{
		"name": "LÒ PHẢN VẬT CHẤT", "tint": Color("#7fe0ff"),
		"nebula_a": Color("#1b3fa0"), "nebula_b": Color("#0e6a8c"),
		"planet": Color("#6aa8ff"), "boss": "sentinel_eye",
		"pool": ["interceptor", "hornet", "bomber", "wasp"],
	},
	{
		"name": "TRÁI TIM HẠM ĐỘI", "tint": Color("#d68aff"),
		"nebula_a": Color("#4d0a6e"), "nebula_b": Color("#2a0a4d"),
		"planet": Color("#ff6ad5"), "boss": "omega_dreadnought",
		"pool": ["tank", "hornet", "bomber", "meteor"],
	},
]

# ---------------------------------------------------------------- tàu (hangar)
const SHIPS := {
	"striker": {"name": "STRIKER", "price": 0, "hp": 100, "dmg": 12, "speed": 620, "fire_rate": 5.2, "perk": "coins+10%", "color": Color("#58e6ff")},
	"zenith": {"name": "ZENITH", "price": 1200, "hp": 110, "dmg": 13, "speed": 660, "fire_rate": 5.6, "perk": "shield_regen_x2", "color": Color("#ffd23e")},
	"challenger": {"name": "CHALLENGER", "price": 2000, "hp": 130, "dmg": 14, "speed": 600, "fire_rate": 5.0, "perk": "shield_max+1", "color": Color("#ff8f6a")},
	"spitfire": {"name": "SPITFIRE", "price": 3200, "hp": 95, "dmg": 16, "speed": 640, "fire_rate": 6.2, "perk": "weapon_lv2", "color": Color("#ff5f7a")},
	"insurgent": {"name": "INSURGENT", "price": 4500, "hp": 105, "dmg": 15, "speed": 650, "fire_rate": 5.4, "perk": "magnet+60%", "color": Color("#7df9a0")},
	"executioner": {"name": "EXECUTIONER", "price": 6000, "hp": 120, "dmg": 18, "speed": 580, "fire_rate": 4.6, "perk": "pierce_1", "color": Color("#c9a8ff")},
	"omen": {"name": "OMEN", "price": 8000, "hp": 115, "dmg": 17, "speed": 630, "fire_rate": 5.2, "perk": "drone+1", "color": Color("#b46cff")},
	"dispatcher": {"name": "DISPATCHER", "price": 10000, "hp": 140, "dmg": 19, "speed": 600, "fire_rate": 5.0, "perk": "drone+2", "color": Color("#4a8aff")},
}
const SHIP_ORDER := ["striker", "zenith", "challenger", "spitfire", "insurgent", "executioner", "omen", "dispatcher"]
const SHIP_MAX_LEVEL := 15

# ---------------------------------------------------------------- công nghệ
const TECH := {
	"cannon": {"name": "PHÁO CHÍNH", "desc": "+8% sát thương / cấp", "max": 20, "base": 140},
	"armor": {"name": "GIÁP THÂN", "desc": "+10% máu / cấp", "max": 20, "base": 120},
	"shield": {"name": "KHIÊN NĂNG LƯỢNG", "desc": "+1 khiên mỗi 3 cấp (tối đa 5)", "max": 9, "base": 180},
	"drone": {"name": "DRONE HỘ VỆ", "desc": "+1 drone mỗi 2 cấp (tối đa 3)", "max": 6, "base": 240},
	"magnet": {"name": "TỪ TRƯỜNG", "desc": "+12% bán kính hút / cấp", "max": 5, "base": 90},
}

# ---------------------------------------------------------------- địch
const ENEMIES := {
	"wasp": {"hp": 12, "speed": 340, "score": 70, "coins": 1, "radius": 22, "behavior": "dive", "wobble": 2.6, "amp": 60, "art": "res://assets/enemies/enemy_wasp.png", "scale": 0.55},
	"hornet": {"hp": 34, "speed": 190, "score": 220, "coins": 3, "radius": 30, "behavior": "hover", "stop_y": 300, "fire_cd": 2.1, "art": "res://assets/enemies/enemy_hornet.png", "scale": 0.8},
	"interceptor": {"hp": 28, "speed": 300, "score": 200, "coins": 3, "radius": 26, "behavior": "dive", "wobble": 2.4, "amp": 90, "fire_cd": 2.8, "art": "res://assets/enemies/enemy_hornet.png", "scale": 0.7, "tint": Color("#ffd6a8")},
	"bomber": {"hp": 90, "speed": 150, "score": 440, "coins": 5, "radius": 38, "behavior": "hover", "stop_y": 240, "fire_cd": 3.2, "spread": 3, "art": "res://assets/enemies/enemy_hornet.png", "scale": 1.05, "tint": Color("#c9a8ff")},
	"tank": {"hp": 120, "speed": 120, "score": 400, "coins": 5, "radius": 42, "behavior": "tank", "fire_cd": 2.6, "art": "res://assets/enemies/enemy_hornet.png", "scale": 1.15, "tint": Color("#9fd0ff")},
	"meteor": {"hp": 40, "speed": 260, "score": 80, "coins": 2, "radius": 34, "behavior": "drift", "spin": 1.6, "art": "res://assets/enemies/meteor.png", "scale": 0.9},
}
const CONTACT_KILL := true

# ---------------------------------------------------------------- boss (6 chủ thể)
const BOSSES := {
	"void_tyrant": {
		"name": "VOID TYRANT", "subject": "Sứa hư không", "hp": 2600, "radius": 92,
		"art": "", "color": Color("#9b5cff"), "patterns": ["aimed3", "fan", "spiral", "tentacle_sweep"],
	},
	"queen_wasp": {
		"name": "ONG CHÚA TINH VÂN", "subject": "Ong chúa khổng lồ", "hp": 3200, "radius": 96,
		"art": "res://assets/bosses/boss_pancake.png", "color": Color("#ff5fd2"), "patterns": ["stinger_dash", "swarm_call", "fan", "ring"],
	},
	"imperator": {
		"name": "SOÁI HẠM ĐẾ QUỐC", "subject": "Soái hạm pháo đài", "hp": 3900, "radius": 100,
		"art": "res://assets/bosses/boss_imperial.png", "color": Color("#ff7a4a"), "patterns": ["broadside", "hangar_wave", "laser_sweep", "wall"],
	},
	"void_spider": {
		"name": "NHỆN HƯ KHÔNG", "subject": "Nhện cơ khí 6 chân", "hp": 4600, "radius": 94,
		"art": "", "color": Color("#ff3c5a"), "patterns": ["web_trap", "leg_slam", "spiderling", "spiral"],
	},
	"sentinel_eye": {
		"name": "MẮT THẦN CANH GIÁC", "subject": "Nhãn cầu vệ tinh cổ", "hp": 5400, "radius": 88,
		"art": "", "color": Color("#4de1ff"), "patterns": ["gaze_beam", "iris_rings", "blind_spikes", "aimed3"],
	},
	"omega_dreadnought": {
		"name": "OMEGA DREADNOUGHT", "subject": "Siêu chiến hạm cuối cùng", "hp": 6800, "radius": 108,
		"art": "res://assets/bosses/boss_dreadnought.png", "color": Color("#b07bff"), "patterns": ["twin_cannons", "wing_missiles", "core_beam", "hell_ring"],
	},
}

# luật boss (spec): KHÔNG sát thương trước khi hết telegraph
# ---------------------------------------------------------------- kho đạn boss
# Mỗi pattern: kind (cách thi triển trong BossBase) + tham số. HARD RULE:
# telegraph >= 0.6s (BOSS_RULES.telegraph_min chốt chặn dưới khi chạy).
const PATTERNS := {
	"aimed3":        {"kind": "aimed",  "telegraph": 0.70, "count": 3, "spread": 0.16, "speed": 340, "radius": 8, "color": "enemy"},
	"fan":           {"kind": "fan",    "telegraph": 0.80, "count": 9, "arc": 70.0,    "speed": 300, "radius": 8, "color": "enemy"},
	"spiral":        {"kind": "spiral", "telegraph": 0.90, "arms": 4,  "rings": 5,     "speed": 260, "radius": 8, "color": "boss"},
	"ring":          {"kind": "ring",   "telegraph": 0.80, "count": 24,                "speed": 240, "radius": 8, "color": "boss"},
	"tentacle_sweep": {"kind": "sweep", "telegraph": 0.85, "count": 7, "arc": 100.0,   "speeds": [300, 240, 190], "radius": 8, "color": "boss"},
	"stinger_dash":  {"kind": "dash",   "telegraph": 0.65, "count": 1, "speed": 640,   "radius": 11, "color": "fast", "orbs": 2},
	"swarm_call":    {"kind": "summon", "telegraph": 0.90, "summon": "wasp", "summon_count": 2, "ring": 12, "speed": 230, "radius": 8, "color": "boss"},
	"broadside":     {"kind": "broadside", "telegraph": 0.75, "count": 6, "arc": 55.0, "speed": 300, "radius": 8, "color": "fast"},
	"hangar_wave":   {"kind": "summon", "telegraph": 1.00, "summon": "interceptor", "summon_count": 3, "fan": 5, "speed": 250, "radius": 8, "color": "enemy"},
	"laser_sweep":   {"kind": "beam_row", "telegraph": 0.70, "count": 8, "speed": 720, "radius": 4, "color": "fast"},
	"wall":          {"kind": "wall",   "telegraph": 1.10, "count": 11, "speed": 220,  "radius": 9, "color": "boss", "gap": 1},
	"web_trap":      {"kind": "ring2",  "telegraph": 0.85, "count": 16, "speed": 150,  "radius": 8, "color": "boss", "offset2": 0.196},
	"leg_slam":      {"kind": "slam",   "telegraph": 0.60, "count": 6, "speed": 560,   "radius": 9, "color": "fast"},
	"spiderling":    {"kind": "summon", "telegraph": 0.90, "summon": "wasp", "summon_count": 3, "aimed": 3, "speed": 320, "radius": 8, "color": "enemy"},
	"gaze_beam":     {"kind": "beam_row", "telegraph": 0.90, "count": 7, "speed": 800, "radius": 5, "color": "fast", "aim": true},
	"iris_rings":    {"kind": "ring2",  "telegraph": 0.80, "count": 18, "speed": 210,  "radius": 8, "color": "boss", "spin2": -1.0, "offset2": 0.175},
	"blind_spikes":  {"kind": "spikes", "telegraph": 0.75, "count": 5, "speed": 260,   "radius": 10, "color": "fast", "homing": 1.6},
	"twin_cannons":  {"kind": "twin",   "telegraph": 0.70, "count": 4, "spread": 0.10, "speed": 480, "radius": 8, "color": "fast"},
	"wing_missiles": {"kind": "homing", "telegraph": 0.95, "count": 6, "speed": 200,   "radius": 9, "color": "fast", "homing": 2.0},
	"core_beam":     {"kind": "core",   "telegraph": 1.20, "ring": 30, "speed": 250,   "radius": 8, "color": "boss", "lance": 3, "lance_speed": 700},
	"hell_ring":     {"kind": "hell",   "telegraph": 1.00, "count": 20, "rings": 3,    "speed": 250, "radius": 8, "color": "boss"},
}

const BOSS_RULES := {
	"phase2_at": 0.66, "phase3_at": 0.33, "enrage_at": 0.10,
	"telegraph_min": 0.6, "enrage_telegraph_mul": 0.7,
	"transition_time": 1.5, "phase3_heal": 0.05,
	"enter_y": -200.0, "idle_y": 260.0, "drift_speed": 90.0,
	"enter_speed": 260.0, "attack_cd": [2.0, 1.6, 1.25], "enrage_cd_mul": 0.75,
	"death_time": 1.9, "contact_radius_mul": 0.8,
}

# ---------------------------------------------------------------- người chơi
const PLAYER := {
	"hitbox_radius": 8, "sprite_scale": 0.85, "follow_k": 22.0,
	"grab_clamp_x": 140.0, "grab_clamp_y": 220.0,
	"lives": 3, "bombs": 2, "invuln": 3.0, "blink_hz": 10.0,
	"bomb_damage": 500, "bomb_radius": 9999, "bomb_boss_mul": 0.3,
	"heal_amount": 35, "drone_dmg_mul": 0.4, "drone_orbit_r": 70.0, "drone_orbit_w": 2.4,
	"temp_drone_time": 20.0, "combo_time": 2.5,
	"bounds_margin": 40,
}
const WEAPONS := [
	{"shots": 1, "dmg": 1.0, "angles": [0.0], "speed": 980},
	{"shots": 2, "dmg": 0.85, "angles": [0.0], "speed": 980, "offset": 14},
	{"shots": 3, "dmg": 0.8, "angles": [-9.0, 0.0, 9.0], "speed": 980},
	{"shots": 5, "dmg": 0.7, "angles": [-24.0, -12.0, 0.0, 12.0, 24.0], "speed": 1000},
	{"shots": 5, "dmg": 0.75, "angles": [-24.0, -12.0, 0.0, 12.0, 24.0], "speed": 1020, "side_laser": 5},
]
const BULLET := {
	"player_speed": 980, "player_radius": 6, "player_color": Color("#58e6ff"),
	"enemy_speed": 300, "enemy_radius": 8, "enemy_color": Color("#ff3c5a"),
	"boss_color": Color("#b46cff"), "boss_fast": Color("#ffa03c"),
}
const POWERUP := {
	"drop_chance": 0.05, "bomb_chance": 0.01, "magnet_radius": 120, "fall_speed": 120,
	"magnet_duration": 8.0,
	"kinds": [["weapon", 0.40], ["heal", 0.20], ["shield", 0.15], ["drone", 0.12], ["magnet", 0.12], ["bomb", 0.01]],
}

# ---------------------------------------------------------------- nền cuộn
const PARALLAX := {
	"scroll_speed": 90.0,
	"stars_scale": Vector2(0.15, 0.10), "stars_mirror": Vector2(720, 1280), "stars_count": 140,
	"nebula_scale": Vector2(0.40, 0.30), "nebula_mirror": Vector2(720, 1280),
	"planet_scale": Vector2(0.80, 0.70), "planet_mirror": Vector2(0, 2560),
}

# ---------------------------------------------------------------- kinh tế
const ECONOMY := {
	"star_gem": 1, "level_reward_base": 90, "level_reward_per": 24, "boss_mul": 2.4,
	"score_per_kill": 100, "combo_step": 5, "combo_max": 5.0, "boss_kill_score": 10000,
	"daily_coins": 260, "daily_streak_step": 140,
}

# ---------------------------------------------------------------- bảng màu UI
## Đúng chuẩn WindWings (docs/windwings-refs/v2/DO_DAC_UI.md + ảnh Ramus).
const UI := {
	"hud_top": Color("#06122c"), "hud_bottom": Color("#0a1a38"),
	"rim_cyan": Color("#46c6f4"), "rim_blue": Color("#2f9fe0"), "rim_dark": Color("#14538c"),
	"hp_fill": Color("#cdea42"), "hp_bg": Color("#12243f"),
	"energy_a": Color("#8fdcff"), "energy_b": Color("#3fa9ff"), "energy_c": Color("#1d64c8"),
	"gold_a": Color("#ffec22"), "gold_b": Color("#ffc21f"), "gold_c": Color("#d68a00"),
	"btn_a": Color("#ffe08a"), "btn_b": Color("#ffb700"), "btn_c": Color("#d97f00"),
	"green_a": Color("#7df05a"), "green_b": Color("#35c21a"),
	"red": Color("#e23a2e"), "panel": Color("#0a1a2e", 0.92),
	"panel_rim": Color("#2f9fe0"), "text": Color("#eaf6ff"), "text_dim": Color("#8fb4d8"),
	"star": Color("#ffd23c"), "star_off": Color("#28405e"),
	"hp_skew": -0.21, "energy_skew": -0.49,   # skewX(-12deg) / skewX(-26deg)
	"portrait_pos": Vector2(16, 88), "portrait_size": Vector2(74, 58),
	"hp_pos": Vector2(62, 92), "hp_size": Vector2(270, 30),
	"coin_pos": Vector2(444, 84), "pause_pos": Vector2(640, 86), "pause_size": 60.0,
	"enemy_count_y": 176.0,
}

# ---------------------------------------------------------------- màn chơi
static func chapter_of(level: int) -> int:
	return clampi(ceili(float(level) / float(LEVELS_PER_CHAPTER)), 1, CHAPTER_COUNT)

static func level_info(n: int) -> Dictionary:
	var num := clampi(n, 1, TOTAL_LEVELS)
	var ch := chapter_of(num)
	var idx := ((num - 1) % LEVELS_PER_CHAPTER) + 1
	var is_boss := idx == LEVELS_PER_CHAPTER
	var diff := 1.0 + float(ch - 1) * 0.42 + float(idx - 1) * 0.075
	var c: Dictionary = CHAPTERS[ch - 1]
	return {
		"number": num, "chapter": ch, "index": idx, "is_boss": is_boss,
		"difficulty": diff,
		"hp_mul": minf(2.4, diff), "speed_mul": minf(1.5, 1.0 + float(num - 1) * 0.007),
		"bullet_mul": minf(1.5, 1.0 + float(num - 1) * 0.006),
		"boss_id": c["boss"] if is_boss else "",
		"boss_name": (BOSSES[c["boss"]]["name"] if is_boss else ""),
		"pool": c["pool"], "tint": c["tint"], "chapter_name": c["name"],
		"reward": int(round((ECONOMY["level_reward_base"] + idx * ECONOMY["level_reward_per"] + ch * 55) * (ECONOMY["boss_mul"] if is_boss else 1.0))),
	}

## Script wave tất định theo seed của màn (không random runtime).
static func wave_script(n: int) -> Array:
	var info := level_info(n)
	var rng := RandomNumberGenerator.new()
	rng.seed = n * 7919 + 13
	var waves: Array = []
	var wave_count := 4 if info["is_boss"] else 5
	var pool: Array = info["pool"]
	for w in range(wave_count):
		var spawns: Array = []
		var t := 0.0
		var beats := 3 + mini(3, info["chapter"])
		for b in range(beats):
			var kind: String = pool[rng.randi() % pool.size()]
			var x := rng.randf_range(120.0, 600.0)
			var count := 2 + (rng.randi() % 3) + mini(2, info["chapter"] / 2)
			for i in range(count):
				spawns.append({
					"t": t + i * 0.32, "type": kind,
					"x": clampf(x + float(i % 2) * 80.0 - 40.0, 70.0, 650.0),
				})
			if info["chapter"] >= 3 and rng.randf() < 0.4:
				spawns.append({"t": t + 0.8, "type": "meteor", "x": rng.randf_range(90.0, 630.0)})
			t += rng.randf_range(2.6, 4.0)
		spawns.sort_custom(func(a, bb): return a["t"] < bb["t"])
		waves.append({"duration": maxf(10.0, minf(16.0, t + 4.0)), "spawns": spawns})
	return waves

static func tech_cost(key: String, level: int) -> int:
	var u: Dictionary = TECH[key]
	return int(round(float(u["base"]) * pow(float(level + 1), 1.62) / 10.0)) * 10

static func ship_level_cost(price: int, level: int) -> int:
	return int(round((price * 0.22 + 120.0 * pow(float(level), 1.55)) / 10.0)) * 10

## Chỉ số tàu cuối: cấp tàu + tech toàn cục + nội tại.
static func ship_stats(ship_id: String, ship_lvl: int, tech: Dictionary) -> Dictionary:
	var s: Dictionary = SHIPS[ship_id]
	var lvl := clampi(ship_lvl, 1, SHIP_MAX_LEVEL)
	var m_hp := 1.0 + 0.05 * (lvl - 1)
	var m_dmg := 1.0 + 0.05 * (lvl - 1)
	var m_spd := 1.0 + 0.02 * (lvl - 1)
	var shield_cap: int = 2 + int(tech.get("shield", 0)) / 3
	if s["perk"] == "shield_max+1":
		shield_cap += 1
	shield_cap = mini(5, shield_cap)
	return {
		"hp": int(round(s["hp"] * m_hp * (1.0 + 0.10 * tech.get("armor", 0)))),
		"dmg": s["dmg"] * m_dmg * (1.0 + 0.08 * tech.get("cannon", 0)),
		"speed": s["speed"] * m_spd,
		"fire_rate": s["fire_rate"],
		"shield_cap": shield_cap,
		"shield_start": mini(shield_cap, int(tech.get("shield", 0)) / 3),
		"drones": mini(3, int(tech.get("drone", 0)) / 2 + (1 if s["perk"] == "drone+1" else 0) + (2 if s["perk"] == "drone+2" else 0)),
		"magnet": POWERUP["magnet_radius"] * (1.0 + 0.12 * tech.get("magnet", 0) + (0.6 if s["perk"] == "magnet+60%" else 0.0)),
		"pierce": 1 if s["perk"] == "pierce_1" else 0,
		"weapon_start": 2 if s["perk"] == "weapon_lv2" else 1,
		"coins_bonus": 0.10 if s["perk"] == "coins+10%" else 0.0,
		"color": s["color"],
	}
