#!/usr/bin/env python3
"""Erzeugt ein Bildmotiv ueber die OpenAI-Bild-API und legt es als PNG ab.

Gedacht fuer Stimmungs- und Gestaltungselemente: Hintergruende, Texturen, Formen,
freigestellte generische Objekte. NICHT fuer Produktbilder — siehe unten.

Schluessel liegt in ~/.config/openai.env:
    KEY=sk-...

Aufruf:
  python3 8b_bild_erzeugen.py --schluessel-pruefen        kostet nichts
  python3 8b_bild_erzeugen.py --prompt "…" --name hero-grund
  python3 8b_bild_erzeugen.py --prompt "…" --name element --transparent
  python3 8b_bild_erzeugen.py --prompt "…" --name breit --format quer --qualitaet hoch
  python3 8b_bild_erzeugen.py --prompt "…" --name band --groesse 2400x1008

Formate: quadrat (1024×1024) · quer (1536×1024) · hoch (1024×1536)
Freie Groesse mit --groesse, nur bei gpt-image-2: beide Seiten durch 16 teilbar,
laengste Kante hoechstens 3840, Seitenverhaeltnis hoechstens 3:1.
Qualitaet: niedrig · mittel · hoch
Modell mit --modell, Standard gpt-image-2. Verfuegbar sind ausserdem gpt-image-1,
gpt-image-1-mini, gpt-image-1.5 und chatgpt-image-latest.

WICHTIG — was hier nicht erzeugt wird:
  Bilder des Produkts, das der Kunde verkauft. Ein generiertes Produktbild zeigt ein
  Produkt, das es so nicht gibt. In einem Shop ist das irrefuehrende Werbung, unabhaengig
  davon, wie gut es aussieht. Produktfotos kommen vom Kunden.
"""
import sys, os, json, base64, subprocess, tempfile

def arg(n, pflicht=False, standard=None):
    if n in sys.argv: return sys.argv[sys.argv.index(n)+1]
    if pflicht: fehler(f'{n} fehlt')
    return standard

def fehler(t):
    print(f'\n  FEHLER  {t}\n', file=sys.stderr); sys.exit(1)

FORMATE = {'quadrat': '1024x1024', 'quer': '1536x1024', 'hoch': '1024x1536'}
# gpt-image-2 kann daneben freie Groessen: beide Seiten durch 16 teilbar,
# laengste Kante <= 3840, Seitenverhaeltnis <= 3:1.
MODELL_STANDARD = 'gpt-image-2'
QUALITAET = {'niedrig': 'low', 'mittel': 'medium', 'hoch': 'high'}

def schluessel(pfad=None):
    pfad = pfad or os.path.expanduser('~/.config/openai.env')
    if not os.path.exists(pfad):
        fehler(f'{pfad} gibt es nicht.\n' + ANLEITUNG)
    for zeile in open(pfad):
        zeile = zeile.strip()
        if zeile.startswith(('KEY=', 'OPENAI_API_KEY=')):
            return zeile.split('=', 1)[1].strip().strip('"\'')
    fehler(f'Keine Zeile KEY= in {pfad}')

ANLEITUNG = '''
  So legst du den Plattform-Schlüssel ab — einmalig je Rechner:

  1. platform.openai.com/api-keys öffnen, mit dem HDC-Konto anmelden
  2. "Create new secret key", Name z. B. "claude-code-<dein-name>"
  3. Den Schlüssel EINMAL kopieren — er wird danach nie wieder angezeigt
  4. Im Terminal, den Platzhalter durch den Schlüssel ersetzen:

     printf 'KEY=sk-DEIN_SCHLUESSEL\\n' > ~/.config/openai.env
     chmod 600 ~/.config/openai.env

  5. Prüfen, ohne etwas abzurechnen:

     python3 8b_bild_erzeugen.py --schluessel-pruefen

  Der Schlüssel gehört NICHT in den Chat, nicht in eine E-Mail, nicht in ein
  Ticket und auf keinen Screenshot. Claude liest die Datei selbst.
  Zugriff auf die Bildmodelle setzt eine verifizierte Organisation voraus.
'''

def pruefen():
    k = schluessel(arg('--env'))
    r = subprocess.run(['curl', '-sS', '-o', '/dev/null', '-w', '%{http_code}',
                        'https://api.openai.com/v1/models/gpt-image-2',
                        '-H', f'Authorization: Bearer {k}', '--max-time', '30'],
                       capture_output=True, text=True, timeout=60)
    code = r.stdout.strip()
    print()
    if code == '200':
        print(f'  ok  Schlüssel gültig, gpt-image-2 freigeschaltet.  ({k[:7]}…{k[-4:]})')
        print('      Es wurde nichts abgerechnet.\n'); return
    if code == '401':
        fehler('Schlüssel wird abgelehnt (401). Neu erzeugen und ablegen:\n' + ANLEITUNG)
    if code in ('403', '404'):
        fehler('Schlüssel gültig, aber gpt-image-2 ist nicht freigeschaltet '
               f'({code}).\n          Im OpenAI-Dashboard unter Settings → '
               'Organization die Verifizierung abschließen.')
    fehler(f'Unerwartete Antwort: HTTP {code}')


def main():
    if '--schluessel-pruefen' in sys.argv: pruefen(); return
    prompt = arg('--prompt', True); name = arg('--name', True)
    fmt = arg('--format', False, 'quer'); qual = arg('--qualitaet', False, 'mittel')
    if fmt not in FORMATE: fehler(f'--format erwartet {" · ".join(FORMATE)}')
    if qual not in QUALITAET: fehler(f'--qualitaet erwartet {" · ".join(QUALITAET)}')

    modell = arg('--modell', False, MODELL_STANDARD)
    groesse = arg('--groesse', False, FORMATE[fmt])
    koerper = {'model': modell, 'prompt': prompt, 'n': 1,
               'size': groesse, 'quality': QUALITAET[qual]}
    if not modell.startswith(('gpt-image-2', 'chatgpt-image')):
        koerper['output_format'] = 'png'
    if '--transparent' in sys.argv:
        koerper['background'] = 'transparent'

    print(f'\n  Erzeuge "{name}" — {modell}, {groesse}, Qualität {qual}'
          + (', transparenter Grund' if '--transparent' in sys.argv else ''))
    print(f'  Prompt: {prompt[:110]}{"…" if len(prompt) > 110 else ""}')

    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
        json.dump(koerper, f); anfrage = f.name
    try:
        r = subprocess.run(
            ['curl', '-sS', '-X', 'POST', 'https://api.openai.com/v1/images/generations',
             '-H', f'Authorization: Bearer {schluessel(arg("--env"))}',
             '-H', 'Content-Type: application/json',
             '--data-binary', f'@{anfrage}', '--max-time', '300'],
            capture_output=True, text=True, timeout=330)
    finally:
        os.unlink(anfrage)
    if r.returncode: fehler(f'curl: {r.stderr[:300]}')
    try:
        d = json.loads(r.stdout)
    except Exception:
        fehler(f'Keine gültige Antwort: {r.stdout[:300]}')
    if 'error' in d:
        e = d['error']
        fehler(f'OpenAI: {e.get("message", e)}'
               + ('\n          Der Schlüssel braucht Zugriff auf gpt-image-1. Bei neuen '
                  'Organisationen\n          ist dafür eine Verifizierung nötig.'
                  if 'model' in str(e).lower() or 'verif' in str(e).lower() else ''))
    if not d.get('data'): fehler(f'Antwort ohne Bilddaten: {json.dumps(d)[:300]}')

    roh = base64.b64decode(d['data'][0]['b64_json'])
    ziel = os.path.abspath(f'{name}.png')
    open(ziel, 'wb').write(roh)
    v = (d.get('usage') or {})
    print(f'\n  {ziel}')
    print(f'  {len(roh)//1024} KB'
          + (f' · {v.get("total_tokens")} Token abgerechnet' if v.get('total_tokens') else ''))
    print('\n  Ansehen, bevor es in den Shop geht. Generierte Bilder sind Gestaltung,')
    print('  keine Abbildung — nichts darf darin so aussehen wie das Produkt des Kunden.\n')

if __name__ == '__main__':
    main()
