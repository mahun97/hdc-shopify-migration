#!/usr/bin/env python3
"""Phase 5b — prueft die ausgefuellte Importliste, bevor irgendetwas in den Shop geht.
Aufruf: python3 3_pruefen.py [Importliste.xlsx] [--env pfad]"""
import sys, os, re, collections, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify import zugang, gql, seiten, titel, fehler
try: import openpyxl
except ImportError: fehler('openpyxl fehlt.  pip3 install openpyxl')

datei = next((a for a in sys.argv[1:] if not a.startswith('--')), 'Importliste.xlsx')
envp  = sys.argv[sys.argv.index('--env')+1] if '--env' in sys.argv else None
if not os.path.exists(datei): fehler(f'{datei} nicht gefunden.')

ws = openpyxl.load_workbook(datei).active
kopf = [c.value for c in ws[1]]
def sp(name):
    if name not in kopf: fehler(f'Spalte "{name}" fehlt in {datei}')
    return kopf.index(name)

zeilen = []
for i, row in enumerate(ws.iter_rows(min_row=3, values_only=True), start=3):
    if not any(row): continue
    zeilen.append((i, {k: row[j] for j, k in enumerate(kopf) if k}))

FEHLER, WARNUNG = [], []
def f(z, txt): FEHLER.append(f'Zeile {z:4d}  {txt}')
def w(z, txt): WARNUNG.append(f'Zeile {z:4d}  {txt}')

# --- Pflichtfelder ---
PFLICHT = ['Artikelnummer','Produkttitel','Verkaufspreis','Gewicht kg','Beschreibung','Tags','Hersteller GPSR']
for z, r in zeilen:
    for p in PFLICHT:
        if r.get(p) in (None, '', ' '): f(z, f'{p} fehlt')
    preis = r.get('Verkaufspreis')
    if preis is not None and not isinstance(preis, (int, float)):
        try: float(str(preis).replace(',', '.'))
        except ValueError: f(z, f'Verkaufspreis "{preis}" ist keine Zahl')
    g = r.get('Gewicht kg')
    if isinstance(g, (int, float)) and g == 0: w(z, 'Gewicht ist 0 — Versand rechnet falsch')

# --- SKU eindeutig ---
sk = collections.defaultdict(list)
for z, r in zeilen:
    if r.get('Artikelnummer'): sk[str(r['Artikelnummer']).strip()].append(z)
for s_, zs in sk.items():
    if len(zs) > 1: f(zs[0], f'Artikelnummer "{s_}" mehrfach vergeben (Zeilen {", ".join(map(str, zs))})')

# --- Varianten je Produkt eindeutig ---
kombi = collections.defaultdict(list)
for z, r in zeilen:
    schl = (str(r.get('Produkttitel') or '').strip(),
            str(r.get('Option 1 Wert') or '').strip(), str(r.get('Option 2 Wert') or '').strip())
    kombi[schl].append(z)
for (t, o1, o2), zs in kombi.items():
    if len(zs) > 1:
        variante = ' / '.join(x for x in (o1, o2) if x) or '(ohne Wert)'
        f(zs[0], f'"{t[:34]}" hat die Variante "{variante}" doppelt (Zeilen {", ".join(map(str, zs))})')
    if not o1 and len([k for k in kombi if k[0] == t]) > 1:
        f(zs[0], f'"{t[:34]}" hat mehrere Varianten, aber keinen Wert in Option 1')

# --- Bilder vorhanden ---
bildordner = next((d for d in ('bilder','Bilder','images') if os.path.isdir(d)), None)
if bildordner:
    vorhanden = {f_.lower() for f_ in os.listdir(bildordner)}
    for z, r in zeilen:
        b = r.get('Bilddatei')
        if b and str(b).strip().lower() not in vorhanden: f(z, f'Bilddatei "{b}" liegt nicht in {bildordner}/')
else:
    WARNUNG.append('       Kein Ordner "bilder/" gefunden — Bilddateien nicht geprüft')

# --- Tags gegen den Shop ---
env = zugang(envp)
shop_tags = {t for p in seiten(env, 'products', 'tags') for t in p['tags']}
benutzt = collections.Counter()
for z, r in zeilen:
    for t in str(r.get('Tags') or '').split(','):
        t = t.strip()
        if not t: continue
        benutzt[t] += 1
        if t not in shop_tags: w(z, f'Tag "{t}" ist im Shop noch unbekannt — Kollektion/Menü greift evtl. nicht')

titel(f'Prüfung von {datei}')
print(f'  Zeilen:            {len(zeilen)}')
print(f'  Produkte:          {len({str(r.get("Produkttitel") or "").strip() for _, r in zeilen})}')
print(f'  verwendete Tags:   {len(benutzt)}')
print(f'\n  Fehler:            {len(FEHLER)}')
print(f'  Warnungen:         {len(WARNUNG)}')
if FEHLER:
    print('\n  FEHLER — Import ist blockiert:')
    for x in FEHLER[:40]: print('   ', x)
    if len(FEHLER) > 40: print(f'    … und {len(FEHLER)-40} weitere')
if WARNUNG:
    print('\n  Warnungen — bitte ansehen, blockieren aber nicht:')
    for x in WARNUNG[:20]: print('   ', x)
    if len(WARNUNG) > 20: print(f'    … und {len(WARNUNG)-20} weitere')
if FEHLER:
    print('\n  Ergebnis: NICHT freigegeben. Bitte korrigieren und erneut prüfen.\n'); sys.exit(1)
print('\n  Ergebnis: Prüfung bestanden.')
print()
