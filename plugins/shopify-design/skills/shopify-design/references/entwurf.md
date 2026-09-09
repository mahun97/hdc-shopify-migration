# Der Startseiten-Entwurf

Zwischen der freigegebenen Copy und dem Theme steht ein eigenes Dokument: eine
gestaltete HTML-Seite, die zeigt, **wie die Startseite aussehen wird**. Sie ist kein
Theme, sie liegt nicht im Shop, sie wird nie veröffentlicht.

## Warum überhaupt

Die Copy beantwortet, *was* dasteht. Der Entwurf beantwortet, *wie es wirkt* — Reihenfolge
der Abschnitte, Bildsprache, Typografie, Rhythmus zwischen ruhig und laut. Beides in einem
Schritt zu klären funktioniert nicht: Über Farben zu diskutieren, während der Text noch
wackelt, kostet zwei Runden statt einer.

Und: Aus dem Entwurf entstehen die Sections. Steht die Abschnittsfolge einmal fest und
ist abgenommen, ist der Theme-Aufbau Ausführung statt Entwurf.

## Woran man einen brauchbaren Entwurf erkennt

**Eigene Gestaltung, nicht Theme-Standard.** Ein Entwurf in den Voreinstellungen des
Themes zeigt nichts, was zu entscheiden wäre. Eigene Palette, eigenes Schriftpaar, eigener
Abschnittsrhythmus.

**Echte Texte.** Die freigegebene Copy, nicht gekürzt und nicht mit Blindtext gemischt.
Wo der Text zu lang für die Fläche ist, ist das ein Befund — kein Grund zum Kürzen im
Entwurf.

**Echte Bilder.** Fotos des Kunden, notfalls von seiner bestehenden Seite verlinkt. Graue
Kästen zeigen nicht, ob die Bildsprache trägt.

**Als Entwurf gekennzeichnet.** Eckbanner „ENTWURF", im Titel und in der Fußzeile „nicht
zur Veröffentlichung". Diese Datei wandert per Mail weiter und darf nie mit der fertigen
Seite verwechselt werden.

**Offene Punkte als Fußnote am Abschnitt**, nicht am Ende. Beispiel aus einem echten
Entwurf:

> *Hinweis für die Umsetzung: Konditionen (Betrag, Mindestbestellwert, Kühllogik) vor
> Livegang final mit der Kundin abstimmen — aktuell kommuniziert die Website zwei
> unterschiedliche Versandregeln.*

Das ist die Stelle, an der ein Widerspruch auffällt: beim Gestalten, nicht beim Livegang.

**Ein Bildschirm zeigt eine Entscheidung.** Wer über eine Seite scrollt und nicht sagen
kann, welche Frage der Abschnitt beantwortet, hat einen Abschnitt zu viel.

## Was der Entwurf nicht ist

Kein Klickdummy. Keine zweite Seite, kein Produktdetail, kein Warenkorb. Genau eine
Startseite — sie trägt die Gestaltungsentscheidung, alles Weitere folgt ihr.

Kein Theme-Vorabbau. Der Entwurf darf CSS benutzen, das im Theme so nicht möglich ist —
solange die Umsetzung danach machbar bleibt. Phase 4 prüft das gegen das echte Inventar
des Themes, bevor gebaut wird.

## Ablauf

```
python3 scripts/3b_entwurf.py --geruest      Gerüst aus konzept.json und der Copy
                                             — Abschnittsfolge, Palette, Schriften
… gestalten …                                das ist die eigentliche Arbeit
python3 scripts/3b_entwurf.py --pruefen      Blindtext, fehlende Bilder, Kennzeichnung
```

Das Gerüst nimmt Arbeit ab, es gestaltet nicht. Was zwischen den beiden Aufrufen passiert,
ist der Entwurf — dafür gilt alles aus `gestaltung.md`.

## Danach

Der abgenommene Entwurf ist die Vorlage für Phase 5. Jeder Abschnitt bekommt seine Section
im Theme, in derselben Reihenfolge. Weicht das Theme ab — weil es eine Section nicht hat —
gehört das gesagt, bevor gebaut wird, nicht danach.
