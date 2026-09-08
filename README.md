# HDC Claude-Plugins

Marketplace für Claude-Code-Plugins von HDC Digital.

## Für Mitarbeiter: einmalig einrichten

Im Terminal `claude` starten und nacheinander eingeben:

```
/plugin marketplace add mahun97/hdc-shopify-migration
```

```
/plugin install shopify-settings@hdc-digital
```

```
/plugin install shopify-migration@hdc-digital
```

Danach in Claude Code neu starten oder `/reload-plugins` ausführen.

Das war's. Das Plugin steht ab jetzt in **jedem** Projektordner zur Verfügung.

> Voraussetzung: Du hast Zugriff auf das GitHub-Repo und bist eingeloggt —
> einmalig mit `gh auth login`.

## Benutzen

Terminal im Kundenordner öffnen, `claude` starten und schreiben — je nachdem,
was ansteht:

> Ich möchte einen Shopify-Shop einrichten.

> Ich möchte Produkte in einen Shopify-Shop migrieren.

Claude führt dich durch alle Phasen. Du musst keine Dateien öffnen und keine
Befehle tippen.

**Reihenfolge:** erst die Grundeinrichtung, dann die Produkte. Stehen Metafelder,
Versandzonen und Pflichtangaben vorher, muss man sie nicht bei hunderten Produkten
nachziehen.

## Updates

Kommen automatisch. Manuell erzwingen:

```
/plugin marketplace update hdc-digital
```

Falls die automatische Aktualisierung bei diesem privaten Repo scheitert, einmalig
in der Shell setzen:

```bash
export CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1
```

## Enthaltene Plugins

| Plugin | Zweck |
|---|---|
| `shopify-settings` | Grundeinrichtung — prüft, was fehlt, und richtet ein, was automatisierbar ist |
| `shopify-migration` | Produktmigration — sieben Phasen, fünf Freigaben |

## Für Entwickler: Änderungen einspielen

Lokal testen, ohne zu installieren:

```bash
claude --plugin-dir ~/Documents/hdc-shopify-migration/plugins/shopify-migration
```

Prüfen und veröffentlichen:

```bash
claude plugin validate ~/Documents/hdc-shopify-migration/plugins/shopify-migration
git add -A && git commit -m "Was geändert wurde" && git push
```

Die Mitarbeiter bekommen die Änderung beim nächsten Marketplace-Abgleich.
Eine Version muss dafür nicht hochgezählt werden — ohne `version`-Feld gilt der
Commit-Stand als Version.

## Aufbau

```
hdc-shopify-migration/
├── .claude-plugin/marketplace.json      Marketplace-Definition
└── plugins/shopify-migration/
    ├── .claude-plugin/plugin.json       Plugin-Manifest
    └── skills/shopify-migration/
        ├── SKILL.md                     führt das Gespräch
        ├── references/                  Claude liest, gibt im Chat wieder
        └── scripts/                     die Werkzeuge
```
