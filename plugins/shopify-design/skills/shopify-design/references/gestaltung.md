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

## Bilder — fünf Sorten, drei davon machbar

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

### Drei Sorten Bild — und was davon hier machbar ist

| | woher | machbar |
|---|---|---|
| **Fläche und Form** — Verläufe, Bühnen, geometrische Motive | HTML-Vorlage, hier gerendert | ja |
| **Stimmung und Element** — Hintergrundtextur, Blattwerk, Werkzeug, generisches Objekt | erzeugt, `8b_bild_erzeugen.py` | ja |
| **Komposition** — Produktfoto freigestellt auf so einer Fläche, mit Schatten und Störer | Kundenfoto + Vorlage | ja |
| **Das Produkt des Kunden** — die Ware selbst, in jeder Ansicht | Shooting, Kunde | **nie erzeugen** |
| **Menschen, die es gibt** — Inhaberin, Team, Werkstatt | Shooting, Kunde | **nie erzeugen** |

**Die vierte und fünfte Zeile sind keine Empfehlung, sondern eine Grenze.** Ein erzeugtes
Produktbild zeigt ein Produkt, das es so nicht gibt — in einem Shop ist das irreführende
Werbung, und zwar die Art, die auffällt, wenn die Ware ankommt. Ein erzeugtes Gesicht auf
einer „Über uns"-Seite behauptet einen Menschen, den es nicht gibt.

Dazwischen liegt viel: der Hintergrund, auf dem das echte Produktfoto steht, die Textur
hinter einem Zitat, das Blatt neben der Zutatenliste. Dafür ist die Bilderzeugung da.

Ein Banner, das nur aus Farbflächen besteht, sieht aus wie eine Präsentationsfolie. Fast
immer ist die mittlere Zeile die Antwort: Der Kunde hat Produktfotos, meist freigestellt
oder auf weißem Grund. Die kommen auf die Fläche, nicht statt ihr.

Freistellen macht `scripts/freisteller.swift` (macOS Vision, wird beim ersten Lauf
automatisch kompiliert). `--foto` genügt:

```
python3 scripts/8_bilder.py --vorlage motiv-buehne --foto produkt.png \
    --grund "#FCFEFF" --buehne "#D3E9F7" --akzent "#E8F4DE" \
    --name hero --groesse 2600x1040 --nur-erzeugen
```

### Erzeugte Motive

```
python3 scripts/8b_bild_erzeugen.py --schluessel-pruefen
python3 scripts/8b_bild_erzeugen.py --format quer --qualitaet mittel --name hero-grund \
    --prompt "…"
python3 scripts/8b_bild_erzeugen.py --transparent --name element --prompt "…"
```

Schlüssel: `~/.config/openai.env`, siehe `schluessel.md`. Das Skript druckt die Anleitung
selbst, wenn die Datei fehlt — es rechnet ab, also erst ein Bild ansehen, dann die Serie.

**`--transparent` liefert freigestellt.** Für erzeugte Elemente entfällt damit der
Freisteller-Umweg: Das PNG hat einen echten Alphakanal und geht direkt als `--foto` in
`motiv-buehne` oder `motiv-produkt`.

**Was in den Prompt gehört:** Bildausschnitt, Licht, Farbstimmung, Detailgrad — und
ausdrücklich, was *nicht* drin sein soll. `kein Text, keine Logos, keine Personen` steht
in fast jedem brauchbaren Prompt, weil das Modell sonst gern Buchstaben erfindet. Für
Hero-Hintergründe zusätzlich: welche Bildhälfte ruhig bleiben muss, damit dort Text stehen
kann.

Vorlagen mit Produktplatz:

- `motiv-buehne` — weicher Verlauf, Produkt rechts, linke Hälfte bleibt ruhig für den Text
- `motiv-produkt` — Farbfeld, runde Bühne, Produkt rechts, roter Störer (`--stoerer-oben`,
  `--stoerer-gross`, `--stoerer-unten`)

Freistellen scheitert bei Motiven ohne klaren Vordergrund (Textur, Flatlay, mehrere
gleichrangige Objekte). Das Skript sagt das und nimmt dann das Original — dann lieber ein
anderes Foto wählen als das Ergebnis durchwinken.

**Seitenverhältnis prüfen.** Das Bild liegt als `cover` hinter der Section. Ist es deutlich
höher als der sichtbare Streifen, schneidet der Browser oben und unten ab — und zwar genau
da, wo das Produkt steht. Bildverhältnis und `section_height` müssen zusammenpassen; sonst
ist der Sprühkopf weg.

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
