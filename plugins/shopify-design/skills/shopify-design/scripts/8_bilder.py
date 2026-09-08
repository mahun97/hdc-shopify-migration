#!/usr/bin/env python3
"""Erzeugt Bildmotive aus einer HTML-Vorlage in den Markenfarben, laedt sie in den Shop
und setzt sie in eine Section.

WICHTIG: Die Vorlagen enthalten bewusst KEINEN Text. Text im Bild ist nicht responsiv,
nicht uebersetzbar, nicht durchsuchbar und nicht vorlesbar — er gehoert in die Section.

Aufruf:
  python3 8_bilder.py --vorlage motiv-formen --akzent "#F6A429" --zweit "#334B70" \
      --grund "#E8E2CD" --name hero-motiv [--groesse 1600x900] [--nur-erzeugen]
  ... --theme <id> --section hero --feld image_1     setzt es zusaetzlich ein
"""
import sys, os, json, re, time, subprocess, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify import zugang, gql, pruefe_fehler, titel, fehler, gate

def arg(n, pflicht=False, standard=None):
    if n in sys.argv: return sys.argv[sys.argv.index(n)+1]
    if pflicht: fehler(f'{n} fehlt')
    return standard

vorlage = arg('--vorlage', True); name = arg('--name', True)
breite, hoehe = (arg('--groesse', False, '1600x900').lower().split('x') + ['900'])[:2]
werte = {'akzent': arg('--akzent', False, '#111111'), 'zweit': arg('--zweit', False, '#444444'),
         'grund': arg('--grund', False, '#FFFFFF'), 'breite': breite, 'hoehe': hoehe}

CHROME = next((p for p in (
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Chromium.app/Contents/MacOS/Chromium',
  '/usr/bin/chromium-browser', '/usr/bin/google-chrome') if os.path.exists(p)), None)
if not CHROME: fehler('Kein Chrome gefunden — wird zum Rendern der Vorlage gebraucht.')

hier = os.path.dirname(os.path.abspath(__file__))
pfad = os.path.join(hier, '..', 'vorlagen', f'{vorlage}.html')
if not os.path.exists(pfad): fehler(f'Vorlage "{vorlage}" nicht gefunden in vorlagen/')
html = open(pfad, encoding='utf-8').read()
for k, v in werte.items(): html = html.replace('{{' + k + '}}', str(v))
offen = re.findall(r'\{\{(\w+)\}\}', html)
if offen: fehler(f'Vorlage hat unbelegte Platzhalter: {", ".join(sorted(set(offen)))}')
if re.search(r'<(h1|h2|h3|p)[ >]', html):
    print('  Hinweis: Die Vorlage enthält Textelemente. Text gehört in die Section, nicht ins Bild.')

tmp_html = os.path.abspath(f'{name}.html'); datei = os.path.abspath(f'{name}.png')
open(tmp_html, 'w', encoding='utf-8').write(html)
subprocess.run([CHROME, '--headless', '--disable-gpu', f'--screenshot={datei}',
                f'--window-size={breite},{hoehe}', '--hide-scrollbars', f'file://{tmp_html}'],
               capture_output=True, timeout=180)
if not os.path.exists(datei): fehler('Chrome hat kein Bild erzeugt.')
titel(f'{name}.png erzeugt')
print(f'  {breite}×{hoehe} px · {os.path.getsize(datei)//1024} KB · Vorlage "{vorlage}"')
print(f'  Farben: {werte["grund"]} / {werte["akzent"]} / {werte["zweit"]}')
if '--nur-erzeugen' in sys.argv:
    print('\n  Bitte ansehen, bevor es in den Shop geht.\n'); sys.exit(0)

env = zugang(arg('--env'))
gate(f'{name}.png in die Dateien von {env["SHOP"]} hochladen.')
S = '''mutation($input:[StagedUploadInput!]!){ stagedUploadsCreate(input:$input){
  stagedTargets { url resourceUrl parameters { name value } } userErrors { message } } }'''
d = gql(env, S, {'input':[{'filename': f'{name}.png', 'mimeType':'image/png',
                           'resource':'FILE', 'httpMethod':'POST'}]})['stagedUploadsCreate']
pruefe_fehler(d, 'stagedUploadsCreate')
z = d['stagedTargets'][0]
cmd = ['curl','-sS','-X','POST', z['url']]
for p in z['parameters']: cmd += ['-F', f'{p["name"]}={p["value"]}']
cmd += ['-F', f'file=@{datei}']
subprocess.run(cmd, capture_output=True, timeout=300)
F = '''mutation($files:[FileCreateInput!]!){ fileCreate(files:$files){ files { id } userErrors { message } } }'''
r = gql(env, F, {'files':[{'originalSource': z['resourceUrl'], 'contentType':'IMAGE',
                           'alt': arg('--alt', False, name.replace('-', ' '))}]})['fileCreate']
pruefe_fehler(r, 'fileCreate'); fid = r['files'][0]['id']
for _ in range(15):
    q = gql(env, 'query($id:ID!){ node(id:$id){ ... on MediaImage { fileStatus image { url } } } }',
            {'id': fid})['node']
    if q and q.get('fileStatus') == 'READY' and q.get('image'): break
    time.sleep(3)
if not (q and q.get('image')): fehler('Bild wurde nicht verarbeitet.')
dateiname = q['image']['url'].split('/')[-1].split('?')[0]
print(f'  Hochgeladen als shopify://shop_images/{dateiname}')

tid, section, feld = arg('--theme'), arg('--section'), arg('--feld', False, 'image')
if not (tid and section):
    print('  Nicht eingesetzt — dafür --theme und --section angeben.\n'); sys.exit(0)
tpl = arg('--template', False, 'index')
basis = f"https://{env['SHOP']}/admin/api/2025-07/themes/{tid}/assets.json"
u = f"{basis}?asset%5Bkey%5D=templates/{tpl}.json"
roh = json.loads(subprocess.run(['curl','-sS',u,'-H',f"X-Shopify-Access-Token: {env['TOKEN']}"],
      capture_output=True, text=True, timeout=120).stdout)['asset']['value']
j = json.loads(re.sub(r'/\*.*?\*/', '', roh, flags=re.S))
getroffen = 0
for sid, s in (j.get('sections') or {}).items():
    if s.get('type') == section:
        s.setdefault('settings', {})[feld] = f'shopify://shop_images/{dateiname}'
        getroffen += 1
if not getroffen: fehler(f'Keine Section "{section}" in templates/{tpl}.json')
p = json.dumps({'asset':{'key': f'templates/{tpl}.json', 'value': json.dumps(j, ensure_ascii=False, indent=2)}})
r2 = subprocess.run(['curl','-sS','-X','PUT', basis, '-H',f"X-Shopify-Access-Token: {env['TOKEN']}",
                     '-H','Content-Type: application/json','-d',p], capture_output=True, text=True, timeout=180)
if 'asset' not in r2.stdout: fehler(r2.stdout[:300])
print(f'  In {getroffen}× "{section}" eingesetzt ({feld}).')
print(f'  Vorschau: https://{env["SHOP"]}/?preview_theme_id={tid}\n')
