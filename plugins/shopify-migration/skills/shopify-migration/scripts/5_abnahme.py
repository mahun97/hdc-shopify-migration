#!/usr/bin/env python3
"""Phase 7 — prueft den Shop nach dem Import und schreibt einen Abnahmebericht.
Aufruf: python3 5_abnahme.py [--env pfad]"""
import sys, os, json, collections, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify import zugang, gql, seiten, titel

envp = sys.argv[sys.argv.index('--env')+1] if '--env' in sys.argv else None
env = zugang(envp)
Z = []
def s(t=''): Z.append(t); print(t)

prods = seiten(env, 'products', '''id title status handle descriptionHtml
  seo { title description } mediaCount { count } resourcePublicationsCount { count }
  collections(first:10){ nodes { handle } }
  variants(first:100){ nodes { sku price inventoryItem { measurement { weight { value } } } } }''')
aktiv = [p for p in prods if p['status'] == 'ACTIVE']

s(f'# Abnahmebericht  ·  {env["SHOP"]}')
s(f'Erstellt am {datetime.datetime.now().strftime("%d.%m.%Y %H:%M")}')
s()
titel('Bestand')
s(f'  Produkte gesamt         {len(prods)}')
s(f'  davon aktiv             {len(aktiv)}')
s(f'  Varianten               {sum(len(p["variants"]["nodes"]) for p in prods)}')
s()

def block(ueberschrift, treffer, hinweis=''):
    zeichen = 'OK   ' if not treffer else 'PRUEFEN'
    s(f'  [{zeichen}] {ueberschrift}: {len(treffer)}')
    if hinweis and treffer: s(f'           {hinweis}')
    for t in treffer[:10]: s(f'           · {t[:62]}')
    if len(treffer) > 10: s(f'           … und {len(treffer)-10} weitere')

titel('Prüfungen')
block('Aktive Produkte ohne Bild', [p['title'] for p in aktiv if p['mediaCount']['count'] == 0],
      'erscheinen im Shop als graue Kachel')
block('Aktiv, aber in keinem Vertriebskanal',
      [p['title'] for p in aktiv if p['resourcePublicationsCount']['count'] == 0],
      'für Kunden nicht sichtbar')
block('Aktive Produkte in keiner Kollektion',
      [p['title'] for p in aktiv if not p['collections']['nodes']],
      'über die Navigation nicht erreichbar')
block('Ohne SEO-Titel oder -Beschreibung',
      [p['title'] for p in prods if not p['seo']['title'] or not p['seo']['description']])
block('Ohne Beschreibung', [p['title'] for p in prods if not (p['descriptionHtml'] or '').strip()])

w0 = [p['title'] for p in prods for v in p['variants']['nodes']
      if (v['inventoryItem']['measurement']['weight'] or {}).get('value') in (0, 0.0)]
block('Varianten mit Gewicht 0,00 kg', sorted(set(w0)), 'gewichtsbasierter Versand rechnet falsch')

sk = collections.defaultdict(set)
for p in prods:
    for v in p['variants']['nodes']:
        if v['sku']: sk[v['sku']].add(p['title'])
block('Mehrfach vergebene Artikelnummern',
      [f'{k}  →  {", ".join(list(v)[:2])}' for k, v in sk.items() if len(v) > 1],
      'blockiert eine spätere Bestandsführung')

p0 = [f'{p["title"]} ({v["sku"] or "ohne SKU"})' for p in prods for v in p['variants']['nodes']
      if float(v['price']) == 0]
block('Varianten mit Preis 0,00', p0)

titel('Kollektionen')
for c in seiten(env, 'collections', 'title handle productsCount{count} ruleSet{ rules{ column relation condition } }'):
    leer = '   <- LEER' if c['productsCount']['count'] == 0 else ''
    s(f'  {c["title"][:34]:34s} {c["productsCount"]["count"]:4d}{leer}')

menus = gql(env, '{ menus(first:20){ nodes { handle items { title url items { title url items { title url } } } } } }', still=True)
if menus:
    tot = []
    def lauf(items, pfad=''):
        for it in items:
            p = (pfad + ' > ' if pfad else '') + it['title']
            if (it['url'] or '').endswith('#'): tot.append(p)
            lauf(it.get('items') or [], p)
    for m in menus['menus']['nodes']: lauf(m['items'])
    titel('Navigation')
    block('Menüpunkte ohne Ziel', tot)

ziel = 'Abnahmebericht.md'
open(ziel, 'w').write('\n'.join(Z) + '\n')
print(f'\n  Bericht geschrieben: {ziel}')
print('  Bitte durchgehen und mit dem Projektverantwortlichen freigeben.\n')
