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

**Hier liegt der eigentliche Wert dieses Skills.** Du schreibst als Senior-Copywriter,
nicht als Formularausfüller. Lies vorher `references/copywriting.md` — dort steht das
Vorgehen im Detail.

**3a — Zielgruppe schärfen.** Das Konzept liefert Segmente als Rohtext. Verdichte sie:
Wer genau kauft, in welcher Situation, mit welchem Auslöser, mit welchen Bedenken, in
welcher Sprache. Leg fest, für wen du primär schreibst — ein Text kann nicht alle gleich
gut bedienen.

**Diese Analyse legst du der Person im Chat vor, bevor du schreibst.** Sie erklärt, warum
die Texte hinterher so klingen, wie sie klingen, und Missverständnisse sind hier billig.

**3b — Botschaftshierarchie.** Ein Satz, der hängenbleiben muss, wenn jemand nach drei
Sekunden wegscrollt. Der gehört in den Hero. Dann Platz zwei und drei.

**3c — Gerüst anlegen.**

```
python3 <pfad>/scripts/2_copy_geruest.py --marke "Name" --regeln regeln.txt
```

**3d — Schreiben.** Alle Felder in `copy.json` füllen, Section für Section. **Das Dokument
wird vollständig gefüllt** — ein Dokument mit Lücken kann niemand freigeben. Was du
fachlich nicht weißt, formulierst du als sichtbare Rückfrage im Feld, statt es leer zu
lassen oder zu erfinden.

Status je Abschnitt auf `entwurf` setzen.

**3e — Ansicht rendern und freigeben lassen.**

```
python3 <pfad>/scripts/3_copy_ansicht.py
```

Veröffentliche `Shop-Copy.html` als Artifact und gib der Person den Link. Fasse im Chat
zusammen: für wen geschrieben, welche Botschaft trägt, wo Rückfragen offen sind.

> **Freigabe 1** — Shop-Copy vom Kunden abgenommen. Erst danach geht es ins Theme.

Nach der Freigabe Status auf `freigegeben` setzen und neu rendern.

### Phase 4 — Theme inventarisieren

```
python3 <pfad>/scripts/4_theme_inventar.py
```

Liest aus, was das Theme wirklich kann: Templates mit ihrem aktuellen Aufbau, alle
verfügbaren Sections mit Anzahl ihrer Einstellungen und Blocktypen, dazu die
Farbeinstellungen. Ergebnis: `theme_inventar.json`.

**Ohne diesen Schritt würdest du raten.** Dieselbe Section heißt je Theme anders:

| Konzept sagt | Horizon | Dawn | Prestige |
|---|---|---|---|
| Hero mit Bild | `hero` | `image-banner` | eigene Namen |
| Bestseller-Reihe | `product-list` | `featured-collection` | eigene Namen |
| Bild-Text | `media-with-content` | `image-with-text` | eigene Namen |

**Dann die Zuordnung erstellen**: welche Konzept-Section wird welche Theme-Section.
Leg sie der Person vor — dort fällt auf, wenn das Theme etwas nicht kann, das im
Konzept steht. Das ist der Moment, das zu klären, nicht mitten im Aufbau.

### Phase 5 — Aufbau

Zuerst ein **Duplikat** des Themes anlegen — nie am aktiven arbeiten. Das Duplikat entsteht
asynchron; erst prüfen, ob die Dateien da sind, dann schreiben.

Dann je Seite bauen, auf Basis der Zuordnung für das konkrete Theme:

```
python3 <pfad>/scripts/5_aufbau.py --seite Startseite --template index \
  --theme <duplikat-id> --zuordnung <pfad>/references/zuordnung-<theme>.json --trocken
```

Ohne `--trocken` schreibt es — nach getipptem JA und nur auf unveröffentlichte Themes.

**Für Horizon liegt eine Zuordnung bei.** Für andere Themes eine eigene anlegen: Die
Vorlagen stammen aus den `presets` der Section-Schemas, die Phase 4 ausgelesen hat.

Reihenfolge, die sich bewährt hat: Farbschema → Header → Footer → Startseite →
Kategorie-Template → Produkt-Template → Unterseiten.

Nach jedem Schritt in der Vorschau ansehen und den Befund vorlegen.

### Phase 6 — Prüfen

```
python3 <pfad>/scripts/6_pruefung.py --theme <duplikat-id>
```

Findet, was aus den Dateien ablesbar ist: offene `[RÜCKFRAGE …]`-Marker, Platzhaltertexte,
Sections ohne zugewiesene Kollektion, nicht gesetzte Bilder, unangepasste Standardlinks,
fehlende Mobil-Einstellungen, zu lange Überschriften, und ob die Copy freigegeben ist.
Endet mit Fehlercode, solange Blocker offen sind.

**Danach im Browser prüfen**, was kein Skript sehen kann:

- Startseite, Kategorie- und Produktseite durchgehen
- Warenkorb öffnen und einen Artikel hineinlegen
- beide Sprachen, wenn der Shop mehrsprachig ist

**Zur Mobilprüfung:** Das Browserfenster zu verkleinern reicht **nicht** — der
Rendering-Viewport bleibt breit, und du prüfst gegen die Desktop-Ansicht, ohne es zu
merken. Es braucht echte Geräteemulation. Steht die nicht zur Verfügung, sag es offen und
bitte die Person, es in den Chrome-Entwicklerwerkzeugen anzusehen — statt eine Prüfung zu
behaupten, die nicht stattgefunden hat.

Auffälligkeiten **dokumentieren, nicht stillschweigend beheben** — manches ist eine
Designentscheidung, keine Panne.

> **Freigabe 2** — Aufbau abgenommen.

## Wenn etwas hakt

`references/fallen.md` lesen.
