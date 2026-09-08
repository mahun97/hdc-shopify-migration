# Referenz: Zugang einrichten

*Für Claude: Gib die Schritte im Chat wieder, einen nach dem anderen. Verweise die Person
nicht auf diese Datei. Kläre ZUERST, welcher der beiden Wege gilt — sie unterscheiden sich
grundlegend. Die Person legt die App selbst an; du erzeugst weder App noch Token.*

---

## Welcher Weg gilt?

Es gibt zwei Arten von Apps. **Frage zuerst, wo die Person die App anlegt:**

| | Weg A — App im Shop-Admin | Weg B — App im Partner Dashboard |
|---|---|---|
| Wo | Shop-Admin → Einstellungen → Apps | partners.shopify.com |
| Erkennungsmerkmal | kein Feld für Weiterleitungs-URL | verlangt **Weiterleitungs-URL** |
| Token | direkt im Admin ablesbar | nur über OAuth-Ablauf |
| Aufwand | ~5 Minuten | ~15 Minuten |

**Empfehle immer Weg A**, wenn er möglich ist. Wenn die Person ein Feld
„Zulässige Weiterleitungs-URL(s)" vor sich hat, ist sie auf Weg B.

---

# Weg A — Custom App im Shop-Admin

## 1 · App anlegen

Im Shop-Admin: **Einstellungen → Apps und Vertriebskanäle → Apps entwickeln → App erstellen**

Name frei wählbar, etwa `HDC Migration`.

Fehlt der Punkt „Apps entwickeln", hat der Shop-Inhaber die Custom-App-Entwicklung nicht
freigegeben — dann entweder freischalten lassen oder Weg B nehmen.

## 2 · Berechtigungen setzen

**Admin API-Integration konfigurieren** anklicken und diese Liste vollständig einfügen:

```
read_products,write_products,
read_files,write_files,
read_inventory,write_inventory,
read_publications,write_publications,
read_themes,write_themes,write_theme_code,
read_translations,write_translations,
read_online_store_navigation,write_online_store_navigation,
read_content,write_content,
read_legal_policies,write_legal_policies,
read_shipping,write_shipping,
read_locales,write_locales,
read_markets,write_markets,
read_locations,write_locations,
read_product_listings
```

Diese Liste deckt **beide** Skills ab — Grundeinrichtung und Produktmigration. Einmal
vollständig setzen erspart mehrfaches Neuinstallieren der App.

Warum vollständig: Bilder brauchen `files`, das Veröffentlichen `publications`,
Pflichtangaben und Tabs sitzen im Theme, Untermenüs in der Navigation. Wer kürzt, merkt es
mitten im Import — und muss die App neu installieren.

Speichern.

## 3 · Installieren und Token holen

Oben rechts **Installieren**, dann Reiter **API-Zugangsdaten** →
**Admin API-Zugriffstoken** anzeigen. Beginnt mit `shpat_`, wird **nur einmal** angezeigt.

Weiter bei „Token ablegen".

---

# Weg B — App im Partner Dashboard

Hier gibt es keinen „Token anzeigen"-Knopf. Das Token entsteht über einen OAuth-Ablauf,
den man einmal von Hand durchspielt.

## 1 · App konfigurieren

Im Dev Dashboard unter **API-Zugriff**:

- **Bereiche**: die Berechtigungsliste aus Weg A, Schritt 2
- **Zulässige Weiterleitungs-URL(s)**: `https://localhost:8001/callback`

Dort läuft nichts — die Adresse muss nur eingetragen sein, damit Shopify die Weiterleitung
zulässt.

## 2 · App freigeben

Zwei Dinge müssen erledigt sein, sonst erscheint der Freigabe-Bildschirm gar nicht:

- die **App-Version ist released**
- **Custom Distribution** ist auf den Zielshop freigegeben

## 3 · Freigabe im Browser erteilen

Diese Adresse aufrufen, mit eingesetzter Shop-Domain und Client-ID:

```
https://DEINSHOP.myshopify.com/admin/oauth/authorize?client_id=DEINE_CLIENT_ID&scope=read_products,write_products,read_files,write_files,read_inventory,write_inventory,read_publications,write_publications,read_themes,write_themes,write_theme_code,read_translations,write_translations,read_online_store_navigation,write_online_store_navigation,read_content,write_content,read_locales,read_markets,read_product_listings&redirect_uri=https://localhost:8001/callback&state=setup
```

Shopify zeigt den Freigabe-Bildschirm → **Installieren**.

## 4 · Code aus der Adresszeile holen

Der Browser meldet „Verbindung fehlgeschlagen" — das ist erwartet, dort läuft kein Server.
Entscheidend ist die Adresszeile:

```
https://localhost:8001/callback?code=DER_TEIL_DEN_DU_BRAUCHST&hmac=…&shop=…
```

Nur den Wert von `code` kopieren.

**Der Code ist einmalig und lebt nur wenige Minuten.** Bei `invalid_request` einfach die
Adresse aus Schritt 3 erneut aufrufen und einen frischen Code holen.

## 5 · Code gegen Token tauschen

Das Secret **zuerst in eine Umgebungsvariable**, damit es nicht in der Shell-History landet:

```bash
export SHOPIFY_SECRET='shpss_DEIN_SECRET'
```

Dann — **in einer Zeile**, ohne Zeilenumbrüche:

```bash
curl -X POST https://DEINSHOP.myshopify.com/admin/oauth/access_token -H 'Content-Type: application/x-www-form-urlencoded' -d 'client_id=DEINE_CLIENT_ID' -d "client_secret=$SHOPIFY_SECRET" -d 'code=DEIN_CODE' -d 'expiring=0'
```

Antwort:

```json
{ "access_token": "shpat_…", "scope": "read_products,write_products,…" }
```

Der Wert von `access_token` ist das Token.

`expiring=0` sorgt dafür, dass es nicht abläuft.

**Häufiger Fehler:** Kopiert man den Befehl mehrzeilig mit `\`, hängt oft ein Leerzeichen
hinter dem Backslash — dann führt die Shell jede Zeile einzeln aus und curl meldet
`411 Length Required`. Deshalb hier bewusst einzeilig.

---

# Token ablegen (beide Wege)

```bash
printf 'SHOP=DEINSHOP.myshopify.com\nTOKEN=shpat_DEIN_TOKEN\n' > ~/.config/shopify-<kunde>.env && chmod 600 ~/.config/shopify-<kunde>.env
```

`chmod 600` heißt: nur du kannst die Datei lesen.

## Sicherheitsregeln

- **Token und Client Secret nie in den Chat**, nie in eine Mail, nie ins Ticket,
  nie auf einen Screenshot. Claude liest die Datei selbst.
- **Das Secret nie in eine Browser-Adresse** — es landet sonst in History und Server-Logs.
- Ist ein Secret doch einmal sichtbar geworden: **im Dev Dashboard rotieren.**
  Achtung, das macht alle damit erzeugten Tokens ungültig — der Zugang muss danach
  neu geholt werden.

## Prüfen

Sobald die Datei liegt: Token testen und Berechtigungen abgleichen. Fehlende konkret
benennen, nicht nur „unvollständig".

## Wenn Berechtigungen fehlen

Nachtragen reicht nicht — **die App muss neu installiert werden**, sonst greift die
Änderung nicht. Bei Weg B heißt das: Schritte 3 bis 5 erneut durchlaufen.
