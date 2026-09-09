# Bekannte Fallen

Aus echten Migrationen. Bei Problemen zuerst hier nachsehen, bevor du selbst suchst.

## Kollektionen und Tags

**Kollektion bleibt leer, obwohl Produkte da sind.**
Automatische Kollektionen filtern auf **exakte** Schreibweisen. `beutel und rollen` ist
nicht `beutel & rollen`. Erst gegen den Steckbrief prüfen. Stimmt die Schreibweise:
Shopify rechnet automatische Kollektionen **asynchron** nach — einige Minuten warten,
bevor du "leer" meldest.

**Menüpunkt zeigt zu viele Produkte.**
Untermenüs arbeiten oft mit Tag-Filter-URLs (`/collections/<koll>/<tag>+<tag>`).
Ein Filter **ohne Treffer** zeigt in Shopify nicht eine leere Seite, sondern die
**komplette Kollektion**. Heißt: Der Tag fehlt am Produkt. Wenn das Produkt noch gar
nicht existiert, den Menüpunkt vorerst ausbauen — sonst führt er in die Irre.

## Metafelder

**Metafeld ist per API gefüllt, im Theme aber unsichtbar.**
Die Definition braucht Storefront-Zugriff `PUBLIC_READ`.

**Vor dem Anlegen nachsehen.** Metafelder wie `custom.produktsicherheit` oder
`custom.mehr_infos` sind in vielen Themes schon angelegt — nur leer. Ein neues Feld
anzulegen erzeugt dann ein zweites, das niemand rendert.

## Theme

**Ein Tab oder Block erscheint nicht.**
Zwei mögliche Ursachen: Der Block ist im Template `"disabled": true`, oder sein Inhalt
zeigt auf ein leeres Metafeld — Shopify blendet ihn dann aus. Beides prüfen, bevor du
etwas Neues baust.

**Pflichtangaben fehlen auf der Produktseite.**
Der Versandkosten-Hinweis erscheint in vielen Themes nur, wenn `shop.shipping_policy`
gefüllt ist. Ist sie leer, muss der Hinweis fest auf die Versandseite verlinken.

**Liquid-Syntax.** `case/when` kennt **kein** `then`. Shopify lehnt den Upload sonst mit
"Unexpected character =" ab — immerhin bleibt die Live-Datei dabei unverändert.

## Navigation

**Menüeinträge vom Typ PRODUCT hängen an der Produkt-ID**, nicht am Handle. Ein
Handle-Tausch repariert so einen Link **nicht** — der Eintrag wandert mit dem Produkt mit.

**`menuUpdate` verlangt die komplette Item-Struktur.** Fehlende Einträge werden gelöscht.
Immer erst auslesen, sichern, dann vollständig zurückschreiben.

**Links können an mehreren Stellen liegen.** Ein "Musterbestellung"-Link kann gleichzeitig
im Footer-Menü und in der Ankündigungsleiste (`sections/header-group.json`) stehen. Beim
Umbenennen von Produkten beide prüfen.

## Bilder

**Produktbilder sind nicht pro Sprache umschaltbar.** Nur der Alt-Text ist übersetzbar.
Wer sprachabhängige Bilder braucht, hängt beide Sätze ans Produkt und filtert im Theme
nach `request.locale.iso_code` — mit Fallback, sonst bleibt die Galerie leer, wenn ein
Produkt nur einen Sprachsatz hat.

## Zugang

**Berechtigung fehlt mitten im Lauf.** Scope nachtragen reicht nicht — die App muss
**neu installiert** werden, sonst greift die Änderung nicht.

## Browser

**Seiten laden nicht oder Klicks wirken nicht.** Chrome drosselt Hintergrund-Tabs, und
der Shopify-Admin lädt dann minutenlang nicht. Tab in den Vordergrund holen. Prüfen lässt
sich das mit `document.visibilityState`.

## Die Skripte sind nicht auffindbar

Sind die Skills lokal nach `~/.claude/skills/` verlinkt statt über den Marketplace
installiert, liegt dort ein Symlink und kein Ordner. `find` folgt Symlinks im Standard
nicht und liefert nichts zurück — es sieht aus, als wäre der Skill nicht installiert.

Deshalb steht in allen Skills `find -L`. Wer den Pfad selbst sucht, muss das `-L`
mitnehmen:

```bash
find -L ~/.claude -type d -name shopify-design -path '*skills*' 2>/dev/null | head -1
```
