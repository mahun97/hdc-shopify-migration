#!/usr/bin/env python3
"""Hero-Bild nach den HDC-Regeln — aus einem JSON-Prompt erzeugen, zuschneiden, überlagern.

Feste Regeln (aus dem HDC-Hero-Prompt-Generator):
  * Ausgabe 3200×900
  * linke Haelfte bleibt frei fuer Text und bekommt ein dezentes Overlay
  * Produkt und visuelle Elemente rechtsbuendig
  * realistische Nutzungsszenen, kein Text im Bild

Aufruf:
  python3 8c_hero.py --vorlage > hero.json                      leere Struktur
  python3 8c_hero.py --json hero.json --name hero               nur erzeugen
  python3 8c_hero.py --json hero.json --name hero \\
      --shop --theme <id> --section hero --feld image_1         bis in den Shop

Ohne --shop bleibt das Bild lokal. Mit --shop laedt es in die Shop-Dateien und traegt
sich in die Section ein. Dazwischen gehoert der Blick darauf — deshalb sind es zwei
Schritte und nicht einer.

Modelle: gpt-image-2 kann beliebige Groessen unter drei Bedingungen — beide Seiten durch
16 teilbar, laengste Kante hoechstens 3840, Seitenverhaeltnis hoechstens 3:1. Ein Hero mit
3200×900 ist 3,56:1 und damit zu breit. Das Skript erzeugt deshalb hoeher als noetig
(3200×1072 = 2,99:1) und schneidet auf das Hero-Band herunter — reiner Zuschnitt, kein
Hochskalieren. Aeltere Modelle (gpt-image-1, gpt-image-1.5) koennen nur 1024×1024,
1024×1536 und 1536×1024 — dann schneidet und skaliert das Skript und sagt es dazu.
"""
import sys, os, json, base64, subprocess, tempfile, datetime, re, time, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

MODELL_FREI = ('gpt-image-2', 'gpt-image-2-2026-04-21', 'chatgpt-image-latest')
MODELL_FEST = {'1024x1024', '1024x1536', '1536x1024'}
MAX_KANTE = 3840
MAX_VERHAELTNIS = 3.0

def sechzehn(w):
    """Auf ein Vielfaches von 16 bringen, ohne die laengste Kante zu ueberschreiten."""
    return max(256, min(MAX_KANTE, int(round(w / 16)) * 16))

def arg(n, pflicht=False, standard=None):
    if n in sys.argv: return sys.argv[sys.argv.index(n)+1]
    if pflicht: fehler(f'{n} fehlt')
    return standard

def fehler(t):
    print(f'\n  FEHLER  {t}\n', file=sys.stderr); sys.exit(1)

VORLAGE = {
 "prompt": "", "size": "3200x900", "n": 1, "transparent_background": False,
 "referenced_image_ids": [],
 "style": {"lighting": "", "color_palette": "", "mood": "", "texture": "",
           "contrast": "", "saturation": "", "sharpness": "", "depth_of_field": "",
           "composition": ""},
 "camera": {"angle": "", "lens": "", "focal_length": "", "aperture": "",
            "exposure": "", "film_type": ""},
 "artist_style": {"inspired_by": "", "medium": "", "period": "", "genre": ""},
 "subject": {"main_object": "", "secondary_objects": [], "background": "",
             "foreground": "", "environment": "", "action": "", "perspective": "",
             "details": ""},
 "output": {"format": "png", "quality": "high", "aspect_ratio": "32:9",
            "background_color": "", "border": "none", "style_strength": ""},
 "metadata": {"title": "", "tags": [], "author": "HDC Digital", "created_at": "",
              "version": "1", "notes": ""}}

if '--vorlage' in sys.argv:
    v = dict(VORLAGE); v['metadata'] = dict(v['metadata'])
    v['metadata']['created_at'] = datetime.date.today().isoformat()
    print(json.dumps(v, indent=2, ensure_ascii=False)); sys.exit(0)

# ---------------------------------------------------------------- JSON zu Prompt
def satz(kopf, werte):
    teile = [f'{k.replace("_", " ")}: {v}' for k, v in werte.items()
             if v and not isinstance(v, (list, dict))]
    for k, v in werte.items():
        if isinstance(v, list) and v: teile.append(f'{k.replace("_", " ")}: {", ".join(map(str, v))}')
    return f'{kopf}: ' + '; '.join(teile) + '.' if teile else ''

def bauen(j):
    s = j.get('subject') or {}
    st = j.get('style') or {}
    ka = j.get('camera') or {}
    ar = j.get('artist_style') or {}
    teile = [j.get('prompt', '').strip()]
    teile.append(satz('Subject', s))
    teile.append(satz('Style', st))
    teile.append(satz('Camera', ka))
    teile.append(satz('Reference style', ar))
    # Die festen HDC-Regeln haengen immer hinten dran, egal was im JSON steht.
    teile.append('Composition for a wide website hero banner: all subject matter, product '
                 'and visual interest placed in the RIGHT half of the frame. The LEFT half '
                 'is deliberately calm and uncluttered — plain surface, floor, wall, sky or '
                 'soft bokeh — so that a headline can be placed over it later. '
                 'Photorealistic, real materials, believable everyday use.')
    teile.append('Absolutely no text, no letters, no numbers, no logos, no watermarks, '
                 'no signage, no UI elements, no borders, no frames.')
    return '\n'.join(t for t in teile if t)

# ---------------------------------------------------------------- API
def schluessel(pfad=None):
    pfad = pfad or os.path.expanduser('~/.config/openai.env')
    if not os.path.exists(pfad):
        fehler(f'{pfad} gibt es nicht — siehe references/schluessel.md, '
               'oder 8b_bild_erzeugen.py ohne Argumente aufrufen.')
    for z in open(pfad):
        z = z.strip()
        if z.startswith(('KEY=', 'OPENAI_API_KEY=')): return z.split('=', 1)[1].strip().strip('"\'')
    fehler(f'Keine Zeile KEY= in {pfad}')

def erzeugen(prompt, qualitaet, referenzen, key, modell, groesse):
    if referenzen:
        cmd = ['curl', '-sS', '-X', 'POST', 'https://api.openai.com/v1/images/edits',
               '-H', f'Authorization: Bearer {key}',
               '-F', f'model={modell}', '-F', f'prompt={prompt}',
               '-F', f'size={groesse}', '-F', f'quality={qualitaet}', '-F', 'n=1']
        for r in referenzen: cmd += ['-F', f'image[]=@{r}']
        cmd += ['--max-time', '600']
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=630)
    else:
        koerper = {'model': modell, 'prompt': prompt, 'n': 1,
                   'size': groesse, 'quality': qualitaet}
        if modell not in MODELL_FREI: koerper['output_format'] = 'png'
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
    if r.returncode: fehler(f'curl: {r.stderr[:300]}')
    try: d = json.loads(r.stdout)
    except Exception: fehler(f'Keine gültige Antwort: {r.stdout[:300]}')
    if 'error' in d: fehler(f'OpenAI: {d["error"].get("message", d["error"])}')
    if not d.get('data'): fehler(f'Antwort ohne Bilddaten: {json.dumps(d)[:300]}')
    return base64.b64decode(d['data'][0]['b64_json']), (d.get('usage') or {})

# ---------------------------------------------------------------- Zuschnitt
def hero_band(roh, ziel_b, ziel_h, overlay, name):
    """Schneidet auf das Zielverhaeltnis und legt links das Overlay auf.
    Passt die Quelle schon, wird nur ueberlagert."""
    from PIL import Image, ImageDraw
    import io
    im = Image.open(io.BytesIO(roh)).convert('RGB')
    verhaeltnis = ziel_b / ziel_h
    # Breitest moegliches Band aus dem Original, vertikal leicht oberhalb der Mitte —
    # dort sitzt bei Innen- und Aussenszenen der Horizont.
    band_h = int(im.width / verhaeltnis)
    if band_h > im.height:
        band_b = int(im.height * verhaeltnis); band_h = im.height
        links = (im.width - band_b) // 2
        aus = im.crop((links, 0, links + band_b, band_h))
    else:
        oben = int((im.height - band_h) * 0.42)
        aus = im.crop((0, oben, im.width, oben + band_h))
    faktor = ziel_b / aus.width
    aus = aus.resize((ziel_b, ziel_h), Image.LANCZOS)

    if overlay != 'kein':
        schicht = Image.new('RGBA', (ziel_b, ziel_h), (0, 0, 0, 0))
        z = ImageDraw.Draw(schicht)
        grund = (12, 12, 14) if overlay == 'dunkel' else (255, 255, 255)
        spitze = 150 if overlay == 'dunkel' else 165
        # Verlauf von links (kraeftig) bis zur Mitte (aus) — spaltenweise
        for x in range(ziel_b // 2):
            t = 1 - (x / (ziel_b / 2)) ** 1.4
            z.line([(x, 0), (x, ziel_h)], fill=grund + (int(spitze * t),))
        aus = Image.alpha_composite(aus.convert('RGBA'), schicht).convert('RGB')

    ziel = os.path.abspath(f'{name}.png')
    aus.save(ziel)
    return ziel, faktor, os.path.getsize(ziel)

def in_den_shop(datei, alt):
    """Laedt das Hero-Bild in die Shop-Dateien und traegt es in die Section ein."""
    from shopify import zugang, gql, pruefe_fehler, bild_hochladen
    env = zugang(arg('--shop-env'))
    tid, section = arg('--theme', True), arg('--section', False, 'hero')
    feld = arg('--feld', False, 'image_1')
    tpl = arg('--template', False, 'index')

    theme = gql(env, 'query($id:ID!){ theme(id:$id){ name role } }',
                {'id': f'gid://shopify/OnlineStoreTheme/{tid}'})['theme']
    if theme['role'] == 'MAIN':
        fehler('Das ist das aktive Theme. Bitte auf einem Duplikat arbeiten.')

    dateiname = bild_hochladen(env, datei, alt)
    print(f'  Hochgeladen als shopify://shop_images/{dateiname}')

    basis = f"https://{env['SHOP']}/admin/api/2025-07/themes/{tid}/assets.json"
    kopf = ['-H', f"X-Shopify-Access-Token: {env['TOKEN']}"]
    u = f"{basis}?asset%5Bkey%5D=templates%2F{tpl}.json"
    r = subprocess.run(['curl', '-sS', u] + kopf, capture_output=True, text=True, timeout=120)
    try:
        roh = json.loads(r.stdout)['asset']['value']
    except Exception:
        fehler(f'templates/{tpl}.json nicht lesbar')
    tj = json.loads(re.sub(r'/\*.*?\*/', '', roh, flags=re.S))
    getroffen = []
    for sid, sec in (tj.get('sections') or {}).items():
        if sec.get('type') == section:
            sec.setdefault('settings', {})[feld] = f'shopify://shop_images/{dateiname}'
            getroffen.append(sid)
    if not getroffen:
        vorhanden = ', '.join(sorted({v.get('type', '?') for v in (tj.get('sections') or {}).values()}))
        fehler(f'Keine Section "{section}" in templates/{tpl}.json.\n'
               f'          Vorhanden sind: {vorhanden}')
    p = json.dumps({'asset': {'key': f'templates/{tpl}.json',
                              'value': json.dumps(tj, ensure_ascii=False, indent=2)}})
    r2 = subprocess.run(['curl', '-sS', '-X', 'PUT', basis] + kopf +
                        ['-H', 'Content-Type: application/json', '-d', p],
                        capture_output=True, text=True, timeout=180)
    if '"asset"' not in r2.stdout: fehler(r2.stdout[:300])
    print(f'  In {len(getroffen)}× Section "{section}" eingesetzt ({feld}).')
    print(f'  Vorschau: https://{env["SHOP"]}/?preview_theme_id={tid}')


def main():
    j = json.load(open(arg('--json', True), encoding='utf-8'))
    name = arg('--name', True)
    modell = arg('--modell', False, 'gpt-image-2')
    overlay = arg('--overlay', False, 'hell')
    if overlay not in ('hell', 'dunkel', 'kein'):
        fehler('--overlay erwartet hell, dunkel oder kein')
    b, h = (int(x) for x in (j.get('size') or '3200x900').lower().split('x'))
    qual = ((j.get('output') or {}).get('quality') or 'high').lower()
    if qual not in ('low', 'medium', 'high'): qual = 'high'
    refs = [r for r in (j.get('referenced_image_ids') or []) if os.path.exists(r)]
    fehlend = [r for r in (j.get('referenced_image_ids') or []) if not os.path.exists(r)]
    if fehlend: fehler('Referenzbilder nicht gefunden: ' + ', '.join(fehlend))

    # Groesse, die das Modell wirklich kann
    if modell in MODELL_FREI:
        api_b, api_h = sechzehn(b), sechzehn(h)
        # Zu breit fuer das Modell? Dann hoeher erzeugen und danach herunterschneiden.
        if api_b / api_h > MAX_VERHAELTNIS:
            api_h = sechzehn(api_b / MAX_VERHAELTNIS + 8)
        elif api_h / api_b > MAX_VERHAELTNIS:
            api_b = sechzehn(api_h / MAX_VERHAELTNIS + 8)
        if max(api_b, api_h) > MAX_KANTE:
            skal = MAX_KANTE / max(api_b, api_h)
            api_b, api_h = sechzehn(api_b * skal), sechzehn(api_h * skal)
        api = f'{api_b}x{api_h}'
        if (api_b, api_h) == (b, h):
            hinweis = f'nativ {api}'
        elif api_b >= b and api_h >= h:
            hinweis = f'{api} erzeugt, dann auf {b}×{h} geschnitten'
        else:
            hinweis = f'{api} erzeugt, dann auf {b}×{h} gebracht'
    else:
        api = '1536x1024' if b >= h else '1024x1536'
        hinweis = f'{api} erzeugt — {modell} kann nichts anderes, wird zugeschnitten'

    prompt = bauen(j)
    print(f'\n  {(j.get("metadata") or {}).get("title") or name}')
    print(f'  {modell} · Ziel {b}×{h} · {hinweis}')
    print(f'  Qualität {qual} · Overlay {overlay}'
          + (f' · {len(refs)} Referenzbilder' if refs else ''))
    print(f'  Prompt {len(prompt)} Zeichen\n')
    roh, verbrauch = erzeugen(prompt, qual, refs, schluessel(arg('--env')), modell, api)
    ziel, faktor, groesse = hero_band(roh, b, h, overlay, name)
    print(f'  {ziel}')
    print(f'  {groesse//1024} KB'
          + (f' · {verbrauch.get("total_tokens")} Token abgerechnet'
             if verbrauch.get('total_tokens') else ''))
    if faktor > 1.02:
        print(f'  Hochskaliert um Faktor {faktor:.2f}'
              + ('  ← ab 2.0 bei feinen Texturen sichtbar' if faktor >= 2 else ''))
    else:
        print('  Nicht hochskaliert.')
    if '--shop' not in sys.argv:
        print('\n  Ansehen. Der Text kommt aus der Section, nicht ins Bild.')
        print('  Passt es, mit --shop --theme <id> in den Shop einsetzen.\n')
        return
    print()
    from shopify import gate
    gate(f'Hero in den Shop laden und in Section "{arg("--section", False, "hero")}" einsetzen.')
    alt = (j.get('metadata') or {}).get('title') or name.replace('-', ' ')
    in_den_shop(ziel, alt)
    print('\n  Jetzt in der Vorschau ansehen — der Zuschnitt wirkt im Theme anders '
          'als in der Datei.\n')

if __name__ == '__main__':
    main()
