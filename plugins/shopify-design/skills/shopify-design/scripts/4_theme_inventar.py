#!/usr/bin/env python3
"""Liest aus, was das aktive Theme kann: Templates mit ihrem Aufbau, verfuegbare Sections
und deren Einstellungen, Farb- und Schrifteinstellungen.
Ohne diesen Schritt wuerde der Aufbau raten — Dawn, Prestige und Horizon haben voellig
verschiedene Section-Namen.
Aufruf: python3 4_theme_inventar.py [--env pfad] [--alle]
"""
import sys, os, json, re, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify import zugang, gql, titel, fehler
import subprocess, tempfile

envp = sys.argv[sys.argv.index('--env')+1] if '--env' in sys.argv else None
ALLE = '--alle' in sys.argv
env = zugang(envp)

def asset(theme_id, key):
    url = (f"https://{env['SHOP']}/admin/api/2025-07/themes/{theme_id}/assets.json"
           f"?asset%5Bkey%5D={urllib.parse.quote(key)}")
    r = subprocess.run(['curl','-sS',url,'-H',f"X-Shopify-Access-Token: {env['TOKEN']}"],
                       capture_output=True, text=True, timeout=120)
    try: return json.loads(r.stdout)['asset']['value']
    except Exception: return None

t = gql(env, '{ themes(first:1, roles:MAIN){ nodes { id name role } } }')['themes']['nodes']
if not t: fehler('Kein aktives Theme gefunden.')
theme = t[0]; tid = theme['id'].split('/')[-1]

r = subprocess.run(['curl','-sS', f"https://{env['SHOP']}/admin/api/2025-07/themes/{tid}/assets.json",
                    '-H', f"X-Shopify-Access-Token: {env['TOKEN']}"], capture_output=True, text=True, timeout=180)
dateien = [a['key'] for a in json.loads(r.stdout).get('assets', [])]
sections = sorted(k for k in dateien if k.startswith('sections/') and k.endswith('.liquid'))
blocks   = sorted(k for k in dateien if k.startswith('blocks/') and k.endswith('.liquid'))
templates = sorted(k for k in dateien if k.startswith('templates/') and k.endswith('.json'))

titel(f'Theme: {theme["name"]}')
print(f'  ID {tid} · {len(dateien)} Dateien · {len(sections)} Sections · '
      f'{len(blocks)} Blocks · {len(templates)} JSON-Templates')

# ---------------------------------------------------------------- Templates
aufbau = {}
print('\n  Templates und ihr aktueller Aufbau:')
for tpl in templates:
    roh = asset(tid, tpl)
    if not roh: continue
    try: j = json.loads(re.sub(r'/\*.*?\*/', '', roh, flags=re.S))
    except Exception: continue
    ordnung = j.get('order') or list((j.get('sections') or {}).keys())
    typen = [(j.get('sections') or {}).get(k, {}).get('type', '?') for k in ordnung]
    aufbau[tpl.replace('templates/','')] = typen
    print(f'    {tpl.replace("templates/",""):26s} {len(typen):2d}  {", ".join(typen[:6])}'
          + (' …' if len(typen) > 6 else ''))

# ---------------------------------------------------------------- Sections
print(f'\n  Verfügbare Sections mit ihren Einstellungen:')
katalog = {}
gelesen = sections if ALLE else sections[:40]
for s in gelesen:
    roh = asset(tid, s)
    if not roh: continue
    name = s.replace('sections/','').replace('.liquid','')
    m = re.search(r'\{%-?\s*schema\s*-?%\}(.*?)\{%-?\s*endschema\s*-?%\}', roh, re.S)
    if not m: katalog[name] = {'schema': False, 'settings': [], 'blocks': []}; continue
    try: sch = json.loads(m.group(1))
    except Exception: katalog[name] = {'schema': 'ungültig', 'settings': [], 'blocks': []}; continue
    katalog[name] = {
      'titel': sch.get('name', name),
      'settings': [x.get('id') for x in sch.get('settings', []) if x.get('id')],
      'blocks': [b.get('type') for b in sch.get('blocks', []) if isinstance(b, dict) and b.get('type')],
    }
for name, info in sorted(katalog.items()):
    if name.startswith('_'): continue
    st = info.get('settings') or []
    bl = info.get('blocks') or []
    print(f'    {name:30s} {len(st):2d} Einstellungen'
          + (f', {len(bl)} Blocktypen' if bl else ''))

# ---------------------------------------------------------------- Farben und Schriften
farbfelder = {}
sd = asset(tid, 'config/settings_data.json')
if sd:
    try:
        cur = json.loads(re.sub(r'/\*.*?\*/', '', sd, flags=re.S)).get('current', {})
        # Neuere Themes wie Horizon legen Farben in einer verschachtelten Palette ab und
        # verweisen aus den Einzelfeldern nur darauf ({{ settings.color_palette.x }}).
        # Deshalb rekursiv suchen statt nur die oberste Ebene.
        def sammle(o, pfad=''):
            if isinstance(o, dict):
                for k, v in o.items(): sammle(v, f'{pfad}.{k}' if pfad else k)
            elif isinstance(o, list):
                for i, v in enumerate(o): sammle(v, f'{pfad}[{i}]')
            elif isinstance(o, str) and re.fullmatch(r'#[0-9A-Fa-f]{3,8}', o.strip()):
                farbfelder[pfad] = o.strip()
        sammle(cur)
        verweise = sum(1 for v in cur.values()
                       if isinstance(v, str) and v.strip().startswith('{{ settings.'))
        if verweise: farbfelder['_hinweis'] = (
            f'{verweise} Felder verweisen auf die Palette statt eigene Werte zu halten — '
            'zum Umfärben die Palette ändern, nicht die Einzelfelder.')
    except Exception: pass
hinweis = farbfelder.pop('_hinweis', None)
if farbfelder:
    print(f'\n  Farbeinstellungen im Theme ({len(farbfelder)}):')
    for k, v in list(farbfelder.items())[:12]: print(f'    {k:38s} {v}')
if hinweis: print(f'    → {hinweis}')

json.dump({'theme': theme['name'], 'theme_id': tid, 'templates': aufbau,
           'sections': katalog, 'farbfelder': farbfelder},
          open('theme_inventar.json','w'), ensure_ascii=False, indent=1)
print('\n  → theme_inventar.json geschrieben')
print('  Darauf bildet der Aufbau ab — nie auf vermutete Section-Namen.\n')
