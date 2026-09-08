#!/usr/bin/env python3
"""Phase 6 — importiert die geprueften Produkte. Wiederholbar: bereits angelegte werden uebersprungen.
Aufruf:
  python3 4_import.py Importliste.xlsx --probe      erst 3 Produkte (Pflicht vor dem Rest)
  python3 4_import.py Importliste.xlsx              der ganze Rest
  python3 4_import.py Importliste.xlsx --trocken    zeigt nur, was passieren wuerde
"""
import sys, os, re, json, unicodedata, collections, mimetypes, subprocess, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify import zugang, gql, pruefe_fehler, titel, fehler, gate
try: import openpyxl
except ImportError: fehler('openpyxl fehlt.  pip3 install openpyxl')

datei   = next((a for a in sys.argv[1:] if not a.startswith('--')), 'Importliste.xlsx')
PROBE   = '--probe' in sys.argv
TROCKEN = '--trocken' in sys.argv
envp    = sys.argv[sys.argv.index('--env')+1] if '--env' in sys.argv else None
STATUS  = os.path.splitext(datei)[0] + '.status.json'
env     = zugang(envp)

def handle(t):
    s = unicodedata.normalize('NFC', t.lower())
    for a, b in (('ä','ae'),('ö','oe'),('ü','ue'),('ß','ss'),('µ','my'),('&','und')): s = s.replace(a, b)
    s = unicodedata.normalize('NFKD', s)
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', s)).strip('-')[:80]

# ---------- Liste einlesen und zu Produkten gruppieren ----------
ws = openpyxl.load_workbook(datei).active
kopf = [c.value for c in ws[1]]
gruppen = collections.OrderedDict()
for i, row in enumerate(ws.iter_rows(min_row=3, values_only=True), start=3):
    if not any(row): continue
    r = {k: row[j] for j, k in enumerate(kopf) if k}
    t = str(r.get('Produkttitel') or '').strip()
    if not t: continue
    g = gruppen.setdefault(t, {'titel': t, 'handle': handle(t), 'zeilen': [],
                               'tags': set(), 'beschreibung': r.get('Beschreibung') or '',
                               'hersteller': r.get('Hersteller GPSR') or '',
                               'seo_t': r.get('SEO-Titel'), 'seo_d': r.get('SEO-Beschreibung')})
    for x in str(r.get('Tags') or '').split(','):
        if x.strip(): g['tags'].add(x.strip())
    g['zeilen'].append(r)

status = json.load(open(STATUS)) if os.path.exists(STATUS) else {}
offen = [g for g in gruppen.values() if g['handle'] not in status]
if PROBE: offen = offen[:3]

titel(f'Import aus {datei}')
print(f'  Shop:              {env["SHOP"]}')
print(f'  Produkte gesamt:   {len(gruppen)}')
print(f'  bereits angelegt:  {len(status)}')
print(f'  jetzt geplant:     {len(offen)}' + ('   (Probelauf)' if PROBE else ''))
if not offen: print('\n  Nichts zu tun.\n'); sys.exit(0)
for g in offen[:6]:
    mengen = {str(z.get('Option 2 Wert') or '') for z in g['zeilen']}
    print(f'    · {g["titel"][:50]:50s} {len(g["zeilen"]):3d} Varianten')
if len(offen) > 6: print(f'    … und {len(offen)-6} weitere')
if TROCKEN: print('\n  Trockenlauf — es wurde nichts geschrieben.\n'); sys.exit(0)

gate(f'{len(offen)} Produkte werden im Shop {env["SHOP"]} angelegt.')

# ---------- Bilder ----------
STAGED = '''mutation($input:[StagedUploadInput!]!){ stagedUploadsCreate(input:$input){
  stagedTargets { url resourceUrl parameters { name value } } userErrors { message } } }'''
def bilder_hochladen(pfade):
    if not pfade: return {}
    d = gql(env, STAGED, {'input': [{'filename': os.path.basename(p).replace(' ', '_'),
        'mimeType': mimetypes.guess_type(p)[0] or 'image/jpeg', 'resource': 'IMAGE',
        'httpMethod': 'POST'} for p in pfade]})['stagedUploadsCreate']
    pruefe_fehler(d, 'stagedUploadsCreate')
    out = {}
    for pfad, ziel in zip(pfade, d['stagedTargets']):
        cmd = ['curl', '-sS', '-X', 'POST', ziel['url']]
        for prm in ziel['parameters']: cmd += ['-F', f'{prm["name"]}={prm["value"]}']
        cmd += ['-F', f'file=@{pfad}']
        if subprocess.run(cmd, capture_output=True, text=True, timeout=600).returncode != 0:
            fehler(f'Bild-Upload fehlgeschlagen: {pfad}')
        out[pfad] = ziel['resourceUrl']
    return out

PRODUCT_SET = '''mutation($input:ProductSetInput!){ productSet(input:$input, synchronous:true){
  product { id handle title variantsCount { count } media(first:30){ nodes { id } } }
  userErrors { field message code } } }'''
PUBLISH = '''mutation($id:ID!,$input:[PublicationInput!]!){ publishablePublish(id:$id, input:$input){
  userErrors { message } } }'''
METAS = '''mutation($m:[MetafieldsSetInput!]!){ metafieldsSet(metafields:$m){ userErrors { message } } }'''

kanal = [p['id'] for p in gql(env, '{ publications(first:10){ nodes { id name } } }')
         ['publications']['nodes'] if p['name'] == 'Online Store']
bildordner = next((d for d in ('bilder','Bilder','images') if os.path.isdir(d)), None)

for n, g in enumerate(offen, 1):
    z0 = g['zeilen'][0]
    o1n = str(z0.get('Option 1 Name') or 'Ausführung').strip()
    o2n = str(z0.get('Option 2 Name') or '').strip()
    hat2 = bool(o2n) and len({str(z.get('Option 2 Wert') or '') for z in g['zeilen']}) > 1
    w1, w2 = [], []
    for z in g['zeilen']:
        v1 = str(z.get('Option 1 Wert') or 'Standard').strip()
        if v1 not in w1: w1.append(v1)
        if hat2:
            v2 = str(z.get('Option 2 Wert') or '').strip()
            if v2 not in w2: w2.append(v2)
    optionen = [{'name': o1n, 'values': [{'name': v} for v in w1]}]
    if hat2: optionen.append({'name': o2n, 'values': [{'name': v} for v in w2]})

    pfade = []
    if bildordner:
        for z in sorted(g['zeilen'], key=lambda x: x.get('Bildposition') or 99):
            b = str(z.get('Bilddatei') or '').strip()
            p = os.path.join(bildordner, b)
            if b and os.path.exists(p) and p not in pfade: pfade.append(p)
    hoch = bilder_hochladen(pfade)

    varianten = []
    for z in g['zeilen']:
        ov = [{'optionName': o1n, 'name': str(z.get('Option 1 Wert') or 'Standard').strip()}]
        if hat2: ov.append({'optionName': o2n, 'name': str(z.get('Option 2 Wert') or '').strip()})
        inv = {'tracked': False}
        if z.get('Artikelnummer'): inv['sku'] = str(z['Artikelnummer']).strip()
        if z.get('Gewicht kg') not in (None, ''):
            inv['measurement'] = {'weight': {'value': float(str(z['Gewicht kg']).replace(',', '.')),
                                             'unit': 'KILOGRAMS'}}
        varianten.append({'optionValues': ov, 'taxable': True, 'inventoryItem': inv,
                          'price': str(float(str(z['Verkaufspreis']).replace(',', '.')))})

    eingabe = {'title': ' '.join(g['titel'].split()), 'handle': g['handle'], 'status': 'ACTIVE',
               'descriptionHtml': f"<p>{g['beschreibung']}</p>" if g['beschreibung'] else '',
               'tags': sorted(g['tags']), 'productOptions': optionen, 'variants': varianten,
               'files': [{'originalSource': hoch[p], 'contentType': 'IMAGE',
                          'alt': f"{g['titel']} – {os.path.splitext(os.path.basename(p))[0]}"} for p in pfade]}
    if g['seo_t'] or g['seo_d']:
        eingabe['seo'] = {'title': g['seo_t'] or None, 'description': g['seo_d'] or None}

    d = gql(env, PRODUCT_SET, {'input': eingabe})['productSet']
    pruefe_fehler(d, f'Produkt "{g["titel"][:40]}"')
    p = d['product']
    if kanal: gql(env, PUBLISH, {'id': p['id'], 'input': [{'publicationId': kanal[0]}]})
    if g['hersteller']:
        gql(env, METAS, {'m': [{'ownerId': p['id'], 'namespace': 'custom', 'key': 'hersteller',
                                'type': 'multi_line_text_field', 'value': str(g['hersteller'])}]})
    status[g['handle']] = p['id']
    json.dump(status, open(STATUS, 'w'), indent=1)
    print(f'  [{n:3d}/{len(offen)}] {p["title"][:46]:46s} {p["variantsCount"]["count"]:3d} Var  '
          f'{len(p["media"]["nodes"]):2d} Bilder')

print(f'\n  Fertig. {len(status)} von {len(gruppen)} Produkten im Shop.')
if PROBE:
    print('\n  Probelauf beendet. Die drei Produkte sollten jetzt geprüft werden.\n')
else:
    print()
