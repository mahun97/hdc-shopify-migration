#!/usr/bin/env python3
"""Prueft ein aufgebautes Theme, bevor es freigegeben wird: offene Marker, leere Sections,
nicht zugewiesene Kollektionen und Bilder, Standardlinks — und ob die Copy vollstaendig
angekommen ist. Die Darstellung selbst prueft der Browser, nicht dieses Skript.
Aufruf: python3 6_pruefung.py --theme <id> [--env pfad]
"""
import sys, os, json, re, subprocess, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify import zugang, gql, titel, fehler

def arg(name, pflicht=True, standard=None):
    if name in sys.argv: return sys.argv[sys.argv.index(name)+1]
    if pflicht: fehler(f'{name} fehlt')
    return standard

env = zugang(arg('--env', False))
tid = arg('--theme')

def asset(key):
    url = (f"https://{env['SHOP']}/admin/api/2025-07/themes/{tid}/assets.json"
           f"?asset%5Bkey%5D={urllib.parse.quote(key)}")
    r = subprocess.run(['curl','-sS',url,'-H',f"X-Shopify-Access-Token: {env['TOKEN']}"],
                       capture_output=True, text=True, timeout=120)
    try: return json.loads(r.stdout)['asset']['value']
    except Exception: return None

theme = gql(env, 'query($id:ID!){ theme(id:$id){ name role } }',
            {'id': f'gid://shopify/OnlineStoreTheme/{tid}'})['theme']
r = subprocess.run(['curl','-sS', f"https://{env['SHOP']}/admin/api/2025-07/themes/{tid}/assets.json",
                    '-H', f"X-Shopify-Access-Token: {env['TOKEN']}"], capture_output=True, text=True, timeout=180)
templates = sorted(a['key'] for a in json.loads(r.stdout).get('assets', [])
                   if a['key'].startswith('templates/') and a['key'].endswith('.json'))

BEFUNDE = []
def merke(schwere, thema, wo, detail):
    BEFUNDE.append((schwere, thema, wo, detail))

MARKER = re.compile(r'\[(RÜCKFRAGE|RUECKFRAGE|TODO|TBD|PLATZHALTER|LOREM)[^\]]*\]', re.I)

def durchlaufe(knoten, pfad, section_typ, ist_section=False):
    """Geht rekursiv durch Sections und Bloecke und sammelt Auffaelligkeiten."""
    if isinstance(knoten, dict):
        st = knoten.get('settings') or {}
        for feld, wert in st.items():
            if not isinstance(wert, str): continue
            m = MARKER.search(wert)
            if m: merke('blocker', 'Offener Marker im Text', pfad, m.group(0)[:70])
            if re.search(r'\b(lorem ipsum|beispieltext|dein text hier)\b', wert, re.I):
                merke('blocker', 'Platzhaltertext', pfad, wert[:60])
            if feld == 'link' and wert == 'shopify://collections/all':
                merke('hinweis', 'Standardlink nicht angepasst', pfad, wert)
        # Kollektion zugewiesen? Nur auf Section-Ebene pruefen, nicht in jedem Block
        if ist_section and section_typ in ('product-list', 'featured-collection') and 'collection' in st and not st['collection']:
            merke('blocker', 'Keine Kollektion zugewiesen', pfad, 'Section zeigt Platzhalterprodukte')
        if ist_section and section_typ == 'collection-list' and not (st.get('collection_list') or []):
            merke('blocker', 'Keine Kollektionen zugewiesen', pfad, 'Section zeigt Platzhalter')
        # Bildfelder leer?
        for feld in ('image', 'image_1', 'image_2', 'video_1'):
            if feld in st and not st[feld]:
                merke('hinweis', 'Bild nicht gesetzt', pfad, feld)
        # Mobile: Themes halten eigene Felder fuer die schmale Ansicht. Ob sie gesetzt sind,
        # ist aus der Datei pruefbar - wie es aussieht, nicht.
        if ist_section:
            mobil = [k for k in st if 'mobile' in k.lower()]
            leer = [k for k in mobil if st[k] in ('', None, [], False)]
            if mobil and len(leer) == len(mobil):
                merke('hinweis', 'Keine Mobil-Einstellung gesetzt', pfad,
                      ', '.join(mobil[:3]) + (' …' if len(mobil) > 3 else ''))
            lang = [(k, v) for k, v in st.items()
                    if isinstance(v, str) and k == 'text' and len(re.sub('<[^>]+>', '', v)) > 68]
            for k, v in lang:
                merke('hinweis', 'Überschrift könnte mobil umbrechen', pfad,
                      f'{len(re.sub("<[^>]+>", "", v))} Zeichen')
        for bid, block in (knoten.get('blocks') or {}).items():
            durchlaufe(block, f'{pfad} › {block.get("type", bid)}', section_typ)

titel(f'Prüfung: {theme["name"]}  ({theme["role"]})')
gesamt_sections = 0
for tpl in templates:
    roh = asset(tpl)
    if not roh: continue
    try: j = json.loads(re.sub(r'/\*.*?\*/', '', roh, flags=re.S))
    except Exception:
        merke('blocker', 'Template nicht lesbar', tpl, 'kein gültiges JSON'); continue
    name = tpl.replace('templates/', '').replace('.json', '')
    sections = j.get('sections') or {}
    ordnung = j.get('order') or list(sections)
    if not ordnung: merke('hinweis', 'Template ohne Sections', name, '')
    for sid in ordnung:
        s = sections.get(sid) or {}
        typ = s.get('type', '?')
        gesamt_sections += 1
        durchlaufe(s, f'{name} › {typ}', typ, ist_section=True)
        if not (s.get('blocks') or s.get('settings')):
            merke('hinweis', 'Section ohne Inhalt', f'{name} › {typ}', '')

# ---------------------------------------------------------------- Copy abgeglichen?
if os.path.exists('copy.json'):
    copy = json.load(open('copy.json'))
    nicht_frei = [(seite, b['section']) for seite, blocks in copy['seiten'].items()
                  for b in blocks if b.get('status') != 'freigegeben']
    for seite, sec in nicht_frei[:8]:
        merke('blocker', 'Copy nicht freigegeben', f'{seite} › {sec[:40]}', '')
    for seite, blocks in copy['seiten'].items():
        for b in blocks:
            for feld, wert in b['texte'].items():
                if MARKER.search(str(wert or '')):
                    merke('blocker', 'Offene Rückfrage in der Copy', f'{seite} › {b["section"][:34]}', feld)

print(f'  {len(templates)} Templates · {gesamt_sections} Sections geprüft\n')
for schwere, sammel in (('blocker', 'Muss vor der Freigabe weg'), ('hinweis', 'Bitte ansehen')):
    treffer = [b for b in BEFUNDE if b[0] == schwere]
    if not treffer:
        print(f'  [ OK ] {sammel}: nichts gefunden'); continue
    print(f'  {sammel} ({len(treffer)}):')
    gesehen = set()
    for _, thema, wo, detail in treffer:
        schluessel = (thema, wo)
        if schluessel in gesehen: continue
        gesehen.add(schluessel)
        print(f'    · {thema} — {wo}' + (f'  [{detail}]' if detail else ''))
    print()

print('  Was dieses Skript NICHT prüfen kann — das gehört in den Browser:')
print('    tatsächliche Darstellung, Überlappungen, Warenkorb, Ladeverhalten.')
print('    Achtung: Das Fenster zu verkleinern reicht für die Mobilprüfung NICHT —')
print('    der Rendering-Viewport bleibt breit. Es braucht echte Geräteemulation.')
print(f'\n  Vorschau: https://{env["SHOP"]}/?preview_theme_id={tid}\n')
sys.exit(1 if any(b[0] == 'blocker' for b in BEFUNDE) else 0)
