# HDC Claude-Plugins

Marketplace für Claude-Code-Plugins von HDC Digital.

## Für Mitarbeiter: einmalig einrichten

Im Terminal `claude` starten und nacheinander eingeben:

```
/plugin marketplace add mahun97/hdc-shopify-migration
```

```
/plugin install shopify-migration@hdc-digital
```

Danach in Claude Code neu starten oder `/reload-plugins` ausführen.

Das war's. Das Plugin steht ab jetzt in **jedem** Projektordner zur Verfügung.

> Voraussetzung: Du hast Zugriff auf das GitHub-Repo und bist eingeloggt —
> einmalig mit `gh auth login`.

## Benutzen

Terminal im Kundenordner öffnen, `claude` starten und schreiben:

> Ich möchte Produkte in einen Shopify-Shop migrieren.

Claude führt dich durch alle sieben Phasen. Du musst keine Dateien öffnen
und keine Befehle tippen.

Alternativ direkt aufrufen: `/shopify-migration:shopify-migration`

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
| `shopify-migration` | Produktmigration in einen Shopify-Shop — sieben Phasen, fünf Freigaben |

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
