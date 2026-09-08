#!/usr/bin/env python3
"""Prueft die Theme-Einstellungen gegen die HDC-Checkliste und setzt sie auf Wunsch.

Das Skript liest zuerst das settings_schema des Themes und arbeitet nur mit
Einstellungen, die dieses Theme wirklich hat. Was es nicht gibt, meldet es als
offen — es schreibt keine Felder ins settings_data, die das Theme ignoriert.

Aufruf:
  python3 9_checkliste.py --theme <id>
  python3 9_checkliste.py --theme <id> --setzen
  python3 9_checkliste.py --theme <id> --logo logo.png --favicon favicon.png --setzen
"""
import sys, os, json, re, subprocess, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify import zugang, gql, titel, fehler, gate, bild_hochladen

def arg(n, pflicht=False, standard=None):
    if n in sys.argv: return sys.argv[sys.argv.index(n)+1]
    if pflicht: fehler(f'{n} fehlt')
    return standard

env = zugang(arg('--env')); tid = arg('--theme', True)
BASIS = f"https://{env['SHOP']}/admin/api/2025-07/themes/{tid}/assets.json"
KOPF  = ['-H', f"X-Shopify-Access-Token: {env['TOKEN']}"]

def asset(key, wert=None):
    if wert is None:
        u = f"{BASIS}?asset%5Bkey%5D={urllib.parse.quote(key, safe='')}"
        r = subprocess.run(['curl','-sS',u]+KOPF, capture_output=True, text=True, timeout=120)
        try: return json.loads(r.stdout)['asset']['value']
        except Exception: return None
    p = json.dumps({'asset': {'key': key, 'value': wert}})
    r = subprocess.run(['curl','-sS','-X','PUT',BASIS]+KOPF+
                       ['-H','Content-Type: application/json','-d',p],
                       capture_output=True, text=True, timeout=180)
    if '"asset"' not in r.stdout: fehler(r.stdout[:300])
    return True

def json_asset(key):
    roh = asset(key)
    return json.loads(re.sub(r'/\*.*?\*/', '', roh, flags=re.S)) if roh else None

theme = gql(env, 'query($id:ID!){ theme(id:$id){ name role } }',
            {'id': f'gid://shopify/OnlineStoreTheme/{tid}'})['theme']
liste = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                    'references', 'theme-checkliste.json')))

schema = json_asset('config/settings_schema.json') or []
vorhanden = {s['id'] for g in schema for s in g.get('settings', []) if s.get('id')}
sd = json_asset('config/settings_data.json') or {'current': {}}
cur = sd.setdefault('current', {})

# ---------- Bilder, falls mitgegeben ----------
bilder = {}
for flag, punkt in (('--logo', 'Logo'), ('--favicon', 'Favicon')):
    pfad = arg(flag)
    if pfad:
        if not os.path.exists(pfad): fehler(f'{flag}: {pfad} gibt es nicht')
        bilder[punkt] = pfad

titel(f'Theme-Checkliste — "{theme["name"]}" ({theme["role"]})')
offen, aenderungen, fehlend = [], [], []

for p in liste['punkte']:
    feld = next((k for k in p['kandidaten'] if k in vorhanden), None)
    if not feld:
        fehlend.append(p); print(f'  ?  {p["name"]:34s} hat dieses Theme nicht')
        continue
    ist = cur.get(feld)
    if p['soll'] == '__bild__':
        if ist: print(f'  ok {p["name"]:34s} {feld} = {str(ist)[:40]}')
        elif p['name'] in bilder: aenderungen.append((p, feld, ist, bilder[p['name']]))
        else: offen.append(p); print(f'  !  {p["name"]:34s} {feld} ist leer  (Datei mit --logo / --favicon mitgeben)')
        continue
    if ist == p['soll']: print(f'  ok {p["name"]:34s} {feld} = {json.dumps(ist)}')
    else: aenderungen.append((p, feld, ist, p['soll']))

for p, feld, ist, soll in aenderungen:
    z = f'Datei {os.path.basename(soll)}' if p['soll'] == '__bild__' else json.dumps(soll)
    print(f'  ->  {p["name"]:34s} {feld}: {json.dumps(ist) if p["soll"] != "__bild__" else "leer"} → {z}')

# ---------- Punkte, die nur in Templates sichtbar sind ----------
print()
prod = json_asset('templates/product.json') or {}
def bloecke(obj, typ, treffer=None):
    treffer = treffer if treffer is not None else []
    if isinstance(obj, dict):
        if obj.get('type') == typ: treffer.append(obj)
        for v in obj.values(): bloecke(v, typ, treffer)
    elif isinstance(obj, list):
        for v in obj: bloecke(v, typ, treffer)
    return treffer
n = len(bloecke(prod, 'accelerated-checkout'))
print(f'  {"ok" if n == 0 else "! "} Express-Checkout auf der Produktseite   '
      f'{"kein Block" if n == 0 else f"{n} Block/Bloecke in templates/product.json — bitte im Editor entfernen"}')
n = sum(len(bloecke(json_asset(f'sections/{g}.json') or {}, 'social-links'))
        for g in ('footer-group', 'header-group'))
print(f'  {"ok" if n else "! "} Social-Media-Links                      '
      f'{"im Footer gesetzt" if n else "kein Social-Block gefunden — im Theme-Editor ergaenzen"}')

if not aenderungen:
    print('\n  Nichts zu setzen.\n'); sys.exit(0)
if '--setzen' not in sys.argv:
    print(f'\n  {len(aenderungen)} Punkte offen. Mit --setzen uebernehmen.\n'); sys.exit(0)
if theme['role'] == 'MAIN':
    fehler('Das ist das aktive Theme. Bitte auf einem Duplikat arbeiten.')
gate(f'{len(aenderungen)} Theme-Einstellungen in "{theme["name"]}" ueberschreiben.')

for p, feld, ist, soll in aenderungen:
    if p['soll'] == '__bild__':
        dateiname = bild_hochladen(env, soll, p['name'] + ' ' + env['SHOP'].split('.')[0])
        cur[feld] = f'shopify://shop_images/{dateiname}'
        print(f'  {feld} = shopify://shop_images/{dateiname}')
    else:
        cur[feld] = soll
asset('config/settings_data.json', json.dumps(sd, ensure_ascii=False, indent=2))
print(f'\n  Gesetzt. Vorschau: https://{env["SHOP"]}/?preview_theme_id={tid}')
if fehlend:
    print(f'  Weiterhin von Hand: {", ".join(p["name"] for p in fehlend)}')
print()
