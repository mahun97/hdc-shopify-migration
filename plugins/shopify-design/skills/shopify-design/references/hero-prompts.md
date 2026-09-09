# Hero-Bilder — die HDC-Regeln

Der Hero ist das einzige Bild, das jeder Besucher sieht, und meistens das einzige, an das
er sich erinnert. Er entsteht deshalb nicht aus einem Halbsatz.

## Feste Regeln

| | |
|---|---|
| Format | 3200×900 |
| Linke Hälfte | bleibt frei für Text, bekommt ein dezentes Overlay — hell oder dunkel je nach Textfarbe |
| Produkt und visuelle Elemente | rechtsbündig |
| Szene | realistische Nutzungssituation, kein Studiofreisteller |
| Text im Bild | nie |

`8c_hero.py` hängt diese Regeln bei jedem Lauf selbst an den Prompt an, egal was im JSON
steht. Sie lassen sich nicht versehentlich weglassen.

## Der Ablauf

**1. Fragen — vor jedem Vorschlag.** In dieser Reihenfolge:

- Was wird verkauft?
- Wer nutzt es, in welcher Situation, an welchem Ort?
- Läuft eine Aktion? Rabatt, Saison, Neueinführung?
- Was genau soll beworben werden — das Sortiment, ein Produkt, ein Versprechen?
- Gibt es Beispielbilder oder Referenzshops, die gefallen?
- Welcher Stil: warm und wohnlich, technisch und klar, laut und werblich?

**2. Drei Szenen auf Deutsch.** Kurz, unterscheidbar, jeweils zwei bis drei Sätze. Drei
Varianten derselben Idee sind keine Auswahl — sie sollen sich in Ort, Tageszeit oder
Blickwinkel wirklich unterscheiden.

**3. Nach der Auswahl: der JSON-Prompt auf Englisch.** Struktur unten.

**4. Erzeugen, ansehen, entscheiden.**

```
python3 scripts/8c_hero.py --vorlage > hero.json
python3 scripts/8c_hero.py --json hero.json --name hero --overlay hell
```

`--overlay dunkel` bei heller Szene und weißer Schrift, `hell` bei dunkler Szene und
schwarzer Schrift, `kein` wenn die Szene links ohnehin ruhig genug ist.

## Die Struktur

```json
{
  "prompt": "", "size": "3200x900", "n": 1,
  "transparent_background": false, "referenced_image_ids": [],
  "style":   {"lighting":"","color_palette":"","mood":"","texture":"","contrast":"",
              "saturation":"","sharpness":"","depth_of_field":"","composition":""},
  "camera":  {"angle":"","lens":"","focal_length":"","aperture":"","exposure":"","film_type":""},
  "artist_style": {"inspired_by":"","medium":"","period":"","genre":""},
  "subject": {"main_object":"","secondary_objects":[],"background":"","foreground":"",
              "environment":"","action":"","perspective":"","details":""},
  "output":  {"format":"","quality":"","aspect_ratio":"","background_color":"",
              "border":"","style_strength":""},
  "metadata":{"title":"","tags":[],"author":"","created_at":"","version":"","notes":""}
}
```

`referenced_image_ids` nimmt lokale Dateipfade. Liegt dort ein echtes Produktfoto des
Kunden, schaltet das Skript auf den Edits-Endpunkt um und das Modell arbeitet damit statt
sich das Produkt auszudenken. **Das ist der saubere Weg, wenn das Produkt im Bild sein
soll.**

## Was die Felder wirklich bewirken

Die Felder, die den größten Unterschied machen, sind nicht die offensichtlichen:

- **`lighting`** trägt fast die ganze Stimmung. „warm late-afternoon daylight raking in
  from a floor-to-ceiling window on the left" liefert ein anderes Bild als „soft daylight".
- **`composition`** entscheidet, ob die linke Hälfte wirklich frei bleibt. Sag, *warum*
  sie frei ist — „so a headline can sit over it" versteht das Modell.
- **`action`** verhindert Katalogoptik. „nobody present, the room is quietly waiting"
  ergibt eine Szene, kein Produktfoto.
- **`details`** ist der Unterschied zwischen echt und generisch: „realistic bevelled plank
  edges, natural grain variation between planks".
- **`depth_of_field`** und **`aperture`** zusammen ergeben die werbliche Anmutung. Ohne
  sie wird alles gleich scharf und sieht nach Render aus.

## Grenzen des Modells

Empirisch ermittelt, nicht aus der Doku:

| | |
|---|---|
| Beide Seiten | durch 16 teilbar |
| Längste Kante | höchstens 3840 |
| Seitenverhältnis | höchstens 3:1 |

3200×900 ist 3,56:1 und damit **zu breit**. Das Skript erzeugt deshalb 3200×1072 (2,99:1)
und schneidet auf das Band herunter — reiner Zuschnitt, kein Hochskalieren. Ein Hero mit
3200×896 kostete im Test 4656 Token bei Qualität `high`.

Modelle auf dem Schlüssel: `gpt-image-2` (Standard, einziges mit freien Größen),
`gpt-image-2-2026-04-21`, `gpt-image-1.5`, `gpt-image-1`, `gpt-image-1-mini`,
`chatgpt-image-latest`. Wechseln mit `--modell`.

## Die harte Grenze

Was im Hero zu sehen ist, muss es geben. Ein erzeugter Raum, eine erzeugte Stimmung, ein
erzeugtes Licht — alles in Ordnung. **Ein erzeugtes Produkt, das der Kunde so nicht
verkauft, ist irreführende Werbung**, und zwar die Art, die auffällt, wenn das Paket
ankommt. Soll das Produkt im Bild sein, kommt es über `referenced_image_ids` als echtes
Foto hinein oder wird nachträglich einkomponiert.

Dasselbe gilt für Menschen: erzeugte Gesichter auf einer „Über uns"-Seite behaupten
Menschen, die es nicht gibt. In einer Nutzungsszene, in der niemand identifizierbar ist,
ist es unkritisch — deshalb steht in guten Prompts oft „no recognisable faces".
