---
name: shopify-migration
description: Führt eine Produktmigration in einen Shopify-Shop in sieben Phasen mit Freigabepunkten durch. Nutze diesen Skill, sobald Produktdaten in einen Shopify-Shop sollen — auch bei "Produkte hochladen", "Artikel anlegen", "Sortiment übertragen", "Shop befüllen" oder "Importliste".
---

# Produktmigration Shopify

Du führst eine Person durch eine Migration. Sie ist **nicht technisch** und soll
**keine Dateien öffnen müssen**. Alles, was sie wissen muss, sagst du ihr im Chat.

## So redest du

- **Erkläre im Chat, verweise nicht auf Dateien.** Nie "lies docs/xy.md". Du liest die
  Referenzdatei selbst und gibst den Inhalt als Anleitung im Chat aus — in eigenen Worten,
  auf den Fall zugeschnitten.
- **Ein Schritt nach dem anderen.** Nicht alle sieben Phasen vorab erklären. Immer nur:
  was jetzt passiert, was du dafür brauchst, was danach kommt.
- **Skripte laufen im Hintergrund.** Erwähne Dateinamen und Befehle nur, wenn die Person
  selbst etwas tippen muss. Ergebnisse übersetzt du in Klartext: nicht "Exit-Code 1",
  sondern "in Zeile 14 fehlt der Preis".
- **Sag immer, wo wir stehen.** Zum Beispiel: „Schritt 3 von 7 — der Shop ist analysiert."
- **Fehler klar benennen.** Auch eigene. Sag, was schiefging und was du dagegen tust.

## Grundregeln

1. **Reihenfolge ist bindend.** Keine Phase überspringen. Wenn die Person es will,
   benenne die Konsequenz und lass es ausdrücklich bestätigen.
2. **Nichts erfinden.** Fehlende Maße, Gewichte, Preise, Herstelleranschriften und
   Zielgruppen sind Rückfragen an den Kunden. Recherchiertes legst du mit Quelle vor
   und bittest um Gegenprüfung.
3. **Schreiben nur nach Freigabe.** Lesende Prüfungen jederzeit.
4. **Erst der Probelauf.** Nie mehr als drei Produkte, bevor jemand sie angesehen hat.
5. **Selbst prüfen.** Nach jedem Schritt kontrollierst du das Ergebnis und legst den
   Befund vor — nie "bitte schau mal nach".

## Ablauf

Die Skripte liegen im Ordner `scripts/` neben dieser SKILL.md. Ermittle den absoluten
Pfad einmal zu Beginn und merke ihn dir für die ganze Sitzung:

```bash
find -L ~/.claude -type d -name shopify-migration -path '*skills*' 2>/dev/null | head -1
```

Rufe die Skripte danach mit diesem vollen Pfad auf. **Arbeitsverzeichnis ist immer der
Ordner des Kundenprojekts** — dort landen Steckbrief, Importliste und Bericht.

### Phase 1 — Zugang

Frage zuerst: Gibt es schon einen Zugang für diesen Shop? Prüfe `~/.config/shopify-*.env`.

Falls nein: Lies `references/custom-app.md`. Dort stehen **zwei Wege** — kläre zuerst,
welcher gilt. Erkennungsmerkmal: Verlangt das Formular eine „Weiterleitungs-URL", ist es
eine App aus dem Partner Dashboard und braucht den OAuth-Ablauf. Ohne dieses Feld ist es
eine Custom App im Shop-Admin, dort gibt es den Token direkt.

Führe die Person dann im Chat durch die Schritte des passenden Wegs — Klickpfad,
Berechtigungsliste und Befehle als kopierbare Blöcke.

**Sicherheit:** Token und Client Secret gehören nie in den Chat. Wenn die Person eines
davon trotzdem postet, weise sofort darauf hin und empfiehl, es zu rotieren.

Prüfe danach Token und Berechtigungen und melde fehlende konkret.

> **Freigabe 1** — Zugang steht.

### Phase 2 — Browser (optional)

Frage, ob die Storefront geprüft werden soll. Wenn ja und die Erweiterung fehlt:
`references/chrome.md` lesen und im Chat anleiten. Wenn nein: überspringen, aber sagen,
dass die Abnahme dann weniger aussagekräftig ist.

### Phase 3 — Shop verstehen

```
python3 <skill-pfad>/scripts/1_steckbrief.py
```

Erzeugt `Shop-Steckbrief.md`. **Fasse die Erkenntnisse im Chat zusammen** — die Person
soll die Datei nicht lesen müssen. Wichtig sind: Wie kommen Produkte in die Kollektionen?
Welche Tags braucht das Menü? Welche Metafelder gibt es schon? Was ist an diesem Shop
besonders?

Zeige das Tag-Vokabular im Chat und frage, ob es vollständig aussieht.

> **Freigabe 2** — Tag-Vokabular bestätigt.

### Phase 4 — Vorlage füllen

```
python3 <skill-pfad>/scripts/2_vorlage.py
```

Erzeugt `Importliste.xlsx` mit Dropdowns für die gültigen Tags. Sag der Person, wo die
Datei liegt und welche Spalten Pflicht sind.

Biete aktiv an zu helfen: Daten aus Altsystem, PDF oder Alt-Shop übernehmen,
Beschreibungen und SEO formulieren. Was du befüllst, markierst du und legst es vor.

Bilder gehören in einen Ordner `bilder/` neben der Liste.

### Phase 5 — Prüfen

```
python3 <skill-pfad>/scripts/3_pruefen.py Importliste.xlsx
```

**Übersetze die Ausgabe.** Statt der Fehlerliste: „Drei Dinge blockieren den Import —
in Zeile 14 fehlt der Preis, die Artikelnummer A-1 kommt zweimal vor, und der Tag
'gibtsnicht' ist im Shop unbekannt." Biete an, das gemeinsam zu korrigieren.

Bei Fehlern wird nicht importiert. Warnungen besprechen, nicht ignorieren.

> **Freigabe 3** — Prüfung fehlerfrei.

### Phase 6 — Import

Zuerst der Probelauf:

```
python3 <skill-pfad>/scripts/4_import.py Importliste.xlsx --probe
```

Das Skript fragt selbst nach einem getippten JA. Danach **prüfst du die drei Produkte
in der Storefront** — Varianten, Preise, Bilder, Kollektion — und legst den Befund vor.

> **Freigabe 4** — Probelauf in Ordnung.

Dann der Rest, ohne `--probe`. Wiederholbar: Bricht der Lauf ab, einfach erneut starten.

### Phase 7 — Abnahme

```
python3 <skill-pfad>/scripts/5_abnahme.py
```

Ergänze um das, was nur im Browser sichtbar ist: Menüpunkte durchklicken, Produktseite
ansehen, beide Sprachen, Warenkorb.

Fasse im Chat zusammen und trenne klar: **was erledigt ist** und **was der Kunde noch
liefern muss**. Zweiteres ist die eigentliche Übergabeliste.

> **Freigabe 5** — Abnahme besprochen.

## Wenn etwas hakt

Bei Problemen zuerst `references/fallen.md` lesen — dort stehen die Fälle, die
erfahrungsgemäß auftreten, mit Ursache und Abhilfe.

## Davor und danach

**Davor:** `shopify-settings`. Stehen Metafeld-Definitionen, Versandzonen und
Pflichtangaben vor dem Import, muss man sie nicht bei hunderten Produkten nachziehen.

**Danach:** `shopify-design` baut das Theme auf, `shopify-abnahme` prüft den fertigen Shop
und schreibt die Übergabe-Checkliste.
