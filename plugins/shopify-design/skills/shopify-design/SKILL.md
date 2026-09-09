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
find -L ~/.claude -type d -name shopify-design -path '*skills*' 2>/dev/null | head -1
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

**Gestaltung gehört dazu, nicht danach.** Ein Textgerüst in Theme-Standardoptik ist kein
Design. Lies `references/gestaltung.md` und setze in dieser Reihenfolge:

1. **Schriften und Farbpalette** — `scripts/7_gestaltung.py`, aus dem Farbschema des Konzepts
2. **Bildmotive** — `scripts/8_bilder.py`, Banner und Kategoriebilder aus den Markenfarben
3. **Sections aufbauen** — `scripts/5_aufbau.py`
4. Header, Footer, dann die Templates: Startseite → Kategorie → Produkt → Unterseiten

**Kein Text in Bildern.** Steht die Überschrift im Bild und in der Section, liest man sie
doppelt — und sie ist weder responsiv noch übersetzbar noch durchsuchbar. Bilder liefern
Fläche und Form, die Worte kommen aus der Section.

**Fotos entstehen nicht am Rechner.** Produktaufnahmen, Menschen, Situationen kommen vom
Kunden. Wer das mit Farbflächen ersetzt, baut einen Shop, der wie eine Präsentationsfolie
aussieht. Fehlen Fotos, sag es — und setze so lange ein Markenmotiv als Platzhalter.

Nach jedem Schritt in der Vorschau ansehen und den Befund vorlegen.

### Phase 6 — Theme-Einstellungen

Farben und Schriften sind nur die Hälfte. Ein Theme hat ein paar Dutzend Schalter, die
niemand sieht, bis sie falsch stehen — Quick-View, das zweite Bild beim Mouseover, der
Warenkorb als Einschub, die Express-Checkout-Buttons, der Bestellhinweis, Logo, Favicon.
Das ist Schritt 2 der HDC-Checkliste.

```
python3 <pfad>/scripts/9_checkliste.py --theme <duplikat-id>
python3 <pfad>/scripts/9_checkliste.py --theme <duplikat-id> \
    --logo logo.png --favicon favicon.png --setzen
```

Das Skript liest erst das `settings_schema` des Themes und arbeitet nur mit Schaltern, die
es dort wirklich gibt. Jeder Punkt kennt mehrere mögliche Namen, weil jedes Theme sie
anders nennt. Findet es keinen, meldet es den Punkt als offen — es schreibt nichts ins
`settings_data`, was das Theme ignorieren würde.

**Logo und Favicon kommen vom Kunden.** Kein Logo im Ordner heißt: nachfragen, nicht
selbst bauen. Ein aus einem Produktfoto herausgeschnittener Schriftzug ist kein Logo.

Zwei Punkte kann das Skript nur melden, weil sie in Templates statt in den Einstellungen
stecken: der Express-Checkout-Block auf der Produktseite und die Social-Media-Links im
Footer. Beides im Theme-Editor.

Was in **Schritt 1** der Checkliste steht — Shop-Details, Währungsformat, Versand, Steuern,
Standorte, Märkte, Sprachen, Checkout-Branding, Benachrichtigungen — gehört nicht hierher,
sondern in den Skill `shopify-settings`. Und **Schritt 3**, die Apps, installiert immer ein
Mensch.

### Phase 7 — Kategorie-, Produkt- und Serviceseiten

Schritt 6 bis 8 der Checkliste. Drei Skripte, alle erst lesend, dann schreibend:

```
python3 <pfad>/scripts/10_kategorieseite.py --theme <id>
python3 <pfad>/scripts/11_produktseite.py  --theme <id>
python3 <pfad>/scripts/12_serviceseiten.py
```

**Kategorieseiten** — Standardsortierung (`--sortierung BEST_SELLING`, bei ständig
wechselndem Sortiment `CREATED_DESC`), ausverkaufte Artikel ans Ende
(`--ausverkauft-ans-ende`, geht nur bei manuell sortierten Kollektionen — sonst sortiert
Shopify selbst und es braucht eine App), Filterleiste, Kategoriebanner, Bildformate.

**Produktseite** — Verfügbarkeit, Versandhinweis am Button, Akkordeon, klebender
Warenkorb-Button, Express-Checkout raus, „Bild mit Text" darunter. Was das Skript ergänzt,
enthält `[RÜCKFRAGE …]` an jeder Stelle, an der eine Zusage an Käufer steht — Lieferzeit,
Versandkosten, Rückgabe. **Die füllt niemand aus dem Bauch.** Phase 8 findet sie wieder.

**Serviceseiten** — FAQ, Versand, Zahlungsarten, Über uns. Werden als Gerüst angelegt und
bleiben **unveröffentlicht**, bis die Rückfragen beantwortet sind. Rechtstexte gehören
nicht hierher, die laufen über `shopify-settings`.

Bewertungen, Größentabellen und Bundles kommen aus Apps. Die installiert ein Mensch.

### Phase 8 — Prüfen

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

## Danach

Der Aufbau ist damit fertig, der Shop aber noch nicht übergabefähig. Es folgen
`shopify-ux`, `shopify-cro` und `shopify-recht`, dann `shopify-uebergabe`.
