#!/usr/bin/env python3
"""Prueft die Pflichtangaben eines deutschen Shops auf Vorhandensein — nicht auf Inhalt.

Das Skript stellt fest, OB eine Angabe da ist. Ob ihr Text traegt, beurteilt ein
Fachanwalt oder ein Dienst wie die IT-Recht Kanzlei. Es schreibt keine Rechtstexte und
gibt keine Rechtsauskunft.

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

def finde(obj, typ, treffer=None):
    treffer = treffer if treffer is not None else []
    if isinstance(obj, dict):
        if obj.get('type') == typ: treffer.append(obj)
        for v in obj.values(): finde(v, typ, treffer)
    elif isinstance(obj, list):
        for v in obj: finde(v, typ, treffer)
    return treffer

punkte, unklar = [], []
def merke(pid, schwere, wo, befund, empfehlung, umsetzung, befehl=None):
    punkte.append({'id': pid, 'schwere': schwere, 'wo': wo, 'befund': befund,
                   'empfehlung': empfehlung, 'umsetzung': umsetzung, 'befehl': befehl})

# ---------- 1. Richtlinien ----------
PFLICHT = {'TERMS_OF_SERVICE': 'AGB', 'REFUND_POLICY': 'Widerrufsbelehrung',
           'PRIVACY_POLICY': 'Datenschutzerklaerung', 'LEGAL_NOTICE': 'Impressum'}
d = gql(env, '{ shop { shopPolicies { type body url } } }', still=True)
if d is None:
    unklar.append('Richtlinien — Berechtigung read_legal_policies fehlt dem Token.')
else:
    da = {p['type']: p for p in d['shop']['shopPolicies']}
    seitenliste = {p['handle']: p for p in seiten(env, 'pages', 'handle title')}
    for typ, name in PFLICHT.items():
        p = da.get(typ)
        text = re.sub(r'<[^>]+>', '', (p or {}).get('body') or '').strip()
        ersatz = typ == 'LEGAL_NOTICE' and any(h in seitenliste for h in ('impressum', 'imprint'))
        if len(text) > 200 or ersatz:
            continue
        merke(f'recht-{typ.lower()}', 'blocker', 'Richtlinien',
              f'{name} fehlt oder ist praktisch leer.',
              f'{name} beim Kunden anfordern oder ueber die IT-Recht Kanzlei erzeugen lassen. '
              'Ohne diese Angabe ist der Shop abmahnbar. Selbst formulieren ist keine Loesung.',
              'mensch', None)

# ---------- 2. Preisangaben (PAngV) ----------
preis = finde(asset('templates/product.json') or {}, 'price')
if preis and not any(b.get('settings', {}).get('show_tax_info') for b in preis):
    merke('recht-mwst-hinweis', 'blocker', 'Produktseite',
          'Am Preis fehlt der Hinweis auf Mehrwertsteuer und Versandkosten.',
          'Im price-Block "show_tax_info" einschalten. § 3 PangV verlangt die Angabe, dass der '
          'Preis die Umsatzsteuer enthaelt, plus einen Verweis auf die Versandkosten.',
          'auto', 'shopify-abnahme/scripts/umsetzen.py')

prod = seiten(env, 'products',
  'handle title status variants(first:100){ nodes{ unitPriceMeasurement{ quantityUnit } } }')
aktiv = [p for p in prod if p['status'] == 'ACTIVE']
MENGE = re.compile(r'\b\d+[\.,]?\d*\s?(ml|l|liter|g|kg|gramm|kilo|stk|stueck|stück|m)\b', re.I)
verdacht = [p['handle'] for p in aktiv
            if MENGE.search(p['title']) and not any(v.get('unitPriceMeasurement') for v in p['variants']['nodes'])]
if verdacht:
    merke('recht-grundpreis', 'blocker', 'Produkte',
          f'{len(verdacht)} Produkte nennen eine Fuellmenge im Titel, haben aber keinen Grundpreis.',
          'Bei Waren nach Volumen, Gewicht, Laenge oder Flaeche verlangt § 4 PangV den Grundpreis '
          '(z. B. "12,90 € / l"). In Shopify pro Variante unter "Grundpreis" pflegen. '
          'Betroffen: ' + ', '.join(verdacht[:8]),
          'mensch', None)

# ---------- 3. Produktsicherheit (GPSR) ----------
defs = gql(env, '{ metafieldDefinitions(first:100, ownerType:PRODUCT){ nodes{ key namespace } } }', still=True)
if defs is None:
    unklar.append('Metafeld-Definitionen — Berechtigung fehlt.')
else:
    schluessel = {f"{n['namespace']}.{n['key']}" for n in defs['metafieldDefinitions']['nodes']}
    hat_gpsr = any('manufacturer' in s or 'hersteller' in s or 'gpsr' in s or 'responsible' in s
                   for s in schluessel)
    if not hat_gpsr:
        merke('recht-gpsr', 'blocker', 'Produkte',
              'Keine Metafelder fuer Herstellerangaben gefunden.',
              'Die EU-Produktsicherheitsverordnung (GPSR) verlangt seit Dezember 2024 Name und '
              'Anschrift von Hersteller und verantwortlicher Person je Produkt, sichtbar vor dem Kauf. '
              'Definitionen anlegen, Daten beim Kunden erfragen, im Theme ausgeben.',
              'mensch', None)

# ---------- 4. Cookie-Einwilligung ----------
apps = gql(env, '{ appInstallations(first:100){ nodes{ app{ title } } } }', still=True)
if apps is None:
    unklar.append('Installierte Apps — Berechtigung read_apps fehlt.')
else:
    namen = ' '.join((a['app']['title'] or '').lower() for a in apps['appInstallations']['nodes'])
    if not re.search(r'cookie|consent|beeclever|usercentrics|cookiebot|ccm', namen):
        merke('recht-cookie-banner', 'blocker', 'Gesamter Shop',
              'Keine Cookie-/Consent-App installiert.',
              'Ohne Einwilligung vor dem Setzen nicht notwendiger Cookies verstoesst der Shop gegen '
              '§ 25 TDDDG. Die im Kickoff vereinbarte App installieren und einrichten.',
              'mensch', None)

# ---------- 5. Versand und Sprachen ----------
vp = gql(env, '{ deliveryProfiles(first:10){ nodes{ name profileLocationGroups{ '
              'locationGroupZones(first:20){ nodes{ methodDefinitions(first:20){ nodes{ name } } } } } } } }',
         still=True)
if vp is None:
    unklar.append('Versandtarife — Berechtigung read_shipping fehlt.')
else:
    tarife = sum(len(z['methodDefinitions']['nodes'])
                 for p in vp['deliveryProfiles']['nodes']
                 for g in p['profileLocationGroups']
                 for z in g['locationGroupZones']['nodes'])
    if not tarife:
        merke('recht-kein-versandtarif', 'blocker', 'Versand',
              'Kein einziger Versandtarif hinterlegt.',
              'Ohne Tarif kann niemand bestellen, und die Versandkosten sind vor dem Kauf nicht '
              'erkennbar. Werte kommen vom Kunden, nicht aus der Schaetzung.',
              'mensch', None)

sprachen = gql(env, '{ shopLocales{ locale primary published } }', still=True)
if sprachen and len([s for s in sprachen['shopLocales'] if s['published']]) > 1:
    merke('recht-uebersetzte-texte', 'wichtig', 'Sprachen',
          'Der Shop ist mehrsprachig. Rechtstexte muessen in jeder veroeffentlichten Sprache vorliegen.',
          'Uebersetzungen pruefen — maschinell uebersetzte Rechtstexte sind ein eigenes Risiko '
          'und gehoeren vom selben Dienst wie das Original.',
          'mensch', None)

merke('recht-bestellbutton', 'wichtig', 'Checkout',
      'Beschriftung des Bestellbuttons pruefen.',
      '§ 312j BGB verlangt "zahlungspflichtig bestellen" oder eine gleich eindeutige Formulierung. '
      'Shopify setzt das im Standard-Checkout selbst — bei angepasstem Checkout oder eigener '
      'Sprachdatei nachsehen.',
      'mensch', None)

os.makedirs('befunde', exist_ok=True)
json.dump({'bereich': 'recht', 'shop': env['SHOP'], 'theme': tid,
           'erstellt': datetime.date.today().isoformat(), 'punkte': punkte, 'unklar': unklar},
          open('befunde/recht.json', 'w'), ensure_ascii=False, indent=2)
titel(f'Rechts-Befund — {env["SHOP"]}')
for p in punkte: print(f'  [{p["schwere"]:8s}] {p["wo"]:16s} {p["befund"]}')
for u in unklar: print(f'  [ungeprueft] {u}')
print(f'\n  {len(punkte)} Punkte in befunde/recht.json.')
print('  Geprueft wurde, OB etwas da ist. Ob der Text traegt, sagt ein Fachanwalt.\n')
