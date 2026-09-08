#!/usr/bin/env python3
"""Rendert copy.json als Shop-Copy.html — das Zwischenasset zur Freigabe durch den Kunden.
Aufruf: python3 3_copy_ansicht.py
"""
import sys, os, json, html, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify import titel, fehler

if not os.path.exists('copy.json'): fehler('copy.json fehlt — erst 2_copy_geruest.py laufen lassen.')
c = json.load(open('copy.json'))
e = lambda s: html.escape(str(s or ''))
akzent = (c.get('farbschema') or ['#1F3864'])[0]

teile = []
def z(s=''): teile.append(s)

z(f'<title>Shop-Copy {e(c.get("marke")) or "Entwurf"}</title>')
z('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap">')
z(f'''<style>
:root{{--ground:#F1F3F6;--surface:#fff;--surface2:#F7F9FB;--ink:#15181D;--ink2:#3D4650;
--muted:#6B7684;--line:#DCE2EA;--soft:#EBEFF4;--akzent:{akzent};
--offen:#B45309;--offen-bg:#FBF2E2;--entwurf:#2C5C93;--entwurf-bg:#E8EFF7;--frei:#2E7D46;--frei-bg:#E8F3EB;}}
@media(prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--ground:#121519;--surface:#1A1E24;
--surface2:#20252C;--ink:#E9EDF2;--ink2:#C2CAD4;--muted:#909AA7;--line:#2E353F;--soft:#262C35;
--offen:#E0A44A;--offen-bg:#2B2113;--entwurf:#77A8DC;--entwurf-bg:#131F2C;--frei:#6BC088;--frei-bg:#13251A;}}}}
:root[data-theme="dark"]{{--ground:#121519;--surface:#1A1E24;--surface2:#20252C;--ink:#E9EDF2;
--ink2:#C2CAD4;--muted:#909AA7;--line:#2E353F;--soft:#262C35;
--offen:#E0A44A;--offen-bg:#2B2113;--entwurf:#77A8DC;--entwurf-bg:#131F2C;--frei:#6BC088;--frei-bg:#13251A;}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--ground);color:var(--ink);font:15px/1.6 "IBM Plex Sans",system-ui,sans-serif}}
.wrap{{max-width:880px;margin:0 auto;padding:38px 22px 70px}}
h1,h2,h3{{font-family:Archivo,sans-serif;margin:0;text-wrap:balance}}
header{{border-bottom:3px solid var(--akzent);padding-bottom:20px;margin-bottom:26px}}
.eyebrow{{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--akzent);
font-weight:600;margin-bottom:10px}}
h1{{font-size:clamp(28px,5vw,40px);font-weight:700;letter-spacing:-.02em}}
.meta{{display:flex;gap:8px 20px;flex-wrap:wrap;margin-top:14px;font-size:12.5px;color:var(--muted)}}
.meta b{{color:var(--ink2)}}
.swatches{{display:flex;gap:7px;margin-top:14px;flex-wrap:wrap}}
.sw{{width:30px;height:30px;border-radius:3px;border:1px solid var(--line)}}
.regeln{{background:var(--offen-bg);border:1px solid var(--offen);border-radius:3px;padding:14px 18px;margin:22px 0 30px}}
.regeln h3{{font-size:13px;text-transform:uppercase;letter-spacing:.07em;color:var(--offen);margin-bottom:8px}}
.regeln ul{{margin:0;padding-left:18px;color:var(--ink2);font-size:14px}}
.regeln li{{margin-bottom:5px}}
h2.seite{{font-size:21px;font-weight:600;margin:38px 0 4px;padding-top:22px;border-top:1px solid var(--line)}}
.hinweis{{color:var(--muted);font-size:13px;margin-bottom:16px}}
.block{{background:var(--surface);border:1px solid var(--soft);border-radius:3px;
box-shadow:0 1px 2px rgba(0,0,0,.05),0 8px 22px -18px rgba(0,0,0,.3);margin-bottom:12px;overflow:hidden}}
.bk{{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;padding:13px 17px 0}}
.bk h3{{font-size:14.5px;font-weight:600;flex:1}}
.st{{font-size:10.5px;letter-spacing:.06em;text-transform:uppercase;padding:2px 8px;border-radius:2px;font-weight:600}}
.st.offen{{background:var(--offen-bg);color:var(--offen)}}
.st.entwurf{{background:var(--entwurf-bg);color:var(--entwurf)}}
.st.freigegeben{{background:var(--frei-bg);color:var(--frei)}}
.quelle{{font-size:11.5px;color:var(--muted)}}
table{{width:100%;border-collapse:collapse;margin-top:11px;font-size:14px}}
th{{text-align:left;font-size:11px;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);
font-weight:600;padding:7px 17px;background:var(--surface2);border-top:1px solid var(--soft)}}
td{{padding:9px 17px;border-top:1px solid var(--soft);vertical-align:top}}
td.feld{{width:34%;color:var(--muted);font-size:13px}}
td.wert{{color:var(--ink)}}
td.wert.leer{{color:var(--offen);font-style:italic}}
.fuss{{margin-top:40px;padding:15px 18px;background:var(--surface2);border:1px solid var(--line);
border-radius:3px;font-size:13px;color:var(--muted)}}
</style>''')

z('<div class="wrap"><header>')
z('<div class="eyebrow">Zwischenasset zur Freigabe · Shop-Texte</div>')
z(f'<h1>Shop-Copy {e(c.get("marke"))}</h1>')
z('<div class="meta">')
if c.get('theme'): z(f'<span><b>Theme</b> {e(c["theme"])}</span>')
if c.get('tonalitaet'): z(f'<span><b>Tonalität</b> {e(c["tonalitaet"])}</span>')
z(f'<span><b>Stand</b> {datetime.date.today().strftime("%d.%m.%Y")}</span>')
z('</div>')
if c.get('farbschema'):
    z('<div class="swatches">' + ''.join(f'<div class="sw" style="background:{e(f)}" title="{e(f)}"></div>'
      for f in c['farbschema']) + '</div>')
z('</header>')

if c.get('harte_regeln'):
    z('<div class="regeln"><h3>Verbindliche Vorgaben für alle Texte</h3><ul>')
    for r in c['harte_regeln']: z(f'<li>{e(r)}</li>')
    z('</ul></div>')

REIHENFOLGE = ['Startseite', 'Kategorieseite', 'Produktseite', 'Unterseiten', 'Warenkorb', 'Menü']
seiten = c.get('seiten', {})
for name in REIHENFOLGE + [s for s in seiten if s not in REIHENFOLGE]:
    blocks = seiten.get(name)
    if not blocks: continue
    z(f'<h2 class="seite">{e(name)}</h2>')
    fehlend = sum(1 for b in blocks for v in b['texte'].values() if not v)
    z(f'<p class="hinweis">{len(blocks)} Abschnitte' +
      (f' · {fehlend} Felder noch offen' if fehlend else ' · vollständig') + '</p>')
    for b in blocks:
        st = b.get('status', 'offen')
        z('<div class="block"><div class="bk">')
        z(f'<h3>{e(b["section"])}</h3>')
        z(f'<span class="st {e(st)}">{e(st)}</span>')
        z(f'<span class="quelle">Konzept S.{b.get("quelle_seite","?")}</span>')
        z('</div><table>')
        z('<tr><th>Textbaustein</th><th>Inhalt</th></tr>')
        for feld, wert in b['texte'].items():
            leer = '' if wert else ' leer'
            inhalt = e(wert) if wert else 'noch offen'
            z(f'<tr><td class="feld">{e(feld)}</td><td class="wert{leer}">{inhalt}</td></tr>')
        z('</table></div>')

z('<div class="fuss">Dieses Dokument ist die Grundlage für den Theme-Aufbau. '
  'Erst nach Freigabe werden die Texte in den Shop übertragen — Korrekturen sind hier '
  'deutlich günstiger als später im Theme.</div>')
z('</div>')

open('Shop-Copy.html', 'w', encoding='utf-8').write('\n'.join(teile) + '\n')
gesamt = sum(len(b['texte']) for s in seiten.values() for b in s)
offen = sum(1 for s in seiten.values() for b in s for v in b['texte'].values() if not v)
titel('Shop-Copy.html geschrieben')
print(f'  Textfelder: {gesamt}   offen: {offen}   gefüllt: {gesamt-offen}')
print('  → als Artifact veröffentlichen und vom Kunden freigeben lassen\n')
