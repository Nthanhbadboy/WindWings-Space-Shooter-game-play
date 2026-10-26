#!/usr/bin/env python3
"""Turn Il2CppDumper's dump.cs into a game-focused reverse-engineering report.

Reads /tmp/apk/il2cpp/dump.cs and writes Markdown into docs/apk-analysis/.
"""
from __future__ import annotations

import os
import re
import sys
from collections import Counter, defaultdict

DUMP = os.environ.get("DUMP", "/tmp/apk/il2cpp/dump.cs")
OUT = os.environ.get("OUT", "docs/apk-analysis")

DECL = re.compile(
    r"^(?:(?:public|internal|private|protected|sealed|abstract|static|readonly|partial)\s+)*"
    r"(class|struct|enum|interface)\s+([\w`<>\[\],. ]+?)(?:\s*:\s*([^/{]+))?\s*(?://.*)?$"
)
GAME_NS = ("", "SpaceShooter", "SpaceShooter.Player", "SpaceShooter.EnemySystem",
           "SpaceShooter.Bullet", "SpaceShooter.Gameplay", "SpaceShooter.SpawnSystem",
           "PVP", "GamePVP", "TuPro")

MODES = {"PlayMode", "PVPMode", "LoadBoardMode", "BoardID", "PurchaseType", "ItemType",
         "EnemyType", "RankType", "CurrencyType"}


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}GB"


def parse(text: str):
    lines = text.splitlines()
    items = []
    ns = ""
    i = 0
    while i < len(lines):
        m = re.match(r"^// Namespace: (.*)$", lines[i])
        if not m:
            i += 1
            continue
        ns = m.group(1).strip()
        if i + 1 >= len(lines):
            break
        dm = DECL.match(lines[i + 1].strip())
        if not dm:
            i += 1
            continue
        kind, name, base = dm.group(1), dm.group(2).strip(), (dm.group(3) or "").strip()
        base = base.split("//")[0].strip()
        body = [lines[i], lines[i + 1]]
        j = i + 2
        while j < len(lines) and not lines[j].startswith("// Namespace: "):
            body.append(lines[j])
            j += 1
        items.append({"ns": ns, "kind": kind, "name": name, "base": base, "body": "\n".join(body), "line": i})
        i = j
    return items


def is_game(item) -> bool:
    return item["ns"] in GAME_NS


def table(rows, header):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def class_index(classes):
    return {c["name"]: c for c in classes if c["kind"] in ("class", "struct", "interface")}


def detail(c) -> str:
    if not c:
        return ""
    return "```csharp\n" + c["body"] + "\n```\n"


def main() -> int:
    text = open(DUMP, encoding="utf-8", errors="replace").read()
    items = parse(text)
    classes = [c for c in items if c["kind"] != "enum"]
    enums = [e for e in items if e["kind"] == "enum"]
    game = [c for c in classes if is_game(c)]
    idx = class_index(classes)
    os.makedirs(OUT, exist_ok=True)

    # ---------- enums ----------
    lines = ["# Enums (game code)", "", f"Total game enums: {len([e for e in enums if is_game(e)])}", ""]
    for e in sorted([e for e in enums if is_game(e)], key=lambda e: (e["ns"], e["name"])):
        lines.append(f"## `{e['ns']}.{e['name']}`")
        lines.append("")
        lines.append("```csharp")
        lines.append(e["body"])
        lines.append("```")
        lines.append("")
    open(os.path.join(OUT, "07-enums.md"), "w").write("\n".join(lines))

    # ---------- UI map ----------
    boards = sorted([c for c in classes if re.match(r"^(Board|Popup|Tab|Cell|Screen)_", c["name"])],
                    key=lambda c: c["name"])
    groups = defaultdict(list)
    for b in boards:
        kind = "Board" if b["name"].startswith("Board_") else ("Popup" if b["name"].startswith("Popup_") else "Tab")
        groups[kind].append(b)
    ui = ["# UI screen map", "", f"- Board/Popup/Tab classes: **{len(boards)}**", ""]
    if "BoardID" in idx:
        ui += ["## BoardID enum (navigation graph)", "", "```csharp", idx["BoardID"]["body"], "```", ""]
    for kind in ("Board", "Popup", "Tab"):
        ui += [f"## {kind} screens ({len(groups[kind])})", "",
               table([[f"`{b['name']}`", b["ns"] or "(global)", b["base"][:60]] for b in groups[kind]],
                     ["class", "namespace", "base"])]
        ui.append("")
    ui += ["## Screen class details", ""]
    for b in boards:
        ui += [f"### `{b['name']}`", "", detail(b)]
    open(os.path.join(OUT, "08-ui-map.md"), "w").write("\n".join(ui))

    # ---------- gameplay systems ----------
    def pick(*names):
        return [idx[n] for n in names if n in idx]

    player_names = [c["name"] for c in game if re.match(
        r"^(Player_|Player\d|Ship|Drone_|Device|Card|Tech_|Talent|Sub_Character|Character|Player_Ingame)", c["name"])]
    enemy_names = [c["name"] for c in game if re.match(
        r"^(Boss|MiniBoss|MB\d|Enemy_|Data_Boss|Droid_|Gun_|Bullet_|Laser|Wukong|Meteor|Invader|Mothership)", c["name"])]
    economy_names = [c["name"] for c in game if re.match(
        r"^(Shop_|Board_Shop|Board_BigShop|Board_Reborn_IAP|Popup_Buy|Popup_Exchange|Popup_First|IAP_|Purchase|Data_Items|Item|Chest|Bundle|Offer|Gift|BattlePass|Season|Rank|Quest|Mission|Daily|Reward|Arena_Shop|ShipSale|ShipTrial|ShipBuffet)", c["name"])]
    pvp_names = [c["name"] for c in game if c["ns"] in ("PVP", "GamePVP") or c["name"].startswith(("Arena", "PVP", "Pvp", "Board_PVP", "Board_Arena"))]

    md = ["# Gameplay systems (from IL2CPP dump)", ""]
    md += ["## Game modes", "", detail(idx.get("GameMode")), detail(idx.get("PlayMode")), detail(idx.get("PVPMode")), ""]
    md += ["## Player / ship / drone / device classes", "",
           f"{len(player_names)} classes", "",
           table([[f"`{n}`", idx[n]["base"][:60]] for n in sorted(player_names)], ["class", "base"]), ""]
    md += ["### Key player classes", ""]
    for n in ["Player_Ingame", "Player_Attack", "Player_Attack_1", "Player_Attack_10", "Player_Ability",
              "Player_Saved_Datas", "Player_Get_Datas", "Player_Device_Saved_Datas", "Player_Sounds",
              "Player_Animations", "Ship_Physics", "Drone_Get_Datas", "Drone_Saved_Datas",
              "Device_Get_Data", "Device_Saved_Data", "DeviceStats", "Tech_Datas", "Tech_Stat", "Talent"]:
        if n in idx:
            md += [f"#### `{n}`", "", detail(idx[n])]
    md += ["## Enemy / boss classes", "",
           f"{len(enemy_names)} classes", "",
           table([[f"`{n}`", idx[n]["base"][:60]] for n in sorted(enemy_names)], ["class", "base"]), ""]
    md += ["### Boss roster (methods/fields)", "",
           table([[f"`{n}`", idx[n]["base"][:40]] for n in sorted(enemy_names) if n.startswith(("Boss", "MiniBoss", "MB"))],
                 ["class", "base"]), ""]
    md += ["### Enemy data & balance", ""]
    for n in ["Enemy_Data_Balance", "Enemy_Data", "Data_Boss", "Data_Items", "Droid_Data_Balance", "Enemy_Hp_Bar", "Enemy_Attack_Event", "Gun_Attack"]:
        if n in idx:
            md += [f"#### `{n}`", "", detail(idx[n])]
    md += ["## Economy / shop / progression classes", "",
           f"{len(economy_names)} classes", "",
           table([[f"`{n}`", idx[n]["base"][:60]] for n in sorted(economy_names)], ["class", "base"]), ""]
    md += ["### Currencies & saved profile", ""]
    for n in ["GameDatas", "IAP_Manager", "Board_ShopGems", "Board_ShopCoins", "Board_ShopEnergy", "Board_BigShop",
              "Board_BattlePass", "Board_BattlePassPro", "Board_Quest", "Popup_PremiumDailyRewards",
              "Popup_FirstPurchase", "Board_Vip", "RankManager", "SeasonRewards"]:
        if n in idx:
            md += [f"#### `{n}`", "", detail(idx[n])]
    md += ["## PvP / arena", "",
           f"{len(pvp_names)} classes", "",
           table([[f"`{n}`", idx[n]["base"][:60]] for n in sorted(set(pvp_names))], ["class", "base"]), ""]
    for n in ["ArenaManager", "ArenaConfig", "ArenaUserProfile", "Board_RoomPVP", "PVP_Player", "PlayerItemPVP", "GamePVP.PlayerItemPVPEndGame"]:
        if n in idx:
            md += [f"#### `{n}`", "", detail(idx[n])]
    md += ["## Ads / IAP / analytics", ""]
    for n in ["AdsCaller", "AdjustEventTracking", "UserDataAnalysics", "LogInFirebase", "IAPSystem"]:
        if n in idx:
            md += [f"#### `{n}`", "", detail(idx[n])]

    open(os.path.join(OUT, "06-gameplay-systems.md"), "w").write("\n".join(md))

    # ---------- numbers / configs ----------
    num = ["# Config classes, formulas and constants", "",
           "IL2CPP dumps keep field names and method signatures but not inspector values.",
           "This file lists every config surface worth reading from the serialized assets.",
           ""]
    cfg = [c for c in game if re.search(r"(_Data|_Datas|_Config|_Balance|_Settings|Data_|GameDatas|Stage_|Level|Map|Wave|Rank|ArenaConfig|Tech_Stat)", c["name"])]
    num.append(f"## Config-type classes ({len(cfg)})")
    num.append("")
    num.append(table([[f"`{c['ns']}.{c['name']}`", c["kind"], c["base"][:50]] for c in sorted(cfg, key=lambda c: c["name"])],
                     ["class", "kind", "base"]))
    num.append("")
    num += ["## Game-specific constants", ""]
    for c in sorted(game, key=lambda c: c["name"]):
        consts = [ln.strip() for ln in c["body"].splitlines()
                  if re.match(r"^\s*public const ", ln) and not re.search(r"TrimType|MaxValue|MinValue|Epsilon|Infinity|NaN|CurrentEra|WaitTimeout", ln)]
        if consts:
            num.append(f"### `{c['name']}`")
            num.append("")
            num.append("```csharp")
            num.extend(consts)
            num.append("```")
            num.append("")
    open(os.path.join(OUT, "09-numbers-and-formulas.md"), "w").write("\n".join(num))

    print("wrote 06/07/08/09 reports;", len(game), "game classes,", len(boards), "screens")
    return 0


if __name__ == "__main__":
    sys.exit(main())
