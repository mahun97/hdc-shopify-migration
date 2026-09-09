#!/usr/bin/env python3
"""Setzt aus den Befunden das um, was sich ohne Rueckfrage entscheiden laesst.

Grundsatz: Umgesetzt wird nur, wofuer es hier einen echten Handgriff gibt. Alles andere
wandert unveraendert in die Uebergabe — mit dem Grund, warum es liegen bleibt. Ein Befund
gilt nie als erledigt, weil ihn jemand fuer erledigbar gehalten hat.

Aufruf:
  python3 umsetzen.py --theme <id>
  python3 umsetzen.py --theme <id> --setzen
"""
import sys, os, json, glob, re, subprocess, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify import zugang, gql, seiten, titel, fehler, gate, pruefe_fehler

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
        try: return json.loads(re.sub(r'/\*.*?\*/', '', json.loads(r.stdout)['asset']['value'], flags=re.S))
        except Exception: return None
    p = json.dumps({'asset': {'key': key, 'value': json.dumps(wert, ensure_ascii=False, indent=2)}})
    r = subprocess.run(['curl','-sS','-X','PUT',BASIS]+KOPF+
                       ['-H','Content-Type: application/json','-d',p], capture_output=True, text=True, timeout=180)
    if '"asset"' not in r.stdout: fehler(r.stdout[:300])

def durchsuche(obj, typ, treffer=None):
    treffer = treffer if treffer is not None else []
    if isinstance(obj, dict):
        if obj.get('type') == typ: treffer.append(obj)
        for v in obj.values(): durchsuche(v, typ, treffer)
    elif isinstance(obj, list):
        for v in obj: durchsuche(v, typ, treffer)
    return treffer

# ---------- Handgriffe ----------
def mwst_hinweis():
    j = asset('templates/product.json')
    bl = durchsuche(j, 'price')
    if not bl: return 0, 'kein price-Block in templates/product.json'
    n = 0
    for b in bl:
        if not b.setdefault('settings', {}).get('show_tax_info'):
            b['settings']['show_tax_info'] = True; n += 1
    if n: asset('templates/product.json', j)
    return n, f'{n}× show_tax_info eingeschaltet'

def warenkorb_einschub():
    sd = asset('config/settings_data.json')
    if (sd.get('current') or {}).get('cart_type') == 'drawer': return 0, 'stand schon auf drawer'
    sd['current']['cart_type'] = 'drawer'
    asset('config/settings_data.json', sd)
    return 1, 'cart_type auf drawer'

def alt_texte():
    ANSICHT = ['Produktansicht', 'Detailansicht', 'Rueckseite', 'Anwendung',
               'Verpackung', 'Groessenvergleich']
    prod = seiten(env, 'products', 'id title media(first:20){ nodes{ id alt } }')
    M = '''mutation($id:ID!,$m:[UpdateMediaInput!]!){ productUpdateMedia(productId:$id, media:$m){
      userErrors{message} } }'''
    n = 0
    for p in prod:
        fehlt = [(i, m) for i, m in enumerate(p['media']['nodes']) if not (m.get('alt') or '').strip()]
        if not fehlt: continue
        eingaben = [{'id': m['id'],
                     'alt': f'{p["title"]} — {ANSICHT[i] if i < len(ANSICHT) else f"Ansicht {i+1}"}'}
                    for i, m in fehlt]
        d = gql(env, M, {'id': p['id'], 'm': eingaben})['productUpdateMedia']
        pruefe_fehler(d, p['title'][:30]); n += len(eingaben)
    return n, f'{n} Alt-Texte aus Produktname und Ansicht gesetzt'

HANDGRIFFE = {
    'recht-mwst-hinweis':  ('Mehrwertsteuer-Hinweis am Preis', mwst_hinweis),
    'cro-warenkorb-seite': ('Warenkorb auf Einschub', warenkorb_einschub),
    'ux-alt-texte':        ('Alt-Texte fuer Produktbilder', alt_texte),
}

# ---------- Befunde einlesen ----------
dateien = sorted(glob.glob('befunde/*.json'))
if not dateien: fehler('Kein befunde/*.json gefunden. Erst die Pruefungen laufen lassen.')
alle = []
for f in dateien:
    d = json.load(open(f))
    for p in d.get('punkte', []): p['_datei'] = f; p['_bereich'] = d.get('bereich', '?'); alle.append(p)

machbar = [p for p in alle if p['id'] in HANDGRIFFE and not p.get('erledigt')]
bleibt  = [p for p in alle if p['id'] not in HANDGRIFFE and not p.get('erledigt')]

titel(f'Umsetzung — {len(alle)} Befunde aus {len(dateien)} Pruefungen')
for p in machbar:
    print(f'  ->  {HANDGRIFFE[p["id"]][0]}   ({p["_bereich"]}, {p["schwere"]})')
falsch_markiert = [p for p in bleibt if p.get('umsetzung') == 'auto']
for p in falsch_markiert:
    print(f'  !   {p["id"]}: als automatisch markiert, aber es gibt keinen Handgriff dafuer.')
print(f'  {len(bleibt)} Punkte bleiben fuer die Uebergabe.')
if not machbar:
    print('\n  Nichts automatisch umsetzbar.\n'); sys.exit(0)
if '--setzen' not in sys.argv:
    print('\n  Mit --setzen umsetzen.\n'); sys.exit(0)

theme = gql(env, 'query($id:ID!){ theme(id:$id){ name role } }',
            {'id': f'gid://shopify/OnlineStoreTheme/{tid}'})['theme']
if theme['role'] == 'MAIN': fehler('Das ist das aktive Theme. Bitte auf einem Duplikat arbeiten.')
gate(f'{len(machbar)} Befunde in {env["SHOP"]} umsetzen.')

for p in machbar:
    name, fn = HANDGRIFFE[p['id']]
    try:
        n, notiz = fn()
        p['erledigt'] = True; p['notiz'] = notiz
        print(f'   {name}: {notiz}')
    except Exception as e:
        p['erledigt'] = False; p['notiz'] = f'fehlgeschlagen: {e}'
        print(f'   {name}: FEHLGESCHLAGEN — {e}')

for f in dateien:
    d = json.load(open(f))
    fuer_datei = {p['id']: p for p in alle if p['_datei'] == f}
    for p in d.get('punkte', []):
        q = fuer_datei.get(p['id'])
        if q and 'erledigt' in q: p['erledigt'] = q['erledigt']; p['notiz'] = q.get('notiz')
    json.dump(d, open(f, 'w'), ensure_ascii=False, indent=2)
print('\n  Befunde aktualisiert. Jetzt uebergabe.py.\n')
