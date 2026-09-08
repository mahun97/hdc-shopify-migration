#!/usr/bin/env python3
"""Erzeugt aus konzept.json ein leeres Copy-Geruest (copy.json).
Die Texte schreibt Claude im Gespraech - dieses Skript legt nur die Struktur an.
Aufruf: python3 2_copy_geruest.py [--marke "Name"] [--regeln "Datei mit Auflagen"]
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify import titel, fehler

if not os.path.exists('konzept.json'): fehler('konzept.json fehlt — erst 1_konzept_lesen.py laufen lassen.')
k = json.load(open('konzept.json'))
marke = sys.argv[sys.argv.index('--marke')+1] if '--marke' in sys.argv else ''
regeln = []
if '--regeln' in sys.argv:
    p = sys.argv[sys.argv.index('--regeln')+1]
    if os.path.exists(p): regeln = [z.strip() for z in open(p, encoding='utf-8') if z.strip()]

if os.path.exists('copy.json'):
    alt = json.load(open('copy.json'))
    print('  copy.json besteht bereits — vorhandene Texte bleiben erhalten.')
else:
    alt = {}
alt_texte = {}
for seite, blocks in (alt.get('seiten') or {}).items():
    for b in blocks: alt_texte[(seite, b['section'], )] = b.get('texte', {})

seiten = {}
for seite, sections in k['seitenaufbau'].items():
    seiten[seite] = []
    for s in sections:
        vorhanden = alt_texte.get((seite, s['section']), {})
        seiten[seite].append({
            'section': s['section'],
            'quelle_seite': s['quelle_seite'],
            'status': 'entwurf' if vorhanden else 'offen',
            'texte': {feld: vorhanden.get(feld, '') for feld in s['texte']},
        })

doc = {
  'marke': marke or alt.get('marke', ''),
  'tonalitaet': alt.get('tonalitaet', ''),
  'harte_regeln': regeln or alt.get('harte_regeln', []),
  'farbschema': k['farbschema'],
  'theme': k['theme_empfehlung'],
  'seiten': seiten,
}
json.dump(doc, open('copy.json', 'w'), ensure_ascii=False, indent=1)
offen = sum(1 for s in seiten.values() for b in s for v in b['texte'].values() if not v)
titel('Copy-Gerüst angelegt')
for seite, blocks in seiten.items():
    print(f'  {seite:16s} {len(blocks):2d} Sections, {sum(len(b["texte"]) for b in blocks):3d} Textfelder')
print(f'\n  {offen} Felder noch leer.')
print('  → copy.json geschrieben. Jetzt die Texte eintragen, dann 3_copy_ansicht.py\n')
