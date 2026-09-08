#!/usr/bin/env python3
"""Liest eine Shop-Konzeptpraesentation (PDF) aus und leitet daraus das Textgeruest ab.
Ergebnis: konzept.json — Farbschema, Theme-Empfehlung, Seitenaufbau, benoetigte Textbausteine.
Aufruf: python3 1_konzept_lesen.py "Shop-Konzeption.pdf"
"""
import sys, os, json, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify import titel, fehler
try: import fitz
except ImportError: fehler('PyMuPDF fehlt.  pip3 install pymupdf')

pdf = next((a for a in sys.argv[1:] if a.lower().endswith('.pdf')), None)
if not pdf: fehler('Bitte die Konzept-PDF angeben:  python3 1_konzept_lesen.py "Konzept.pdf"')
if not os.path.exists(pdf): fehler(f'{pdf} nicht gefunden')
d = fitz.open(pdf)

# ---------------------------------------------------------------- Farbschema
flaechen = collections.Counter()
for p in d:
    for z in p.get_drawings():
        f = z.get('fill')
        if not f or len(f) < 3: continue
        h = '#%02X%02X%02X' % tuple(int(round(c*255)) for c in f[:3])
        if h in ('#FFFFFF', '#000000'): continue
        r, g, b = (int(h[i:i+2], 16) for i in (1, 3, 5))
        if max(r,g,b) - min(r,g,b) < 12 and 200 < max(r,g,b): continue   # Grautoene der Folie
        flaechen[h] += abs(z['rect'].width * z['rect'].height)
farben = [h for h, _ in flaechen.most_common(6)]

# ---------------------------------------------------------------- Theme
theme = None
for p in d:
    m = re.search(r'Empfehlung:\s*([A-Za-zÄÖÜäöü][\w\- ]{2,24})', p.get_text())
    if m: theme = m.group(1).strip(); break

# ---------------------------------------------------------------- Markenprofil
def abschnitt(*marker):
    """Liefert den ROHTEXT einer Konzeptseite. Bewusst ohne Aufbereitung: Praesentationen
    trennen Aufzaehlungen oft weder durch Satzzeichen noch durch Abstaende, jede Heuristik
    zerschneidet also an der falschen Stelle. Die Deutung uebernimmt Claude im Skill."""
    for p in d:
        zeilen = [z.strip() for z in p.get_text().split('\n') if z.strip()]
        if any(z in marker for z in zeilen):
            return [z for z in zeilen if z not in marker and len(z) > 2]
    return []

profil = {
  'zielgruppe':  abschnitt('Zielgruppe'),
  'wettbewerb':  abschnitt('Konkurrenten', 'Wettbewerber'),
  'kategorien':  abschnitt('Produkt-Kategorie-', 'Produkt-Kategorie-Aufteilung'),
  'unterseiten': abschnitt('Unterseiten') if False else [],
  'filter':      abschnitt('Filter'),
}

# ---------------------------------------------------------------- Seitenaufbau
SEITEN = ('Startseite', 'Kategorieseite', 'Produktseite', 'Unterseiten', 'Warenkorb', 'Menü')
aufbau = collections.defaultdict(list)
for i, p in enumerate(d, 1):
    zeilen = [z.strip() for z in p.get_text().split('\n') if z.strip()]
    for typ in SEITEN:
        if any(z == typ or z.startswith(typ) for z in zeilen):
            rest = [z for z in zeilen if z != typ and not z.startswith('Design-Element')]
            for r in rest:
                if len(r) > 6: aufbau[typ].append({'seite': i, 'beschreibung': r})

# ---------------------------------------------------------------- Textbausteine ableiten
def bausteine(beschreibung):
    """Welche Texte braucht eine so beschriebene Section?"""
    b = beschreibung.lower()
    out = []
    if 'hero' in b or 'bildbanner' in b or 'titel mit bild' in b:
        out += ['Überschrift', 'Unterzeile', 'Button-Text']
    if 'bild-text' in b or 'bild - text' in b:
        out += ['Überschrift', 'Fließtext', 'Button-Text']
    if 'bestseller' in b or 'kollektion' in b or 'weiterer produkte' in b or 'kategorien' in b:
        out += ['Sektionsüberschrift', 'ggf. Unterzeile']
    if 'newsletter' in b:
        out += ['Überschrift', 'Kurztext', 'Button-Text', 'Datenschutzhinweis']
    if 'usp' in b or 'beschreibung' in b:
        out += ['Produktbeschreibung', 'USP-Liste', 'Anwendungshinweis']
    if 'footer' in b:
        out += ['Spaltenüberschriften', 'Kurzvorstellung']
    return out or ['Überschrift', 'Fließtext']

plan = {}
for typ, eintraege in aufbau.items():
    plan[typ] = [{'quelle_seite': e['seite'], 'section': e['beschreibung'],
                  'texte': bausteine(e['beschreibung'])} for e in eintraege]

ergebnis = {'quelle': os.path.basename(pdf), 'seiten_im_konzept': d.page_count,
            'farbschema': farben, 'theme_empfehlung': theme,
            'markenprofil': profil, 'seitenaufbau': plan}
json.dump(ergebnis, open('konzept.json', 'w'), ensure_ascii=False, indent=1)

titel(f'Konzept ausgewertet: {os.path.basename(pdf)}')
print(f'  Seiten:            {d.page_count}')
print(f'  Theme-Empfehlung:  {theme or "nicht gefunden"}')
print(f'  Farbschema:        {", ".join(farben) or "nicht gefunden"}')
if profil['zielgruppe']:
    print(f'\n  Zielgruppe laut Konzept (Rohtext — bitte selbst verdichten):')
    for zg in profil['zielgruppe']: print(f'    {zg[:92]}')
if profil['wettbewerb']:
    print(f'\n  Wettbewerber: {", ".join(profil["wettbewerb"])}')
print(f'\n  Seitenaufbau:')
gesamt = 0
for typ, eintraege in plan.items():
    print(f'    {typ:16s} {len(eintraege)} Sections')
    gesamt += sum(len(e['texte']) for e in eintraege)
print(f'\n  {gesamt} Textbausteine zu schreiben.')
print('  → konzept.json geschrieben\n')
