#!/usr/bin/env python3
"""Gesamt-Abnahme: laesst die drei Pruefungen nacheinander laufen und fasst zusammen.

Findet die Nachbarskills ueber den eigenen Pfad — funktioniert sowohl im Plugin-Ordner
als auch unter ~/.claude/skills/, weil die Skills dort gleich nebeneinander liegen.

Aufruf:
  python3 abnahme.py --theme <id>              nur pruefen
  python3 abnahme.py --theme <id> --stand      Zwischenstand aus vorhandenen Befunden
"""
import sys, os, json, glob, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify import zugang, titel, fehler

def arg(n, pflicht=False, standard=None):
    if n in sys.argv: return sys.argv[sys.argv.index(n)+1]
    if pflicht: fehler(f'{n} fehlt')
    return standard

HIER = os.path.dirname(os.path.abspath(__file__))
NACHBARN = os.path.dirname(os.path.dirname(HIER))
PRUEFUNGEN = [('shopify-ux', 'UX — Benutzerfuehrung'),
              ('shopify-cro', 'CRO — Verkaufspsychologie'),
              ('shopify-recht', 'Recht — Pflichtangaben')]

env = zugang(arg('--env')); tid = arg('--theme', True)
titel(f'Gesamt-Abnahme — {env["SHOP"]}')

if '--stand' not in sys.argv:
    for ordner, name in PRUEFUNGEN:
        pfad = os.path.join(NACHBARN, ordner, 'scripts', 'befund.py')
        if not os.path.exists(pfad):
            print(f'  ! {name}: {ordner} nicht gefunden — Skill installiert?'); continue
        print(f'\n  ── {name} ' + '─' * max(0, 50 - len(name)))
        r = subprocess.run([sys.executable, pfad, '--theme', tid]
                           + (['--env', arg('--env')] if arg('--env') else []),
                           capture_output=True, text=True, timeout=900)
        for zeile in (r.stdout or '').splitlines():
            if zeile.strip() and not zeile.startswith('─'): print('  ' + zeile)
        if r.returncode: print('  ' + (r.stderr or '').strip()[:400])

# ---------- Zusammenfassung ----------
dateien = sorted(glob.glob('befunde/*.json'))
if not dateien: fehler('Keine Befunde entstanden.')
alle, unklar = [], []
for f in dateien:
    d = json.load(open(f))
    unklar += d.get('unklar', [])
    for p in d.get('punkte', []): p['_bereich'] = d.get('bereich', '?'); alle.append(p)

offen = [p for p in alle if not p.get('erledigt')]
zaehler = {s: sum(1 for p in offen if p['schwere'] == s) for s in ('blocker', 'wichtig', 'kosmetik')}
titel('Stand')
print(f'  {len(alle)} Befunde aus {len(dateien)} Dateien · {len(alle)-len(offen)} erledigt')
print(f'  {zaehler["blocker"]} Blocker · {zaehler["wichtig"]} wichtig · {zaehler["kosmetik"]} kosmetisch')
if unklar: print(f'  {len(unklar)} ungeprueft (fehlende Berechtigungen)')
fehlend = [n for o, n in PRUEFUNGEN
           if not any(json.load(open(f)).get('bereich') == o.split('-')[1] for f in dateien)]
if fehlend: print(f'\n  Es fehlt: {", ".join(fehlend)}')
durchgang = [f for f in dateien if 'durchgang' in f]
print(f'\n  {"ok" if durchgang else "! "} Browserdurchgang '
      f'{"dokumentiert in " + ", ".join(durchgang) if durchgang else "fehlt — die Skripte sehen nur die messbare Haelfte"}')
print('\n  Weiter mit umsetzen.py, dann uebergabe.py.\n')
