# Referenz: Gestaltung — Schriften, Farben, Bilder

Ein Textgerüst in Theme-Standardoptik ist noch kein Design. Drei Dinge machen den
Unterschied, und alle drei sind steuerbar.

## Schriften und Farben — vollständig per API

Themes halten dafür überraschend viele Stellschrauben. Horizon zum Beispiel: **49
Typografie-Einstellungen**, davon vier Schriftwähler (Überschrift, Fließtext, Zwischentitel,
Akzent) und 32 für Größen, Zeilenhöhen, Laufweite und Groß-/Kleinschreibung.

```
python3 scripts/7_gestaltung.py --theme <id> --zeigen
python3 scripts/7_gestaltung.py --theme <id> --heading archivo_n7 --body ibm_plex_sans_n4 \
    --akzent "#F6A429" --zweit "#334B70"
```

Schriftkennungen haben die Form `<familie>_n<gewicht>` — `archivo_n7`, `work_sans_n4`.
**Ein Name ohne passende Datei fällt still auf die Systemschrift zurück**, ohne Fehler.
Nach dem Setzen also immer gegenlesen:

```js
getComputedStyle(document.querySelector('h1')).fontFamily
```

**Farben laufen bei neueren Themes über eine Palette.** Einzelfelder verweisen nur darauf
(`{{ settings.color_palette.background }}`). Wer ein Einzelfeld überschreibt, zerreißt den
Verweis — immer die Palette ändern.

## Bilder — drei Wege, in dieser Reihenfolge

**1. Der Kunde liefert.** Der Regelfall bei Produktfotos. Hochladen, Alt-Text setzen, fertig.

**2. Vorhandenes aufbereiten.** Zuschnitt, Format, Freisteller. Auf dem Mac gehen Pillow und
`sips` ohne Zusatzsoftware.

**3. Motive erzeugen.** Banner, Kategoriebilder, Farbflächen, Muster:

```
python3 scripts/8_bilder.py --vorlage motiv-formen --akzent "#F6A429" \
    --zweit "#334B70" --grund "#E8E2CD" --name hero-motiv --nur-erzeugen
```

Die Vorlage ist HTML, gerendert über headless Chrome. Erst `--nur-erzeugen`, ansehen, dann
ohne das Flag hochladen und einsetzen.

**Was so nicht entsteht: Fotos.** Ein Pferd im Stall, ein Produkt in der Hand, eine Person
bei der Anwendung — das kommt vom Kunden oder aus einem Shooting. Wer das mit Farbflächen
ersetzen will, bekommt einen Shop, der aussieht wie eine Präsentationsfolie.

## Die wichtigste Regel: kein Text im Bild

Das ist der Fehler, der beim ersten Versuch am naheliegendsten ist — und er zeigt sich
sofort: Steht die Überschrift im Bild **und** im Section-Textblock, liest man sie doppelt.

Text im Bild ist außerdem:

- **nicht responsiv** — auf dem Handy wird er mitskaliert und unlesbar
- **nicht übersetzbar** — die englische Fassung zeigt weiter deutschen Text
- **nicht durchsuchbar** — weder für Google noch für die Shop-Suche
- **nicht vorlesbar** — Screenreader sehen nur den Alt-Text

Deshalb enthalten die Vorlagen bewusst keinen Text, und das Skript warnt, wenn eine Vorlage
Textelemente hat. Bilder liefern Fläche, Farbe und Form — die Worte kommen aus der Section.

## Formatierung

Was oft mehr bringt als ein neues Bild: Ausrichtung, Abstände, Schriftgrößen. In Horizon
sitzen die in den Section-Settings (`horizontal_alignment_…`, `padding-block-start`, `gap`)
und in der Typografie-Gruppe der Theme-Einstellungen (`type_size_h1`, `type_line_height_h1`).

Beim Aufbau mitgeben statt hinterher nachziehen — die Zuordnungsdatei ist der richtige Ort.
