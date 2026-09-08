#!/usr/bin/env python3
"""Schritt 6 der Checkliste — Kategorieseiten.

Prueft und setzt, was ohne Rueckfrage entscheidbar ist: Standardsortierung der
Kollektionen, ausverkaufte Artikel ans Ende, Filter- und Sortierleiste im Template,
Kategoriebanner, einheitliche Bildformate.

Aufruf:
  python3 10_kategorieseite.py --theme <id>
  python3 10_kategorieseite.py --theme <id> --sortierung BEST_SELLING --setzen
  python3 10_kategorieseite.py --theme <id> --ausverkauft-ans-ende --setzen
Sortierung: BEST_SELLING (Standard) oder CREATED_DESC (bei staendig neuen Produkten).
"""
import sys, os, json, re, subprocess, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify import zugang, gql, seiten, titel, fehler, gate, pruefe_fehler

def arg(n, pflicht=False, standard=None):
    if n in sys.argv: return sys.argv[sys.argv.index(n)+1]
    if pflicht: fehler(f'{n} fehlt')
    return standard

env = zugang(arg('--env')); tid = arg('--theme', True)
BASIS = f"https://{env['SHOP']}/admin/api/2025-07/themes/{tid}/assets.json"
KOPF  = ['-H', f"X-Shopify-Access-Token: {env['TOKEN']}"]
SETZEN = '--setzen' in sys.argv

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

def bloecke(obj, typ, treffer=None):
    treffer = treffer if treffer is not None else []
    if isinstance(obj, dict):
        if obj.get('type') == typ: treffer.append(obj)
        for v in obj.values(): bloecke(v, typ, treffer)
    elif isinstance(obj, list):
        for v in obj: bloecke(v, typ, treffer)
    return treffer

theme = gql(env, 'query($id:ID!){ theme(id:$id){ name role } }',
            {'id': f'gid://shopify/OnlineStoreTheme/{tid}'})['theme']
titel(f'Kategorieseiten — "{theme["name"]}" ({theme["role"]})')

# ---------- 1. Standardsortierung ----------
koll = seiten(env, 'collections',
  'id handle title sortOrder productsCount{count} image{url} ruleSet{appliedDisjunctively}')
soll = arg('--sortierung')
if soll and soll not in ('BEST_SELLING', 'CREATED_DESC', 'MANUAL'):
    fehler('--sortierung erwartet BEST_SELLING, CREATED_DESC oder MANUAL')

falsch = [k for k in koll if soll and k['sortOrder'] != soll]
print(f'  {len(koll)} Kollektionen, Sortierung:')
for k in sorted(koll, key=lambda x: x['title'])[:40]:
    marke = '->' if soll and k['sortOrder'] != soll else 'ok'
    print(f'   {marke} {k["title"][:38]:40s} {k["sortOrder"]:14s} {k["productsCount"]["count"]:4d} Produkte'
          f'{"" if k.get("image") else "   ohne Banner-Bild"}')
if len(koll) > 40: print(f'   … und {len(koll)-40} weitere')

# ---------- 2. Filter- und Sortierleiste ----------
tpl = asset('templates/collection.json') or {}
n_filter = len(bloecke(tpl, 'filters'))
print()
print(f'  {"ok" if n_filter else "! "} Filter- und Sortierleiste            '
      f'{"vorhanden" if n_filter else "fehlt in templates/collection.json — Block filters ergaenzen"}')
ohne_bild = [k for k in koll if not k.get('image')]
print(f'  {"ok" if not ohne_bild else "! "} Kategoriebanner                      '
      f'{"alle gesetzt" if not ohne_bild else f"{len(ohne_bild)} Kollektionen ohne Bild: " + ", ".join(k["title"] for k in ohne_bild[:5])}')

# ---------- 3. Einheitliche Bildformate ----------
prod = seiten(env, 'products',
  'handle featuredMedia{ ... on MediaImage{ image{ width height } } }')
masse, ohne = {}, []
for p in prod:
    m = (p.get('featuredMedia') or {}).get('image')
    if not m: ohne.append(p['handle']); continue
    masse[f"{m['width']}x{m['height']}"] = masse.get(f"{m['width']}x{m['height']}", 0) + 1
klein = [f for f, n in masse.items() if min(int(x) for x in f.split('x')) < 1000]
nicht_quadratisch = [f for f in masse if len(set(f.split('x'))) > 1]
print(f'  {"ok" if len(masse) <= 3 else "! "} Bildformate                          '
      f'{len(masse)} verschiedene Groessen bei {len(prod)} Produkten')
if klein: print(f'     unter 1000 px: {", ".join(sorted(klein)[:6])}')
if nicht_quadratisch: print(f'     nicht quadratisch: {", ".join(sorted(nicht_quadratisch)[:6])}')
if ohne: print(f'  !  {len(ohne)} Produkte ohne Bild: {", ".join(ohne[:5])}')

# ---------- 4. Schreiben ----------
arbeit = []
if soll and falsch: arbeit.append(('sortierung', falsch))
raus = '--ausverkauft-ans-ende' in sys.argv
manuell = [k for k in koll if k['sortOrder'] == 'MANUAL']
if raus:
    if not manuell:
        print('\n  --ausverkauft-ans-ende: keine Kollektion steht auf MANUAL.')
        print('     Nur dort laesst sich die Reihenfolge festlegen. Bei BEST_SELLING'
              '\n     sortiert Shopify selbst — dann braucht es eine App.')
    else: arbeit.append(('ausverkauft', manuell))

if not arbeit:
    print('\n  Nichts zu setzen.\n'); sys.exit(0)
print()
for art, ziel in arbeit:
    print(f'  ->  {len(ziel)} Kollektionen: '
          + ('Sortierung → ' + soll if art == 'sortierung' else 'ausverkaufte Artikel ans Ende'))
if not SETZEN:
    print('\n  Mit --setzen uebernehmen.\n'); sys.exit(0)
gate(f'{sum(len(z) for _, z in arbeit)} Kollektionen in {env["SHOP"]} aendern.')

for art, ziel in arbeit:
    if art == 'sortierung':
        M = 'mutation($i:CollectionInput!){ collectionUpdate(input:$i){ userErrors{message} } }'
        for k in ziel:
            pruefe_fehler(gql(env, M, {'i': {'id': k['id'], 'sortOrder': soll}})['collectionUpdate'], k['handle'])
            print(f'   {k["handle"]}: {k["sortOrder"]} → {soll}')
    else:
        L = '''query($id:ID!,$c:String){ collection(id:$id){ products(first:250, after:$c){
          nodes{ id title totalInventory tracksInventory }
          pageInfo{hasNextPage endCursor} } } }'''
        R = '''mutation($id:ID!,$m:[MoveInput!]!){ collectionReorderProducts(id:$id, moves:$m){
          userErrors{message} } }'''
        for k in ziel:
            c, liste = None, []
            while True:
                d = gql(env, L, {'id': k['id'], 'c': c})['collection']['products']
                liste += d['nodes']
                if not d['pageInfo']['hasNextPage']: break
                c = d['pageInfo']['endCursor']
            def leer(p): return p['tracksInventory'] and (p['totalInventory'] or 0) <= 0
            neu = [p for p in liste if not leer(p)] + [p for p in liste if leer(p)]
            if [p['id'] for p in neu] == [p['id'] for p in liste]:
                print(f'   {k["handle"]}: schon richtig'); continue
            moves = [{'id': p['id'], 'newPosition': str(i)} for i, p in enumerate(neu)]
            pruefe_fehler(gql(env, R, {'id': k['id'], 'm': moves})['collectionReorderProducts'], k['handle'])
            print(f'   {k["handle"]}: {sum(1 for p in liste if leer(p))} ausverkaufte ans Ende')
print(f'\n  Fertig. Shopify braucht fuer die Neusortierung ein paar Sekunden.\n')
