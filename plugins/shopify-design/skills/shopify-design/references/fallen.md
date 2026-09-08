# Bekannte Fallen beim Theme-Aufbau

**Konzeptpräsentationen sind oft nicht als Text extrahierbar.** Viele nutzen
Font-Subsetting — dann liefert die Textextraktion Buchstabensalat. PyMuPDF (`fitz`)
kommt damit klar, die meisten anderen Werkzeuge nicht. Farbwerte lassen sich als
Vektorflächen auslesen, das ist zuverlässiger als aus Screenshots zu schätzen.

**Die Farbextraktion findet auch Folienhintergründe.** Grautöne und sehr große Flächen
sind meist Layout der Präsentation, nicht Markenfarben. Das Skript filtert das grob —
prüf das Ergebnis trotzdem gegen die Folie.

**Section-Namen unterscheiden sich je Theme.** Was in Dawn `image-banner` heißt, kann in
Prestige anders heißen. Immer erst das konkrete Theme inventarisieren.

**Templates sind JSON.** Section-Reihenfolge steht in `templates/*.json` unter `order`,
die Einstellungen je Section darunter. Blöcke mit `"disabled": true` erscheinen nicht —
das sieht aus, als gäbe es sie nicht.

**Ein Tab mit leerem Inhalt wird ausgeblendet.** Zeigt eine Section auf ein leeres
Metafeld, rendert Shopify sie gar nicht. Beim Aufbau also Beispielinhalt einsetzen,
sonst prüfst du gegen eine unsichtbare Section.

**Der Shopify-Admin läuft im Shadow DOM.** Für Theme-Einstellungen, die nur über die
Oberfläche gehen: `find` benutzen, nicht `querySelector`, und Werte tippen statt zuweisen.
Details in der Referenz des `shopify-settings`-Plugins.

**Textlänge bestimmt das Layout.** Deshalb Copy vor Aufbau. Eine Überschrift, die im
Dokument gut aussieht, kann im Hero über drei Zeilen brechen — dann lieber den Text
kürzen als die Section umbauen.

**Farben liegen je Theme woanders.** Ältere Themes haben pro Zweck ein eigenes Hex-Feld.
Horizon und andere neue Themes halten eine **Farbpalette** und verweisen aus den
Einzelfeldern nur darauf (`{{ settings.color_palette.background }}`). Wer dort ein
Einzelfeld überschreibt, zerreißt den Verweis — zum Umfärben die Palette ändern.
Das Inventar-Skript weist darauf hin, wenn es solche Verweise findet.

**Horizon ist blockbasiert.** Neben `sections/` gibt es `blocks/` mit eigenen Dateien
(im Testshop 95 Stück). Der Aufbau läuft dort stärker über Blöcke innerhalb weniger
Sections als über viele Sections. Vor dem Aufbau ins Inventar schauen.

**Horizon: Texte liegen in Blöcken, nicht in Section-Settings.** Eine Überschrift ist ein
`text`-Block mit `type_preset: h1`, ein Button ein `button`-Block. Wer `settings.heading`
sucht, findet nichts.

**Manche Sections erlauben keine freien Blöcke.** `media-with-content` hat im Schema
`"blocks": null` und arbeitet mit **statischen, verschachtelten** Blöcken (`media`,
`content`, darin `group` mit `heading` und `text`). Freie Blöcke quittiert Shopify mit
*„Blocks are not allowed in this context"* und lehnt den Upload ab — immerhin, ohne das
Template zu beschädigen. Deshalb bildet die Zuordnung ganze Vorlagen ab, keine Feldlisten.
Die Vorlagen stammen aus den `presets` der Section-Schemas.

**Theme-Duplikate entstehen asynchron.** Direkt nach `themeDuplicate` liefert die Asset-API
noch nichts. Erst prüfen, ob Dateien da sind, dann schreiben.

**`themeDuplicate` gibt `newTheme` zurück**, nicht `theme`.

**Mobilprüfung braucht echte Geräteemulation.** Das Browserfenster zu verkleinern genügt
nicht: `outerWidth` schrumpft, `innerWidth` bleibt breit — der Screenshot zeigt weiterhin
die Desktop-Ansicht. Wer das übersieht, meldet eine Mobilprüfung, die nie stattgefunden hat.
Prüfbar ohne Emulation ist nur, **ob** die Mobil-Einstellungen einer Section gesetzt sind;
wie sie aussehen, nicht.
