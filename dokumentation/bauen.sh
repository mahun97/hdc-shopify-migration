#!/usr/bin/env bash
# Baut HDC-Shopify-Prozess.pdf aus den HTML-Teilen.
# Chrome rendert das Layout, reportlab stempelt Fusszeile und Seitenzahlen darueber —
# Chrome unterstuetzt die CSS-Randboxen fuer Seitenzahlen nicht.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$CHROME" ] || { echo "Google Chrome nicht gefunden"; exit 1; }

cat teil1.html teil2.html teil3.html teil4.html > handbuch.html
"$CHROME" --headless --disable-gpu --no-sandbox --virtual-time-budget=20000 \
  --print-to-pdf=roh.pdf --no-pdf-header-footer "file://$PWD/handbuch.html" 2>/dev/null

python3 - << 'PY'
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from pypdf import PdfReader, PdfWriter
import io, os
roh = PdfReader('roh.pdf'); n = len(roh.pages); B, H = A4
buf = io.BytesIO(); c = canvas.Canvas(buf, pagesize=A4)
for i in range(n):
    if i > 0:                                   # Titelseite ohne Fusszeile
        c.setStrokeColorRGB(.874, .886, .917); c.setLineWidth(.6); c.line(48, 38, B-48, 38)
        c.setFont('Helvetica', 7.2); c.setFillColorRGB(.357, .384, .439)
        c.drawString(48, 28, 'HDC Shopify-Kit — Prozessdokumentation Shop-Erstellung')
        c.setFont('Helvetica-Bold', 7.6); c.setFillColorRGB(.004, .043, .502)
        c.drawRightString(B-48, 28, f'{i+1} / {n}')
    c.showPage()
c.save(); buf.seek(0)
num = PdfReader(buf); w = PdfWriter()
for i, s in enumerate(roh.pages):
    s.merge_page(num.pages[i]); w.add_page(s)
w.add_metadata({'/Title': 'HDC Shopify-Kit — Prozessdokumentation Shop-Erstellung',
                '/Author': 'HDC Digital GmbH',
                '/Subject': 'Vollständiger Prozess von der Grundeinrichtung bis zur Übergabe',
                '/Creator': 'HDC Digital'})
with open('HDC-Shopify-Prozess.pdf', 'wb') as f: w.write(f)
print(f'HDC-Shopify-Prozess.pdf — {n} Seiten, {os.path.getsize("HDC-Shopify-Prozess.pdf")//1024} KB')
PY
rm -f roh.pdf handbuch.html
