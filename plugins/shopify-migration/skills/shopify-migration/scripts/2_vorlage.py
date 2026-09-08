#!/usr/bin/env python3
"""Phase 5a — erzeugt aus dem Steckbrief eine Importvorlage mit Dropdowns fuer die gueltigen Tags.
Aufruf: python3 2_vorlage.py [steckbrief.md] [ziel.xlsx]"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify import titel, fehler
try:
    import openpyxl
    from openpyxl.worksheet.datavalidation import DataValidation
    from openpyxl.styles import Font, PatternFill, Alignment
except ImportError:
    fehler('openpyxl fehlt.  Installieren mit:  pip3 install openpyxl')

quelle = sys.argv[1] if len(sys.argv) > 1 else 'Shop-Steckbrief.md'
ziel   = sys.argv[2] if len(sys.argv) > 2 else 'Importliste.xlsx'
if not os.path.exists(quelle): fehler(f'{quelle} nicht gefunden. Erst  python3 1_steckbrief.py  laufen lassen.')

# Tag-Vokabular aus Abschnitt 3 des Steckbriefs lesen
text = open(quelle).read()
block = re.search(r'## 3 .*?```(.*?)```', text, re.S)
tags = sorted({m.group(1).strip() for m in re.finditer(r'^\s*\d+×\s+(.+)$', block.group(1), re.M)}) if block else []
print(f'  {len(tags)} gültige Tags aus dem Steckbrief übernommen')

SPALTEN = [
 ('Artikelnummer', 16, 'Pflicht — muss shopweit eindeutig sein'),
 ('Produkttitel', 46, 'Pflicht — gleicher Titel = ein Produkt mit mehreren Varianten'),
 ('Option 1 Name', 14, 'z. B. Format. Pflicht, sobald es mehrere Varianten gibt'),
 ('Option 1 Wert', 20, 'Pflicht — muss je Produkt eindeutig sein'),
 ('Option 2 Name', 14, 'optional, z. B. Menge'),
 ('Option 2 Wert', 18, 'nur wenn Option 2 Name gefüllt ist'),
 ('Verkaufspreis', 14, 'Pflicht — Zahl, Punkt als Dezimaltrenner'),
 ('Gewicht kg', 12, 'Pflicht — sonst rechnet der Versand falsch'),
 ('Beschreibung', 54, 'Pflicht'),
 ('Tags', 40, 'Pflicht — kommagetrennt, nur Werte aus dem Tabellenblatt "Gültige Tags"'),
 ('Bilddatei', 30, 'Pflicht — Dateiname im Bilderordner'),
 ('Bildposition', 12, '1 = Hauptbild'),
 ('Hersteller GPSR', 40, 'Pflicht — Name, Anschrift, Kontakt'),
 ('SEO-Titel', 34, 'optional — wird sonst erzeugt'),
 ('SEO-Beschreibung', 44, 'optional — wird sonst erzeugt'),
]
wb = openpyxl.Workbook()
ws = wb.active; ws.title = 'Produkte'
kopf = Font(bold=True, color='FFFFFF'); fuell = PatternFill('solid', fgColor='1F3864')
hinweis = Font(italic=True, size=9, color='666666')
for i, (name, breite, hilfe) in enumerate(SPALTEN, 1):
    c = ws.cell(1, i, name); c.font = kopf; c.fill = fuell
    c.alignment = Alignment(vertical='center', wrap_text=True)
    h = ws.cell(2, i, hilfe); h.font = hinweis
    h.alignment = Alignment(vertical='top', wrap_text=True)
    ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = breite
ws.row_dimensions[1].height = 28; ws.row_dimensions[2].height = 46
ws.freeze_panes = 'A3'

wt = wb.create_sheet('Gültige Tags')
wt['A1'] = 'Nur diese Tags sind im Shop in Gebrauch'; wt['A1'].font = Font(bold=True)
wt.column_dimensions['A'].width = 40
for i, t in enumerate(tags, 2): wt.cell(i, 1, t)
if tags:
    dv = DataValidation(type='list', formula1=f"='Gültige Tags'!$A$2:$A${len(tags)+1}", allow_blank=True)
    dv.error = 'Nur Tags aus dem Blatt "Gültige Tags" verwenden.'
    dv.errorTitle = 'Unbekannter Tag'
    ws.add_data_validation(dv)
    for r in range(3, 400): dv.add(ws.cell(r, 10))

wb.save(ziel)
titel(f'{ziel} erstellt')
print(f'  Spalten:        {len(SPALTEN)}')
print(f'  Tag-Dropdown:   {len(tags)} Werte (Spalte "Tags", Zeilen 3–399)')
print(f'\n  Bilder gehören in einen Ordner "bilder/" neben der Liste.')
