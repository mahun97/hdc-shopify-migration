# Zugangsschlüssel ablegen

Für dieses Kit braucht jeder Rechner zwei Sorten Schlüssel. Beide liegen in Dateien unter
`~/.config/`, nie im Chat.

| Schlüssel | Datei | Wofür |
|---|---|---|
| Shopify-Token, je Kunde | `~/.config/shopify-<kunde>.env` | Alles, was im Shop passiert |
| OpenAI-Plattform-Schlüssel, einmal | `~/.config/openai.env` | Bildmotive erzeugen |

## Die Regel

**Kein Schlüssel wandert durch den Chat.** Nicht ins Gespräch mit Claude, nicht in eine
E-Mail, nicht in ein Ticket, auf keinen Screenshot. Claude liest die Datei selbst — es
braucht den Wert nie zu sehen.

Der Grund ist unspektakulär: Chatverläufe werden weitergeleitet, Screenshots landen in
Slack, Tickets werden exportiert. Ein Schlüssel, der einmal in einem dieser Kanäle war,
gilt als kompromittiert und muss rotiert werden — mitsamt allem, was daran hängt.

**Claude erzeugt die Schlüssel nicht.** Das macht ein Mensch im jeweiligen Dashboard.

## OpenAI-Plattform-Schlüssel

Einmalig je Rechner, gilt für alle Kunden.

1. [platform.openai.com/api-keys](https://platform.openai.com/api-keys) öffnen, mit dem
   HDC-Konto anmelden
2. **Create new secret key**, Name z. B. `claude-code-<dein-name>` — ein eigener Schlüssel
   je Mitarbeiter, damit man ihn einzeln sperren kann, ohne alle anderen zu treffen
3. Schlüssel **einmal** kopieren. Er wird danach nie wieder angezeigt
4. Im Terminal ablegen, den Platzhalter ersetzen:

```bash
printf 'KEY=sk-DEIN_SCHLUESSEL\n' > ~/.config/openai.env && chmod 600 ~/.config/openai.env
```

5. Prüfen — das kostet nichts:

```bash
python3 scripts/8b_bild_erzeugen.py --schluessel-pruefen
```

Erwartete Ausgabe: `ok  Schlüssel gültig, gpt-image-2 freigeschaltet.`

### Wenn die Prüfung meckert

| Meldung | Ursache | Lösung |
|---|---|---|
| `401` | Schlüssel falsch kopiert oder widerrufen | Neu erzeugen, Schritt 3–4 wiederholen |
| `403` / `404` | Organisation nicht verifiziert | Im OpenAI-Dashboard unter Settings → Organization die Verifizierung abschließen. Die Bildmodelle setzen sie voraus |

### Welche Modelle der Schlüssel kann

```bash
curl -sS https://api.openai.com/v1/models -H "Authorization: Bearer $(grep ^KEY= ~/.config/openai.env | cut -d= -f2-)" \
  | python3 -c "import json,sys; [print(' ', x['id']) for x in sorted(json.load(sys.stdin)['data'], key=lambda m: m['id']) if 'image' in x['id']]"
```

Stand September 2026: `gpt-image-2`, `gpt-image-2-2026-04-21`, `gpt-image-1.5`,
`gpt-image-1`, `gpt-image-1-mini`, `chatgpt-image-latest`. Standard im Kit ist
`gpt-image-2` — nur das kann freie Bildgrößen.
| Datei fehlt | Schritt 4 übersprungen | Das Skript druckt die Anleitung selbst |

## Shopify-Token

Je Kunde einer. Der Weg zur Custom App steht in
`shopify-migration/references/custom-app.md`, die nötigen Berechtigungen in
`shopify-settings/references/berechtigungen.md`.

```bash
printf 'SHOP=kunde-xxxx.myshopify.com\nTOKEN=shpat_DEIN_TOKEN\n' > ~/.config/shopify-kunde.env
chmod 600 ~/.config/shopify-kunde.env
```

## Kosten

Der Shopify-Token kostet nichts. Der OpenAI-Schlüssel rechnet **je erzeugtem Bild** ab.
Das Skript gibt nach jedem Lauf die abgerechneten Token aus — danach hat man echte Zahlen
statt einer Schätzung. Vor einer Serie erst ein Bild erzeugen, ansehen, dann den Rest.
