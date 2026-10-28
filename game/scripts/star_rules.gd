class_name StarRules
extends RefCounted

## Star awarding for the launch slice.
##
## STATIC_CONFIRMED — docs/spec/MISSIONS_STARS.md §7.3: the three tiers
## [.20, .45, .80] / [.35, .60, .98] / [.50, .80, 1.00] are the three levels of
## one mode each, and a finished run awards at most three stars.
## The denominator used by the source build is the stage enemy count; the slice
## denies a per-stage table and uses the entries it actually spawned, which is a
## documented slice decision (the counted denomimator for stages 2/3 in the spec
## is 262 and 238, i.e. exactly that kind of enemy count).

const MAX_STARS := 3

const TIERS := {
	0: [0.20, 0.45, 0.80],
	1: [0.35, 0.60, 0.98],
	2: [0.50, 0.80, 1.00],
}

# STATIC_CONFIRMED — docs/spec/MISSIONS_STARS.md / BALANCE.md §1.1b.
const DEFAULT_START_STAR_COST := 30
const DEFAULT_DELTA_STAR_COST := 50


static func tiers_for(mode: int) -> Array:
	if TIERS.has(mode):
		return TIERS[mode]
	return TIERS[0]


static func stars_for(killed: int, total_entries: int, mode: int) -> int:
	if total_entries <= 0:
		return 0
	var ratio := clampf(float(maxi(killed, 0)) / float(total_entries), 0.0, 1.0)
	var stars := 0
	for tier: float in tiers_for(mode):
		if ratio + 0.000001 >= tier:
			stars += 1
	return clampi(stars, 0, MAX_STARS)


static func next_tier_ratio(stars: int, mode: int) -> float:
	var tiers := tiers_for(mode)
	if stars < 0 or stars >= tiers.size():
		return 1.0
	return float(tiers[stars])


static func star_cost_for(stage_level: int) -> int:
	# Stage star cost grows by DeltaStarCost per level above StartStarCost.
	return DEFAULT_START_STAR_COST + DEFAULT_DELTA_STAR_COST * maxi(stage_level, 0)
