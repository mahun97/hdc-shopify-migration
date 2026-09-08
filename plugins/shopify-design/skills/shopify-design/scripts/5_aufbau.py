#!/usr/bin/env python3
"""Baut ein Template aus freigegebener Copy und Theme-Inventar zusammen.
Arbeitet immer auf einem Theme-Duplikat, nie auf dem aktiven.
Aufruf:
  python3 5_aufbau.py --seite Startseite --template index --theme <id> --zuordnung <datei.json>
  ... --trocken     zeigt nur, was gebaut wuerde
"""
import sys, os, json, re, random, string, subprocess, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify import zugang, gql, titel, fehler, gate

def arg(name, pflicht=True, standard=None):
    if name in sys.argv: return sys.argv[sys.argv.index(name)+1]
    if pflicht: fehler(f'{name} fehlt')
    return standard

env      = zugang(arg('--env', False))
seite    = arg('--seite')
template = arg('--template', False, 'index')
tid      = arg('--theme')
zdatei   = arg('--zuordnung')
TROCKEN  = '--trocken' in sys.argv

for f in ('copy.json',):
    if not os.path.exists(f): fehler(f'{f} fehlt.')
copy = json.load(open('copy.json'))
zu   = json.load(open(zdatei))
if seite not in copy.get('seiten', {}): fehler(f'Seite "{seite}" nicht in copy.json')

nicht_frei = [b['section'] for b in copy['seiten'][seite] if b.get('status') != 'freigegeben']
if nicht_frei:
    print(f'\n  ACHTUNG: {len(nicht_frei)} Abschnitte sind noch nicht freigegeben.')
    for n in nicht_frei[:4]: print(f'    · {n[:64]}')

def id_(praefix):
    return praefix + '_' + ''.join(random.choices(string.ascii_letters + string.digits, k=6))

def finde_section(beschreibung):
    b = beschreibung.lower()
    for regel in zu['erkennung']:
        if any(w in b for w in regel['enthaelt']):
            return regel['section'], regel.get('grund')
    return None, 'keine Zuordnung hinterlegt'

sections, ordnung, uebersprungen = {}, [], []

def fuellen(knoten, texte):
    """Setzt {{Feldname}} durch den Text. Bloecke, deren Platzhalter leer bleibt, fallen weg —
    Horizon verschachtelt Bloecke, deshalb rekursiv."""
    if isinstance(knoten, dict):
        out = {}
        for k, v in knoten.items():
            if k == 'blocks' and isinstance(v, dict):
                kinder, behalten = {}, []
                for bid, block in v.items():
                    gefuellt = fuellen(block, texte)
                    if gefuellt is None: continue
                    kinder[bid] = gefuellt; behalten.append(bid)
                out['blocks'] = kinder
                if 'block_order' in knoten:
                    out['block_order'] = [b for b in knoten['block_order'] if b in behalten]
            elif k == 'block_order':
                continue
            else:
                out[k] = fuellen(v, texte)
        # Ein Block, dessen Text leer geblieben ist, wird verworfen
        st = out.get('settings') or {}
        for feld in ('text', 'label'):
            if feld in st and st[feld] is None: return None
        return out
    if isinstance(knoten, list): return [fuellen(x, texte) for x in knoten]
    if isinstance(knoten, str):
        m = re.fullmatch(r'\{\{(.+?)\}\}', knoten.strip())
        if m:
            wert = (texte.get(m.group(1)) or '').strip()
            if not wert: return None
            return wert if m.group(1).endswith('Text') or 'Button' in m.group(1) else f'<p>{wert}</p>'
    return knoten

for block in copy['seiten'][seite]:
    typ, grund = finde_section(block['section'])
    if not typ:
        uebersprungen.append((block['section'], grund)); continue
    vorlage = zu['sections'].get(typ)
    if not vorlage:
        uebersprungen.append((block['section'], f'Section "{typ}" nicht in der Zuordnung')); continue
    gebaut = fuellen({'type': typ, **vorlage}, block['texte'])
    if gebaut is None:
        uebersprungen.append((block['section'], 'alle Texte leer')); continue
    sid = id_(typ.replace('-', '_'))
    sections[sid] = gebaut
    ordnung.append(sid)

titel(f'{seite} → templates/{template}.json  ({zu["theme"]})')
def zaehle(k):
    n = 0
    if isinstance(k, dict):
        for bid, b in (k.get('blocks') or {}).items(): n += 1 + zaehle(b)
    return n
for sid in ordnung:
    s = sections[sid]
    print(f'  {s["type"]:22s} {zaehle(s)} Blöcke')
for name, grund in uebersprungen:
    print(f'  übersprungen: {name[:52]} — {grund}')

neu = json.dumps({'sections': sections, 'order': ordnung}, ensure_ascii=False, indent=2)
if TROCKEN:
    print(f'\n  Trockenlauf. Vorschau:\n')
    print('\n'.join('   ' + z for z in neu.split('\n')[:26]))
    sys.exit(0)

theme = gql(env, 'query($id:ID!){ theme(id:$id){ name role } }',
            {'id': f'gid://shopify/OnlineStoreTheme/{tid}'})['theme']
if theme['role'] == 'MAIN':
    fehler('Das ist das aktive Theme. Bitte auf einem Duplikat arbeiten.')
gate(f'templates/{template}.json im Theme "{theme["name"]}" ({theme["role"]}) überschreiben.')

nutzlast = json.dumps({'asset': {'key': f'templates/{template}.json', 'value': neu}})
r = subprocess.run(['curl','-sS','-X','PUT',
     f"https://{env['SHOP']}/admin/api/2025-07/themes/{tid}/assets.json",
     '-H', f"X-Shopify-Access-Token: {env['TOKEN']}", '-H','Content-Type: application/json',
     '-d', nutzlast], capture_output=True, text=True, timeout=180)
try:
    d = json.loads(r.stdout)
except Exception:
    fehler(f'Antwort nicht lesbar: {r.stdout[:200]}')
if 'asset' not in d: fehler(json.dumps(d, ensure_ascii=False)[:400])
print(f'\n  Gebaut. {len(ordnung)} Sections in templates/{template}.json.')
print(f'  Vorschau: https://{env["SHOP"]}/?preview_theme_id={tid}\n')
