---
name: shopify-cro
description: Prüft einen fertig aufgebauten Shopify-Shop auf Verkaufspsychologie und Conversion-Optimierung. Nutze diesen Skill bei "CRO", "Conversion", "warum kauft niemand", "Verkaufspsychologie", "Shop optimieren" oder vor einer Übergabe.
---

# CRO-Prüfung

Du prüfst nicht, ob der Shop schön ist, sondern ob er die Fragen beantwortet, die zwischen
Interesse und Kauf stehen. Jede unbeantwortete Frage ist ein Abbruch.

## Die wichtigste Regel: Einwände statt Features

Die fünf Fragen, die jeder Käufer stellt, in dieser Reihenfolge:

1. **Bin ich hier richtig?** — beantwortet der erste Bildschirm
2. **Ist das das Richtige für mich?** — beantwortet die Produktseite
3. **Kann ich denen glauben?** — beantworten Bewertungen, Impressum, Zahlungsarten
4. **Was kostet es wirklich?** — beantworten Versandkosten und Lieferzeit, früh
5. **Was, wenn es nicht passt?** — beantwortet die Rückgabe

Geh den Shop entlang dieser fünf Fragen ab. Wo eine Frage erst im Checkout beantwortet
wird, ist sie zu spät beantwortet.

## So redest du

Jeder Befund nennt den Einwand, den er auflöst. "Bewertungen fehlen" ist schwach.
"Frage 3 bleibt offen: Es gibt nichts auf der Seite, das belegt, dass hier schon jemand
gekauft hat" ist ein Befund.

## Grundregeln

1. **Keine erfundenen Zahlen.** Kein "Nur noch 3 auf Lager", wenn das nicht stimmt. Kein
   Countdown, der beim Neuladen wieder von vorn beginnt. Kein Vergleichspreis, der nie
   gegolten hat — das ist irreführende Werbung, keine Optimierung.
2. **Keine Sozialbeweise, die es nicht gibt.** Bewertungen kommen von Käufern, nicht aus
   dem Textgenerator. Wenn es noch keine gibt, ist die Antwort ein ehrliches Argument,
   kein erfundener Stern.
3. **Erst messen, dann behaupten.** Ohne Daten sagst du "das ist ein bekannter Hebel",
   nicht "das bringt 20 % mehr Umsatz".
4. **Prüfen, nicht umbauen.** Umsetzung läuft über `shopify-abnahme`.

## Ablauf

```bash
find -L ~/.claude -type d -name shopify-cro -path '*skills*' 2>/dev/null | head -1
```

### Phase 1 — Das Zählbare

```
python3 <pfad>/scripts/befund.py --theme <id>
```

Produkte mit zu wenigen Bildern, leere Kategorien, fehlende Bewertungen, fehlende
Empfehlungen, Zahlungsicons, Newsletter, Versandversprechen, Warenkorb-Verhalten.
Schreibt `befunde/cro.json`.

### Phase 2 — Der Kaufweg

Leg ein Produkt in den Warenkorb und geh bis zum Checkout. Notiere an jeder Station, was
fehlt:

- **Startseite** — steht das Wertversprechen in einem Satz da, oder muss man es sich
  zusammensuchen? Sind Bestseller sichtbar oder erst nach dreimal Scrollen?
- **Kategorie** — kann man filtern, wonach die Zielgruppe entscheidet? Bei Kleidung
  Größe, bei Technik Leistung, bei Verbrauchsmaterial Menge.
- **Produktseite** — Untertitel mit dem Hauptnutzen? Verfügbarkeit am Button?
  Versandkosten am Button? Was ist im Lieferumfang?
- **Warenkorb** — sieht man den Weg zu versandkostenfrei? Gibt es eine Möglichkeit
  weiterzustöbern, ohne den Warenkorb zu verlieren?
- **Checkout** — wie viele Felder? Gastbestellung möglich?

### Phase 3 — Die Zielgruppe gegenlesen

Im Konzept steht, für wen der Shop ist. Lies die Startseite noch einmal mit dieser Person
im Kopf. Ein Shop für Betriebe braucht Mengenstaffeln, Rechnungskauf und Datenblätter.
Ein Shop für Privatkunden braucht Anwendung, Bilder und ein einfaches Rückgaberecht.
Derselbe Text kann für die eine Gruppe überzeugend und für die andere unbrauchbar sein.

### Phase 4 — Befund ergänzen

`befunde/durchgang-cro.json`, gleiche Form wie in `shopify-ux` beschrieben. Sortiere nach
Hebel, nicht nach Aufwand: Was löst den frühesten Einwand auf, kommt zuerst.

> **Freigabe** — Befund besprochen.

## Verkaufspsychologie im Detail

`references/verkaufspsychologie.md` — die Hebel, wann sie tragen und wann sie kippen.
