#!/usr/bin/env python3
"""Sammelt die CRO-Punkte, die man zaehlen kann — Bildanzahl, Sackgassen-Kategorien,
fehlende Vertrauenselemente, Warenkorb-Verhalten. Schreibt befunde/cro.json.

Was ein Skript NICHT beurteilt: ob die Argumente ueberzeugen, ob die Reihenfolge der
Einwaende stimmt, ob der Preis glaubwuerdig wirkt. Das kommt aus dem Durchgang.

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

def zaehle(obj, typ):
    n = 0
    if isinstance(obj, dict):
        if obj.get('type') == typ: n += 1
        for v in obj.values(): n += zaehle(v, typ)
    elif isinstance(obj, list):
        for v in obj: n += zaehle(v, typ)
    return n

punkte = []
def merke(pid, schwere, wo, befund, empfehlung, umsetzung, befehl=None):
    punkte.append({'id': pid, 'schwere': schwere, 'wo': wo, 'befund': befund,
                   'empfehlung': empfehlung, 'umsetzung': umsetzung, 'befehl': befehl})

idx = asset('templates/index.json') or {}
prodtpl = asset('templates/product.json') or {}
fg = asset('sections/footer-group.json') or {}
hg = asset('sections/header-group.json') or {}
sd = (asset('config/settings_data.json') or {}).get('current', {})

# ---------- Produktseite: was die Entscheidung traegt ----------
prod = seiten(env, 'products',
  'handle title status descriptionHtml totalInventory tracksInventory '
  'media(first:20){ nodes{ id } } '
  'variants(first:100){ nodes{ price compareAtPrice unitPriceMeasurement{ quantityUnit } } }')
aktiv = [p for p in prod if p['status'] == 'ACTIVE']
wenig = [p['handle'] for p in aktiv if len(p['media']['nodes']) < 3]
if wenig:
    merke('cro-wenig-bilder', 'wichtig', 'Produktseite',
          f'{len(wenig)} von {len(aktiv)} aktiven Produkten haben weniger als drei Bilder.',
          'Drei Ansichten sind die Untergrenze: Produkt, Detail, Anwendung. Ein Bild verkauft nicht. '
          'Betroffen: ' + ', '.join(wenig[:8]),
          'mensch', None)
ohne_bild = [p['handle'] for p in aktiv if not p['media']['nodes']]
if ohne_bild:
    merke('cro-kein-bild', 'blocker', 'Produktseite',
          f'{len(ohne_bild)} aktive Produkte ohne Bild: ' + ', '.join(ohne_bild[:8]),
          'Ein Produkt ohne Bild wird nicht gekauft. Bis das Bild da ist, auf Entwurf setzen.',
          'mensch', None)
if not zaehle(prodtpl, 'review'):
    merke('cro-keine-bewertungen', 'wichtig', 'Produktseite',
          'Kein Bewertungsblock auf der Produktseite.',
          'Bewertungen sind der staerkste einzelne Hebel. Judge.me installieren und den App-Block einsetzen.',
          'mensch', None)
if not zaehle(prodtpl, 'product-recommendations'):
    merke('cro-keine-empfehlungen', 'wichtig', 'Produktseite',
          'Keine Produktempfehlungen unter dem Produkt.',
          'Ohne Weiterweg endet die Sitzung, wenn das Produkt nicht passt.',
          'mensch', None)

# ---------- Kategorien ohne Substanz ----------
koll = seiten(env, 'collections', 'handle title productsCount{count}')
leer = [k['title'] for k in koll if k['productsCount']['count'] == 0]
duenn = [k['title'] for k in koll if 0 < k['productsCount']['count'] < 3]
if leer:
    merke('cro-kategorie-leer', 'blocker', 'Kategorien',
          f'{len(leer)} Kategorien ohne Produkte: ' + ', '.join(leer[:6]),
          'Eine leere Kategorie ist eine Sackgasse mitten im Kaufweg. Fuellen oder aus dem Menue nehmen.',
          'mensch', None)
if duenn:
    merke('cro-kategorie-duenn', 'kosmetik', 'Kategorien',
          f'{len(duenn)} Kategorien mit ein bis zwei Produkten: ' + ', '.join(duenn[:6]),
          'Wirkt wie ein leeres Regal. Zusammenlegen, bis genug drin ist.',
          'mensch', None)

# ---------- Vertrauen und Bindung ----------
roh_fg = json.dumps(fg, ensure_ascii=False)
if 'payment-icons' not in roh_fg:
    merke('cro-keine-zahlungsicons', 'wichtig', 'Footer',
          'Keine Zahlungsanbieter-Icons im Footer.',
          'Die Icons beantworten die Frage "kann ich hier sicher zahlen" ohne einen Klick.',
          'mensch', None)
if 'social' not in roh_fg.lower():
    merke('cro-keine-social', 'kosmetik', 'Footer',
          'Keine Social-Media-Icons im Footer.',
          'Belegt, dass hinter dem Shop jemand steht.',
          'mensch', None)
if not (zaehle(idx, 'email-signup') or 'email-signup' in roh_fg):
    merke('cro-kein-newsletter', 'wichtig', 'Startseite / Footer',
          'Keine Newsletter-Anmeldung.',
          'Der groesste Teil der Besucher kauft beim ersten Mal nicht. Ohne Anmeldung sind sie weg.',
          'mensch', None)
ank = json.dumps(hg, ensure_ascii=False).lower()
if not re.search(r'versandkostenfrei|kostenloser versand|gratis versand', ank):
    merke('cro-kein-versandversprechen', 'wichtig', 'Ankuendigungsleiste',
          'In der Ankuendigungsleiste steht kein Versandversprechen.',
          'Versandkosten sind der haeufigste Abbruchgrund. Die Schwelle gehoert nach ganz oben — '
          'sofern es sie gibt. Erfinden ist keine Option.',
          'mensch', None)
if sd.get('cart_type') != 'drawer':
    merke('cro-warenkorb-seite', 'wichtig', 'Warenkorb',
          f'Warenkorb ist "{sd.get("cart_type")}", nicht Einschub.',
          'Die Warenkorbseite reisst aus dem Stoebern heraus.',
          'auto', f'shopify-design 9_checkliste.py --theme {tid} --setzen')

# ---------- Preisgestaltung ----------
ohne_anker = sum(1 for p in aktiv if not any(v.get('compareAtPrice') for v in p['variants']['nodes']))
if aktiv and ohne_anker == len(aktiv):
    merke('cro-keine-vergleichspreise', 'kosmetik', 'Preise',
          'Kein einziges Produkt hat einen Vergleichspreis.',
          'Wo es echte Streichpreise gibt, sollten sie gepflegt sein. Vergleichspreise ohne '
          'realen Vorpreis sind irrefuehrende Werbung — also nur eintragen, wo der Preis '
          'wirklich einmal gegolten hat.',
          'mensch', None)

os.makedirs('befunde', exist_ok=True)
json.dump({'bereich': 'cro', 'shop': env['SHOP'], 'theme': tid,
           'erstellt': datetime.date.today().isoformat(), 'punkte': punkte},
          open('befunde/cro.json', 'w'), ensure_ascii=False, indent=2)
titel(f'CRO-Befund — {env["SHOP"]}')
for p in punkte: print(f'  [{p["schwere"]:8s}] {p["wo"]:22s} {p["befund"]}')
if not punkte: print('  Nichts gefunden, was sich zaehlen laesst.')
print(f'\n  {len(punkte)} Punkte in befunde/cro.json.\n')
