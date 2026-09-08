# Referenz: Claude in Chrome

*Für Claude: Im Chat wiedergeben, nicht auf diese Datei verweisen.*

Für den Datenteil der Migration reicht der API-Zugang aus Phase 1.
Die Browser-Erweiterung brauchst du, wenn Claude die **Storefront ansehen** soll:
Menüpunkte durchklicken, Produktseiten prüfen, den Warenkorb testen, das Altsystem auslesen.

Empfehlung: einrichten. Der Abnahmelauf in Phase 7 ist damit deutlich aussagekräftiger,
weil Claude sieht, was der Kunde sieht — statt nur, was in der Datenbank steht.

## Installation

1. Erweiterung installieren:
   https://chromewebstore.google.com/detail/fcoeoabgfenejglbffodgkkbkcdhcgfn
2. In Chrome die Claude-Seitenleiste öffnen und **mit demselben Konto anmelden**,
   mit dem du auch Claude Code nutzt.

## Wichtig beim Arbeiten

**Der Tab muss im Vordergrund sein.** Chrome drosselt Hintergrund-Tabs, und der
Shopify-Admin lädt dann minutenlang nicht oder reagiert nicht auf Klicks. Wenn Claude
meldet, eine Seite lade nicht: Tab anklicken und das Fenster aktiv lassen.

**Passwortgeschützte Dev-Shops** sind für Claude erreichbar, solange du in diesem Chrome
am Shop angemeldet bist.

## Was Claude im Browser nicht tun darf

- Passwörter oder Zahlungsdaten eingeben
- Bestellungen abschließen
- Einstellungen ändern, die nicht abgesprochen sind

Wenn ein Schritt das erfordert, macht Claude ihn nicht selbst, sondern sagt dir, was zu tun ist.
