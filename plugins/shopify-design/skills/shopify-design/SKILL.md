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

### Phase 0 — Schlüssel

Vor dem ersten Lauf einmal je Rechner. **Zeig der Person, wie sie den Schlüssel ablegt —
nimm ihn nicht entgegen.** Ein Schlüssel im Chat gilt als kompromittiert.

```
python3 <pfad>/scripts/8b_bild_erzeugen.py --schluessel-pruefen
```

Fehlt die Datei, druckt das Skript die vollständige Anleitung. Gib sie im Chat wieder,
statt auf `references/schluessel.md` zu verweisen — dort steht dasselbe für später zum
Nachschlagen, aber niemand soll erst eine Datei öffnen müssen.

Ergebnis: `ok  Schlüssel gültig, gpt-image-1 freigeschaltet.` Alles andere ist in
`schluessel.md` in einer Tabelle aufgeschlüsselt: `401` heißt falsch kopiert, `403`/`404`
heißt Organisation nicht verifiziert.

Der Shopify-Token je Kunde läuft nach demselben Muster — Datei, nicht Chat.

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

> **Freigabe 1** — Shop-Copy vom Kunden abgenommen.

Nach der Freigabe Status auf `freigegeben` setzen und neu rendern.

### Phase 4 — Startseiten-Entwurf

Die Copy sagt, *was* dasteht. Der Entwurf sagt, *wie es wirkt* — und aus ihm entstehen
später die Sections. Beides in einem Schritt zu klären kostet zwei Runden statt einer.

```
python3 <pfad>/scripts/3b_entwurf.py --geruest
… gestalten — das ist die eigentliche Arbeit …
python3 <pfad>/scripts/3b_entwurf.py --pruefen
```

Das Gerüst zieht die Abschnittsfolge aus der freigegebenen Copy und legt Palette und
Schriften aus dem Konzept an. Danach gestaltest du: eigene Typografie, echte Bilder,
Abschnittsrhythmus. `references/entwurf.md` sagt, woran ein brauchbarer Entwurf zu
erkennen ist.

**Genau eine Startseite**, kein Klickdummy. Sie trägt die Gestaltungsentscheidung, alles
Weitere folgt ihr.

**Offene Punkte als Fußnote am Abschnitt**, nicht am Ende. Beim Gestalten fällt fast immer
etwas auf, das vorher niemand gesehen hat — zwei widersprüchliche Versandregeln, ein Preis,
den es zweimal gibt. Genau dort gehört der Hinweis hin.

Die Prüfung endet mit Fehlercode, solange Blindtext, Platzhalter oder eine fehlende
Entwurfs-Kennzeichnung drin sind. Bildplatzhalter für noch fehlende Kundenfotos sind
dagegen in Ordnung — sie sind eine Lieferung, kein Mangel.

> **Freigabe 2** — Entwurf vom Kunden abgenommen. Erst danach wird das Theme angefasst.

### Phase 5 — Theme inventarisieren

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

### Phase 6 — Aufbau

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
2. **Bilder**, vier Werkzeuge für vier Aufgaben:

   | Skript | Wofür |
   |---|---|
   | `8_bilder.py` | Flächen, Bühnen, Kompositionen aus Markenfarben und Kundenfoto |
   | `8b_bild_erzeugen.py` | einzelne Motive, Texturen, freigestellte Elemente (`--transparent`) |
   | `8c_hero.py` | der Hero nach den HDC-Hero-Regeln, aus einem JSON-Prompt |
   | `8d_kategoriebanner.py` | Kategoriebanner **als Satz** — ein Stil, viele Motive |
3. **Sections aufbauen** — `scripts/5_aufbau.py`
4. Header, Footer, dann die Templates: Startseite → Kategorie → Produkt → Unterseiten

**Kein Text in Bildern.** Steht die Überschrift im Bild und in der Section, liest man sie
doppelt — und sie ist weder responsiv noch übersetzbar noch durchsuchbar. Bilder liefern
Fläche und Form, die Worte kommen aus der Section.

**Zwei Bildsorten werden nie erzeugt: das Produkt des Kunden und Menschen, die es
wirklich gibt.** Ein erzeugtes Produktbild zeigt Ware, die es so nicht gibt — das ist
irreführende Werbung, und zwar die Art, die auffällt, wenn das Paket ankommt. Ein
erzeugtes Gesicht auf „Über uns" behauptet einen Menschen, den es nicht gibt. Beides
kommt aus einem Shooting oder vom Kunden.

Alles dazwischen — Hintergründe, Texturen, generische Elemente — ist erzeugbar und macht
den Unterschied zwischen einem Shop und einer Präsentationsfolie. Fehlen echte Fotos, sag
es, und setze so lange ein Markenmotiv.

#### Der Hero

Der Hero ist das einzige Bild, das jeder Besucher sieht. Er entsteht nicht aus einem
Halbsatz, sondern aus einem Interview — frag der Reihe nach: Was wird verkauft? Wer nutzt
es, in welcher Situation? Läuft eine Aktion? Was genau soll beworben werden? Gibt es
Beispielbilder oder Referenzshops? Welcher Stil?

**Erst danach** schlägst du **drei Szenen auf Deutsch** vor, kurz und unterscheidbar —
nicht drei Varianten derselben Idee. Nach der Auswahl baust du den JSON-Prompt auf
Englisch, in der Struktur aus `references/hero-prompts.md`.

Feste Regeln, die das Skript ohnehin anhängt: 3200×900, linke Hälfte frei für Text mit
dezentem Overlay, Produkt und visuelle Elemente rechtsbündig, realistische Nutzungsszene,
kein Text im Bild.

```
python3 <pfad>/scripts/8c_hero.py --vorlage > hero.json
python3 <pfad>/scripts/8c_hero.py --json hero.json --name hero --overlay hell
… ansehen …
python3 <pfad>/scripts/8c_hero.py --json hero.json --name hero --overlay hell \\
    --shop --theme <duplikat-id> --section hero --feld image_1
```

Der zweite Aufruf geht den ganzen Weg: hochladen in die Shop-Dateien, eintragen in die
Section, Vorschaulink. **Du lieferst das fertige Hero-Bild im Shop ab, nicht einen Prompt
und nicht eine PNG-Datei.**

**Vor dem Einsetzen prüfen, ob das Modell Produkte dazuerfunden hat.** Es tut das: In
einem Hero für einen Desinfektionsmittel-Shop standen zwei Sprühflaschen auf der Fläche,
die in der Objektliste nicht vorkamen. Damit wird aus einem Stimmungsbild ein Produktbild.
Die Produktkategorie des Kunden gehört deshalb in die Negativliste des Prompts.

#### Kategoriebanner

Die sieht niemand einzeln. Wer sich durch den Shop klickt, sieht vier hintereinander —
sie müssen als Satz wirken. Deshalb **eine Stil-Datei für alle** und nur das Motiv je
Kollektion.

```
python3 <pfad>/scripts/8d_kategoriebanner.py --vorlage > stil.json
python3 <pfad>/scripts/8d_kategoriebanner.py --stil stil.json --pruefen
python3 <pfad>/scripts/8d_kategoriebanner.py --stil stil.json --alle --setzen
```

`--pruefen` sagt, welche Kollektionen kein Banner haben und für welche noch das Motiv
fehlt. **Ein Motiv erfindet das Skript nicht** — was in einer Kategorie zu sehen ist,
weiß der Kunde. Vor `--setzen` alle nebeneinander ansehen: Ein Satz, bei dem eines aus
der Reihe fällt, wirkt schlechter als gar keiner.

Nach jedem Schritt in der Vorschau ansehen und den Befund vorlegen.

### Phase 7 — Demo-Produkt

**Vor** der Produktmigration, nicht danach. An einem einzigen Produkt wird geprüft, ob die
ganze Kette hält: Definition da → Wert gesetzt → Storefront-Zugriff offen → Theme gibt es
aus.

```
python3 <pfad>/scripts/13_demoprodukt.py --theme <id> --pruefen
python3 <pfad>/scripts/13_demoprodukt.py --anlegen
```

Das Skript legt ein Produkt als **Entwurf** mit Tag `hdc-demo` an und füllt jede
Metafeld-Definition mit einem Demo-Wert. Felder, die auf echte Objekte verweisen, kann es
nicht füllen — die nennt es, damit sie von Hand gesetzt werden.

Dann in der Theme-Vorschau öffnen und **jedes Feld suchen**. Der Fehler, den dieser
Schritt abfängt, ist immer derselbe: Ein Metafeld ist im Admin gefüllt und im Theme
unsichtbar, weil `access.storefront` nicht auf `PUBLIC_READ` steht. Bei einem Produkt
kostet das zehn Minuten. Bei dreihundert kostet es einen Tag.

**Vor dem Livegang löschen:** `13_demoprodukt.py --entfernen`. Das steht auch in der
Übergabe.

### Phase 8 — Theme-Einstellungen

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

### Phase 9 — Kategorie-, Produkt- und Serviceseiten

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

### Phase 10 — Prüfen

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

> **Freigabe 3** — Aufbau abgenommen.

## Wenn etwas hakt

`references/fallen.md` lesen.

## Danach

Der Shop steht — mit einem Demo-Produkt, an dem die Metafelder geprüft sind. Jetzt erst
kommen die echten Produkte: **`shopify-migration`**. Danach `shopify-abnahme` für UX, CRO,
Recht und die Übergabe-Checkliste.
