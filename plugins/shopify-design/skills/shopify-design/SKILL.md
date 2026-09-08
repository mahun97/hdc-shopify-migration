---
name: shopify-design
description: Setzt ein Shop-Konzept im Shopify-Theme um — erst die Shop-Copy als freigebbares Zwischenasset, dann Farbschema, Sections und Templates. Nutze diesen Skill bei "Theme aufbauen", "Shop gestalten", "Konzept umsetzen", "Startseite aufbauen", "Shop-Texte schreiben" oder wenn eine Konzeptpräsentation vorliegt.
---

# Shop-Design umsetzen

Du setzt ein abgestimmtes Shop-Konzept im Theme um. Grundlage sind zwei Dokumente,
die im Projekt vorliegen: das **Scope-Dokument** (Rahmen, Auflagen, Umfang) und die
**Konzeptpräsentation** (Struktur, Farben, Seitenaufbau).

## Die wichtigste Regel: Texte zuerst

**Bevor eine einzige Section im Theme angefasst wird, steht die Shop-Copy.** Sie ist ein
eigenes Zwischenasset, das der Kunde freigibt. Gründe:

- Eine Überschrift im Freigabedokument zu ändern kostet Sekunden, im aufgebauten Theme
  Minuten — und bei 60 Textbausteinen summiert sich das.
- Der Kunde sieht früh, was auf seinem Shop stehen wird, und nicht erst am Ende.
- Bei regulierten Produkten (Biozide, Medizinprodukte, Nahrungsergänzung) muss der Text
  **vor** dem Aufbau juristisch abgesegnet sein.
- Das Layout richtet sich nach der Textlänge, nicht umgekehrt.

## So redest du

Im Chat erklären, nicht auf Dateien verweisen. Die Person ist nicht technisch.
Ergebnisse in Klartext. Immer sagen, wo ihr steht.

## Grundregeln

1. **Keine Werbeaussagen erfinden, die rechtlich riskant sind.** Bei regulierten Produkten
   die Auflagen aus dem Scope-Dokument als harte Regeln übernehmen und im Copy-Dokument
   sichtbar dokumentieren.
2. **Die fachliche Freigabe liegt beim Kunden.** Du formulierst Vorschläge, keine
   verbindlichen Aussagen.
3. **Nichts im Theme anfassen, bevor die Copy freigegeben ist.**
4. **Live-Themes werden dupliziert**, bevor du sie änderst — es sei denn, es ist
   ausdrücklich anders vereinbart.

## Ablauf

Skripte liegen in `scripts/` neben dieser Datei. Pfad einmal ermitteln:

```bash
find ~/.claude -type d -name shopify-design -path '*skills*' 2>/dev/null | head -1
```

### Phase 1 — Unterlagen sichten

Frage nach Scope-Dokument und Konzeptpräsentation. Lies beide.

Aus dem **Scope** ziehst du: Marke, Zielgruppe, Tonalität, regulatorische Auflagen,
was ausdrücklich nicht dazugehört. Schreib die Auflagen in eine Textdatei (eine Regel
pro Zeile) — sie landen im Copy-Dokument.

### Phase 2 — Konzept auswerten

```
python3 <pfad>/scripts/1_konzept_lesen.py "Shop-Konzeption.pdf"
```

Liest Farbschema, Theme-Empfehlung und Seitenaufbau aus. Ergebnis: `konzept.json`.

**Prüfe das Ergebnis gegen die PDF**, bevor du weitermachst — die Extraktion ist gut,
aber nicht unfehlbar. Zeig der Person die gefundenen Farben und den Seitenaufbau.

### Phase 3 — Shop-Copy schreiben

```
python3 <pfad>/scripts/2_copy_geruest.py --marke "Name" --regeln regeln.txt
python3 <pfad>/scripts/3_copy_ansicht.py
```

Das erste Skript legt `copy.json` an — die Struktur mit allen Textfeldern, leer.
**Die Texte schreibst du**, direkt in `copy.json`, auf Basis von Scope, Altshop,
vorhandenen Produkttexten und dem, was die Person beisteuert.

Beim Schreiben:
- Tonalität aus dem Scope einhalten
- bei regulierten Produkten konservativ formulieren
- keine Superlative ohne Beleg
- Überschriften kurz, Fließtext in Sätzen, die jemand laut vorlesen würde
- Button-Texte sagen, was passiert („Produkt ansehen", nicht „Mehr")

Setz den Status je Abschnitt auf `entwurf`, wenn du ihn geschrieben hast.

Das zweite Skript rendert `Shop-Copy.html`. **Veröffentliche das als Artifact** und
gib der Person den Link zur Freigabe beim Kunden.

> **Freigabe 1** — Shop-Copy vom Kunden abgenommen. Erst danach geht es ins Theme.

Nach der Freigabe Status auf `freigegeben` setzen und die Ansicht neu rendern.

### Phase 4 — Theme inventarisieren

Erst wenn das Theme im Shop liegt: auslesen, welche Sections es anbietet und wie ihre
Einstellungen heißen. Ohne das würdest du raten. Prestige, Dawn und Enterprise haben
völlig verschiedene Section-Namen.

### Phase 5 — Aufbau

In der Reihenfolge, die sich bewährt hat:

1. Farbschema und Typografie in den Theme-Einstellungen
2. Header und Navigation
3. Footer
4. Startseite
5. Kategorieseiten-Template
6. Produktseiten-Template
7. zentrale Unterseiten

Nach jedem Schritt in der Storefront prüfen und den Befund vorlegen.

### Phase 6 — Darstellung prüfen

Desktop und Mobil getrennt durchgehen, Warenkorb testen. Auffälligkeiten dokumentieren,
statt sie stillschweigend zu beheben — manche sind Designentscheidungen.

> **Freigabe 2** — Aufbau abgenommen.

## Wenn etwas hakt

`references/fallen.md` lesen.
