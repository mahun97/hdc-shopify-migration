# Pflichtangaben eines deutschen Onlineshops

Diese Übersicht sagt, **was verlangt wird und wer es liefert**. Sie ist keine
Rechtsberatung und ersetzt keine anwaltliche Prüfung. Stand: September 2026 — bei jedem
Projekt gegenprüfen, das Gebiet ändert sich.

## Die vier Texte

| Text | Grundlage | Wer liefert |
|---|---|---|
| Impressum | § 5 DDG | Kunde — Angaben aus dem Handelsregister |
| Datenschutzerklärung | Art. 13 DSGVO | Anwalt / IT-Recht Kanzlei, abhängig von den eingesetzten Tools |
| AGB | freiwillig, praktisch nötig | Anwalt / IT-Recht Kanzlei |
| Widerrufsbelehrung + Muster-Widerrufsformular | § 312g, § 355 BGB, Art. 246a EGBGB | Anwalt / IT-Recht Kanzlei |

**Niemals selbst formulieren.** Auch nicht als Entwurf, auch nicht "nur zum Testen" — ein
Platzhaltertext, der live geht, ist genau der Fall, den die Abmahnung trifft.

Im Shop liegen sie als **Richtlinien** (Einstellungen → Richtlinien), nicht als Seiten.
Nur dann verlinkt Shopify sie automatisch im Checkout. Das Impressum ist die Ausnahme —
es darf auch eine Seite sein, muss aber von jeder Seite aus in zwei Klicks erreichbar sein.

## Preise

**Endpreis.** Jeder Preis enthält die Umsatzsteuer und wird als solcher gekennzeichnet,
mit Hinweis auf zusätzliche Versandkosten und einem Link dorthin. An **jeder** Stelle, an
der ein Preis steht — Kategorie, Produktseite, Warenkorb. In Horizon: `show_tax_info` im
price-Block.

**Grundpreis** (§ 4 PAngV). Bei Waren nach Volumen, Gewicht, Länge oder Fläche zusätzlich
der Preis je Liter, Kilogramm, Meter oder Quadratmeter. In Shopify je Variante unter
„Grundpreis". Betrifft fast alle Flüssigkeiten, Pulver, Folien, Kabel, Stoffe.

**Streichpreise** (§ 11 PAngV). Der durchgestrichene Preis muss der **niedrigste der
letzten 30 Tage** sein. Ein zum Start gesetzter Fantasie-Vorpreis ist irreführende Werbung.

## Bestellprozess

**Button-Beschriftung** (§ 312j BGB): „zahlungspflichtig bestellen" oder gleich eindeutig.
Shopify setzt das im Standard-Checkout selbst. Bei angepasstem Checkout oder eigener
Sprachdatei nachsehen.

**Bestellübersicht** vor dem Absenden: Ware, Gesamtpreis, Versandkosten, Steuern.

## Produktsicherheit (GPSR)

Seit Dezember 2024 verlangt die EU-Produktsicherheitsverordnung **vor dem Kauf sichtbar**:

- Name, eingetragener Handelsname und Anschrift des Herstellers, plus E-Mail oder Website
- dieselben Angaben zur verantwortlichen Person in der EU, wenn der Hersteller außerhalb sitzt
- Angaben zur Identifikation des Produkts (Bild, Typ, Chargen- oder Seriennummer)
- Warnhinweise und Sicherheitsinformationen in deutscher Sprache

Umsetzung: Metafeld-Definitionen je Produkt anlegen, Daten **beim Kunden erfragen**, im
Theme ausgeben. Recherchierte Adressen immer mit Quelle vorlegen und bestätigen lassen —
eine falsche Herstelleradresse ist schlimmer als eine fehlende.

## Cookies und Einwilligung

§ 25 TDDDG: Einwilligung **vor** dem Setzen nicht notwendiger Cookies. Praktisch heißt
das: Consent-Tool, das Google Analytics, Meta Pixel und Co. blockiert, bis zugestimmt
wurde. „Ablehnen" muss genauso leicht erreichbar sein wie „Akzeptieren". Nachweisbar
protokolliert.

Ein Banner, das nur informiert, aber nichts blockiert, erfüllt die Anforderung nicht.

## Steuern

Umsatzsteuer-Identifikationsnummer hinterlegen. Kleinunternehmerregelung oder OSS
auswählen — falsch gesetzt rechnet der Shop mit 0 % und die Differenz zahlt der Kunde
später aus eigener Tasche. Bei Steuerregistrierungen im EU-Ausland gehört immer der Kunde
selbst eingetragen.

## Branchenspezifisch

Diese Liste ist nicht vollständig, und genau das ist der Punkt: Für Biozide, Lebensmittel,
Nahrungsergänzung, Kosmetik, Spielzeug, Elektro (WEEE, Batterien, Verpackungsregister),
Textilien und Möbel gelten eigene Kennzeichnungspflichten. **Frag den Kunden, welche
Vorschriften für sein Sortiment gelten** — er kennt sie, das Theme nicht.

## Werbeaussagen

Wirksamkeit, Gesundheit, Bio, Nachhaltigkeit, Klimaneutralität: jeweils eigene
Rechtsgebiete mit eigenen Belegpflichten. Steht so etwas im Text, markieren und dem Kunden
vorlegen — nicht löschen, nicht abschwächen, nicht selbst entscheiden.
