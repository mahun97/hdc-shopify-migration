#!/usr/bin/env python3
"""Erzeugt HDC-Shopify-Prozess-Diagramme.pdf — nur Grafik, kein Fliesstext.

Seite 1  Gesamtprozess grob — vier Stufen, sonst nichts
Seite 2  Alle Phasen und Freigaben auf einem Blatt
Seite 3  shopify-settings
Seite 4  shopify-migration
Seite 5  shopify-design
Seite 6  shopify-abnahme mit den drei Fachpruefungen
Seite 7  Bildwerkzeuge — welches Skript fuer welche Bildsorte

Aufruf:  python3 diagramme.py
"""
import os, subprocess, io

BLAU, DUNKEL, GOLD = '#010B80', '#0E112D', '#A79563'
GRAU, LINIE, HELL, TEXT = '#5B6270', '#DFE2EA', '#F5F6FA', '#1D1D1F'
B, H = 1120, 792                      # A4 quer bei 96 dpi

# wer: ki = Claude fuehrt aus | hand = Mensch im Admin | kunde = Kunde liefert
STUFEN = [
 {'nr': 1, 'skill': 'shopify-settings', 'titel': 'Grundeinrichtung',
  'ergebnis': 'Einrichtungsstand.md',
  'schritte': [
    {'n': 1, 't': 'Zugang',                     'wer': 'hand'},
    {'n': 2, 't': 'Bestandsaufnahme',           'wer': 'ki',   's': '1_bestandsaufnahme.py',
     'a': 'Einrichtungsstand.md'},
    {'g': 'Befund besprochen'},
    {'n': 3, 't': 'Rechtliches',                'wer': 'kunde','s': '2_richtlinien.py',
     'a': 'AGB · Widerruf · Datenschutz · Impressum'},
    {'n': 4, 't': 'Versand',                    'wer': 'kunde', 'a': 'Zonen · Tarife'},
    {'n': 5, 't': 'Sprachen, Märkte, Metafelder','wer': 'ki',
     'a': 'Metafeld-Definitionen  PUBLIC_READ'},
    {'n': 6, 't': 'Nur von Hand',               'wer': 'hand',
     'a': 'Zahlung · Domain · Checkout · Konten'},
    {'g': 'Checkliste abgearbeitet'},
    {'n': 7, 't': 'Abschluss',                  'wer': 'ki',   's': '1_bestandsaufnahme.py',
     'a': 'Soll-Ist-Vergleich'}]},
 {'nr': 2, 'skill': 'shopify-migration', 'titel': 'Produktmigration',
  'ergebnis': 'Produkte im Shop',
  'schritte': [
    {'n': 1, 't': 'Zugang',           'wer': 'hand', 'a': 'Custom App · Token'},
    {'g': 'Zugang steht'},
    {'n': 2, 't': 'Browser einrichten','wer': 'hand', 'a': 'Claude in Chrome — Pflicht'},
    {'n': 3, 't': 'Shop verstehen',   'wer': 'ki',   's': '1_steckbrief.py',
     'a': 'Metafelder · Optionen · Tags'},
    {'g': 'Tag-Vokabular bestätigt'},
    {'n': 4, 't': 'Vorlage füllen',   'wer': 'ki',   's': '2_vorlage.py', 'a': 'Importvorlage'},
    {'n': 5, 't': 'Prüfen',           'wer': 'ki',   's': '3_pruefen.py',
     'a': 'SKUs · Handles · Varianten'},
    {'g': 'Prüfung fehlerfrei'},
    {'n': 6, 't': 'Import',           'wer': 'ki',   's': '4_import.py',
     'a': 'Probelauf, dann Rest'},
    {'g': 'Probelauf in Ordnung'},
    {'n': 7, 't': 'Abnahme',          'wer': 'ki',   's': '5_abnahme.py', 'a': 'Soll-Ist'},
    {'g': 'Abnahme besprochen'}]},
 {'nr': 3, 'skill': 'shopify-design', 'titel': 'Aufbau im Theme',
  'ergebnis': 'Theme-Duplikat + Demo-Produkt',
  'schritte': [
    {'n': 0, 't': 'Schlüssel',            'wer': 'hand', 'a': '~/.config/openai.env'},
    {'n': 1, 't': 'Unterlagen sichten',   'wer': 'hand', 'a': 'Scope · Konzept'},
    {'n': 2, 't': 'Konzept auswerten',    'wer': 'ki',   's': '1_konzept_lesen.py',
     'a': 'konzept.json'},
    {'n': 3, 't': 'Shop-Copy schreiben',  'wer': 'ki',
     's': '2_copy_geruest.py · 3_copy_ansicht.py', 'a': 'Shop-Copy.html'},
    {'g': 'Copy vom Kunden abgenommen'},
    {'n': 4, 't': 'Website-Konzept',      'wer': 'ki',   's': '3b_entwurf.py',
     'a': 'Entwurf-Startseite.html — daraus entstehen die Sections'},
    {'g': 'Entwurf vom Kunden abgenommen'},
    {'n': 5, 't': 'Theme inventarisieren','wer': 'ki',   's': '4_theme_inventar.py'},
    {'n': 6, 't': 'Gestaltung',           'wer': 'ki',   's': '7_gestaltung.py',
     'a': 'Schriften · Farbpalette'},
    {'n': 7, 't': 'Bilder',               'wer': 'ki',
     's': '8_bilder.py · 8b_bild_erzeugen.py · 8c_hero.py · 8d_kategoriebanner.py',
     'a': 'Hero · Kategoriebanner · Motive'},
    {'n': 8, 't': 'Sections aufbauen',    'wer': 'ki',   's': '5_aufbau.py',
     'a': 'aus dem Entwurf, in derselben Reihenfolge'},
    {'n': 9, 't': 'Demo-Produkt',         'wer': 'ki',   's': '13_demoprodukt.py',
     'a': 'Metafelder füllen und im Theme prüfen'},
    {'n': 10, 't': 'Theme-Einstellungen', 'wer': 'ki',   's': '9_checkliste.py',
     'a': 'Logo · Favicon · Warenkorb'},
    {'n': 11, 't': 'Kategorie, Produkt, Service', 'wer': 'ki',
     's': '10_ · 11_ · 12_', 'a': 'Sortierung · Bausteine · Seiten'},
    {'n': 12, 't': 'Prüfen',              'wer': 'ki',   's': '6_pruefung.py',
     'a': '[RÜCKFRAGE …] finden'},
    {'g': 'Aufbau abgenommen'}]},
 {'nr': 4, 'skill': 'shopify-abnahme', 'titel': 'Abnahme & Übergabe',
  'ergebnis': 'Uebergabe.md',
  'schritte': [
    {'n': 1, 't': 'Alle drei Prüfungen', 'wer': 'ki', 's': 'abnahme.py',
     'a': 'befunde/ux · cro · recht.json'},
    {'n': 2, 't': 'Der Durchgang',       'wer': 'hand',
     'a': 'befunde/durchgang.json'},
    {'g': 'Befund vollständig'},
    {'n': 3, 't': 'Umsetzen',            'wer': 'ki', 's': 'umsetzen.py',
     'a': 'nur mit hinterlegtem Handgriff'},
    {'n': 4, 't': 'Übergabe',            'wer': 'ki', 's': 'uebergabe.py', 'a': 'Uebergabe.md'},
    {'g': 'Übergabe abgenommen'}]},
]

# Reihenfolge: erst der Shop steht — mit einem Demo-Produkt, an dem die Metafelder
# geprueft werden — dann kommen die echten Produkte. Andersherum muesste man
# Metafelder bei hunderten Produkten nachziehen.
STUFEN = [STUFEN[0], STUFEN[2], STUFEN[1], STUFEN[3]]
for _i, _st in enumerate(STUFEN): _st['nr'] = _i + 1

FARBE = {'ki': BLAU, 'hand': DUNKEL, 'kunde': GOLD}


def esc(t):
    return (t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def umbruch(text, max_zeichen):
    worte, zeilen, akt = text.split(' '), [], ''
    for w in worte:
        if len(akt) + len(w) + 1 <= max_zeichen or not akt:
            akt = f'{akt} {w}'.strip()
        else:
            zeilen.append(akt); akt = w
    if akt: zeilen.append(akt)
    return zeilen


def txt(x, y, s, gr=11, farbe=TEXT, gew=400, anker='start', mono=False, ls=0):
    fam = "'IBM Plex Mono',monospace" if mono else "Poppins,sans-serif"
    return (f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{gr}" fill="{farbe}" '
            f'font-weight="{gew}" text-anchor="{anker}"'
            + (f' letter-spacing="{ls}"' if ls else '') + f'>{esc(s)}</text>')


def sechseck(cx, cy, r, fuell, strich=None):
    p = []
    for i in range(6):
        import math
        a = math.radians(60 * i - 90)
        p.append(f'{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}')
    st = f' stroke="{strich}" stroke-width="1.5"' if strich else ''
    return f'<polygon points="{" ".join(p)}" fill="{fuell}"{st}/>'


def kopf(titel, unter):
    o = [f'<rect x="0" y="0" width="{B}" height="{H}" fill="#FFFFFF"/>']
    o.append(txt(48, 46, 'HDC DIGITAL', 11, BLAU, 800, ls=2.4))
    o.append(txt(48, 84, titel, 27, TEXT, 700))
    o.append(txt(48, 106, unter, 11.5, GRAU, 500))
    o.append(f'<line x1="48" y1="122" x2="{B-48}" y2="122" stroke="{BLAU}" stroke-width="2.5"/>')
    return o


def legende(y, rechts=False):
    o = []
    x = 48
    if rechts:
        gesamt = sum(19 + len(n) * 5.9 + 30 for n in
                     ('Claude führt aus', 'Mensch im Admin', 'Kunde liefert')) + 130
        x = B - 48 - gesamt
    for wer, name in (('ki', 'Claude führt aus'), ('hand', 'Mensch im Admin'),
                      ('kunde', 'Kunde liefert')):
        if wer == 'hand':
            o.append(f'<circle cx="{x+6}" cy="{y-2.5}" r="5.6" fill="#FFFFFF" '
                     f'stroke="{DUNKEL}" stroke-width="2"/>')
        else:
            o.append(f'<circle cx="{x+6}" cy="{y-2.5}" r="6.4" fill="{FARBE[wer]}"/>')
        o.append(txt(x + 19, y + 1, name, 9.5, GRAU, 500))
        x += 19 + len(name) * 5.9 + 30
    o.append(sechseck(x + 7, y - 2.5, 8, GOLD))
    o.append(txt(x + 7, y + 1.5, '✓', 9, '#FFFFFF', 700, 'middle'))
    o.append(txt(x + 21, y + 1, 'Freigabe — getipptes JA', 9.5, GRAU, 500))
    return o


# ---------------------------------------------------------------- Seite 1
def seite_grob():
    """Vier Stufen, sonst nichts. Der Blick, den man an die Wand haengt."""
    o = kopf('Shop-Erstellung', 'Vier Stufen · jede setzt voraus, dass die vorige abgenommen ist')
    n_ph = sum(len([x for x in st['schritte'] if 'n' in x]) for st in STUFEN)
    n_fg = sum(len([x for x in st['schritte'] if 'g' in x]) for st in STUFEN)
    br, luecke, y = 232, 44, 210
    for i, st in enumerate(STUFEN):
        x = 48 + i * (br + luecke)
        ph = len([q for q in st['schritte'] if 'n' in q])
        fg = len([q for q in st['schritte'] if 'g' in q])
        o.append(f'<rect x="{x}" y="{y}" width="{br}" height="250" rx="10" fill="{BLAU}"/>')
        o.append(sechseck(x + br / 2, y + 62, 34, '#FFFFFF'))
        o.append(txt(x + br / 2, y + 73, str(st['nr']), 34, BLAU, 800, 'middle'))
        o.append(txt(x + br / 2, y + 130, st['titel'], 17, '#FFFFFF', 700, 'middle'))
        o.append(txt(x + br / 2, y + 152, st['skill'], 10.5, '#AEB4DC', 500, 'middle', mono=True))
        o.append(f'<line x1="{x+30}" y1="{y+174}" x2="{x+br-30}" y2="{y+174}" '
                 f'stroke="#3B45A0" stroke-width="1"/>')
        o.append(txt(x + br / 2, y + 198, f'{ph} Phasen · {fg} Freigaben', 11, '#D5D8EE', 500, 'middle'))
        o.append(txt(x + br / 2, y + 226, st['ergebnis'], 11.5, GOLD, 600, 'middle', mono=True))
        if i < len(STUFEN) - 1:
            xa = x + br + 8
            o.append(f'<path d="M{xa} {y+125} h26 l-8 -7 m8 7 l-8 7" stroke="{BLAU}" '
                     f'stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    o.append(f'<line x1="48" y1="{y+300}" x2="{B-48}" y2="{y+300}" stroke="{LINIE}"/>')
    for i, (gross, klein) in enumerate((
            (str(n_ph), 'Phasen insgesamt'), (str(n_fg), 'Freigabepunkte'),
            ('7', 'Skills in 4 Plugins'), ('JA', 'vor jedem Schreibvorgang'))):
        x = 48 + i * 268
        o.append(txt(x, y + 348, gross, 32, BLAU, 800))
        o.append(txt(x, y + 372, klein, 11, GRAU, 500))
    return o


def seite_gesamt():
    n_ph = sum(len([x for x in st['schritte'] if 'n' in x]) for st in STUFEN)
    n_fg = sum(len([x for x in st['schritte'] if 'g' in x]) for st in STUFEN)
    o = kopf('Shop-Erstellung — alle Phasen',
             f'{len(STUFEN)} Stufen · 7 Skills · {n_ph} Phasen · {n_fg} Freigaben')
    sp_b, luecke, y0 = 244, 12, 156
    for i, st in enumerate(STUFEN):
        x = 48 + i * (sp_b + luecke)
        o.append(f'<rect x="{x}" y="{y0}" width="{sp_b}" height="{H-y0-96}" rx="7" '
                 f'fill="#FFFFFF" stroke="{LINIE}" stroke-width="1.2"/>')
        o.append(f'<rect x="{x}" y="{y0}" width="{sp_b}" height="52" rx="7" fill="{BLAU}"/>')
        o.append(f'<rect x="{x}" y="{y0+40}" width="{sp_b}" height="12" fill="{BLAU}"/>')
        o.append(sechseck(x + 26, y0 + 26, 15, '#FFFFFF'))
        o.append(txt(x + 26, y0 + 31, str(st['nr']), 15, BLAU, 800, 'middle'))
        o.append(txt(x + 50, y0 + 21, st['titel'], 12.5, '#FFFFFF', 700))
        o.append(txt(x + 50, y0 + 38, st['skill'], 9.2, '#B9BEDD', 500, mono=True))
        if i < 3:
            xa = x + sp_b + 1
            o.append(f'<path d="M{xa} {y0+26} h7 l-3 -4 m3 4 l-3 4" stroke="{BLAU}" '
                     f'stroke-width="1.8" fill="none" stroke-linecap="round"/>')
        y = y0 + 70
        eng = len(st['schritte']) > 11        # Design-Stufe ist die laengste
        for s in st['schritte']:
            if 'g' in s:
                o.append(f'<rect x="{x+10}" y="{y-11}" width="{sp_b-20}" height="21" rx="10.5" '
                         f'fill="#FBF7EE" stroke="{GOLD}" stroke-width="1"/>')
                o.append(sechseck(x + 22, y - 0.5, 7.5, GOLD))
                o.append(txt(x + 22, y + 2.5, '✓', 8, '#FFFFFF', 700, 'middle'))
                o.append(txt(x + 34, y + 3, s['g'], 8.6, '#7A6C42', 600))
                y += 25 if eng else 30; continue
            f = FARBE[s['wer']]
            if s['wer'] == 'hand':
                o.append(f'<circle cx="{x+21}" cy="{y}" r="8.2" fill="#FFFFFF" '
                         f'stroke="{DUNKEL}" stroke-width="2"/>')
                o.append(txt(x + 21, y + 3.4, str(s['n']), 9.5, DUNKEL, 700, 'middle'))
            else:
                o.append(f'<circle cx="{x+21}" cy="{y}" r="9" fill="{f}"/>')
                o.append(txt(x + 21, y + 3.4, str(s['n']), 9.5, '#FFFFFF', 700, 'middle'))
            zeilen = umbruch(s['t'], 24 if eng else 26)
            for j, z in enumerate(zeilen):
                o.append(txt(x + 36, y + 3.5 + j * 12 - (len(zeilen) - 1) * 6, z, 10, TEXT, 600))
            yy = y + 6 + (len(zeilen) - 1) * 6
            if s.get('a') and not eng:
                yy += 12
                o.append(txt(x + 36, yy, s['a'], 8.2, GRAU, 400, mono=True))
            y = yy + (13 if eng else 24)
        o.append(f'<line x1="{x+10}" y1="{H-140}" x2="{x+sp_b-10}" y2="{H-140}" '
                 f'stroke="{LINIE}" stroke-width="1"/>')
        o.append(txt(x + 12, H - 124, 'ERGEBNIS', 7.4, GOLD, 700, ls=1.4))
        o.append(txt(x + 12, H - 110, st['ergebnis'], 10, BLAU, 600, mono=True))
    o += legende(H - 52)
    return o


# ---------------------------------------------------------------- Seiten 2-5
def seite_stufe(st, spalten_zahl=2, breite=470, x0=70):
    o = kopf(f'Stufe {st["nr"]} — {st["titel"]}', st['skill'])
    o += legende(146, rechts=True)          # oben rechts, nicht unten
    schritte = st['schritte']
    if spalten_zahl == 2:
        mitte = (len(schritte) + 1) // 2
        spalten = [schritte[:mitte], schritte[mitte:]]
    else:
        spalten = [schritte]
    enden = []
    for si, sp in enumerate(spalten):
        x = x0 + si * (breite + 60)
        y = 190
        knoten = []
        for s in sp:
            if 'g' in s:
                o.append(f'<rect x="{x-22}" y="{y-19}" width="{breite}" height="38" rx="19" '
                         f'fill="#FBF7EE" stroke="{GOLD}" stroke-width="1.2"/>')
                o.append(sechseck(x, y, 13, GOLD))
                o.append(txt(x, y + 4.5, '✓', 12, '#FFFFFF', 700, 'middle'))
                o.append(txt(x + 24, y - 1, 'FREIGABE', 7.6, GOLD, 700, ls=1.4))
                o.append(txt(x + 24, y + 11, s['g'], 10.5, '#6B5E38', 600))
                knoten.append(y); y += 64; continue
            f = FARBE[s['wer']]
            if s['wer'] == 'hand':
                o.append(f'<circle cx="{x}" cy="{y}" r="13.5" fill="#FFFFFF" '
                         f'stroke="{DUNKEL}" stroke-width="3"/>')
                o.append(txt(x, y + 5, str(s['n']), 13, DUNKEL, 700, 'middle'))
            else:
                o.append(f'<circle cx="{x}" cy="{y}" r="15" fill="{f}"/>')
                o.append(txt(x, y + 5, str(s['n']), 13, '#FFFFFF', 700, 'middle'))
            o.append(txt(x + 26, y + 1, s['t'] + (' (optional)' if s.get('opt') else ''),
                         13, TEXT, 700))
            zy = y + 17
            if s.get('s'):
                o.append(f'<rect x="{x+26}" y="{zy-10}" width="{min(breite-40, 14+len(s["s"])*5.6)}" '
                         f'height="16" rx="3" fill="{HELL}"/>')
                o.append(txt(x + 33, zy + 2, s['s'], 8.8, BLAU, 500, mono=True)); zy += 24
            if s.get('a'):
                o.append(f'<path d="M{x+28} {zy-4} h8" stroke="{GOLD}" stroke-width="1.6"/>')
                o.append(txt(x + 42, zy, s['a'], 9.6, GRAU, 400)); zy += 18
            knoten.append(y)
            y = max(y + 62, zy + 28)
        # Rueckgrat nur so lang wie die Spalte wirklich ist
        o.insert(len(kopf('', '')) + 1,
                 f'<line x1="{x}" y1="{knoten[0]}" x2="{x}" y2="{knoten[-1]}" '
                 f'stroke="{LINIE}" stroke-width="2"/>')
        enden.append((x, knoten[-1]))
    # Uebergang von Spalte 1 nach Spalte 2, als Bogen nach unten und wieder hoch
    if len(enden) == 2:
        (x1, y1), (x2, _) = enden
        tief, riser = H - 118, x2 - 36
        o.append(f'<path d="M{x1} {y1} V{tief} H{riser} V190 H{x2-16}" stroke="{LINIE}" '
                 f'stroke-width="1.6" fill="none" stroke-dasharray="4 4" '
                 f'stroke-linejoin="round"/>')
        o.append(f'<path d="M{x2-22} 185 l6 5 l-6 5" stroke="{LINIE}" stroke-width="1.8" '
                 f'fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    o.append(f'<line x1="48" y1="{H-84}" x2="{B-48}" y2="{H-84}" stroke="{LINIE}"/>')
    o.append(txt(48, H - 62, 'ERGEBNIS', 7.6, GOLD, 700, ls=1.4))
    o.append(txt(48, H - 44, st['ergebnis'], 14, BLAU, 600, mono=True))
    return o


def pruefungen_kasten(o):
    """Die drei Fachpruefungen als Nebenspur auf der Abnahme-Seite."""
    x, y, br = 610, 168, 462
    o.append(f'<rect x="{x}" y="{y}" width="{br}" height="330" rx="7" fill="#FAFBFD" '
             f'stroke="{LINIE}"/>')
    o.append(txt(x + 18, y + 26, 'Phase 1 startet drei Prüfungen', 12, TEXT, 700))
    daten = [('shopify-ux', 'Benutzerführung',
              ['Kontraste WCAG', 'Startseitenlänge', 'tote Menüpunkte', 'Alt-Texte'],
              'befunde/ux.json'),
             ('shopify-cro', 'Verkaufspsychologie',
              ['Bilder je Produkt', 'leere Kategorien', 'Bewertungen', 'Zahlungsicons'],
              'befunde/cro.json'),
             ('shopify-recht', 'Pflichtangaben',
              ['Richtlinien', 'MwSt · Grundpreis', 'GPSR', 'Consent'],
              'befunde/recht.json')]
    sb = (br - 36 - 20) / 3
    for i, (skill, was, punkte, out) in enumerate(daten):
        cx = x + 18 + i * (sb + 10)
        o.append(f'<rect x="{cx}" y="{y+42}" width="{sb}" height="270" rx="5" fill="#FFFFFF" '
                 f'stroke="{LINIE}"/>')
        o.append(f'<rect x="{cx}" y="{y+42}" width="{sb}" height="4" rx="2" fill="{BLAU}"/>')
        o.append(txt(cx + 12, y + 68, skill, 9.4, BLAU, 600, mono=True))
        o.append(txt(cx + 12, y + 84, was, 10.5, TEXT, 700))
        for j, p in enumerate(punkte):
            o.append(f'<circle cx="{cx+15}" cy="{y+104+j*20}" r="2.2" fill="{GOLD}"/>')
            o.append(txt(cx + 24, y + 107 + j * 20, p, 9, GRAU, 400))
        o.append(f'<line x1="{cx+12}" y1="{y+196}" x2="{cx+sb-12}" y2="{y+196}" '
                 f'stroke="{LINIE}"/>')
        o.append(txt(cx + 12, y + 214, out, 8.4, BLAU, 500, mono=True))
        o.append(txt(cx + 12, y + 240, '+ Durchgang', 9, TEXT, 600))
        o.append(txt(cx + 12, y + 254, 'im Browser', 9, TEXT, 600))
        o.append(txt(cx + 12, y + 276, '4 Phasen', 8.6, GRAU, 400))
        o.append(txt(cx + 12, y + 290, '1 Freigabe', 8.6, GRAU, 400))
    o.append(f'<path d="M{x-118} 190 H{x-14}" stroke="{LINIE}" stroke-width="1.6" '
             f'fill="none" stroke-dasharray="4 4"/>')
    o.append(f'<path d="M{x-20} 185 l6 5 l-6 5" stroke="{LINIE}" stroke-width="1.8" '
             f'fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    return o


def seite_bilder():
    """Welches Skript fuer welche Bildsorte — und wo die Grenze liegt."""
    o = kopf('Bilder', 'Vier Werkzeuge, fünf Bildsorten, zwei harte Grenzen')
    spalten = [
        ('8_bilder.py', 'Fläche und Form',
         ['Verläufe und Bühnen', 'geometrische Motive', 'Komposition mit Kundenfoto',
          'Freisteller über macOS Vision'], 'HTML-Vorlage, hier gerendert', 'ki'),
        ('8b_bild_erzeugen.py', 'Einzelmotiv',
         ['Texturen und Stimmungen', 'freigestellte Elemente', '--transparent gibt Alphakanal',
          'geht direkt in die Vorlagen'], 'erzeugt, gpt-image-2', 'ki'),
        ('8c_hero.py', 'Der Hero',
         ['Interview vor dem Vorschlag', 'drei Szenen auf Deutsch', 'JSON-Prompt auf Englisch',
          '3200×900, links frei'], 'erzeugt nach HDC-Regeln', 'ki'),
        ('8d_kategoriebanner.py', 'Bannersatz',
         ['ein Stil für alle', 'ein Motiv je Kollektion', 'Motiv kommt vom Kunden',
          'setzt sie in die Kollektion'], 'erzeugt als Satz', 'ki'),
    ]
    br = (B - 96 - 3 * 14) / 4
    for i, (skript, name, punkte, herkunft, wer) in enumerate(spalten):
        x = 48 + i * (br + 14)
        o.append(f'<rect x="{x}" y="156" width="{br}" height="286" rx="7" fill="#FFFFFF" '
                 f'stroke="{LINIE}"/>')
        o.append(f'<rect x="{x}" y="156" width="{br}" height="5" rx="2.5" fill="{BLAU}"/>')
        o.append(txt(x + 16, 186, skript, 9.6, BLAU, 600, mono=True))
        o.append(txt(x + 16, 210, name, 14, TEXT, 700))
        o.append(txt(x + 16, 230, herkunft, 9.4, GRAU, 400))
        for j, p in enumerate(punkte):
            o.append(f'<circle cx="{x+19}" cy="{258+j*24}" r="2.4" fill="{GOLD}"/>')
            for k, z in enumerate(umbruch(p, 28)):
                o.append(txt(x + 29, 262 + j * 24 + k * 12, z, 9.6, TEXT, 400))
    o.append(f'<rect x="48" y="470" width="{B-96}" height="118" rx="7" fill="#FDF4F3" '
             f'stroke="#E8C4C0"/>')
    o.append(txt(70, 502, 'Wird nie erzeugt', 14, '#B3261E', 700))
    for i, (was, warum) in enumerate((
            ('Das Produkt des Kunden',
             'Zeigt Ware, die es so nicht gibt. Fällt auf, wenn das Paket ankommt.'),
            ('Menschen, die es wirklich gibt',
             'Ein erzeugtes Gesicht auf „Über uns" behauptet einen Menschen.'))):
        x = 70 + i * 510
        o.append(f'<path d="M{x} {528} h14" stroke="#B3261E" stroke-width="2"/>')
        o.append(txt(x + 24, 532, was, 11.5, TEXT, 600))
        for k, z in enumerate(umbruch(warum, 52)):
            o.append(txt(x + 24, 550 + k * 14, z, 9.6, GRAU, 400))
    o.append(txt(70, 618, 'Soll das Produkt im Bild sein: als echtes Foto über '
                 'referenced_image_ids hineingeben oder nachträglich einkomponieren.',
                 11, TEXT, 500))
    o.append(f'<line x1="48" y1="654" x2="{B-48}" y2="654" stroke="{LINIE}"/>')
    o.append(txt(48, 678, 'GRENZEN DES MODELLS', 7.6, GOLD, 700, ls=1.4))
    for i, t in enumerate(('beide Seiten durch 16 teilbar', 'längste Kante höchstens 3840',
                           'Seitenverhältnis höchstens 3:1',
                           '3200×900 wird höher erzeugt, dann geschnitten')):
        o.append(txt(48 + i * 264, 700, t, 10, GRAU, 400))
    o += legende(H - 46)
    return o


def bauen():
    seiten = [seite_grob(), seite_gesamt()]
    for i, st in enumerate(STUFEN):
        if st['skill'] == 'shopify-abnahme':
            seiten.append(pruefungen_kasten(seite_stufe(st, spalten_zahl=1, breite=430)))
        else:
            seiten.append(seite_stufe(st))
    seiten.append(seite_bilder())
    teile = []
    for inhalt in seiten:
        teile.append(f'<div class="blatt"><svg viewBox="0 0 {B} {H}" '
                     f'xmlns="http://www.w3.org/2000/svg">' + ''.join(inhalt) + '</svg></div>')
    html = f"""<!doctype html><html lang="de"><head><meta charset="utf-8">
<title>HDC Shopify-Kit — Prozessdiagramme</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500&display=swap');
@page{{size:A4 landscape;margin:0}}
*{{margin:0;padding:0}}
body{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.blatt{{width:297mm;height:210mm;break-after:page;overflow:hidden}}
.blatt:last-child{{break-after:auto}}
svg{{width:100%;height:100%;display:block}}
</style></head><body>{''.join(teile)}</body></html>"""
    hier = os.path.dirname(os.path.abspath(__file__))
    q = os.path.join(hier, 'diagramme.html')
    open(q, 'w').write(html)
    chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    ziel = os.path.join(hier, 'HDC-Shopify-Prozess-Diagramme.pdf')
    subprocess.run([chrome, '--headless', '--disable-gpu', '--no-sandbox',
                    '--virtual-time-budget=20000', f'--print-to-pdf={ziel}',
                    '--no-pdf-header-footer', f'file://{q}'],
                   capture_output=True, timeout=300)
    os.remove(q)
    from pypdf import PdfReader, PdfWriter
    r = PdfReader(ziel); w = PdfWriter()
    for s in r.pages: w.add_page(s)
    w.add_metadata({'/Title': 'HDC Shopify-Kit — Prozessdiagramme',
                    '/Author': 'HDC Digital GmbH', '/Creator': 'HDC Digital'})
    with open(ziel, 'wb') as f: w.write(f)
    print(f'{os.path.basename(ziel)} — {len(r.pages)} Seiten, '
          f'{os.path.getsize(ziel)//1024} KB')


if __name__ == '__main__':
    bauen()
