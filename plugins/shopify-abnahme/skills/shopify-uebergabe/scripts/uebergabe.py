#!/usr/bin/env python3
"""Fuehrt alle Befunde zusammen und schreibt Uebergabe.md — die Liste, was noch fehlt,
bis dieser Shop live gehen kann.

Vier Abschnitte, nach Zustaendigkeit sortiert, nicht nach Thema:
  1. Blocker — ohne das kein Livegang
  2. Beim Kunden — Angaben, Texte, Fotos, Entscheidungen
  3. Von Hand im Admin — geht technisch, aber nicht ueber die API
  4. Erledigt — damit nachvollziehbar ist, was gemacht wurde

Aufruf:  python3 uebergabe.py --theme <id>
"""
import sys, os, json, glob, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify import zugang, gql, titel, fehler

def arg(n, pflicht=False, standard=None):
    if n in sys.argv: return sys.argv[sys.argv.index(n)+1]
    if pflicht: fehler(f'{n} fehlt')
    return standard

env = zugang(arg('--env')); tid = arg('--theme', True)

# Punkte, die in jedem Shop vor dem Livegang anstehen und in keinem Befund auftauchen,
# weil sie ausserhalb von Theme und Katalog liegen.
IMMER = [
 ('Zahlungsanbieter aktiv und getestet', 'kunde',
  'Bankdaten und Ausweis gehen nur ueber den Shop-Inhaber. Danach eine echte Testbestellung.'),
 ('Domain verbunden und als primaer gesetzt', 'kunde',
  'Solange die myshopify-Adresse primaer ist, laufen Links und Tracking darauf.'),
 ('Bezahlter Plan gebucht', 'kunde', 'Ein Entwicklungsshop kann nicht verkaufen.'),
 ('Passwortschutz aufheben', 'hand',
  'Zum Schluss. Vorher ist der Shop fuer Suchmaschinen und Neugierige zu.'),
 ('Testbestellung durchgefuehrt', 'hand',
  'Bestellung, Bestaetigungsmail, Rechnung, Storno. Einmal komplett.'),
 ('E-Mail-Vorlagen auf das Branding angepasst', 'hand',
  'Bestellbestaetigung und Versandbenachrichtigung sind die meistgelesenen Seiten des Shops.'),
 ('Weiterleitungen der alten URLs', 'hand',
  'Nur bei einem Relaunch. Ohne sie faellt die alte Sichtbarkeit weg.'),
 ('Analytics und Consent eingerichtet', 'hand',
  'Messung erst nach Einwilligung. Beides gehoert vor den ersten Werbeklick.'),
]

dateien = sorted(glob.glob('befunde/*.json'))
if not dateien: fehler('Kein befunde/*.json. Erst die Pruefungen laufen lassen.')
alle, unklar = [], []
for f in dateien:
    d = json.load(open(f))
    unklar += [(d.get('bereich', '?'), u) for u in d.get('unklar', [])]
    for p in d.get('punkte', []):
        p['_bereich'] = d.get('bereich', '?'); alle.append(p)

BEREICH = {'ux': 'UX', 'cro': 'CRO', 'recht': 'Recht', 'durchgang': 'Durchgang'}
erledigt = [p for p in alle if p.get('erledigt')]
offen    = [p for p in alle if not p.get('erledigt')]
blocker  = [p for p in offen if p['schwere'] == 'blocker']
beim_kunden = [p for p in offen if p['schwere'] != 'blocker' and p.get('umsetzung') == 'mensch']
von_hand    = [p for p in offen if p['schwere'] != 'blocker' and p.get('umsetzung') != 'mensch']

shop = gql(env, '{ shop { name myshopifyDomain primaryDomain{ host } } }')['shop']
theme = gql(env, 'query($id:ID!){ theme(id:$id){ name role } }',
            {'id': f'gid://shopify/OnlineStoreTheme/{tid}'})['theme']

z = []
z.append(f'# Uebergabe — {shop["name"]}\n')
z.append(f'Stand {datetime.date.today().strftime("%d.%m.%Y")} · Shop `{shop["myshopifyDomain"]}` · '
         f'Domain `{shop["primaryDomain"]["host"]}` · Theme "{theme["name"]}" ({theme["role"]})\n')
z.append(f'Grundlage: {len(alle)} Befunde aus {len(dateien)} Pruefungen. '
         f'{len(erledigt)} umgesetzt, {len(offen)} offen, davon {len(blocker)} blockierend.\n')

def block(ueberschrift, einleitung, punkte):
    z.append(f'\n## {ueberschrift}\n')
    z.append(einleitung + '\n')
    if not punkte: z.append('\nNichts offen.\n'); return
    for p in punkte:
        z.append(f'\n### {p["befund"]}')
        z.append(f'\n*{BEREICH.get(p["_bereich"], p["_bereich"])} · {p["wo"]}*\n')
        z.append(f'\n{p["empfehlung"]}\n')

block('1. Blocker vor dem Livegang',
      'Solange einer dieser Punkte offen ist, geht der Shop nicht live. '
      'Die rechtlichen darunter sind keine Empfehlung, sondern Voraussetzung.', blocker)
block('2. Liegt beim Kunden',
      'Angaben, Texte, Fotos und Entscheidungen, die niemand anders treffen kann. '
      'Geschaetzte Werte waeren an dieser Stelle eine Zusage an Kaeufer.', beim_kunden)
block('3. Von Hand im Shop-Admin',
      'Technisch machbar, aber nicht ueber die Schnittstelle erreichbar.', von_hand)

z.append('\n## 4. Immer vor dem Livegang\n')
z.append('\nUnabhaengig vom Befund — diese Punkte betreffen jeden Shop.\n\n')
z.append('| Punkt | Zustaendig | Warum |\n|---|---|---|\n')
for name, wer, warum in IMMER:
    z.append(f'| {name} | {"Kunde" if wer == "kunde" else "Agentur"} | {warum} |\n')

if erledigt:
    z.append('\n## 5. Erledigt\n\n')
    for p in erledigt:
        z.append(f'- **{p["befund"]}** — {p.get("notiz") or "umgesetzt"}\n')

if unklar:
    z.append('\n## 6. Nicht pruefbar\n\n')
    z.append('Diese Punkte konnten nicht geprueft werden. Sie sind damit **nicht** in Ordnung, '
             'sondern unbekannt.\n\n')
    for b, u in unklar: z.append(f'- {BEREICH.get(b, b)}: {u}\n')

open('Uebergabe.md', 'w').write(''.join(z))
titel(f'Uebergabe — {shop["name"]}')
print(f'  {len(blocker)} Blocker · {len(beim_kunden)} beim Kunden · '
      f'{len(von_hand)} von Hand · {len(erledigt)} erledigt')
if unklar: print(f'  {len(unklar)} Punkte ungeprueft — fehlende Berechtigungen')
print('\n  Uebergabe.md geschrieben. Als Artifact veroeffentlichen und dem Kunden geben.\n')
