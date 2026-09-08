---
name: shopify-ux
description: Prüft einen fertig aufgebauten Shopify-Shop auf Benutzerführung und Bedienbarkeit. Nutze diesen Skill bei "UX prüfen", "Usability", "Benutzerführung", "ist der Shop verständlich", "Shop-Review Design" oder vor einer Übergabe.
---

# UX-Prüfung

Du gehst durch einen fertigen Shop wie jemand, der ihn zum ersten Mal sieht und etwas
kaufen will. Nicht wie jemand, der ihn gebaut hat.

## Die wichtigste Regel: erst gehen, dann urteilen

Ein UX-Befund entsteht aus einem Weg, nicht aus einer Liste. Nimm dir drei Aufgaben vor
und versuche sie wirklich:

1. **"Ich weiß, was ich will."** Startseite → Kategorie → Produkt → Warenkorb.
2. **"Ich weiß es noch nicht."** Startseite → stöbern → vergleichen → entscheiden.
3. **"Ich habe eine Frage."** Versandkosten finden, ohne zu bestellen.

Zähle bei jedem Weg die Klicks und schreib auf, wo du stockst. Genau da liegt der Befund.
Wo du nicht stockst, gibt es nichts zu melden — auch wenn eine Checkliste etwas anderes
sagt.

## So redest du

Im Chat erklären, nicht auf Dateien verweisen. Jeder Befund braucht drei Sätze: was ist,
warum das stört, was stattdessen. Ohne den mittleren Satz ist es Geschmack.

## Grundregeln

1. **Kein Umbau während der Prüfung.** Erst der vollständige Befund, dann die Umsetzung
   über `shopify-uebergabe`. Wer während des Durchgangs schraubt, prüft am Ende sich selbst.
2. **Geschmack von Fehler trennen.** "Ich hätte das anders gemacht" ist kein Befund.
   Ein Befund ist: jemand findet etwas nicht, versteht etwas falsch, oder bricht ab.
3. **Nichts behaupten, was du nicht gesehen hast.** Besonders mobil — siehe unten.
4. **Der Kunde hat entschieden.** Farben, Logo, Bildsprache stehen im Konzept. Prüf, ob
   sie funktionieren, nicht ob sie dir gefallen.

## Ablauf

Skripte liegen in `scripts/` neben dieser Datei:

```bash
find ~/.claude -type d -name shopify-ux -path '*skills*' 2>/dev/null | head -1
```

### Phase 1 — Das Messbare

```
python3 <pfad>/scripts/befund.py --theme <id>
```

Kontraste nach WCAG, Länge der Startseite, Breite der Navigation, tote Menüpunkte,
fehlende Alt-Texte, dünne Beschreibungen, überlange Titel. Schreibt `befunde/ux.json`.

Das ist die kleinere Hälfte. Ein Skript sieht, dass ein Kontrast 3,1:1 beträgt — nicht,
dass die Kategorienamen nicht zum Sortiment passen.

### Phase 2 — Der Durchgang

Die drei Aufgaben oben, im Browser, am echten Shop. Achte auf:

- **Erster Bildschirm** — steht dort, was der Shop verkauft und für wen? Oder nur ein Bild?
- **Kategorienamen** — heißen sie wie die Wörter der Zielgruppe oder wie die interne Struktur?
- **Produktkarte** — Bild, Name, Preis auf einen Blick? Springt der Preis beim Laden?
- **Produktseite** — steht die Kaufentscheidung über der Falz oder muss man scrollen?
- **Formulare** — sind Pflichtfelder erkennbar, sind Fehlermeldungen verständlich?
- **Leere Zustände** — leere Suche, leerer Warenkorb, ausverkauftes Produkt.
- **Ladeverhalten** — springt das Layout, während Bilder nachladen?

### Phase 3 — Mobil

**Das Fenster zu verkleinern reicht nicht.** Der Rendering-Viewport bleibt breit; du prüfst
gegen die Desktop-Ansicht, ohne es zu merken. Es braucht echte Geräteemulation.

Steht sie nicht zur Verfügung: **sag es**, und bitte die Person, die drei Wege am Handy
selbst zu gehen. Eine behauptete Mobilprüfung ist schlimmer als keine — sie schließt den
Punkt, ohne ihn zu prüfen.

Mobil zuerst prüfen, wo Shops typischerweise brechen: Klickflächen unter 44 px, Varianten
zu eng beieinander, klebender Warenkorb-Button verdeckt den Preis, Tabellen laufen über
den Rand, Overlays ohne sichtbares Schließen.

### Phase 4 — Befund ergänzen

Trag deine Beobachtungen in `befunde/durchgang.json` ein, gleiche Form wie `ux.json`:

```json
{"bereich":"durchgang","punkte":[
 {"id":"ux-kategorienamen","schwere":"wichtig","wo":"Navigation",
  "befund":"Die Kategorie heißt 'Sonstiges' und enthält vier Produktgruppen.",
  "empfehlung":"Aufteilen und nach dem benennen, wonach Kunden fragen.",
  "umsetzung":"mensch","befehl":null}]}
```

`schwere`: `blocker` (verhindert den Kauf), `wichtig` (kostet Umsatz), `kosmetik`.
`umsetzung`: `auto` nur, wenn es dafür in `shopify-uebergabe` wirklich einen Handgriff
gibt — sonst `mensch`.

> **Freigabe** — Befund besprochen, bevor irgendetwas geändert wird.

Danach: `shopify-cro`, `shopify-recht`, zuletzt `shopify-uebergabe`.
