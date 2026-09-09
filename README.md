# HDC Shopify-Kit

Claude-Code-Plugins für den kompletten Weg vom leeren Entwicklungsshop bis zur
Übergabe an den Kunden. Vier Plugins, sieben Skills, ein durchgehender Ablauf.

Alles läuft nach demselben Muster: **Der Ablauf ist fest, Claude macht den größten Teil,
ein Mensch kontrolliert und gibt frei.** Schreibende Schritte verlangen ein getipptes
`JA`. Was niemand wissen kann — Lieferzeiten, Preise, Herstelleradressen, Rechtstexte —
wird nicht geraten, sondern als Rückfrage markiert.

---

## Für Mitarbeiter: einmalig einrichten

Im Terminal `claude` starten und nacheinander eingeben:

```
/plugin marketplace add mahun97/hdc-shopify-migration
```

```
/plugin install shopify-settings@hdc-digital
```

```
/plugin install shopify-migration@hdc-digital
```

```
/plugin install shopify-design@hdc-digital
```

```
/plugin install shopify-abnahme@hdc-digital
```

Danach Claude Code neu starten oder `/reload-plugins` ausführen. Die Plugins stehen ab
dann in **jedem** Projektordner zur Verfügung.

> Voraussetzung: Zugriff auf das GitHub-Repo, einmalig `gh auth login`.

### Zugang zum Shop

Jeder Skill braucht einen Shop-Token. Der wird **nicht** von Claude erzeugt, sondern vom
Menschen im Shop-Admin — der Weg steht in `shopify-migration/references/custom-app.md`.
Der Token landet in einer Datei, nie im Chat:

```
~/.config/shopify-<kunde>.env
```

```
SHOP=kunde-xxxx.myshopify.com
TOKEN=shpat_...
```

Welche Berechtigungen nötig sind, steht in
`shopify-settings/references/berechtigungen.md`. Sie decken alle Skills ab.

---

## Benutzen

Terminal im Kundenordner öffnen, `claude` starten, in normaler Sprache sagen, was ansteht:

> Ich möchte einen Shopify-Shop einrichten.

> Ich möchte Produkte in einen Shopify-Shop migrieren.

> Setz mir das Konzept im Theme um.

> Mach eine Abnahme — kann der Shop live gehen?

Claude wählt den passenden Skill und führt durch alle Phasen. Man muss keine Datei öffnen
und keinen Befehl tippen.

### Reihenfolge

```
shopify-settings  →  shopify-design  →  shopify-migration  →  shopify-abnahme
   Rahmen              Aufbau            Produkte             Prüfung + Übergabe
```

Die Reihenfolge ist kein Vorschlag. Stehen Metafelder, Versandzonen und Pflichtangaben
vor dem Import, muss man sie nicht bei hunderten Produkten nachziehen. Und eine Prüfung
an einem halbfertigen Shop erzeugt Befunde, die sich beim Weiterbauen von selbst
erledigen.

---

## Die Skills im Einzelnen

### `shopify-settings` — Grundeinrichtung

Richtet den Rahmen ein: Stammdaten, Richtlinien, Versand, Sprachen, Märkte, Standorte,
Steuern, Metafeld-Definitionen. Prüft zuerst, was fehlt, und trennt dabei drei Dinge —
was blockiert, was geprüft gehört, und was mangels Berechtigung *unklar* blieb.

| Skript | Was es tut |
|---|---|
| `1_bestandsaufnahme.py` | Prüft den gesamten Einrichtungsstand, schreibt `Einrichtungsstand.md` |
| `2_richtlinien.py` | Spielt eine **gelieferte** Richtlinie ein — schreibt selbst keine |

**Grenzen:** Keine Rechtstexte, keine geschätzten Versandkosten oder Steuersätze, nie
Zahlungsanbieter (dort werden Bankdaten und Ausweise verlangt).

Nachschlagen: `berechtigungen.md`, `browser-einstellungen.md` (der Shopify-Admin steckt in
Shadow DOM — Werte müssen getippt, nicht zugewiesen werden), `fallen.md`.

---

### `shopify-migration` — Produktmigration

Sieben Phasen, fünf Freigaben: Zugang, Shop-Analyse, Steckbrief, Importvorlage, Prüfung,
Import, Abnahme.

| Skript | Was es tut |
|---|---|
| `1_steckbrief.py` | Liest den Zielshop aus — Metafelder, Optionen, Tag-Struktur, Kollektionen |
| `2_vorlage.py` | Erzeugt die Importvorlage passend zu diesem Shop |
| `3_pruefen.py` | Prüft die gefüllte Vorlage vor dem Import — Pflichtfelder, Dubletten, Handles |
| `4_import.py` | Importiert über `productSet`, mit Wiederaufnahme nach Abbruch |
| `5_abnahme.py` | Vergleicht Soll und Ist nach dem Import |

Nachschlagen: `custom-app.md` (zwei Wege zum Token — Shop-Admin gibt ihn direkt, das
Partner Dashboard nur über OAuth), `chrome.md`, `fallen.md`.

---

### `shopify-design` — Konzept im Theme umsetzen

Acht Phasen. Beginnt bewusst mit der **Copy als eigenem Zwischenasset**, das freigegeben
wird, bevor irgendetwas ins Theme geht.

| Skript | Was es tut |
|---|---|
| `1_konzept_lesen.py` | Liest Scope-Dokument und Konzeptpräsentation aus, inklusive Farbwerten |
| `3b_entwurf.py` | Startseiten-Entwurf: Gerüst aus Copy und Konzept, danach Prüfung |
| `2_copy_geruest.py` | Baut das Copy-Gerüst aus der Konzeptstruktur |
| `3_copy_ansicht.py` | Rendert die Copy als HTML zur Freigabe |
| `4_theme_inventar.py` | Liest, welche Sections und Blöcke dieses Theme wirklich hat |
| `5_aufbau.py` | Setzt die freigegebene Copy in die Sections ein |
| `6_pruefung.py` | Findet offene `[RÜCKFRAGE …]`, Platzhalter, nicht gesetzte Bilder |
| `7_gestaltung.py` | Schriften und Farbpalette |
| `8_bilder.py` | Bildmotive aus HTML-Vorlagen, stellt Produktfotos frei, lädt hoch |
| `8b_bild_erzeugen.py` | Einzelmotive über die OpenAI-Bild-API, `--transparent` für freigestellte Elemente |
| `8c_hero.py` | Hero nach den HDC-Hero-Regeln aus einem JSON-Prompt, 3200×900 |
| `8d_kategoriebanner.py` | Kategoriebanner als Satz — ein Stil, ein Motiv je Kollektion |
| `9_checkliste.py` | Theme-Einstellungen nach HDC-Checkliste (Schritt 2) |
| `10_kategorieseite.py` | Sortierung, ausverkaufte Artikel ans Ende, Filter, Banner, Bildformate (Schritt 6) |
| `11_produktseite.py` | Verfügbarkeit, Versandhinweis, Akkordeon, Express-Checkout raus (Schritt 7) |
| `12_serviceseiten.py` | FAQ, Versand, Zahlung, Über uns als Gerüst (Schritt 8) |
| `13_demoprodukt.py` | Demo-Produkt mit allen Metafeldern — prüft die Kette vor der Migration |

**Bilder — vier Werkzeuge, fünf Sorten, zwei harte Grenzen:**

| Sorte | woher | machbar |
|---|---|---|
| Fläche und Form | HTML-Vorlage | ja |
| Stimmung, Textur, freigestelltes Element | erzeugt | ja |
| Komposition aus Kundenfoto und Fläche | Kundenfoto + Vorlage | ja |
| **Das Produkt des Kunden** | Shooting, Kunde | **nie erzeugen** |
| **Menschen, die es wirklich gibt** | Shooting, Kunde | **nie erzeugen** |

Die letzten beiden Zeilen sind keine Empfehlung. Ein erzeugtes Produktbild zeigt Ware,
die es so nicht gibt; ein erzeugtes Gesicht behauptet einen Menschen. Soll das Produkt im
Bild sein, kommt es als echtes Foto über `referenced_image_ids` hinein.

Freigestellt wird über die macOS-Vision-Bibliothek oder direkt beim Erzeugen mit
`--transparent`. Der Hero folgt festen Regeln — 3200×900, linke Hälfte frei für Text,
alles Visuelle rechtsbündig, kein Text im Bild — und entsteht erst nach einem Interview
und drei Szenenvorschlägen. Kategoriebanner entstehen immer als Satz aus einer Stil-Datei.

**Harte Regeln:** Kein Text im Bild — er wäre nicht responsiv, nicht übersetzbar, nicht
durchsuchbar, nicht vorlesbar. Nie auf dem aktiven Theme arbeiten, immer auf einem
Duplikat; die Skripte verweigern das MAIN-Theme.

Nachschlagen: `copywriting.md`, `entwurf.md`, `gestaltung.md`, `hero-prompts.md`,
`schluessel.md`, `theme-checkliste.json`, `zuordnung-horizon.json`, `fallen.md`.

**Schlüssel:** Der OpenAI-Plattform-Schlüssel liegt in `~/.config/openai.env`, einmal je
Rechner. Claude zeigt die Ablage und nimmt ihn nicht entgegen. Prüfen kostet nichts:

```bash
python3 scripts/8b_bild_erzeugen.py --schluessel-pruefen
```

---

### `shopify-abnahme` — Prüfung und Übergabe

Vier Skills in einem Plugin. `shopify-abnahme` führt die drei anderen nacheinander aus;
sie funktionieren aber auch einzeln und schreiben in dieselben Befund-Dateien.

```
shopify-abnahme
   ├── shopify-ux      Benutzerführung
   ├── shopify-cro     Verkaufspsychologie
   └── shopify-recht   Pflichtangaben
```

#### `shopify-ux`

Prüft entlang von drei festgelegten Kaufwegen — „ich weiß was ich will", „ich weiß es
noch nicht", „ich habe eine Frage". Das Skript misst WCAG-Kontraste, Startseitenlänge,
Navigationsbreite, tote Menüpunkte, fehlende Alt-Texte, dünne Beschreibungen.

Alles Weitere kommt aus dem Browserdurchgang. **Mobil wird nur behauptet, wenn es geprüft
wurde** — das Fenster zu verkleinern reicht nicht, der Rendering-Viewport bleibt breit.

Nachschlagen: `heuristiken.md` — zehn Fragen, an denen sich fast jeder Befund festmachen
lässt, plus die Kontrastwerte, die nicht verhandelbar sind.

#### `shopify-cro`

Geht die fünf Einwände in fester Reihenfolge durch: Bin ich hier richtig → Ist das das
Richtige → Kann ich denen glauben → Was kostet es wirklich → Was, wenn es nicht passt.
Eine Frage, die erst im Checkout beantwortet wird, ist zu spät beantwortet.

Das Skript zählt Bilder je Produkt, leere Kategorien, fehlende Bewertungen und
Empfehlungen, Zahlungsicons, Newsletter, Versandversprechen, Warenkorb-Typ.

Nachschlagen: `verkaufspsychologie.md` — trennt Hebel, die tragen (Sozialbeweis,
Konkretheit, Verlustaversion), von denen, die kippen (erfundene Knappheit, Streichpreise
ohne echten Vorpreis nach § 11 PAngV, generierte Bewertungen).

#### `shopify-recht`

Stellt fest, **ob** Pflichtangaben da sind — nicht, ob ihr Text trägt. Schreibt keine
Rechtstexte, auch nicht als Entwurf, und gibt keine Rechtsauskunft.

Geprüft werden: AGB, Widerruf, Datenschutz, Impressum; Mehrwertsteuer- und
Versandkostenhinweis am Preis; Grundpreis nach PAngV; Metafelder für Herstellerangaben
nach GPSR; Cookie-Einwilligung; Versandtarife; Rechtstexte in allen veröffentlichten
Sprachen.

**Fehlt eine Berechtigung, gilt der Punkt als ungeprüft — nicht als in Ordnung.**

Nachschlagen: `pflichtangaben.md`.

#### Der Abnahme-Skill selbst

| Skript | Was es tut |
|---|---|
| `abnahme.py` | Startet alle drei Prüfungen nacheinander, fasst den Stand zusammen |
| `abnahme.py --stand` | Nur zusammenrechnen, ohne neu zu prüfen |
| `umsetzen.py` | Setzt um, wofür es einen echten Handgriff gibt |
| `uebergabe.py` | Schreibt `Uebergabe.md` |

Alle Befunde laufen in `befunde/*.json` zusammen, in einem gemeinsamen Format:

```json
{"bereich":"ux","punkte":[
 {"id":"ux-kontrast-text","schwere":"blocker","wo":"Farbpalette",
  "befund":"…","empfehlung":"…","umsetzung":"mensch","befehl":null}]}
```

Claude trägt dort auch ein, was es im Durchgang selbst gefunden hat.

**Zwei Regeln, die den Wert des Dokuments ausmachen:**

- Ein Befund gilt nur als erledigt, wenn er nachweislich umgesetzt wurde. Ein als `auto`
  markierter Punkt ohne hinterlegten Handgriff wird gemeldet, nicht abgehakt.
- Ungeprüft ist nicht in Ordnung. Fehlende Berechtigungen stehen als eigener Abschnitt in
  der Übergabe.

`Uebergabe.md` ist nach **Zuständigkeit** sortiert, nicht nach Thema:

1. Blocker vor dem Livegang
2. Liegt beim Kunden
3. Von Hand im Shop-Admin
4. Immer vor dem Livegang — Zahlung, Domain, Plan, Passwortschutz, Testbestellung,
   E-Mail-Vorlagen, Weiterleitungen, Analytics
5. Erledigt — mit dem, was tatsächlich gemacht wurde
6. Nicht prüfbar

---

## Was Claude in diesem Kit nicht tut

Diese Grenzen sind in den Skills festgeschrieben, nicht Auslegungssache:

- **Keine Rechtstexte.** AGB, Widerruf, Datenschutz, Impressum kommen vom Kunden, seinem
  Anwalt oder einem Dienst wie der IT-Recht Kanzlei. Auch kein Entwurf.
- **Keine erfundenen Fakten.** Maße, Gewichte, Preise, Lieferzeiten, Herstelleradressen,
  Zielgruppenzuordnungen. Recherchiertes wird mit Quelle vorgelegt und bestätigt.
- **Keine Zahlungsanbieter, keine Domains, keine Tarifwahl.** Dort werden Bankdaten und
  Ausweise verlangt.
- **Kein Token, kein Client Secret im Chat**, in Mails, in Tickets oder auf Screenshots.
  Claude liest die Datei selbst.
- **Die App erstellt der Mensch.** Claude erzeugt keine Zugangsdaten.
- **Nie auf dem aktiven Theme.** Immer Duplikat.
- **Schreiben nur nach getipptem `JA`.**

---

## Prozessdokumentation

Zwei Dokumente in `dokumentation/`:

| Datei | Was drin ist | Bauen |
|---|---|---|
| `HDC-Shopify-Prozess.pdf` | 23 Seiten Handbuch — Prinzip, Kette, Vorbereitung, alle vier Stufen mit Phasen und Freigaben, die Übergabe, im Anhang die Zuordnung der alten HDC-Checkliste | `bash dokumentation/bauen.sh` |
| `HDC-Shopify-Prozess-Diagramme.pdf` | 7 Seiten nur Grafik, A4 quer — erst grob (vier Stufen), dann alle Phasen auf einem Blatt, dann je Stufe ein Ablaufdiagramm, zuletzt die Bildwerkzeuge | `python3 dokumentation/diagramme.py` |

Beide brauchen Google Chrome. Das Handbuch zusätzlich `reportlab` und `pypdf` — Chrome
rendert das Layout, reportlab stempelt Fußzeile und Seitenzahlen darüber, weil Chrome die
CSS-Randboxen für Seitenzahlen nicht kennt.

Die Diagramme entstehen als SVG aus einer einzigen Datenstruktur in `diagramme.py`.
Ändert sich eine Phase, wird sie dort geändert — nicht in fünf Zeichnungen.

## Updates

Kommen automatisch. Manuell erzwingen:

```
/plugin marketplace update hdc-digital
```

---

## Für Entwickler

Lokal testen, ohne zu installieren:

```bash
claude --plugin-dir ~/Documents/hdc-shopify-migration/plugins/shopify-abnahme
```

Prüfen und veröffentlichen:

```bash
claude plugin validate ~/Documents/hdc-shopify-migration/plugins/shopify-abnahme
git add -A && git commit -m "Was geändert wurde" && git push
```

Eine Version muss nicht hochgezählt werden — ohne `version`-Feld gilt der Commit-Stand.

### Aufbau

```
hdc-shopify-migration/
├── .claude-plugin/marketplace.json      Marketplace-Definition
└── plugins/<plugin>/
    ├── .claude-plugin/plugin.json       Plugin-Manifest
    └── skills/<skill>/
        ├── SKILL.md                     führt das Gespräch
        ├── references/                  Claude liest, gibt im Chat wieder
        ├── vorlagen/                    HTML-Vorlagen für Bildmotive
        └── scripts/                     nummeriert in Ablaufreihenfolge
            └── shopify.py               geteiltes Modul, in jedem Skill identisch
```

`scripts/shopify.py` liegt bewusst in jedem Skill als Kopie — Skills sollen einzeln
lauffähig sein. Änderungen daran gehören in alle Kopien.

### Warum curl statt urllib

Die Python-Standardbibliothek scheitert auf einigen Rechnern an der Zertifikatsprüfung.
`gql()` ruft deshalb `curl` als Unterprozess auf. Das ist Absicht, kein Provisorium.

### Lokale Installation ohne Marketplace

Zum Entwickeln oder wenn die Marketplace-Installation nicht in Frage kommt, lassen sich
die Skills direkt nach `~/.claude/skills/` hängen:

```bash
bash werkzeuge/lokal-installieren.sh
```

Das legt Symlinks an — Änderungen im Repo wirken damit sofort, ohne Neuinstallation.
