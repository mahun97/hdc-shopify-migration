#!/usr/bin/env python3
"""Prueft die Grundeinrichtung eines Shops und schreibt Einrichtungsstand.md.
Laeuft auch mit unvollstaendigen Berechtigungen - fehlende werden benannt.
Aufruf: python3 1_bestandsaufnahme.py [--env pfad]"""
import sys, os, re, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify import zugang, gql, titel

envp = sys.argv[sys.argv.index('--env')+1] if '--env' in sys.argv else None
env = zugang(envp)
Z, OFFEN, SCOPES = [], [], set()
def s(t=''): Z.append(t)

def frag(query, scope_hinweis=None):
    """Liest einen Bereich. Fehlt die Berechtigung, wird sie vermerkt statt abzubrechen."""
    d = gql(env, query, still=True)
    if d is None and scope_hinweis: SCOPES.add(scope_hinweis)
    return d

def punkt(zustand, thema, befund, todo=None):
    zeichen = {'ok':'[ OK      ]', 'fehlt':'[ FEHLT   ]', 'pruefen':'[ PRÜFEN  ]', 'offen':'[ UNKLAR  ]'}[zustand]
    s(f'{zeichen} {thema}')
    if befund: s(f'             {befund}')
    if todo:
        s(f'             → {todo}')
        OFFEN.append((zustand, thema, todo))

# ---------------------------------------------------------------- Kopf
shop = gql(env, '''{ shop { name email currencyCode ianaTimezone weightUnit
  billingAddress { company address1 zip city country } taxesIncluded taxShipping } }''')['shop']
s(f'# Einrichtungsstand · {shop["name"]}')
s(f'Geprüft am {datetime.datetime.now().strftime("%d.%m.%Y %H:%M")} · `{env["SHOP"]}`')
s()

titel_map = []
def block(name):
    s(); s(f'## {name}'); s()

# ---------------------------------------------------------------- Allgemein
block('Allgemein')
a = shop['billingAddress'] or {}
adresse = ', '.join(x for x in (a.get('company'), a.get('address1'), a.get('zip'), a.get('city'), a.get('country')) if x)
punkt('ok' if shop['email'] else 'fehlt', 'Shop-E-Mail', shop['email'] or 'nicht gesetzt')
punkt('pruefen', 'Shop-Adresse', adresse or 'nicht gesetzt',
      'Gehört dem Kunden, nicht der Agentur? Erscheint auf Rechnungen und Versandpapieren.')
punkt('ok', 'Währung / Zeitzone / Gewicht',
      f'{shop["currencyCode"]} · {shop["ianaTimezone"]} · {shop["weightUnit"]}')
punkt('ok' if shop['taxesIncluded'] else 'pruefen', 'Preise inkl. Steuer',
      'ja' if shop['taxesIncluded'] else 'nein — in der EU im B2C unüblich',
      None if shop['taxesIncluded'] else 'Prüfen, ob B2C oder B2B gemeint ist')

# ---------------------------------------------------------------- Sichtbarkeit
block('Sichtbarkeit')
ol = frag('{ onlineStore { passwordProtection { enabled } } }')
if ol:
    an = ol['onlineStore']['passwordProtection']['enabled']
    punkt('ok' if an else 'pruefen', 'Passwortschutz',
          'aktiv — der Shop ist nicht öffentlich' if an else 'AUS — der Shop ist öffentlich erreichbar',
          None if an else 'Vor Livegang bewusst prüfen')
pub = frag('{ publications(first:20){ nodes { name autoPublish } } }')
if pub:
    namen = [p['name'] for p in pub['publications']['nodes']]
    auto = [p['name'] for p in pub['publications']['nodes'] if p['autoPublish']]
    punkt('ok', 'Vertriebskanäle', ', '.join(namen) or 'keine',
          None if auto else 'Kein Kanal veröffentlicht neue Produkte automatisch — beim Import explizit publizieren')

# ---------------------------------------------------------------- Rechtliches
block('Rechtliches')
pol = frag('{ shop { shopPolicies { type title url body } } }', 'read_legal_policies')
if pol:
    da = {p['type']: p for p in pol['shop']['shopPolicies'] if (p.get('body') or '').strip()}
    PFLICHT = {'TERMS_OF_SERVICE':'AGB', 'PRIVACY_POLICY':'Datenschutzerklärung',
               'REFUND_POLICY':'Widerrufs- / Rückgabebelehrung', 'SHIPPING_POLICY':'Versandinformationen',
               'LEGAL_NOTICE':'Impressum'}
    for typ, name in PFLICHT.items():
        if typ in da:
            laenge = len(re.sub('<[^>]+>', '', da[typ]['body']))
            zustand = 'ok' if laenge > 400 else 'pruefen'
            punkt(zustand, name, f'{laenge} Zeichen',
                  'auffällig kurz — auf Vollständigkeit prüfen' if laenge <= 400 else None)
        else:
            punkt('fehlt', name, 'nicht hinterlegt', 'Text vom Kunden oder Rechtsdienstleister einholen')
else:
    punkt('offen', 'Richtlinien', 'nicht prüfbar', 'Berechtigung read_legal_policies ergänzen')

# ---------------------------------------------------------------- Versand
block('Versand und Zustellung')
dp = frag('''{ deliveryProfiles(first:10){ nodes { name default
  profileLocationGroups { locationGroupZones(first:20){ nodes { zone { name }
  methodDefinitions(first:10){ nodes { name active } } } } } } } }''', 'read_shipping')
if dp:
    zonen = 0; tarife = 0
    for p in dp['deliveryProfiles']['nodes']:
        for g in p['profileLocationGroups']:
            for z in g['locationGroupZones']['nodes']:
                zonen += 1
                tarife += len([m for m in z['methodDefinitions']['nodes'] if m['active']])
    punkt('ok' if tarife else 'fehlt', 'Versandzonen und -tarife',
          f'{zonen} Zonen, {tarife} aktive Tarife',
          None if tarife else 'Ohne Tarif kann niemand bestellen — Versandkosten vom Kunden einholen')
else:
    punkt('offen', 'Versand', 'nicht prüfbar', 'Berechtigung read_shipping ergänzen')

# ---------------------------------------------------------------- Sprachen und Märkte
block('Sprachen und Märkte')
loc = frag('{ shopLocales { locale name primary published } }', 'read_locales')
if loc:
    sp = [f"{l['name']}{' (Standard)' if l['primary'] else ''}{'' if l['published'] else ' — NICHT veröffentlicht'}"
          for l in loc['shopLocales']]
    punkt('ok', 'Sprachen', ' · '.join(sp))
else:
    punkt('offen', 'Sprachen', 'nicht prüfbar', 'Berechtigung read_locales ergänzen')
mk = frag('{ markets(first:20){ nodes { name handle status } } }', 'read_markets')
if mk:
    punkt('ok', 'Märkte', ' · '.join(f"{m['name']} ({m['status']})" for m in mk['markets']['nodes']))
else:
    punkt('offen', 'Märkte', 'nicht prüfbar', 'Berechtigung read_markets ergänzen')

# ---------------------------------------------------------------- Standorte
block('Standorte und Steuern')
lo = frag('{ locations(first:20){ nodes { name isActive address { city country } } } }', 'read_locations')
if lo:
    akt = [l for l in lo['locations']['nodes'] if l['isActive']]
    punkt('ok' if akt else 'fehlt', 'Lagerstandorte',
          ' · '.join(f"{l['name']} ({l['address']['city']})" for l in akt) or 'keiner aktiv')
else:
    punkt('offen', 'Standorte', 'nicht prüfbar', 'Berechtigung read_locations ergänzen')
punkt('pruefen', 'Versandkosten besteuert', 'ja' if shop['taxShipping'] else 'nein',
      'In DE sind Versandkosten steuerpflichtig — prüfen' if not shop['taxShipping'] else None)

# ---------------------------------------------------------------- Metafelder
block('Metafelder')
md = frag('{ metafieldDefinitions(first:100, ownerType:PRODUCT){ nodes { namespace key name access { storefront } } } }')
if md:
    eigene = [d for d in md['metafieldDefinitions']['nodes'] if not d['namespace'].startswith('shopify')]
    ohne = [f"{d['namespace']}.{d['key']}" for d in eigene if d['access']['storefront'] != 'PUBLIC_READ']
    punkt('ok' if eigene else 'pruefen', 'Eigene Produkt-Metafelder',
          ' · '.join(f"{d['namespace']}.{d['key']}" for d in eigene) or 'keine',
          f'Ohne Storefront-Zugriff (im Theme unsichtbar): {", ".join(ohne)}' if ohne else None)

# ---------------------------------------------------------------- nur manuell
block('Nur von Hand einrichtbar')
s('Diese Bereiche bietet die API nicht an. Sie gehören in die geführte Checkliste:')
s()
for name, warum in [
  ('Zahlungsanbieter', 'Onboarding mit Bankdaten und Identitätsprüfung'),
  ('Domain', 'Kauf oder Verbindung einer bestehenden Domain'),
  ('Checkout-Einstellungen', 'Felder, Pflichtangaben, Marketing-Einwilligung'),
  ('Kundenkonten', 'klassisch oder neue Kundenkonten'),
  ('E-Mail-Benachrichtigungen', 'Vorlagen und Absenderadresse'),
  ('Plan', 'Tarifwahl vor dem Livegang'),
]:
    s(f'- **{name}** — {warum}')

# ---------------------------------------------------------------- Fazit
s(); s('---'); s()
kritisch = [t for z, t, _ in OFFEN if z == 'fehlt']
s(f'**{len(OFFEN)} offene Punkte**' + (f', davon {len(kritisch)} blockierend.' if kritisch else '.'))
if SCOPES:
    s()
    s('**Nicht prüfbar mangels Berechtigung:** ' + ', '.join(f'`{x}`' for x in sorted(SCOPES)))
    s('Nachtragen und die App neu installieren, dann erneut prüfen.')

open('Einrichtungsstand.md', 'w').write('\n'.join(Z) + '\n')
print('\n'.join(Z))
print(f'\n  → Einrichtungsstand.md geschrieben\n')
