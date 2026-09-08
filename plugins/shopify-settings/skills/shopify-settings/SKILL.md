---
name: shopify-settings
description: Grundeinrichtung eines Shopify-Shops — prüft, was fehlt, setzt automatisierbare Einstellungen und führt durch den Rest. Nutze diesen Skill bei "Shop einrichten", "Grundeinstellungen", "Shop aufsetzen", "Was fehlt noch im Shop", "Versandkosten anlegen", "Richtlinien hinterlegen" oder vor einem Livegang.
---

# Grundeinrichtung Shopify

Du richtest den **Rahmen** eines Shops ein — nicht die Produkte. Die kommen danach mit
`shopify-migration`. Diese Reihenfolge ist wichtig: Stehen Metafelder, Versandzonen und
Pflichtangaben vorher, muss man sie nicht bei hunderten Produkten nachziehen.

## So redest du

Wie beim Migrations-Skill: **im Chat erklären, nicht auf Dateien verweisen.** Die Person
ist nicht technisch und soll nichts öffnen müssen. Ergebnisse übersetzt du in Klartext.
Sag immer, wo ihr steht.

## Grundregeln

1. **Rechtstexte werden nicht geschrieben.** Du prüfst, ob AGB, Widerruf, Datenschutz und
   Impressum vorhanden und vollständig wirken. Formulieren tut sie der Kunde, ein
   Fachanwalt oder ein Dienst wie die IT-Recht Kanzlei. Ein selbst geschriebener Widerruf
   ist ein Abmahnrisiko, kein Zeitgewinn.
2. **Versandkosten und Steuersätze werden nicht geschätzt.** Die kommen aus einer Quelle.
3. **Schreiben nur nach Freigabe.** Lesende Prüfungen jederzeit.
4. **Nichts anfassen, was nicht besprochen ist.** Einstellungen wirken sofort und global.

## Ablauf

Die Skripte liegen in `scripts/` neben dieser Datei. Ermittle den Pfad einmal:

```bash
find ~/.claude -type d -name shopify-settings -path '*skills*' 2>/dev/null | head -1
```

### Phase 1 — Zugang

Wie beim Migrations-Skill. **Dieser Skill braucht mehr Berechtigungen** — die vollständige
Liste steht in `references/berechtigungen.md`, sie deckt beide Skills ab. Fehlen welche,
laufen die Prüfungen trotzdem und melden konkret, was fehlt.

### Phase 2 — Bestandsaufnahme

```
python3 <pfad>/scripts/1_bestandsaufnahme.py
```

Prüft Stammdaten, Sichtbarkeit, Richtlinien, Versand, Sprachen, Märkte, Standorte,
Steuern und Metafelder. Schreibt `Einrichtungsstand.md`.

**Fasse im Chat zusammen**, sortiert nach Dringlichkeit. Trenne dabei drei Dinge:
was blockiert, was geprüft gehört, und was mangels Berechtigung unklar blieb.

Erfahrungsgemäß lohnt der Blick auf: Zeitzone (Dev-Shops stehen oft auf US-Zeit),
Shop-Adresse (steht oft noch auf der Agentur), Versandtarife (ohne Tarif kann niemand
bestellen), fehlende Richtlinien.

> **Freigabe 1** — Befund besprochen, Reihenfolge festgelegt.

### Phase 3 — Rechtliches

Fehlende Richtlinien anfordern, nicht schreiben. Liegen Texte vor, spielst du sie ein:

```
python3 <pfad>/scripts/2_richtlinien.py --datei agb.html --typ TERMS_OF_SERVICE
```

Danach in der Storefront prüfen, ob die Seiten erreichbar und im Footer verlinkt sind.

### Phase 4 — Versand

Versandzonen und Tarife brauchen konkrete Werte vom Kunden: welche Länder, welcher Preis,
ab welchem Warenwert versandkostenfrei. Ohne diese Angaben nicht anlegen.

### Phase 5 — Sprachen, Märkte, Metafelder

Metafeld-Definitionen **vor** der Produktmigration anlegen — sonst fehlen sie später bei
allen Produkten. Achte auf `PUBLIC_READ`, sonst sind sie im Theme unsichtbar.

### Phase 6 — Was nur von Hand geht

Zahlungen, Domain, Checkout, Kundenkonten, E-Mail-Vorlagen, Plan. Führe die Person durch
den Shop-Admin. Wenn der Browser zur Verfügung steht, kannst du Formulare selbst ausfüllen
— lies dafür `references/browser-einstellungen.md`, dort stehen die Besonderheiten des
Shopify-Admins.

**Zahlungsanbieter richtest du nie selbst ein.** Dort werden Bankdaten und Ausweise
verlangt.

> **Freigabe 2** — Checkliste abgearbeitet.

### Phase 7 — Abschluss

Bestandsaufnahme erneut laufen lassen und mit dem ersten Lauf vergleichen. Was ist
erledigt, was bleibt offen, was liegt beim Kunden.

## Wenn etwas hakt

`references/fallen.md` lesen.
