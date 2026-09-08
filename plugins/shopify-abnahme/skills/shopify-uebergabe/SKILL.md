---
name: shopify-uebergabe
description: Führt die Befunde aus UX-, CRO- und Rechtsprüfung zusammen, setzt um was maschinell geht, und erstellt die Übergabe-Checkliste für den Livegang. Nutze diesen Skill bei "Übergabe", "Shop live schalten", "was fehlt noch", "Abnahme" oder "Livegang-Checkliste".
---

# Übergabe

Du bringst zusammen, was die drei Prüfungen gefunden haben, setzt davon um, was ohne
Rückfrage entscheidbar ist, und schreibst auf, was übrig bleibt — sortiert danach, **wer**
es tun muss.

## Die wichtigste Regel: nichts als erledigt zählen, was nicht erledigt ist

Der Wert dieses Dokuments liegt darin, dass man ihm glauben kann. Ein Punkt gilt nur als
erledigt, wenn er nachweislich umgesetzt wurde — nicht, weil er umsetzbar aussah, nicht,
weil ein Skript ihn angefasst hat, und schon gar nicht, weil die Liste dann kürzer wird.

Ebenso: **ungeprüft ist nicht in Ordnung.** Fehlte eine Berechtigung, steht das so drin.

## Voraussetzung

Die drei Prüfungen sind gelaufen und es gibt `befunde/*.json`:

```
python3 <ux>/scripts/befund.py    --theme <id>
python3 <cro>/scripts/befund.py   --theme <id>
python3 <recht>/scripts/befund.py --theme <id>
```

Fehlt eine, sag das — eine Übergabe ohne Rechtsprüfung ist keine Übergabe.

## Ablauf

```bash
find ~/.claude -type d -name shopify-uebergabe -path '*skills*' 2>/dev/null | head -1
```

### Phase 1 — Umsetzen, was geht

```
python3 <pfad>/scripts/umsetzen.py --theme <id>
python3 <pfad>/scripts/umsetzen.py --theme <id> --setzen
```

Das Skript hat für einzelne Befunde einen echten Handgriff hinterlegt — Mehrwertsteuer-
Hinweis am Preis, Warenkorb als Einschub, Alt-Texte aus Produktname und Ansicht. Alles
andere bleibt liegen, auch wenn es im Befund als `auto` markiert war; das meldet es dann
ausdrücklich. Lieber ein offener Punkt zu viel als ein falsch abgehakter.

**Neue Handgriffe gehören ins Skript, nicht in den Chat.** Wenn du einen Befund von Hand
löst, den man automatisieren könnte, trag ihn in `HANDGRIFFE` ein. Sonst macht ihn beim
nächsten Shop wieder jemand von Hand.

### Phase 2 — Umsetzen, was nur du kannst

Für Befunde, die kein Skript abdeckt, die aber im Theme lösbar sind — fehlende Abschnitte,
Texte, Reihenfolgen — nutze `shopify-design`. Nach jeder Änderung den betroffenen Punkt in
der Befund-Datei auf `"erledigt": true` setzen und in `notiz` schreiben, **was** gemacht
wurde. Steht dort nur "umgesetzt", ist es später nicht nachvollziehbar.

**Nicht umsetzen, was eine Zusage an Käufer ist.** Lieferzeit, Versandkosten, Garantie,
Herstelleradresse, Wirksamkeitsangaben — die kommen vom Kunden. Ein plausibler Platzhalter
ist an dieser Stelle eine Falschangabe mit Anlauf.

### Phase 3 — Übergabe schreiben

```
python3 <pfad>/scripts/uebergabe.py --theme <id>
```

Schreibt `Uebergabe.md` in sechs Abschnitten:

1. **Blocker** — ohne das kein Livegang
2. **Beim Kunden** — Angaben, Texte, Fotos, Entscheidungen
3. **Von Hand im Admin** — technisch machbar, nicht über die Schnittstelle
4. **Immer vor dem Livegang** — Zahlung, Domain, Plan, Passwortschutz, Testbestellung,
   E-Mail-Vorlagen, Weiterleitungen, Analytics
5. **Erledigt** — mit dem, was tatsächlich gemacht wurde
6. **Nicht prüfbar** — fehlende Berechtigungen

### Phase 4 — Vorlegen

Veröffentliche `Uebergabe.md` als Artifact und gib den Link weiter. Fasse im Chat in
drei Sätzen zusammen: wie viele Blocker, was der Kunde liefern muss, was als Nächstes
ansteht.

**Sag die schlechte Nachricht zuerst.** Wenn der Shop in zwei Wochen live soll und noch
sechs Blocker offen sind, ist das der erste Satz — nicht der letzte.

> **Freigabe** — Übergabe abgenommen.

## Reihenfolge im Gesamtablauf

`shopify-settings` → `shopify-migration` → `shopify-design` → `shopify-ux` →
`shopify-cro` → `shopify-recht` → `shopify-uebergabe`.

Die drei Prüfungen laufen erst, wenn der Shop steht. Ein halbfertiger Shop erzeugt
Befunde, die sich beim Weiterbauen von selbst erledigen — das kostet nur Zeit.
