extends Node
## Game.gd — tiến trình người chơi (save user://), tiền tệ, sao, mở khoá 60 màn.

const SAVE_PATH := "user://ww_galaxy_ace.json"

signal coins_changed(amount: int)
signal progress_changed

var data := {}

func _ready() -> void:
	load_game()

func default_data() -> Dictionary:
	return {
		"version": 1,
		"coins": 300,
		"gems": 12,
		"unlocked": 1,
		"stars": {},          # "level(int as string)" -> 1..3
		"ship_id": "striker",
		"ships": {"striker": {"owned": true, "lvl": 1}},
		"tech": {"cannon": 0, "armor": 0, "shield": 0, "drone": 0, "magnet": 0},
		"best_score": 0,
		"runs": 0,
		"last_daily": "",
		"daily_streak": 0,
	}

func load_game() -> void:
	data = default_data()
	if not FileAccess.file_exists(SAVE_PATH):
		return
	var f := FileAccess.open(SAVE_PATH, FileAccess.READ)
	if f == null:
		return
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if typeof(parsed) == TYPE_DICTIONARY:
		var d: Dictionary = parsed
		for k in data.keys():
			if d.has(k):
				data[k] = d[k]

func save_game() -> void:
	var f := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if f == null:
		return
	f.store_string(JSON.stringify(data))
	f.close()

# ---------------------------------------------------------------- tiền tệ
func add_coins(n: int) -> void:
	data["coins"] = int(data["coins"]) + maxi(0, n)
	save_game()
	coins_changed.emit(int(data["coins"]))

func spend_coins(n: int) -> bool:
	if int(data["coins"]) < n:
		return false
	data["coins"] = int(data["coins"]) - n
	save_game()
	coins_changed.emit(int(data["coins"]))
	return true

func add_gems(n: int) -> void:
	data["gems"] = int(data["gems"]) + maxi(0, n)
	save_game()

func spend_gems(n: int) -> bool:
	if int(data["gems"]) < n:
		return false
	data["gems"] = int(data["gems"]) - n
	save_game()
	return true

# ---------------------------------------------------------------- màn chơi / sao
func is_unlocked(level: int) -> bool:
	return level <= int(data["unlocked"])

func stars_of(level: int) -> int:
	return int((data["stars"] as Dictionary).get(str(level), 0))

func total_stars() -> int:
	var t := 0
	for v in (data["stars"] as Dictionary).values():
		t += int(v)
	return t

## Ghi nhận qua màn: sao (1-3), mở màn kế; trả về số sao tốt nhất.
func record_clear(level: int, stars: int) -> int:
	var best := maxi(stars_of(level), clampi(stars, 1, 3))
	var prev := stars_of(level)
	(data["stars"] as Dictionary)[str(level)] = best
	if level == int(data["unlocked"]) and level < Balance.TOTAL_LEVELS:
		data["unlocked"] = level + 1
	var gained := best - prev
	if gained > 0:
		data["gems"] = int(data["gems"]) + gained * Balance.ECONOMY["star_gem"]
	save_game()
	progress_changed.emit()
	return best

# ---------------------------------------------------------------- tàu / tech
func current_ship() -> String:
	return str(data["ship_id"])

func ship_record(id: String) -> Dictionary:
	return (data["ships"] as Dictionary).get(id, {"owned": false, "lvl": 1})

func is_owned(id: String) -> bool:
	return bool(ship_record(id)["owned"])

func ship_level(id: String) -> int:
	return int(ship_record(id)["lvl"]) if is_owned(id) else 1

func buy_ship(id: String) -> bool:
	if is_owned(id) or not Balance.SHIPS.has(id):
		return false
	if not spend_coins(int(Balance.SHIPS[id]["price"])):
		return false
	(data["ships"] as Dictionary)[id] = {"owned": true, "lvl": 1}
	data["ship_id"] = id
	save_game()
	progress_changed.emit()
	return true

func select_ship(id: String) -> bool:
	if not is_owned(id):
		return false
	data["ship_id"] = id
	save_game()
	progress_changed.emit()
	return true

func level_up_ship(id: String) -> bool:
	if not is_owned(id) or ship_level(id) >= Balance.SHIP_MAX_LEVEL:
		return false
	var cost := Balance.ship_level_cost(int(Balance.SHIPS[id]["price"]), ship_level(id))
	if not spend_coins(cost):
		return false
	((data["ships"] as Dictionary)[id] as Dictionary)["lvl"] = ship_level(id) + 1
	save_game()
	progress_changed.emit()
	return true

func buy_tech(key: String) -> bool:
	var t: Dictionary = data["tech"]
	var lvl := int(t.get(key, 0))
	if lvl >= int(Balance.TECH[key]["max"]):
		return false
	if not spend_coins(Balance.tech_cost(key, lvl)):
		return false
	t[key] = lvl + 1
	save_game()
	progress_changed.emit()
	return true

func tech_levels() -> Dictionary:
	return data["tech"]

func stats_now() -> Dictionary:
	return Balance.ship_stats(current_ship(), ship_level(current_ship()), tech_levels())

# ---------------------------------------------------------------- daily / kỷ lục
func daily_key(now := Time.get_datetime_dict_from_system()) -> String:
	return "%04d-%02d-%02d" % [now["year"], now["month"], now["day"]]

func claim_daily() -> Dictionary:
	var key := daily_key()
	if str(data["last_daily"]) == key:
		return {}
	var streak := (int(data["daily_streak"]) % 7) + 1
	var coins: int = Balance.ECONOMY["daily_coins"] + streak * Balance.ECONOMY["daily_streak_step"]
	data["last_daily"] = key
	data["daily_streak"] = streak
	add_coins(coins)
	add_gems(2 + streak / 2)
	return {"streak": streak, "coins": coins}

func record_best(score: int) -> bool:
	data["runs"] = int(data["runs"]) + 1
	if score > int(data["best_score"]):
		data["best_score"] = score
		save_game()
		return true
	save_game()
	return false

func reset_all() -> void:
	data = default_data()
	save_game()
	progress_changed.emit()
