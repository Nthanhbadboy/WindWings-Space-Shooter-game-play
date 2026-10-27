#!/usr/bin/env python3
"""Assemble, not draw, review-only comparisons from pinned input PNG/JPEGs.

Each row contains one reference and one or two actual deliverables. Sprites are
fit, without distortion, to the same maximum visible-subject footprint; frames
use the same maximum frame footprint. Original contact tiles are 150px JPEGs;
therefore do NOT infer fine reference detail from enlarged 20–50px atlas crops.
A CSV index records exact source paths, source crop coordinates and SHA-256s.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# (side, wave, exact basename) resolves inside pinned trees, never other branches.
def A(wave, name): return ("A", wave, name)
def B(wave, name): return ("B", wave, name)
def sheet(name, tile, box=None, mode="subject"):
    filename = f"{name}.jpg" if name.startswith("unclassified-") else f"{name}-01.jpg"
    return ("tile", f"docs/assets/contact-sheets/{filename}", tile, box, mode)
def screen(name):
    return ("screen", f"docs/apk-analysis/ramus/2026-10-23-phone/{name}.png", None, None, "frame")

def p(label, ref, left=None, right=None):
    return (label, ref, left, right)

BOARDS = [
 ("01_w0", "W0: listing key art + scene composition", "A W0", "B W0", [
  p("Icon: compare ship finish, not a recovered store icon", sheet("ships",19), A("w0-listing","amazon_icon_large_512x512.png"), B("w0-listing-b","amazon_icon_large_512x512.png")),
  p("Scene 1: enemy formation / tutorial", screen("p_2_Game"), A("w0-listing","huawei_screenshot_1_450x800.png"), B("w0-listing-b","huawei_screenshot_1_450x800.png")),
  p("Scene 2: encounter / boss staging", screen("slow_8_Game"), A("w0-listing","huawei_screenshot_2_450x800.png"), B("w0-listing-b","huawei_screenshot_2_450x800.png")),
  p("Scene 3: player, enemies and effects", screen("p_4_Game"), A("w0-listing","huawei_screenshot_3_450x800.png"), B("w0-listing-b","huawei_screenshot_3_450x800.png")),
  p("Scene 4: beam and impact", screen("live_1_Game"), A("w0-listing","huawei_screenshot_4_450x800.png"), B("w0-listing-b","huawei_screenshot_4_450x800.png")),
 ]),
 ("02_player", "W1: player fighters and drones", "A W1", "B W1", [
  p("Ship: pointed hull and side nacelles", sheet("ships",19), A("w1-player","player_ship_01_256@ember.png"), B("w1-player-b","player_ship_01_256@solar.png")),
  p("Ship: delta fuselage", sheet("ships",3), A("w1-player","player_ship_08_256@ember.png"), B("w1-player-b","player_ship_08_256@solar.png")),
  p("Ship: broad hull and articulated wings", sheet("ships",14), A("w1-player","player_ship_13_256@ember.png"), B("w1-player-b","player_ship_13_256@solar.png")),
  p("Drone: orb and guards", sheet("drones",4), A("w1-player","player_drone_05_128@gold.png"), B("w1-player-b","player_drone_04_128@cyan.png")),
  p("Drone: twin modules", sheet("drones",7), A("w1-player","player_drone_03_128@gold.png"), B("w1-player-b","player_drone_05_128@cyan.png")),
 ]),
 ("03_enemy", "W2: enemy bodies (atlas details enlarged)", "A W2", "B W2", [
  p("Orb / central core", sheet("enemy",1), A("w2-enemy","enemy_body_orbiter01_128@teal.png"), B("w2-enemy-b","enemy_body_06_swarmling_pod_128@amber.png")),
  p("Red hull: items #2, also visible in enemy atlas", sheet("items",2), A("w2-enemy","enemy_body_shard01_128@teal.png"), B("w2-enemy-b","enemy_body_05_beetle_cruiser_128@crimson.png")),
  p("Green hull: items #3, also visible in enemy atlas", sheet("items",3), A("w2-enemy","enemy_body_saucer01_128@teal.png"), B("w2-enemy-b","enemy_body_18_phantom_hex_128@violet.png")),
  p("Narrow red dart [source atlas crop 27x28]", sheet("enemy",30,(57,63,84,91)), A("w2-enemy","enemy_body_lance01_128@teal.png"), B("w2-enemy-b","enemy_body_01_scout_dart_128@crimson.png")),
  p("AP-0067 enemy_hp: white fill / body / bar; binding unverified", sheet("enemy",2), A("w2-enemy","enemy_body_orbiter04_128@teal.png"), B("w2-enemy-b","enemy_body_22_hp_pip_bar_128@crimson.png")),
 ]),
 ("04_boss", "W3: bosses / overlap, proportion, silhouettes", "A W3", "B W3", [
  p("Layered armour / central core", sheet("bosses",2), A("w3-boss","boss_sentinel_512@ember.png"), B("w3-boss-b","boss_body_01_sovereign_s_512@crimson.png")),
  p("Circular fortress / articulated modules", sheet("bosses",6), A("w3-boss","boss_ringfort01_512@ember.png"), B("w3-boss-b","boss_body_07_chronos_mk1_512@violet.png")),
  p("Heavy mech / side cannons", sheet("bosses",13), A("w3-boss","boss_behemoth01_512@ember.png"), B("w3-boss-b","boss_body_11_colossus_mk1_512@amber.png")),
  p("Insectoid / articulated arms", sheet("bosses",14), A("w3-boss","boss_spider01_512@ember.png"), B("w3-boss-b","boss_body_05_arachnid_mk1_512@emerald.png")),
  p("Wide multi-layer wing silhouette", sheet("bosses",17), A("w3-boss","boss_mantis01_512@ember.png"), B("w3-boss-b","boss_body_09_kraken_mk1_512@crimson.png")),
 ]),
 ("05_projectiles", "W1/W2: player and enemy projectiles", "A", "B", [
  p("Player vertical laser", sheet("bullet",1), A("w1-player","player_bullet_beam_32x512@emberdim.png"), B("w1-player-b","player_bullet_beam_32x512@cyan.png")),
  p("Player plasma orb (glowing core crop)", sheet("bullet",10,(58,55,94,94)), A("w1-player","player_bullet_plasmaorb_32@emberdim.png"), B("w1-player-b","player_bullet_plasmaorb_32@cyan.png")),
  p("Enemy glowing orb", sheet("enemy",20,(48,40,101,106)), A("w2-enemy","enemy_bullet_miniorb_64@emberdim.png"), B("w2-enemy-b","enemy_bullet_10_plasma_orb_64@crimson.png")),
  p("Enemy dart / triangular warning", sheet("enemy",21,(44,39,106,108)), A("w2-enemy","enemy_bullet_arrow_64@emberdim.png"), B("w2-enemy-b","enemy_bullet_01_needle_dart_64@crimson.png")),
 ]),
 ("06_fx_items", "W4: FX and items", "A W4", "B W4 core", [
  p("Impact / explosion", sheet("bullet",20), A("w4-fx-item","fx_boom_256@paper.png"), B("w4-core-b","fx_boom_02_starburst_blast_256@solar.png")),
  p("Cross / star flare", sheet("bullet",64), A("w4-fx-item","fx_crossfire_256@paper.png"), B("w4-core-b","fx_boom_03_cross_flare_256@cyan.png")),
  p("Glowing halo", sheet("fx",44), A("w4-fx-item","fx_haloring_256@paper.png"), B("w4-core-b","fx_glow_09_tint_halo_256@cyan.png")),
  p("Round pickup / shield", sheet("items",1), A("w4-fx-item","item_cellround_128@gold.png"), B("w4-core-b","item_drop_02_shield_orb_128@cyan.png")),
  p("Power pickup (function match, not a shape identity)", sheet("items",4), A("w4-fx-item","item_fullpower_128@gold.png"), B("w4-core-b","item_drop_06_max_overdrive_128@magenta.png")),
 ]),
 ("07_b_bg", "B W4/W5: background layers and objects", "B W4 core", "B W5 full", [
  p("Background atmosphere: sky versus nebula", sheet("background",9,mode="frame"), B("w4-core-b","bg_parallax_01_sky_far_1024@cerulean.png"), B("w5-full-b","bg_ap_0090_stage_sky_normal_1024@cerulean.png")),
  p("Cloud / nebula layer: closest atmospheric analogue", sheet("background",14,mode="frame"), B("w4-core-b","bg_parallax_02_cloud_mid_1024@solar.png"), B("w5-full-b","bg_ap_0092_cumulus_cloud_cluster_1024@pearl.png")),
  p("Environment structure / surface", sheet("background",24), B("w4-core-b","bg_parallax_03_archipelago_near_1024@emerald.png"), B("w5-full-b","bg_ap_0093_carrier_bow_platform_1024@azure.png")),
  p("Planet: Earth-like", sheet("background",20), None, B("w5-full-b","bg_ap_0094_planet_earth_terra_1024@cerulean.png")),
  p("Planet: gas giant", sheet("background",43), None, B("w5-full-b","bg_ap_0096_planet_jupiter_giant_1024@solar.png")),
 ]),
 ("08_b_ui", "B W4/W5: UI icons, plates and borders", "B W4 core", "B W5 full", [
  p("Coin icon", sheet("ui",3), B("w4-core-b","ui_icon_gold_coin_64@solar.png"), B("w5-full-b","ui_ap_0181_icon_coinicon_64@solar.png")),
  p("Back navigation", sheet("ui",15), B("w4-core-b","ui_kit_back_btn_256@azure.png"), B("w5-full-b","ui_ap_0260_kit_backmap_256@azure.png")),
  p("Rank / victory crest", sheet("ui",41), B("w4-core-b","ui_kit_victory_laurel_crest_256@solar.png"), B("w5-full-b","ui_ap_0346_meta_arenamedal_256@solar.png")),
  p("Nine-slice-style frame (static image only)", sheet("ui",7), B("w4-core-b","ui_kit_frame_standard_256@azure.png"), B("w5-full-b","ui_ap_0352_meta_frame_base_256@azure.png")),
  p("Horizontal UI bar", sheet("ui",61), B("w4-core-b","ui_hud_stat_bar_secondary_256@cyan.png"), B("w5-full-b","ui_ap_0323_kit_linelock_256@azure.png")),
 ]),
 ("09_b_w5_fx", "B W5: effects (not logos or glyphs)", "B W4 core", "B W5 full", [
  p("Glow ring", sheet("fx",44), B("w4-core-b","fx_glow_09_tint_halo_256@cyan.png"), B("w5-full-b","fx_ap_0142_azure_shock_ring_256@cyan.png")),
  p("Four-point impact flare", sheet("bullet",64), B("w4-core-b","fx_boom_03_cross_flare_256@cyan.png"), B("w5-full-b","fx_ap_0145_armor_shatter_burst_256@solar.png")),
  p("Explosion / hit flash", sheet("bullet",20), B("w4-core-b","fx_boom_02_starburst_blast_256@solar.png"), B("w5-full-b","fx_ap_0088_enemy_hit_spark_128@crimson.png")),
  p("Radial flare / bloom", sheet("fx",61), B("w4-core-b","fx_boom_01_mega_nova_256@solar.png"), B("w5-full-b","fx_ap_0151_omega_boss_corona_256@magenta.png")),
 ]),
 ("10_b_w5_semantics", "B W5: identical pixels across distinct slots", "B named slot", "B other slot (same bytes)", [
  p("ShopIcon vs event-button background", sheet("ui",50), B("w5-full-b","ui_ap_0443_shop_shopicon_256@azure.png"), B("w5-full-b","ui_ap_0462_shop_btn_event_banner_256@azure.png")),
  p("Event-button background vs ShopIcon", sheet("unclassified-24",34), B("w5-full-b","ui_ap_0462_shop_btn_event_banner_256@azure.png"), B("w5-full-b","ui_ap_0443_shop_shopicon_256@azure.png")),
  p("Blink light vs tech node", sheet("unclassified-02",57), B("w5-full-b","ui_ap_0264_kit_blink_256@azure.png"), B("w5-full-b","ui_ap_0251_kit_tech_node_a_256@azure.png")),
  p("Coin pack vs individual coin", sheet("unclassified-12",14), B("w5-full-b","ui_ap_0191_icon_coin_pack_64@solar.png"), B("w5-full-b","ui_ap_0181_icon_coinicon_64@solar.png")),
 ]),
]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def find(roots: dict[str, Path], selection):
    if selection is None:
        return None, ""
    side, wave, name = selection
    matches = list((roots[side] / "art" / wave).rglob(name))
    # W1..W5 may contain identically named masters and exported sprites; audit
    # the delivered sprite, not the higher-resolution source master.
    sprite_matches = [path for path in matches if "sprites" in path.parts]
    if sprite_matches:
        matches = sprite_matches
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one {selection}; got {len(matches)}: {matches}")
    path = matches[0]
    return path, path.relative_to(roots[side]).as_posix()


def foreground_box(im: Image.Image):
    # JPEG checkerboard is dark grey; retain bright or coloured pixels and pad.
    # This is for DISPLAY CROPS ONLY, never used for art metrics or approval.
    im = im.convert("RGB")
    w,h = im.size
    xy = []
    for y in range(h):
        for x in range(w):
            rgb = im.getpixel((x,y)); mx=max(rgb); mn=min(rgb)
            if mx >= 75 or (mx >= 50 and mx-mn >= 18): xy.append((x,y))
    if not xy:
        return (0,0,w,h)
    x0=min(x for x,y in xy); x1=max(x for x,y in xy)+1
    y0=min(y for x,y in xy); y1=max(y for x,y in xy)+1
    return (max(0,x0-3),max(0,y0-3),min(w,x1+3),min(h,y1+3))


def reference(spec_root: Path, ref):
    kind, rel, number, box, mode = ref
    path = spec_root / rel
    im = Image.open(path).convert("RGB")
    if kind == "screen":
        return im, rel, (0,0,im.width,im.height), mode
    col, row = (number-1)%8, (number-1)//8
    x, y = col*150, 26+row*150
    if box:
        x0,y0,x1,y1 = box
        bounds = (x+x0,y+y0,x+x1,y+y1)
    else:
        # Excludes bottom tile number/label; keep full tile for background frames.
        bounds = (x,y,x+150,min(y+134,im.height))
    if mode == "subject" and not box:
        dx0,dy0,dx1,dy1 = foreground_box(im.crop(bounds))
        bounds = (bounds[0]+dx0,bounds[1]+dy0,bounds[0]+dx1,bounds[1]+dy1)
    return im.crop(bounds), rel, bounds, mode


def candidate(path, mode):
    im = Image.open(path).convert("RGBA")
    if mode == "subject" and im.getchannel("A").getextrema() != (255,255):
        # Use alpha > 127 to match the metric's definition of subject; include 3px AA.
        mask=im.getchannel("A").point(lambda a: 255 if a > 127 else 0)
        bb=mask.getbbox()
        if bb:
            im=im.crop((max(0,bb[0]-3),max(0,bb[1]-3),min(im.width,bb[2]+3),min(im.height,bb[3]+3)))
    return im


def fit(im: Image.Image, size: int):
    scale=size/max(im.width,im.height)
    return im.resize((max(1,round(im.width*scale)),max(1,round(im.height*scale))),Image.Resampling.LANCZOS)


def checker(size):
    im=Image.new("RGB",(size,size),(38,38,42)); d=ImageDraw.Draw(im)
    for y in range(0,size,12):
        for x in range(0,size,12):
            if ((x//12)+(y//12))%2: d.rectangle((x,y,x+11,y+11),fill=(50,50,54))
    return im


def font(size, bold=False):
    path=f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf"
    return ImageFont.truetype(path,size)


def shorten(s: str, count=31):
    return s if len(s)<=count else s[:count-3]+"..."


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec-root",type=Path,required=True)
    ap.add_argument("--a-root",type=Path,required=True)
    ap.add_argument("--b-root",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args(); args.out.mkdir(parents=True,exist_ok=True)
    roots={"A":args.a_root.resolve(),"B":args.b_root.resolve()}; spec=args.spec_root.resolve()
    index=[]
    for board_name,title,left_name,right_name,rows in BOARDS:
        width, cell, left0, top, row_h = 846, 220, 26, 99, 276
        out=Image.new("RGB",(width,top+row_h*len(rows)+40),(13,18,28));d=ImageDraw.Draw(out)
        d.text((26,14),title,fill=(241,244,249),font=font(21,True))
        d.text((26,44),"Pinned inputs | same max subject/frame footprint | reference-only, NOT game assets",fill=(188,198,210),font=font(12))
        for x,label in [(left0,"REFERENCE"),(left0+270,left_name),(left0+540,right_name)]:
            d.text((x,68),label,fill=(114,206,221),font=font(14,True))
        for n,(label,ref,left,right) in enumerate(rows,1):
            y=top+(n-1)*row_h
            d.text((left0,y),f"{n}. {label}",fill=(242,224,178),font=font(13,True))
            ref_im,ref_rel,ref_box,mode=reference(spec,ref)
            lpath,lrel=find(roots,left); rpath,rrel=find(roots,right)
            for x,im,path in ((left0,ref_im,None),(left0+270,candidate(lpath,mode) if lpath else None,lpath),(left0+540,candidate(rpath,mode) if rpath else None,rpath)):
                base=checker(cell)
                if im:
                    im=fit(im,194).convert("RGBA")
                    base.paste(im,((cell-im.width)//2,(cell-im.height)//2),im)
                else:
                    ImageDraw.Draw(base).text((36,100),"no matching asset",font=font(13),fill=(191,193,202))
                out.paste(base,(x,y+23)); d.rectangle((x,y+23,x+cell,y+23+cell),outline=(66,79,99),width=1)
            ref_caption=Path(ref_rel).name+(f" #{ref[2]}" if ref[2] else "")
            captions=[ref_caption,Path(lrel).name if lrel else "--",Path(rrel).name if rrel else "--"]
            for x,caption in zip((left0,left0+270,left0+540),captions):
                d.text((x,y+248),shorten(caption),fill=(183,193,208),font=font(10))
            index.append({"board":board_name+".png","row":n,"description":label,"reference":ref_rel,
                          "tile":ref[2] or "","reference_crop_xyxy":str(ref_box),"reference_sha256":sha(spec/ref_rel),
                          "display_mode":mode,"left_set":left[0] if left else "","left_path":lrel,
                          "left_sha256":sha(lpath) if lpath else "","right_set":right[0] if right else "",
                          "right_path":rrel,"right_sha256":sha(rpath) if rpath else ""})
        d.text((26,out.height-27),"JPEG reference is downsampled; enlarged atlas crops are silhouette evidence only.",fill=(153,165,183),font=font(11))
        target=args.out/(board_name+".png"); out.save(target,optimize=True)
        print(f"{target}: {len(rows)} rows")
    columns=["board","row","description","reference","tile","reference_crop_xyxy","reference_sha256","display_mode","left_set","left_path","left_sha256","right_set","right_path","right_sha256"]
    with (args.out/"index.csv").open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=columns,lineterminator="\n");writer.writeheader();writer.writerows(index)
    print(f"{len(index)} reference rows indexed")


if __name__ == "__main__": main()
