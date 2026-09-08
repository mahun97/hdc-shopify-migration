#!/usr/bin/env python3
"""Schritt 7 der Checkliste — Produktseite.

Prueft, ob die Pflichtbausteine der Produktseite vorhanden sind, und ergaenzt die
fehlenden. Texte, die niemand erfinden darf — Lieferzeit, Versandkosten, Garantie —
setzt das Skript als [RUECKFRAGE …] ein. 6_pruefung.py findet die spaeter wieder.

Aufruf:
  python3 11_produktseite.py --theme <id>
  python3 11_produktseite.py --theme <id> --ergaenzen
"""
import sys, os, json, re, subprocess, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify import zugang, gql, titel, fehler, gate

def arg(n, pflicht=False, standard=None):
    if n in sys.argv: return sys.argv[sys.argv.index(n)+1]
    if pflicht: fehler(f'{n} fehlt')
    return standard

env = zugang(arg('--env')); tid = arg('--theme', True)
BASIS = f"https://{env['SHOP']}/admin/api/2025-07/themes/{tid}/assets.json"
KOPF  = ['-H', f"X-Shopify-Access-Token: {env['TOKEN']}"]
TPL   = 'templates/' + arg('--template', False, 'product') + '.json'

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

def finde(obj, pruef, pfad=()):
    """Liefert (block, elternteil-dict-mit-blocks, schluessel) fuer den ersten Treffer."""
    if isinstance(obj, dict):
        for k in ('sections', 'blocks'):
            kinder = obj.get(k)
            if isinstance(kinder, dict):
                for kk, vv in kinder.items():
                    if pruef(vv): return vv, obj, kk
                    t = finde(vv, pruef, pfad + (kk,))
                    if t: return t
    return None

def zaehle(obj, typ):
    n = 0
    if isinstance(obj, dict):
        if obj.get('type') == typ: n += 1
        for v in obj.values(): n += zaehle(v, typ)
    elif isinstance(obj, list):
        for v in obj: n += zaehle(v, typ)
    return n

theme = gql(env, 'query($id:ID!){ theme(id:$id){ name role } }',
            {'id': f'gid://shopify/OnlineStoreTheme/{tid}'})['theme']
j = asset(TPL)
if not j: fehler(f'{TPL} nicht lesbar')
titel(f'Produktseite — "{theme["name"]}" ({theme["role"]})')

# Die Detailspalte ist der Block, der die Kaufbuttons enthaelt.
kauf = finde(j, lambda b: isinstance(b, dict) and b.get('type') == 'buy-buttons')
if not kauf: fehler(f'Kein buy-buttons-Block in {TPL} — ist das wirklich die Produktseite?')
kaufblock, spalte, kaufname = kauf
spalte.setdefault('blocks', {}); spalte.setdefault('block_order', list(spalte['blocks']))
ordnung = spalte['block_order']

RUECK = ('[RÜCKFRAGE: Lieferzeit und Versandkosten beim Kunden erfragen und hier eintragen. '
         'Nicht schaetzen — die Angabe ist nach PAngV verbindlich.]')

def nach(name, versatz=1):
    return ordnung.index(name) + versatz if name in ordnung else len(ordnung)

punkte = [
    {'name': 'Verfuegbarkeit ("Auf Lager")', 'typ': 'product-inventory',
     'warum': 'Ohne Bestandshinweis fehlt am Button die Sicherheit, dass es sofort lieferbar ist.',
     'neu': lambda: ('bestand', {'type': 'product-inventory',
                                 'settings': {'inventory_threshold': 10, 'show_inventory_quantity': False}},
                     ordnung.index(kaufname) if kaufname in ordnung else len(ordnung))},
    {'name': 'Versand- und Kostenhinweis am Button', 'typ': '__trusttext__',
     'warum': 'Lieferzeit, Versandkosten und Rueckgabe gehoeren neben den Warenkorb-Button, nicht in den Footer.',
     'neu': lambda: ('versandhinweis', {'type': 'text',
                     'settings': {'text': f'<p>{RUECK}</p>', 'width': '100%', 'max_width': 'none',
                                  'type_preset': 'rte', 'alignment': 'left', 'padding-block-start': 12}},
                     nach(kaufname))},
    {'name': 'Akkordeon (Beschreibung, Versand, Lieferumfang)', 'typ': 'accordion',
     'warum': 'Lange Fliesstexte auf der Produktseite liest niemand. Aufgeklappte Bloecke schieben den Button nach unten.',
     'neu': lambda: ('produkt_akkordeon', {'type': 'accordion', 'settings': {'dividers': True},
                     'blocks': {'row_beschreibung': {'type': '_accordion-row',
                        'settings': {'heading': 'Beschreibung', 'open_by_default': True},
                        'blocks': {'inhalt': {'type': 'product-description', 'settings': {'width': '100%'}}},
                        'block_order': ['inhalt']},
                       'row_versand': {'type': '_accordion-row',
                        'settings': {'heading': 'Versand und Lieferzeit'},
                        'blocks': {'inhalt': {'type': 'text',
                            'settings': {'text': f'<p>{RUECK}</p>', 'width': '100%'}}},
                        'block_order': ['inhalt']}},
                     'block_order': ['row_beschreibung', 'row_versand']}, len(ordnung))},
]

offen, vorhanden = [], []
for p in punkte:
    da = zaehle(spalte, p['typ']) if p['typ'] != '__trusttext__' else 0
    if p['typ'] == '__trusttext__':
        # ein Textblock direkt nach den Kaufbuttons
        i = ordnung.index(kaufname) if kaufname in ordnung else -1
        da = 1 if 0 <= i < len(ordnung) - 1 and spalte['blocks'].get(ordnung[i+1], {}).get('type') == 'text' else 0
    (vorhanden if da else offen).append(p)
    print(f'  {"ok" if da else "! "} {p["name"]}')
    if not da: print(f'       {p["warum"]}')

# ---------- Punkte ohne eigenen Block ----------
print()
n_express = zaehle(j, 'accelerated-checkout')
print(f'  {"ok" if not n_express else "->"} Express-Checkout-Buttons             '
      f'{"nicht vorhanden" if not n_express else f"{n_express} Block — springt am Warenkorb vorbei, wird entfernt"}')
haupt = j['sections'][j.get('order', list(j['sections']))[0]] if j.get('sections') else {}
sticky = None
for s in j.get('sections', {}).values():
    if s.get('type') in ('product-information', 'main-product'):
        sticky = s.get('settings', {}).get('enable_sticky_add_to_cart'); haupt = s
print(f'  {"ok" if sticky is not False else "->"} Klebender Warenkorb-Button           '
      f'{"an" if sticky is not False else "aus — auf langen Seiten verliert man den Button"}')
atc = finde(j, lambda b: isinstance(b, dict) and b.get('type') == 'add-to-cart')
stil = atc[0]['settings'].get('style_class') if atc and atc[0].get('settings') else None
print(f'  {"ok" if stil == "button" else "->"} Warenkorb-Button als Primaerfarbe    '
      f'{stil or "nicht gesetzt"} — laut Checkliste das sichtbarste Element der Seite')
n_ueber = sum(1 for s in j.get('sections', {}).values()
              if s.get('type') in ('media-with-content', 'image-with-text', 'rich-text'))
print(f'  {"ok" if n_ueber else "! "} Abschnitt "Bild mit Text" unterhalb  '
      f'{f"{n_ueber} vorhanden" if n_ueber else "fehlt — hier steht sonst nichts ueber das Unternehmen"}')
n_bew = zaehle(j, 'review')
print(f'  {"ok" if n_bew else "! "} Bewertungen                          '
      f'{"Block vorhanden" if n_bew else "kein Bewertungsblock — kommt aus der Bewertungs-App (Judge.me), von Hand einsetzen"}')

arbeit = len(offen) + n_express + (1 if stil != 'button' else 0) + (1 if sticky is False else 0)
if not arbeit:
    print('\n  Nichts zu ergaenzen.\n'); sys.exit(0)
if '--ergaenzen' not in sys.argv:
    print(f'\n  {arbeit} Punkte offen. Mit --ergaenzen uebernehmen.\n'); sys.exit(0)
if theme['role'] == 'MAIN': fehler('Das ist das aktive Theme. Bitte auf einem Duplikat arbeiten.')
gate(f'{arbeit} Bausteine in {TPL} aendern.')

for p in offen:
    name, block, pos = p['neu']()
    spalte['blocks'][name] = block
    ordnung.insert(min(pos, len(ordnung)), name)
    print(f'   ergaenzt: {p["name"]}')

def raus(obj, typ):
    n = 0
    if isinstance(obj, dict):
        b = obj.get('blocks')
        if isinstance(b, dict):
            for k in [k for k, v in b.items() if isinstance(v, dict) and v.get('type') == typ]:
                b.pop(k); n += 1
                if k in (obj.get('block_order') or []): obj['block_order'].remove(k)
        for v in obj.values(): n += raus(v, typ) if isinstance(v, (dict, list)) else 0
    elif isinstance(obj, list):
        for v in obj: n += raus(v, typ)
    return n
if n_express: print(f'   entfernt: {raus(j, "accelerated-checkout")}× Express-Checkout')
if stil != 'button': atc[0].setdefault('settings', {})['style_class'] = 'button'; print('   Warenkorb-Button auf Primaerfarbe')
if sticky is False: haupt['settings']['enable_sticky_add_to_cart'] = True; print('   klebender Warenkorb-Button an')

asset(TPL, j)
print(f'\n  Gesetzt. Vorschau: https://{env["SHOP"]}/?preview_theme_id={tid}')
print('  Die [RÜCKFRAGE …]-Marker im Template mit echten Angaben ersetzen.\n')
