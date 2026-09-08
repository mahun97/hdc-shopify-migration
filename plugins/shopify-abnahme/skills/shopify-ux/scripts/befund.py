#!/usr/bin/env python3
"""Sammelt die UX-Punkte, die man messen kann — Kontraste, Textmengen, Navigationstiefe,
fehlende Alt-Texte. Schreibt befunde/ux.json.

Was ein Skript NICHT sieht: ob eine Seite Sinn ergibt, ob die Reihenfolge stimmt, ob der
Text verstaendlich ist. Das kommt aus dem Browserdurchgang und wird von Hand ergaenzt.

Aufruf:  python3 befund.py --theme <id>
"""
import sys, os, json, re, subprocess, urllib.parse, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify import zugang, gql, seiten, titel, fehler

def arg(n, pflicht=False, standard=None):
    if n in sys.argv: return sys.argv[sys.argv.index(n)+1]
    if pflicht: fehler(f'{n} fehlt')
    return standard

env = zugang(arg('--env')); tid = arg('--theme', True)
BASIS = f"https://{env['SHOP']}/admin/api/2025-07/themes/{tid}/assets.json"
KOPF  = ['-H', f"X-Shopify-Access-Token: {env['TOKEN']}"]

def asset(key):
    u = f"{BASIS}?asset%5Bkey%5D={urllib.parse.quote(key, safe='')}"
    r = subprocess.run(['curl','-sS',u]+KOPF, capture_output=True, text=True, timeout=120)
    try: return json.loads(re.sub(r'/\*.*?\*/', '', json.loads(r.stdout)['asset']['value'], flags=re.S))
    except Exception: return None

# ---------- WCAG-Kontrast ----------
def kanal(c):
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def helligkeit(hexwert):
    h = (hexwert or '').strip().lstrip('#')
    if len(h) == 3: h = ''.join(c*2 for c in h)
    if not re.fullmatch(r'[0-9A-Fa-f]{6}', h or ''): return None
    r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    return 0.2126*kanal(r) + 0.7152*kanal(g) + 0.0722*kanal(b)
def kontrast(vorne, hinten):
    a, b = helligkeit(vorne), helligkeit(hinten)
    if a is None or b is None: return None
    hell, dunkel = max(a, b), min(a, b)
    return round((hell + 0.05) / (dunkel + 0.05), 2)

punkte = []
def merke(pid, schwere, wo, befund, empfehlung, umsetzung, befehl=None):
    punkte.append({'id': pid, 'schwere': schwere, 'wo': wo, 'befund': befund,
                   'empfehlung': empfehlung, 'umsetzung': umsetzung, 'befehl': befehl})

sd = asset('config/settings_data.json') or {'current': {}}
cur = sd.get('current', {})
pal = cur.get('color_palette') or {}
grund, text = pal.get('background'), pal.get('foreground')

k = kontrast(text, grund)
if k is not None and k < 4.5:
    merke('ux-kontrast-text', 'blocker', 'Farbpalette',
          f'Fliesstext auf Hintergrund hat Kontrast {k}:1 (WCAG AA verlangt 4.5:1).',
          'Textfarbe abdunkeln oder Hintergrund aufhellen, bis 4.5:1 erreicht ist.',
          'halbauto', f'7_gestaltung.py --theme {tid} --text "#…"')

for name, feld_v, feld_h in (('Primaerbutton', 'palette_primary_button_text', 'palette_primary_button_background'),
                             ('Sekundaerbutton', 'palette_secondary_button_text', 'palette_secondary_button_background')):
    v, h = cur.get(feld_v), cur.get(feld_h)
    v = pal.get(v.split('.')[-1].rstrip(' }')) if isinstance(v, str) and v.startswith('{{') else v
    h = pal.get(h.split('.')[-1].rstrip(' }')) if isinstance(h, str) and h.startswith('{{') else h
    k = kontrast(v, h)
    if k is not None and k < 3:
        merke(f'ux-kontrast-{name.lower()}', 'wichtig', 'Farbpalette',
              f'{name}: Beschriftung auf Buttonflaeche hat Kontrast {k}:1.',
              'Unter 3:1 ist auch grosse Schrift schwer lesbar. Buttonfarbe dunkler oder Text heller.',
              'mensch', None)

# ---------- Startseite: Laenge und Aufbau ----------
idx = asset('templates/index.json') or {}
ordnung = idx.get('order') or list((idx.get('sections') or {}).keys())
typen = [idx['sections'][s]['type'] for s in ordnung if s in (idx.get('sections') or {})]
if len(typen) > 12:
    merke('ux-startseite-lang', 'wichtig', 'Startseite',
          f'{len(typen)} Abschnitte auf der Startseite.',
          'Ueber zwoelf Abschnitte liest niemand zu Ende. Zusammenfassen oder auf Unterseiten verschieben.',
          'mensch', None)
if typen and typen[0] not in ('hero', 'slideshow', 'image-banner', 'layered-slideshow', 'media-with-content'):
    merke('ux-kein-hero', 'wichtig', 'Startseite',
          f'Der erste Abschnitt ist "{typen[0]}" — kein Hero.',
          'Der erste Bildschirm entscheidet. Er braucht Bild, Aussage und einen klaren Button.',
          'mensch', None)

# ---------- Navigation ----------
menues = {m['handle']: m for m in seiten(env, 'menus', 'handle title items{ title url items{ title url } }')}
haupt = menues.get('main-menu')
if haupt:
    n = len(haupt.get('items') or [])
    if n > 7:
        merke('ux-menue-breit', 'wichtig', 'Navigation',
              f'{n} Punkte in der Hauptnavigation.',
              'Ab acht Punkten scannt niemand mehr, sondern sucht. Bündeln oder in Untermenues legen.',
              'mensch', None)
    tot = [i['title'] for i in (haupt.get('items') or []) if (i.get('url') or '').rstrip('/').endswith('#')]
    if tot:
        merke('ux-menue-tot', 'blocker', 'Navigation',
              'Menuepunkte ohne Ziel: ' + ', '.join(tot),
              'Ein Menuepunkt, der nirgendwohin fuehrt, wirkt wie ein kaputter Shop.',
              'mensch', None)

# ---------- Produkte ----------
prod = seiten(env, 'products',
  'handle title descriptionHtml media(first:10){ nodes{ alt ... on MediaImage{ image{ width height } } } }')
ohne_alt = [p['handle'] for p in prod if any(not (m.get('alt') or '').strip() for m in p['media']['nodes'])]
if ohne_alt:
    merke('ux-alt-texte', 'wichtig', 'Produktbilder',
          f'{len(ohne_alt)} von {len(prod)} Produkten haben Bilder ohne Alt-Text.',
          'Alt-Texte sind das, was Screenreader vorlesen und was Google liest. Aus Produktname und Ansicht bilden.',
          'auto', 'shopify-uebergabe/scripts/alt_texte.py')
lang = [p['handle'] for p in prod if len(p['title']) > 70]
if lang:
    merke('ux-titel-lang', 'kosmetik', 'Produkte',
          f'{len(lang)} Produkttitel ueber 70 Zeichen.',
          'In der Kategorieuebersicht bricht das um und schiebt die Karten auseinander.',
          'mensch', None)
duenn = [p['handle'] for p in prod if len(re.sub(r'<[^>]+>', '', p['descriptionHtml'] or '')) < 200]
if duenn:
    merke('ux-beschreibung-duenn', 'wichtig', 'Produkte',
          f'{len(duenn)} Produkte mit unter 200 Zeichen Beschreibung.',
          'Zu wenig, um eine Kaufentscheidung zu tragen. Betroffen: ' + ', '.join(duenn[:6]),
          'mensch', None)

# ---------- Ausgabe ----------
os.makedirs('befunde', exist_ok=True)
ergebnis = {'bereich': 'ux', 'shop': env['SHOP'], 'theme': tid,
            'erstellt': datetime.date.today().isoformat(), 'punkte': punkte}
json.dump(ergebnis, open('befunde/ux.json', 'w'), ensure_ascii=False, indent=2)

titel(f'UX-Befund — {env["SHOP"]}')
if not punkte: print('  Nichts gefunden, was sich messen laesst.')
for p in punkte:
    print(f'  [{p["schwere"]:8s}] {p["wo"]:16s} {p["befund"]}')
print(f'\n  {len(punkte)} Punkte in befunde/ux.json.')
print('  Das ist die messbare Haelfte. Der Browserdurchgang gehoert dazu.\n')
