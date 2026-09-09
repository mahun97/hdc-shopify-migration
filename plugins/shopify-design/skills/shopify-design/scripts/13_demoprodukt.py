#!/usr/bin/env python3
"""Demo-Produkt anlegen und daran die Metafelder pruefen — VOR der Produktmigration.

Der Grund fuer die Reihenfolge: Ein Metafeld, das im Admin gefuellt aussieht, aber im
Theme nicht ankommt, faellt sonst erst auf, wenn dreihundert Produkte drin sind. An einem
einzigen Demo-Produkt kostet der Fehler zehn Minuten.

Geprueft wird die ganze Kette: Definition da → Wert gesetzt → Storefront-Zugriff offen
→ Theme gibt es aus.

Aufruf:
  python3 13_demoprodukt.py --pruefen
  python3 13_demoprodukt.py --anlegen
  python3 13_demoprodukt.py --theme <id> --pruefen     zusaetzlich: gibt das Theme es aus?
  python3 13_demoprodukt.py --entfernen
"""
import sys, os, json, re, subprocess, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify import zugang, gql, seiten, titel, fehler, gate, pruefe_fehler

def arg(n, pflicht=False, standard=None):
    if n in sys.argv: return sys.argv[sys.argv.index(n)+1]
    if pflicht: fehler(f'{n} fehlt')
    return standard

env = zugang(arg('--env'))
HANDLE = 'hdc-demo-pruefstueck'
TAG = 'hdc-demo'

BEISPIEL = {
 'single_line_text_field': 'Demo-Wert',
 'multi_line_text_field': 'Demo-Wert, mehrzeilig.\nZweite Zeile.',
 'rich_text_field': json.dumps({'type': 'root', 'children': [{'type': 'paragraph',
    'children': [{'type': 'text', 'value': 'Demo-Wert im Rich-Text-Feld.'}]}]}),
 'number_integer': '42', 'number_decimal': '4.2', 'boolean': 'true',
 'date': '2026-01-01', 'date_time': '2026-01-01T12:00:00Z',
 'url': 'https://example.com/demo', 'color': '#1B92CE',
 'dimension': json.dumps({'value': 10.0, 'unit': 'CENTIMETERS'}),
 'weight': json.dumps({'value': 1.0, 'unit': 'KILOGRAMS'}),
 'volume': json.dumps({'value': 1.0, 'unit': 'LITERS'}),
 'money': json.dumps({'amount': '9.90', 'currency_code': 'EUR'}),
 'json': json.dumps({'demo': True}),
 'list.single_line_text_field': json.dumps(['Demo A', 'Demo B']),
 'list.number_integer': json.dumps([1, 2]),
 'list.url': json.dumps(['https://example.com/a']),
}

def definitionen():
    d = gql(env, '''{ metafieldDefinitions(first:250, ownerType:PRODUCT){ nodes{
      key namespace name type{ name } access{ storefront } } } }''', still=True)
    if d is None: fehler('Metafeld-Definitionen nicht lesbar — Berechtigung fehlt.')
    return d['metafieldDefinitions']['nodes']

def demo_holen():
    d = gql(env, 'query($q:String!){ products(first:5, query:$q){ nodes{ id handle title '
                 'metafields(first:250){ nodes{ namespace key value } } } } }',
            {'q': f'handle:{HANDLE}'})
    n = d['products']['nodes']
    return n[0] if n else None

defs = definitionen()
ohne_zugriff = [f'{x["namespace"]}.{x["key"]}' for x in defs
                if (x.get('access') or {}).get('storefront') != 'PUBLIC_READ']
nicht_fuellbar = [x for x in defs if x['type']['name'] not in BEISPIEL]

# ---------------------------------------------------------------- entfernen
if '--entfernen' in sys.argv:
    p = demo_holen()
    if not p: fehler('Kein Demo-Produkt vorhanden.')
    titel(f'Demo-Produkt entfernen — {env["SHOP"]}')
    print(f'  {p["title"]}  ({p["handle"]})')
    gate('Demo-Produkt endgültig löschen.')
    r = gql(env, 'mutation($i:ProductDeleteInput!){ productDelete(input:$i){ userErrors{message} } }',
            {'i': {'id': p['id']}})['productDelete']
    pruefe_fehler(r, 'productDelete')
    print('\n  Gelöscht.\n'); sys.exit(0)

# ---------------------------------------------------------------- pruefen
p = demo_holen()
titel(f'Demo-Produkt und Metafelder — {env["SHOP"]}')
print(f'  {len(defs)} Metafeld-Definitionen für Produkte')
if ohne_zugriff:
    print(f'\n  ! {len(ohne_zugriff)} ohne Storefront-Zugriff — im Theme unsichtbar,')
    print( '    obwohl im Admin gefüllt. Das ist der Fehler, der sonst erst bei')
    print( '    dreihundert Produkten auffällt:')
    for k in ohne_zugriff[:10]: print(f'       {k}')
    print('    Definition auf access.storefront = PUBLIC_READ setzen.')
if nicht_fuellbar:
    print(f'\n  ? {len(nicht_fuellbar)} Felder kann das Skript nicht füllen '
          '(Referenzen auf echte Objekte):')
    for x in nicht_fuellbar[:8]: print(f'       {x["namespace"]}.{x["key"]}  {x["type"]["name"]}')
    print('    Die von Hand am Demo-Produkt setzen.')

if p:
    gesetzt = {f'{m["namespace"]}.{m["key"]}' for m in p['metafields']['nodes'] if m['value']}
    soll = {f'{x["namespace"]}.{x["key"]}' for x in defs if x['type']['name'] in BEISPIEL}
    fehlt = soll - gesetzt
    print(f'\n  Demo-Produkt: {p["title"]}  /{p["handle"]}')
    print(f'  {len(gesetzt & soll)} von {len(soll)} füllbaren Feldern gesetzt'
          + (f', {len(fehlt)} offen' if fehlt else ''))
else:
    print('\n  Kein Demo-Produkt vorhanden. Mit --anlegen erzeugen.')

# ---------------------------------------------------------------- Theme-Ausgabe
tid = arg('--theme')
if tid:
    BASIS = f"https://{env['SHOP']}/admin/api/2025-07/themes/{tid}/assets.json"
    KOPF = ['-H', f"X-Shopify-Access-Token: {env['TOKEN']}"]
    roh = ''
    for key in ('templates/product.json', 'sections/product-information.liquid',
                'sections/main-product.liquid'):
        u = f"{BASIS}?asset%5Bkey%5D={urllib.parse.quote(key, safe='')}"
        r = subprocess.run(['curl', '-sS', u] + KOPF, capture_output=True, text=True, timeout=120)
        try: roh += json.loads(r.stdout)['asset']['value']
        except Exception: pass
    genutzt, ungenutzt = [], []
    for x in defs:
        k = f'{x["namespace"]}.{x["key"]}'
        (genutzt if (k in roh or x['key'] in roh) else ungenutzt).append(k)
    print(f'\n  Im Theme ausgegeben: {len(genutzt)} von {len(defs)}')
    if ungenutzt:
        print('  Nicht ausgegeben — stehen im Admin, sieht aber niemand:')
        for k in ungenutzt[:10]: print(f'     {k}')

if '--anlegen' not in sys.argv:
    print('\n  Mit --anlegen das Demo-Produkt erzeugen und alle Felder füllen.\n')
    sys.exit(0)

# ---------------------------------------------------------------- anlegen
werte = [{'namespace': x['namespace'], 'key': x['key'], 'type': x['type']['name'],
          'value': BEISPIEL[x['type']['name']]}
         for x in defs if x['type']['name'] in BEISPIEL]
print(f'\n  Anlegen: 1 Produkt, Entwurf, Tag "{TAG}", {len(werte)} Metafelder gefüllt.')
gate(f'Demo-Produkt in {env["SHOP"]} anlegen.')
M = '''mutation($p:ProductSetInput!){ productSet(synchronous:true, input:$p){
  product{ id handle } userErrors{ message field } } }'''
eingabe = {'handle': HANDLE, 'title': 'DEMO — Prüfstück für Metafelder',
           'status': 'DRAFT', 'tags': [TAG],
           'descriptionHtml': '<p>Prüfstück. Alle Metafeld-Definitionen sind hier mit '
                              'Demo-Werten gefüllt, damit sich vor der Produktmigration '
                              'prüfen lässt, ob das Theme sie ausgibt. '
                              '<strong>Vor dem Livegang löschen.</strong></p>',
           'metafields': werte}
if p: eingabe['id'] = p['id']
d = gql(env, M, {'p': eingabe})['productSet']
pruefe_fehler(d, 'productSet')
print(f'\n  Angelegt: /{d["product"]["handle"]}  (Entwurf, nicht sichtbar)')
print('  Jetzt in der Theme-Vorschau öffnen und prüfen, ob jedes Feld erscheint.')
print('  Danach: python3 13_demoprodukt.py --entfernen — spätestens vor dem Livegang.\n')
