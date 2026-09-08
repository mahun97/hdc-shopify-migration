#!/usr/bin/env python3
"""Setzt Schriften, Farbpalette und Formatierung im Theme — aus konzept.json oder direkt.
Aufruf:
  python3 7_gestaltung.py --theme <id> --zeigen
  python3 7_gestaltung.py --theme <id> --heading archivo_n7 --body ibm_plex_sans_n4 \
      --akzent "#F6A429" --zweit "#334B70" --hintergrund "#FFFFFF" --text "#101418"
Schriftnamen sind Shopify-Kennungen: <familie>_n<gewicht>, z. B. archivo_n7, work_sans_n4.
"""
import sys, os, json, re, subprocess, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify import zugang, gql, titel, fehler, gate

def arg(n, pflicht=False, standard=None):
    if n in sys.argv: return sys.argv[sys.argv.index(n)+1]
    if pflicht: fehler(f'{n} fehlt')
    return standard

env = zugang(arg('--env')); tid = arg('--theme', True)

def asset(key, wert=None):
    basis = f"https://{env['SHOP']}/admin/api/2025-07/themes/{tid}/assets.json"
    if wert is None:
        u = f"{basis}?asset%5Bkey%5D={urllib.parse.quote(key)}"
        r = subprocess.run(['curl','-sS',u,'-H',f"X-Shopify-Access-Token: {env['TOKEN']}"],
                           capture_output=True, text=True, timeout=120)
        try: return json.loads(r.stdout)['asset']['value']
        except Exception: return None
    p = json.dumps({'asset':{'key':key,'value':wert}})
    r = subprocess.run(['curl','-sS','-X','PUT',basis,'-H',f"X-Shopify-Access-Token: {env['TOKEN']}",
                        '-H','Content-Type: application/json','-d',p], capture_output=True, text=True, timeout=180)
    d = json.loads(r.stdout)
    if 'asset' not in d: fehler(json.dumps(d, ensure_ascii=False)[:300])
    return True

theme = gql(env, 'query($id:ID!){ theme(id:$id){ name role } }',
            {'id': f'gid://shopify/OnlineStoreTheme/{tid}'})['theme']
roh = asset('config/settings_data.json')
if not roh: fehler('settings_data.json nicht lesbar')
sd = json.loads(re.sub(r'/\*.*?\*/', '', roh, flags=re.S))
cur = sd.setdefault('current', {})

SCHRIFT = {'--heading':'type_heading_font', '--body':'type_body_font',
           '--subheading':'type_subheading_font', '--akzentschrift':'type_accent_font'}
FARBE   = {'--hintergrund':'background', '--text':'foreground',
           '--akzent':'color1', '--zweit':'color2'}

if '--zeigen' in sys.argv or not any(a in sys.argv for a in list(SCHRIFT)+list(FARBE)):
    titel(f'Gestaltung in "{theme["name"]}"')
    for flag, feld in SCHRIFT.items():
        print(f'  {feld:24s} {cur.get(feld, "—")}   (setzen mit {flag})')
    pal = cur.get('color_palette') or {}
    print()
    for flag, feld in FARBE.items():
        print(f'  color_palette.{feld:12s} {pal.get(feld, "—")}   (setzen mit {flag})')
    verweise = [k for k, v in cur.items() if isinstance(v, str) and v.strip().startswith('{{ settings.')]
    if verweise:
        print(f'\n  {len(verweise)} Felder verweisen auf die Palette — zum Umfärben nur die Palette ändern.')
    print()
    sys.exit(0)

aenderungen = []
for flag, feld in SCHRIFT.items():
    w = arg(flag)
    if w: aenderungen.append((feld, cur.get(feld), w)); cur[feld] = w
pal = dict(cur.get('color_palette') or {})
for flag, feld in FARBE.items():
    w = arg(flag)
    if w:
        if not re.fullmatch(r'#[0-9A-Fa-f]{6}', w): fehler(f'{flag}: "{w}" ist kein Hex-Farbwert')
        aenderungen.append((f'color_palette.{feld}', pal.get(feld), w)); pal[feld] = w
if pal: cur['color_palette'] = pal

titel(f'Gestaltung setzen in "{theme["name"]}" ({theme["role"]})')
for feld, alt, neu in aenderungen: print(f'  {feld:30s} {str(alt or "—"):22s} → {neu}')
if theme['role'] == 'MAIN': fehler('Das ist das aktive Theme. Bitte auf einem Duplikat arbeiten.')
gate(f'{len(aenderungen)} Einstellungen im Theme überschreiben.')
asset('config/settings_data.json', json.dumps(sd, ensure_ascii=False, indent=2))
print(f'\n  Gesetzt. Vorschau: https://{env["SHOP"]}/?preview_theme_id={tid}')
print('  Bitte gegenlesen — Schriftnamen ohne passende Datei fallen still auf die Systemschrift zurück.\n')
