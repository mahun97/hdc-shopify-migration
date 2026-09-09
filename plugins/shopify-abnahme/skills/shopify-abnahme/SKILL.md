---
name: shopify-abnahme
description: Führt die komplette Abnahme eines fertigen Shopify-Shops durch — UX, CRO und Recht nacheinander, setzt die Befunde um und erstellt die Übergabe-Checkliste. Nutze diesen Skill bei "Abnahme", "Gesamtprüfung", "Shop komplett prüfen", "kann der Shop live gehen", "Endabnahme" oder "Shop übergeben".
---

# Gesamt-Abnahme

Du führst die drei Prüfungen und die Übergabe als **einen** Vorgang durch. Der Mitarbeiter
soll einmal „Abnahme" sagen und danach eine belastbare Liste in der Hand haben — nicht
vier Skills nacheinander aufrufen müssen.

## Die wichtigste Regel: der Durchgang gehört dazu

Die Skripte finden die messbare Hälfte — Kontraste, Zahlen, fehlende Pflichtfelder. Die
andere Hälfte findet nur, wer den Shop benutzt. Eine Abnahme, die nur aus Skriptausgaben
besteht, ist eine halbe Abnahme, und das musst du dann auch so sagen.

## Ablauf

```bash
find -L ~/.claude -type d -name shopify-abnahme -path '*skills*' 2>/dev/null | head -1
```

Arbeite in einem Ordner je Kunde. Alles landet dort in `befunde/` und am Ende in
`Uebergabe.md`.

### Phase 1 — Alle drei Prüfungen

```
python3 <pfad>/scripts/abnahme.py --theme <duplikat-id>
```

Startet nacheinander die Skripte aus `shopify-ux`, `shopify-cro` und `shopify-recht` und
schreibt `befunde/ux.json`, `befunde/cro.json`, `befunde/recht.json`. Am Ende steht der
Stand: wie viele Blocker, wie viele ungeprüft.

**Fasse im Chat zusammen**, bevor du weitermachst — nach Schwere sortiert, Blocker zuerst.

### Phase 2 — Der Durchgang

Jetzt die Fachbrille aufsetzen, drei Mal. Die Skills liegen daneben und du liest sie
wirklich, statt aus dem Gedächtnis zu prüfen:

1. **`shopify-ux`** — die drei Kaufwege gehen, Klicks zählen, notieren wo man stockt.
   Dann `references/heuristiken.md` gegenlesen.
2. **`shopify-cro`** — die fünf Einwände abklopfen. `references/verkaufspsychologie.md`
   trennt dabei die Hebel, die tragen, von denen, die rechtlich kippen.
3. **`shopify-recht`** — im Shop nachsehen, was kein Skript sieht: Footer-Verlinkung,
   Cookie-Banner vor dem Setzen, Preisangaben in jeder Ansicht, branchenspezifische
   Pflichtangaben. `references/pflichtangaben.md`.

Ergänze deine Beobachtungen in `befunde/durchgang.json`, gleiche Form wie die
Skriptbefunde:

```json
{"bereich":"durchgang","punkte":[
 {"id":"ux-filter-fehlt","schwere":"wichtig","wo":"Kategorie",
  "befund":"Es gibt keinen Filter nach Menge, obwohl es das Kaufkriterium ist.",
  "empfehlung":"Filter nach Gebindegröße ergänzen.",
  "umsetzung":"mensch","befehl":null}]}
```

**Mobil:** Das Fenster zu verkleinern reicht nicht — der Rendering-Viewport bleibt breit.
Ohne echte Geräteemulation sagst du das offen und bittest die Person, die Wege am Handy
selbst zu gehen. Keine behauptete Prüfung.

> **Freigabe 1** — Befund vollständig, bevor irgendetwas geändert wird.

### Phase 3 — Umsetzen

```
python3 <pfad>/scripts/umsetzen.py --theme <id>
python3 <pfad>/scripts/umsetzen.py --theme <id> --setzen
```

Setzt um, wofür es einen echten Handgriff gibt. Alles andere bleibt liegen — auch wenn
ein Befund `"umsetzung": "auto"` sagt; das meldet das Skript ausdrücklich.

Was im Theme lösbar ist, aber kein Skript abdeckt, machst du mit `shopify-design`. Danach
den Punkt in der Befund-Datei auf `"erledigt": true` setzen und in `notiz` schreiben,
**was** gemacht wurde.

**Nicht umsetzen, was eine Zusage an Käufer ist** — Lieferzeit, Versandkosten, Garantie,
Herstelleradresse, Wirksamkeit. Die kommen vom Kunden.

### Phase 4 — Übergabe

```
python3 <pfad>/scripts/uebergabe.py --theme <id>
```

Schreibt `Uebergabe.md`: Blocker, beim Kunden, von Hand im Admin, die Punkte die jeden
Shop betreffen, das Erledigte und das Ungeprüfte.

Veröffentliche es als Artifact und gib den Link weiter. Im Chat drei Sätze: wie viele
Blocker, was der Kunde liefern muss, was als Nächstes ansteht. **Die schlechte Nachricht
zuerst.**

> **Freigabe 2** — Übergabe abgenommen.

## Zwischenstand

```
python3 <pfad>/scripts/abnahme.py --theme <id> --stand
```

Rechnet nur zusammen, was schon in `befunde/` liegt, ohne neu zu prüfen. Gut für die
Frage „wo stehen wir".

## Einzeln statt gesamt

Wenn nur ein Blickwinkel gefragt ist, rufe den einzelnen Skill auf — `shopify-ux`,
`shopify-cro`, `shopify-recht`. Sie funktionieren für sich und schreiben in dieselben
Befund-Dateien, sodass eine spätere Gesamt-Abnahme darauf aufsetzt.

## Vorher

Die Abnahme läuft erst, wenn der Shop steht: `shopify-settings` → `shopify-migration` →
`shopify-design`. Ein halbfertiger Shop erzeugt Befunde, die sich beim Weiterbauen von
selbst erledigen.
