"""Offline metadata/SDF-atlas reference, not a TMP rendering preview."""
import gzip
from html import escape
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def render(contract):
    cards=[]
    for f in contract['fonts']:
        atlas=f['atlases'][0];ident=f['identity'];png=atlas['png']
        details=json.dumps(f,ensure_ascii=True,indent=2)
        cards.append(f'''<article><h2>{escape(f['name'])}</h2>
<p>{escape(ident['serialized_file'])} · MonoBehaviour #{ident['path_id']}</p>
<p>Family label: {escape(f['family'])} · {f['character_count']} character rows / {f['glyph_count']} glyphs · Static / SDFAA</p>
<img loading="lazy" src="{escape(png['path'],quote=True)}" alt="Raw SDF atlas for {escape(f['name'],quote=True)}">
<p>Atlas {atlas['source_dimensions'][0]} × {atlas['source_dimensions'][1]}, padding {f['atlas_padding']} · <a href="{escape(png['path'],quote=True)}">Original v2 PNG</a></p>
<details><summary>Raw-derived face metrics / Unicode → glyph / rectangles / fallback refs</summary><pre>{escape(details)}</pre></details></article>''')
    order=' → '.join(str(i['path_id']) for i in contract['static_chain_order'])
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>WindWings — serialized TMP font references</title><style>
body{font:15px/1.6 system-ui,sans-serif;max-width:1100px;margin:32px auto;padding:0 20px;color:#20272c;background:#f2f4f5}h1,h2{line-height:1.25}article{background:white;border:1px solid #ccd3d7;border-radius:12px;padding:20px;margin:24px 0}img{max-width:100%;max-height:520px;object-fit:contain;background:#151b24;display:block}pre{overflow:auto;max-height:400px;background:#f2f4f5;padding:12px;font-size:12px}a{color:#075fa8}.warning{background:#fff4cd;padding:16px;border-left:4px solid #a76e00}code{overflow-wrap:anywhere}</style>
<h1>Seven serialized TMP font assets</h1><p>WindWings 1.3.118 · provisional static reference · report 73.</p>
<div class="warning"><b>Not a game-font rendering preview.</b> These are original v2 SDF atlas PNGs plus serialized metadata. No Unity shader, glyph placement, kerning, rich text, RTL or shaping is executed. Browser typography is not the APK font.</div>
<p>Copy this HTML file to the root of extracted <code>assets-v2.zip</code>, beside its <code>Texture2D/</code> directory, then open offline. The Git copy has no original media and cannot show PNGs by itself. The one v2 TTF is a separate exported font program; do not invent a source-font pointer for the seven static TMP assets.</p>
<p>Settings default: #105. Asset-local ordered fallback chain: '''+order+'''. Global settings contain one null fallback entry, not an empty local chain. All seven recovered assets use static population mode 0; all source-font pointers are null.</p>
'''+''.join(cards)+'''<footer>Source: reverse-engineering/raw/font-language/ · datas/font_language_contract.json.gz. Typed owning-file identities and source hashes are retained. No original font programs or pixels are embedded in this HTML.</footer></html>\n'''


def main():
    contract=json.load(gzip.open(ROOT/'datas/font_language_contract.json.gz','rt'))
    (ROOT/'docs/assets/font-browser.html').write_text(render(contract))


if __name__=='__main__':main()
