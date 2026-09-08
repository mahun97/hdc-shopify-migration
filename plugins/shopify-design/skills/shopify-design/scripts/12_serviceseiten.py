#!/usr/bin/env python3
"""Schritt 8 der Checkliste — Service-Seiten.

Prueft, ob FAQ, Versanddetails, Zahlungsinformationen und "Ueber uns" existieren und
im Footer verlinkt sind. Legt fehlende an — als Geruest mit [RUECKFRAGE …]-Markern,
nicht mit erfundenen Lieferzeiten, Preisen oder Firmengeschichte.

Rechtstexte (AGB, Widerruf, Datenschutz, Impressum) gehoeren NICHT hierher. Die sind
Shop-Richtlinien und kommen ueber shopify-settings vom Kunden oder vom Anwalt.

Aufruf:
  python3 12_serviceseiten.py
  python3 12_serviceseiten.py --anlegen
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify import zugang, gql, seiten, titel, fehler, gate, pruefe_fehler

def arg(n, standard=None):
    return sys.argv[sys.argv.index(n)+1] if n in sys.argv else standard

env = zugang(arg('--env'))

def frage(was):
    return (f'<p>[RÜCKFRAGE: {was} Diese Angabe kommt vom Kunden. Nicht schaetzen — '
            f'was hier steht, ist eine Zusage an die Kaeufer.]</p>')

SEITEN = [
 {'handle': 'faq', 'titel': 'Haeufige Fragen',
  'sucht': ['faq', 'haufige-fragen', 'haeufige-fragen', 'fragen'],
  'body': '<h2>Bestellung und Lieferung</h2>' + frage('Welche Fragen kommen im Support am haeufigsten?')
        + '<h2>Produkt und Anwendung</h2>' + frage('Welche Anwendungsfragen stellen Kunden regelmaessig?')
        + '<h2>Rueckgabe</h2>' + frage('Wie laeuft eine Rueckgabe konkret ab?')},
 {'handle': 'versand', 'titel': 'Versand und Lieferzeiten',
  'sucht': ['versand', 'versandinformationen', 'lieferung', 'versanddetails'],
  'body': '<h2>Versandkosten</h2>' + frage('Welche Versandkosten gelten, ab welchem Warenwert ist es versandkostenfrei?')
        + '<h2>Lieferzeit</h2>' + frage('Wie lange dauert die Lieferung im Inland, wie lange ins Ausland?')
        + '<h2>Versanddienstleister</h2>' + frage('Wer liefert, und gibt es eine Sendungsverfolgung?')},
 {'handle': 'zahlung', 'titel': 'Zahlungsarten',
  'sucht': ['zahlung', 'zahlungsarten', 'zahlungsinformationen', 'bezahlung'],
  'body': '<h2>Diese Zahlungsarten koennen Sie nutzen</h2>'
        + frage('Welche Zahlungsarten sind im Checkout wirklich freigeschaltet?')
        + '<p>Die Liste muss mit den aktiven Zahlungsanbietern uebereinstimmen. '
          'Eine Zahlungsart zu nennen, die es im Checkout nicht gibt, ist ein Abbruchgrund.</p>'},
 {'handle': 'ueber-uns', 'titel': 'Ueber uns',
  'sucht': ['ueber-uns', 'uber-uns', 'about', 'about-us', 'unternehmen'],
  'body': '<h2>Wer wir sind</h2>' + frage('Seit wann gibt es das Unternehmen, wer steht dahinter, was ist die Geschichte?')
        + '<h2>Wofuer wir stehen</h2>' + frage('Was unterscheidet euch von den Wettbewerbern — konkret, nicht "Qualitaet und Service"?')},
]

titel(f'Service-Seiten — {env["SHOP"]}')
da = seiten(env, 'pages', 'id handle title')
vorhandene = {p['handle']: p for p in da}
menues = seiten(env, 'menus', 'id handle title items{ title url }')
verlinkt = {i['url'].rstrip('/').split('/')[-1] for m in menues for i in (m.get('items') or [])}

fehlt, unverlinkt = [], []
for s in SEITEN:
    treffer = next((vorhandene[h] for h in s['sucht'] if h in vorhandene), None)
    if not treffer:
        fehlt.append(s); print(f'  !  {s["titel"]:32s} fehlt')
    elif treffer['handle'] not in verlinkt:
        unverlinkt.append(treffer)
        print(f'  -> {s["titel"]:32s} /{treffer["handle"]} — in keinem Menue verlinkt')
    else:
        print(f'  ok {s["titel"]:32s} /{treffer["handle"]}')

print()
print('  Rechtstexte (AGB, Widerruf, Datenschutz, Impressum) pruefst du mit shopify-settings —')
print('  die sind Shop-Richtlinien, keine Seiten, und werden hier nicht angefasst.')

if unverlinkt:
    print(f'\n  {len(unverlinkt)} Seiten sind nicht verlinkt. Menuepunkte legst du im Shop-Admin an')
    print('  (Onlineshop → Navigation) — das Skript fasst Menues nicht an, weil ein falsch')
    print('  gesetzter Menuepunkt sofort im Footer steht.')
if not fehlt:
    print('\n  Keine Seite anzulegen.\n'); sys.exit(0)
print(f'\n  {len(fehlt)} Seiten anzulegen: ' + ', '.join(s['titel'] for s in fehlt))
if '--anlegen' not in sys.argv:
    print('  Mit --anlegen erstellen.\n'); sys.exit(0)
gate(f'{len(fehlt)} Seiten in {env["SHOP"]} anlegen — als Geruest mit Rueckfragen, nicht fertig.')

M = '''mutation($page:PageCreateInput!){ pageCreate(page:$page){ page{ handle } userErrors{message} } }'''
for s in fehlt:
    d = gql(env, M, {'page': {'title': s['titel'], 'handle': s['handle'],
                              'body': s['body'], 'isPublished': False}})['pageCreate']
    pruefe_fehler(d, s['handle'])
    print(f'   angelegt (unveroeffentlicht): /{d["page"]["handle"]}')
print('\n  Die Seiten stehen auf "nicht sichtbar". Erst veroeffentlichen, wenn die')
print('  [RÜCKFRAGE …]-Stellen durch echte Angaben ersetzt sind.\n')
