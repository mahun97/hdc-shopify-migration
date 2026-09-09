#!/usr/bin/env python3
"""Kategoriebanner als Satz erzeugen — ein Stil, viele Motive.

Der Unterschied zum Hero: Kategoriebanner werden nie einzeln betrachtet. Wer sich
durch den Shop klickt, sieht drei, vier, fuenf davon hintereinander. Sie muessen
zusammengehoeren — gleiches Licht, gleiche Kamera, gleiche Farbwelt — und sich nur
im Motiv unterscheiden. Deshalb eine Stil-Datei fuer alle und ein Motiv je Kollektion.

Aufruf:
  python3 8d_kategoriebanner.py --vorlage > stil.json
  python3 8d_kategoriebanner.py --stil stil.json --pruefen
  python3 8d_kategoriebanner.py --stil stil.json --handle beutel-rollen
  python3 8d_kategoriebanner.py --stil stil.json --alle
  python3 8d_kategoriebanner.py --stil stil.json --alle --setzen
"""
import sys, os, json, base64, subprocess, tempfile, time, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify import zugang, gql, seiten, titel, fehler, gate, pruefe_fehler

def arg(n, pflicht=False, standard=None):
    if n in sys.argv: return sys.argv[sys.argv.index(n)+1]
    if pflicht: fehler(f'{n} fehlt')
    return standard

MAX_KANTE, MAX_VERHAELTNIS = 3840, 3.0
def sechzehn(w): return max(256, min(MAX_KANTE, int(round(w / 16)) * 16))

VORLAGE = {
 "size": "2560x880",
 "modell": "gpt-image-2",
 "qualitaet": "high",
 "textseite": "links",
 "overlay": "dunkel",
 "_hinweis": "style/camera/artist_style gelten fuer ALLE Banner. Nur motive unterscheidet sich.",
 "style": {"lighting": "", "color_palette": "", "mood": "", "texture": "",
           "contrast": "", "saturation": "", "sharpness": "", "depth_of_field": "",
           "composition": ""},
 "camera": {"angle": "", "lens": "", "focal_length": "", "aperture": "",
            "exposure": "", "film_type": ""},
 "artist_style": {"inspired_by": "", "medium": "photography", "period": "contemporary",
                  "genre": "product and lifestyle advertising"},
 "motive": {
   "beispiel-handle": {
     "main_object": "", "secondary_objects": [], "environment": "",
     "action": "", "details": ""}},
 "metadata": {"title": "", "author": "HDC Digital", "created_at": "", "version": "1"}}

if '--vorlage' in sys.argv:
    v = json.loads(json.dumps(VORLAGE))
    v['metadata']['created_at'] = datetime.date.today().isoformat()
    print(json.dumps(v, indent=2, ensure_ascii=False)); sys.exit(0)

def schluessel(pfad=None):
    pfad = pfad or os.path.expanduser('~/.config/openai.env')
    if not os.path.exists(pfad):
        fehler(f'{pfad} gibt es nicht — siehe references/schluessel.md')
    for z in open(pfad):
        z = z.strip()
        if z.startswith(('KEY=', 'OPENAI_API_KEY=')): return z.split('=', 1)[1].strip().strip('"\'')
    fehler(f'Keine Zeile KEY= in {pfad}')

def satz(kopf, werte):
    teile = [f'{k.replace("_", " ")}: {v}' for k, v in werte.items()
             if v and not isinstance(v, (list, dict)) and not k.startswith('_')]
    for k, v in werte.items():
        if isinstance(v, list) and v: teile.append(f'{k.replace("_", " ")}: {", ".join(map(str, v))}')
    return f'{kopf}: ' + '; '.join(teile) + '.' if teile else ''

def prompt_bauen(stil, motiv, titel_text, textseite):
    frei = 'LEFT' if textseite == 'links' else 'RIGHT'
    voll = 'RIGHT' if textseite == 'links' else 'LEFT'
    teile = [f'Wide category banner for the shop section "{titel_text}".']
    teile.append(satz('Subject', motiv))
    teile.append(satz('Style', stil.get('style') or {}))
    teile.append(satz('Camera', stil.get('camera') or {}))
    teile.append(satz('Reference style', stil.get('artist_style') or {}))
    teile.append(f'Composition for a wide banner: subject matter and visual interest in the '
                 f'{voll} half, the {frei} half deliberately calm and uncluttered so a '
                 f'category headline can sit over it. Photorealistic, real materials.')
    teile.append('Absolutely no text, no letters, no numbers, no logos, no watermarks, '
                 'no signage, no borders, no frames, no collage, no split screen.')
    return '\n'.join(t for t in teile if t)

def erzeugen(prompt, stil, key):
    b, h = (int(x) for x in stil.get('size', '2560x880').lower().split('x'))
    api_b, api_h = sechzehn(b), sechzehn(h)
    if api_b / api_h > MAX_VERHAELTNIS: api_h = sechzehn(api_b / MAX_VERHAELTNIS + 8)
    koerper = {'model': stil.get('modell', 'gpt-image-2'), 'prompt': prompt, 'n': 1,
               'size': f'{api_b}x{api_h}', 'quality': stil.get('qualitaet', 'high')}
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
        json.dump(koerper, f); pfad = f.name
    try:
        r = subprocess.run(['curl', '-sS', '-X', 'POST',
                            'https://api.openai.com/v1/images/generations',
                            '-H', f'Authorization: Bearer {key}',
                            '-H', 'Content-Type: application/json',
                            '--data-binary', f'@{pfad}', '--max-time', '600'],
                           capture_output=True, text=True, timeout=630)
    finally: os.unlink(pfad)
    d = json.loads(r.stdout or '{}')
    if 'error' in d: fehler(f'OpenAI: {d["error"].get("message", d["error"])}')
    if not d.get('data'): fehler(f'Antwort ohne Bilddaten: {r.stdout[:250]}')
    return base64.b64decode(d['data'][0]['b64_json']), (d.get('usage') or {}), (b, h)

def zuschneiden(roh, b, h, textseite, overlay, name):
    from PIL import Image, ImageDraw
    import io
    im = Image.open(io.BytesIO(roh)).convert('RGB')
    v = b / h
    bh = int(im.width / v)
    if bh <= im.height:
        oben = int((im.height - bh) * 0.45)
        im = im.crop((0, oben, im.width, oben + bh))
    else:
        bb = int(im.height * v); links = (im.width - bb) // 2
        im = im.crop((links, 0, links + bb, im.height))
    im = im.resize((b, h), Image.LANCZOS)
    if overlay != 'kein':
        s = Image.new('RGBA', (b, h), (0, 0, 0, 0)); z = ImageDraw.Draw(s)
        grund = (12, 12, 14) if overlay == 'dunkel' else (255, 255, 255)
        spitze = 150 if overlay == 'dunkel' else 165
        for i in range(b // 2):
            t = 1 - (i / (b / 2)) ** 1.4
            x = i if textseite == 'links' else b - 1 - i
            z.line([(x, 0), (x, h)], fill=grund + (int(spitze * t),))
        im = Image.alpha_composite(im.convert('RGBA'), s).convert('RGB')
    ziel = os.path.abspath(f'{name}.png'); im.save(ziel)
    return ziel, os.path.getsize(ziel)

def hochladen_und_setzen(env, datei, koll_id, alt):
    S = ('mutation($i:[StagedUploadInput!]!){ stagedUploadsCreate(input:$i){'
         ' stagedTargets{url resourceUrl parameters{name value}} userErrors{message} } }')
    d = gql(env, S, {'i': [{'filename': os.path.basename(datei), 'mimeType': 'image/png',
                            'resource': 'FILE', 'httpMethod': 'POST'}]})['stagedUploadsCreate']
    pruefe_fehler(d, 'stagedUploadsCreate'); z = d['stagedTargets'][0]
    cmd = ['curl', '-sS', '-X', 'POST', z['url']]
    for p in z['parameters']: cmd += ['-F', f'{p["name"]}={p["value"]}']
    cmd += ['-F', f'file=@{datei}']
    subprocess.run(cmd, capture_output=True, timeout=300)
    M = ('mutation($i:CollectionInput!){ collectionUpdate(input:$i){'
         ' collection{ image{ url } } userErrors{message} } }')
    r = gql(env, M, {'i': {'id': koll_id, 'image': {'src': z['resourceUrl'], 'altText': alt}}})
    pruefe_fehler(r['collectionUpdate'], 'collectionUpdate')
    return (r['collectionUpdate']['collection'].get('image') or {}).get('url', '—')

def main():
    env = zugang(arg('--env'))
    stil = json.load(open(arg('--stil', True), encoding='utf-8'))
    koll = seiten(env, 'collections', 'id handle title descriptionHtml image{url}')
    nach_handle = {k['handle']: k for k in koll}
    motive = stil.get('motive') or {}

    if '--pruefen' in sys.argv:
        titel(f'Kategoriebanner — {env["SHOP"]}')
        for k in sorted(koll, key=lambda x: x['title']):
            m = 'ok' if k.get('image') else '! '
            hat_motiv = 'Motiv da' if k['handle'] in motive else 'KEIN MOTIV in der Stil-Datei'
            print(f'  {m} {k["title"][:34]:36s} {k["handle"][:26]:28s} '
                  f'{"Banner gesetzt" if k.get("image") else hat_motiv}')
        ohne = [k for k in koll if not k.get('image')]
        fehlt = [k['handle'] for k in ohne if k['handle'] not in motive]
        print(f'\n  {len(ohne)} ohne Banner, davon {len(fehlt)} ohne Motiv in der Stil-Datei.')
        if fehlt:
            print('  Erst ergänzen — ein Motiv erfindet das Skript nicht:')
            for h in fehlt[:10]: print(f'     "{h}": {{"main_object": "…", "environment": "…"}}')
        print()
        return

    ziele = []
    if arg('--handle'):
        h = arg('--handle')
        if h not in nach_handle: fehler(f'Kollektion "{h}" gibt es nicht.')
        ziele = [nach_handle[h]]
    elif '--alle' in sys.argv:
        ziele = [k for k in koll if not k.get('image') and k['handle'] in motive]
    else:
        fehler('--pruefen, --handle <handle> oder --alle angeben.')
    if not ziele: fehler('Nichts zu tun — alle haben ein Banner oder es fehlt das Motiv.')

    titel(f'{len(ziele)} Kategoriebanner erzeugen — ein Stil, {len(ziele)} Motive')
    print(f'  {stil.get("size")} · {stil.get("modell", "gpt-image-2")} · '
          f'Text {stil.get("textseite", "links")} · Overlay {stil.get("overlay", "dunkel")}\n')
    key = schluessel(arg('--env-openai'))
    gemacht, token = [], 0
    for k in ziele:
        motiv = motive.get(k['handle'])
        if not motiv:
            print(f'  ! {k["handle"]}: kein Motiv, übersprungen'); continue
        p = prompt_bauen(stil, motiv, k['title'], stil.get('textseite', 'links'))
        roh, verbrauch, (b, h) = erzeugen(p, stil, key)
        datei, groesse = zuschneiden(roh, b, h, stil.get('textseite', 'links'),
                                     stil.get('overlay', 'dunkel'), f'banner-{k["handle"]}')
        token += verbrauch.get('total_tokens') or 0
        gemacht.append((k, datei))
        print(f'  {k["title"][:30]:32s} → {os.path.basename(datei)}  {groesse//1024} KB')
    print(f'\n  {len(gemacht)} erzeugt, {token} Token abgerechnet.')
    print('  Erst alle nebeneinander ansehen — ein Satz wirkt nur, wenn er zusammenpasst.')
    if '--setzen' not in sys.argv:
        print('  Mit --setzen hochladen und in die Kollektionen eintragen.\n'); return
    gate(f'{len(gemacht)} Banner in {env["SHOP"]} hochladen und setzen.')
    for k, datei in gemacht:
        url = hochladen_und_setzen(env, datei, k['id'], f'{k["title"]} — Kategoriebanner')
        print(f'   {k["handle"]}: gesetzt')
    print()

if __name__ == '__main__':
    main()
