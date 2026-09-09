#!/usr/bin/env python3
"""Startseiten-Entwurf — Geruest bauen und fertigen Entwurf pruefen.

Das Skript gestaltet nicht. Es legt das Geruest an (Abschnittsfolge aus der Copy,
Palette und Schriften aus dem Konzept, Entwurfs-Kennzeichnung) und prueft danach,
was sich pruefen laesst.

Aufruf:
  python3 3b_entwurf.py --geruest [--datei Entwurf-Startseite.html]
  python3 3b_entwurf.py --pruefen [--datei Entwurf-Startseite.html]
"""
import sys, os, re, json, html

def arg(n, standard=None):
    return sys.argv[sys.argv.index(n)+1] if n in sys.argv else standard

def fehler(t):
    print(f'\n  FEHLER  {t}\n', file=sys.stderr); sys.exit(1)

def titel(t):
    print(f'\n{t}\n' + '─' * min(len(t), 72))

DATEI = arg('--datei', 'Entwurf-Startseite.html')
KONZEPT = arg('--konzept', 'konzept.json')
COPY = arg('--copy', 'Shop-Copy.html')

# ---------------------------------------------------------------- Geruest
def geruest():
    if os.path.exists(DATEI):
        fehler(f'{DATEI} gibt es schon. Loeschen oder --datei anders setzen — '
               'ein Geruest wuerde die Gestaltung ueberschreiben.')
    k = json.load(open(KONZEPT)) if os.path.exists(KONZEPT) else {}
    farben = k.get('farben') or {}
    schriften = k.get('schriften') or {}
    marke = k.get('marke') or k.get('shop') or 'Shop'

    # Abschnitte aus der Copy ziehen, sonst aus dem Konzept, sonst Standardfolge
    abschnitte = []
    if os.path.exists(COPY):
        roh = open(COPY, encoding='utf-8').read()
        for m in re.finditer(r'<h2[^>]*>(.*?)</h2>', roh, re.S | re.I):
            t = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            if t and t.lower() not in [a['titel'].lower() for a in abschnitte]:
                abschnitte.append({'titel': t})
    if not abschnitte:
        abschnitte = [{'titel': t} for t in k.get('abschnitte', [])]
    if not abschnitte:
        fehler(f'Keine Abschnitte gefunden — weder in {COPY} noch in {KONZEPT}. '
               'Erst die Copy schreiben und freigeben lassen.')

    def f(name, standard):
        return farben.get(name) or standard
    css_vars = '\n    '.join(f'--{n}:{v};' for n, v in
                             (('grund', f('hintergrund', '#FFFFFF')),
                              ('text', f('text', '#1D1D1F')),
                              ('akzent', f('akzent', '#2E4B2F')),
                              ('zweit', f('zweit', '#C9A227')),
                              ('linie', '#E4E2DC'),
                              ('gedaempft', '#6C7269')))
    kopf_schrift = schriften.get('ueberschrift', 'Fraunces')
    lauf_schrift = schriften.get('fliesstext', 'Instrument Sans')
    fam = f"family={kopf_schrift.replace(' ', '+')}:wght@400;500;600&family={lauf_schrift.replace(' ', '+')}:wght@400;500;600"

    kaesten = []
    for i, a in enumerate(abschnitte):
        kaesten.append(f"""
<section class="abschnitt" id="a{i+1}">
  <div class="wrap">
    <p class="eyebrow">ABSCHNITT {i+1}</p>
    <h2>{html.escape(a['titel'])}</h2>
    <!-- GESTALTEN: Layout, Bild, Fliesstext aus der freigegebenen Copy einsetzen.
         Offene Punkte als <p class="fussnote">Hinweis für die Umsetzung: …</p> -->
    <div class="platzhalter">noch zu gestalten</div>
  </div>
</section>""")

    seite = f"""<!DOCTYPE html>
<html lang="de"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(marke)} — Startseiten-Entwurf · HDC Digital</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?{fam}&display=swap" rel="stylesheet">
<style>
  :root{{
    {css_vars}
  }}
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{font-family:"{lauf_schrift}",Arial,sans-serif;color:var(--text);
    background:var(--grund);line-height:1.6;font-size:17px}}
  h1,h2,h3{{font-family:"{kopf_schrift}",Georgia,serif;font-weight:500;line-height:1.15}}
  img{{display:block;max-width:100%}}
  .wrap{{max-width:1180px;margin:0 auto;padding:0 24px}}
  .eyebrow{{font-size:13px;letter-spacing:.14em;text-transform:uppercase;
    color:var(--gedaempft);font-weight:600;margin-bottom:14px}}
  section{{padding:88px 0}}
  @media(max-width:760px){{section{{padding:56px 0}}}}
  .draft-badge{{position:fixed;top:14px;right:-46px;transform:rotate(38deg);
    background:var(--zweit);color:var(--text);font-size:12px;font-weight:600;
    letter-spacing:.1em;padding:6px 52px;z-index:99;box-shadow:0 2px 8px rgba(0,0,0,.15)}}
  .platzhalter{{border:1.5px dashed var(--linie);color:var(--gedaempft);
    padding:60px 24px;text-align:center;font-size:14px;margin-top:20px}}
  .fussnote{{font-size:14px;color:var(--gedaempft);font-style:italic;
    border-left:2px solid var(--zweit);padding-left:14px;margin-top:22px}}
  footer{{background:var(--text);color:#fff;padding:40px 0;font-size:14px}}
</style></head><body>
<div class="draft-badge">ENTWURF · HDC</div>
{''.join(kaesten)}
<footer><div class="wrap">
  Startseiten-Entwurf · HDC Digital GmbH · nicht zur Veröffentlichung
</div></footer>
</body></html>"""
    open(DATEI, 'w', encoding='utf-8').write(seite)
    titel(f'Gerüst geschrieben — {DATEI}')
    print(f'  {len(abschnitte)} Abschnitte aus '
          f'{COPY if os.path.exists(COPY) else KONZEPT}:')
    for i, a in enumerate(abschnitte): print(f'   {i+1:2d}  {a["titel"]}')
    print(f'\n  Palette und Schriften stehen als Ausgangspunkt drin, nicht als Ergebnis.')
    print('  Jetzt gestalten — references/entwurf.md und gestaltung.md.\n')

# ---------------------------------------------------------------- Pruefen
def pruefen():
    if not os.path.exists(DATEI): fehler(f'{DATEI} gibt es nicht.')
    q = open(DATEI, encoding='utf-8').read()
    text = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', q, flags=re.S | re.I)
    text = re.sub(r'<[^>]+>', ' ', text)
    titel(f'Entwurf prüfen — {DATEI}')
    befunde = []

    def pruef(ok, name, hinweis_wenn_nicht):
        print(f'  {"ok" if ok else "! "} {name}')
        if not ok:
            print(f'       {hinweis_wenn_nicht}'); befunde.append(name)

    pruef('draft-badge' in q or 'ENTWURF' in q, 'Als Entwurf gekennzeichnet',
          'Eckbanner „ENTWURF" fehlt — die Datei wandert per Mail weiter.')
    pruef('nicht zur Veröffentlichung' in q, 'Fußzeilen-Hinweis',
          '„nicht zur Veröffentlichung" in der Fußzeile ergänzen.')
    ungestaltet = q.lower().count('noch zu gestalten')
    pruef(not ungestaltet, 'Alle Abschnitte gestaltet',
          f'{ungestaltet}× „noch zu gestalten" — das Gerüst steht dort unverändert.')
    bildluecken = len(re.findall(r'Bildplatzhalter|Bild folgt|Foto folgt', q, re.I))
    blind = re.findall(r'lorem ipsum|dolor sit amet|Blindtext|Beispieltext', text, re.I)
    pruef(not blind, 'Kein Blindtext', f'{len(blind)} Fundstellen.')
    offen = re.findall(r'\[RÜCKFRAGE[^\]]*\]', q)
    pruef(not offen, 'Keine offenen Rückfragen',
          f'{len(offen)} offene [RÜCKFRAGE …] — vor der Abnahme klären oder als '
          'Fußnote am Abschnitt formulieren.')

    bilder = re.findall(r'<img[^>]+src="([^"]+)"', q) + \
             re.findall(r'url\((["\']?)(https?://[^)"\']+)', q)
    n_bilder = len(bilder)
    pruef(n_bilder >= 3, 'Echte Bilder',
          f'nur {n_bilder} Bilder — graue Flächen zeigen nicht, ob die Bildsprache trägt.')
    leer = [b for b in re.findall(r'<img[^>]+src="([^"]*)"', q) if not b.strip()]
    if leer: pruef(False, 'Leere Bildquellen', f'{len(leer)} <img> ohne src.')

    abschnitte = re.findall(r'<section', q)
    pruef(len(abschnitte) >= 4, 'Abschnittsfolge',
          f'{len(abschnitte)} Abschnitte — für eine Startseite meist zu wenig.')
    pruef('@media' in q, 'Mobil bedacht', 'Keine einzige @media-Regel.')
    pruef('fonts.googleapis.com' in q or '@font-face' in q, 'Eigene Schriften',
          'Keine Schrift eingebunden — der Entwurf läuft auf Systemschrift.')

    # Theme-Standard erkennen: nur Graustufen deutet auf ungestaltet hin
    farben = set(re.findall(r'#([0-9A-Fa-f]{6})\b', q))
    bunt = [f for f in farben if len({f[0:2].lower(), f[2:4].lower(), f[4:6].lower()}) > 1]
    pruef(len(bunt) >= 3, 'Eigene Palette',
          f'nur {len(bunt)} nicht-graue Farbwerte — sieht nach Theme-Standard aus.')

    hinweise = len(re.findall(r'class="[^"]*fussnote', q))
    print(f'\n  {n_bilder} Bilder, {len(abschnitte)} Abschnitte, '
          f'{hinweise} Umsetzungshinweise am Abschnitt.')
    if bildluecken:
        print(f'  {bildluecken} Bildplatzhalter — Fotos fehlen noch beim Kunden.')
        print('     Kein Blocker für die Abnahme des Entwurfs, aber für den Livegang.')
    if not hinweise:
        print('  Kein einziger Umsetzungshinweis. Beim Gestalten fällt sonst immer etwas '
              'auf —\n     Widersprüche in Versandregeln, fehlende Angaben, zwei Preise '
              'für dasselbe.')
    if befunde:
        print(f'\n  {len(befunde)} Punkte offen: ' + ', '.join(befunde) + '\n')
        sys.exit(1)
    print('\n  Entwurf ist vorlagefähig. Jetzt dem Kunden zeigen — Freigabe 2.\n')

if '--geruest' in sys.argv: geruest()
elif '--pruefen' in sys.argv: pruefen()
else: print(__doc__)
