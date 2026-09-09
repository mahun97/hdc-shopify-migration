---
name: shopify-recht
description: Prüft einen Shopify-Shop auf die Pflichtangaben eines deutschen Onlineshops. Nutze diesen Skill bei "rechtlich prüfen", "Abmahnung", "Pflichtangaben", "Impressum", "GPSR", "Grundpreis", "DSGVO" oder vor einem Livegang.
---

# Rechtliche Prüfung

Du stellst fest, **ob** die Pflichtangaben da sind. Du beurteilst nicht, ob ihr Text
trägt, und du schreibst sie nicht.

## Die wichtigste Regel: keine Rechtsberatung

Du bist kein Anwalt und gibst keine Rechtsauskunft. Was du tust:

- prüfen, ob eine Pflichtangabe vorhanden ist
- benennen, welche Vorschrift sie verlangt
- sagen, wer sie liefern muss

Was du nicht tust: AGB, Widerruf, Datenschutzerklärung oder Impressum formulieren, auch
nicht "als Entwurf". Ein selbst geschriebener Widerruf ist ein Abmahnrisiko, kein
Zeitgewinn. Der Text kommt vom Kunden, von seinem Anwalt oder von einem Dienst wie der
IT-Recht Kanzlei.

Sag das offen, wenn danach gefragt wird. Nicht als Ausrede, sondern mit dem nächsten
Schritt: welcher Text fehlt, wer ihn beschafft, wie lange das dauert.

## Grundregeln

1. **Ungeprüft ist nicht in Ordnung.** Fehlt eine Berechtigung, ist der Punkt *unbekannt*
   und wandert als solcher in die Übergabe. Nie stillschweigend abhaken.
2. **Rechtliche Blocker sind keine Empfehlungen.** Sie stehen in der Übergabe unter
   Blocker, nicht unter "wäre schön".
3. **Werbeaussagen sind Teil der Prüfung.** Gesundheits-, Bio-, Wirksamkeits- und
   Nachhaltigkeitsaussagen sind eigene Rechtsgebiete. Steht "wirkt gegen 99,9 % der
   Viren" im Text, ist die Frage nicht, ob es stimmt, sondern ob es belegt und zulässig ist.

## Ablauf

```bash
find -L ~/.claude -type d -name shopify-recht -path '*skills*' 2>/dev/null | head -1
```

### Phase 1 — Pflichtangaben

```
python3 <pfad>/scripts/befund.py --theme <id>
```

Prüft: AGB, Widerruf, Datenschutz, Impressum; Mehrwertsteuer- und Versandkostenhinweis am
Preis; Grundpreis nach PAngV; Metafelder für Herstellerangaben nach GPSR;
Cookie-Einwilligung; Versandtarife; Rechtstexte in allen veröffentlichten Sprachen.
Schreibt `befunde/recht.json`.

Fehlende Berechtigungen landen unter `unklar` und tauchen in der Übergabe als *ungeprüft*
auf. Die Liste der nötigen Rechte steht in `shopify-settings/references/berechtigungen.md`.

### Phase 2 — Im Shop nachsehen

Was kein Skript sieht:

- Sind die Rechtstexte **im Footer verlinkt** und ohne Anmeldung erreichbar?
- Steht der Widerruf **vor** dem Kaufabschluss zur Verfügung, nicht erst in der Mail?
- Erscheint das **Cookie-Banner vor** dem Setzen der Cookies — und funktioniert "Ablehnen"?
- Steht der **Preis mit Mehrwertsteuer** an jeder Stelle, an der ein Preis steht — auch in
  der Kategorieübersicht und im Warenkorb?
- Sind bei Produkten mit Füllmenge **Grundpreise** sichtbar?
- Bei Biozid-, Lebensmittel-, Kosmetik- oder Elektroprodukten: die branchenspezifischen
  Pflichtangaben. Die kennt der Kunde, nicht das Theme.

### Phase 3 — Texte gegenlesen

Geh die Produkttexte auf Aussagen durch, die belegt sein müssen. Markiere sie, statt sie
zu löschen — die Entscheidung trifft der Kunde mit seinem Anwalt.

### Phase 4 — Befund ergänzen

`befunde/durchgang-recht.json`. Alles Rechtliche, das den Verkauf betrifft, ist
`blocker` — nicht `wichtig`.

> **Freigabe** — Befund besprochen und an den Kunden weitergegeben.

## Nachschlagen

`references/pflichtangaben.md` — was verlangt wird, woher es kommt, wer es liefert.
