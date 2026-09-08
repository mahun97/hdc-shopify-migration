"""Gemeinsame Bausteine fuer alle Kit-Skripte: API-Zugriff, Laden der Zugangsdaten, Ausgabe."""
import json, os, sys, subprocess, tempfile, time, glob

API_VERSION = '2025-07'

def zugang(pfad=None):
    """Laedt SHOP und TOKEN. Reihenfolge: Argument, $SHOPIFY_ENV, einzige Datei in ~/.config/shopify-*.env"""
    if not pfad: pfad = os.environ.get('SHOPIFY_ENV')
    if not pfad:
        treffer = glob.glob(os.path.expanduser('~/.config/shopify-*.env'))
        if len(treffer) == 1: pfad = treffer[0]
        elif not treffer: fehler('Keine Zugangsdatei gefunden. Siehe docs/01-custom-app.md')
        else: fehler('Mehrere Shops konfiguriert. Bitte angeben:\n  ' + '\n  '.join(treffer))
    pfad = os.path.expanduser(pfad)
    if not os.path.exists(pfad): fehler(f'Zugangsdatei nicht gefunden: {pfad}')
    d = dict(l.strip().split('=', 1) for l in open(pfad) if '=' in l and l.strip())
    if 'SHOP' not in d or 'TOKEN' not in d: fehler(f'{pfad} braucht die Zeilen SHOP= und TOKEN=')
    return d

def gql(env, query, variables=None, still=False):
    """GraphQL-Aufruf mit Wiederholung bei Drosselung. still=True -> None statt Abbruch."""
    body = json.dumps({'query': query, 'variables': variables or {}})
    for versuch in range(5):
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
            f.write(body); tmp = f.name
        try:
            r = subprocess.run(['curl', '-sS', '-X', 'POST',
                f"https://{env['SHOP']}/admin/api/{API_VERSION}/graphql.json",
                '-H', f"X-Shopify-Access-Token: {env['TOKEN']}",
                '-H', 'Content-Type: application/json', '--data-binary', f'@{tmp}'],
                capture_output=True, text=True, timeout=300)
        finally:
            os.unlink(tmp)
        if r.returncode != 0:
            if versuch < 4: time.sleep(2 ** versuch); continue
            fehler(f'Verbindung fehlgeschlagen: {r.stderr[:200]}')
        d = json.loads(r.stdout)
        if d.get('errors'):
            text = json.dumps(d['errors'], ensure_ascii=False)
            if 'THROTTLED' in text and versuch < 4: time.sleep(2 ** versuch); continue
            if still: return None
            fehler('Shopify meldet:\n' + json.dumps(d['errors'], ensure_ascii=False, indent=1)[:600])
        return d['data']
    fehler('Zu viele Wiederholungen')

def seiten(env, feld, felder):
    """Holt alle Datensaetze eines Listenfeldes ueber die Seitengrenze hinweg."""
    out, cursor = [], None
    while True:
        d = gql(env, 'query($c:String){ %s(first:100, after:$c){ nodes { %s } pageInfo { hasNextPage endCursor } } }'
                % (feld, felder), {'c': cursor})[feld]
        out += d['nodes']
        if not d['pageInfo']['hasNextPage']: return out
        cursor = d['pageInfo']['endCursor']

def pruefe_fehler(payload, wo):
    errs = payload.get('userErrors') or []
    if errs: fehler(f'{wo}: ' + json.dumps(errs, ensure_ascii=False, indent=1)[:600])

def fehler(text):
    print(f'\n  FEHLER  {text}\n', file=sys.stderr); sys.exit(1)

def titel(text):
    print(f'\n{text}\n' + '─' * min(len(text), 72))

def gate(frage):
    """Freigabepunkt. Ohne ausdrueckliches Ja geht es nicht weiter."""
    print(f'\n  ┌{"─"*70}┐\n  │ FREIGABE ERFORDERLICH{" "*48}│\n  └{"─"*70}┘')
    print(f'  {frage}')
    if input('  Tippe JA zum Fortfahren: ').strip().upper() != 'JA':
        print('  Abgebrochen. Es wurde nichts geändert.'); sys.exit(0)
