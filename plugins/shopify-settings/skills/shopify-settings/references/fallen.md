# Bekannte Fallen bei der Grundeinrichtung

**Zeitzone steht auf US-Zeit.** Development-Stores werden oft mit `America/New_York`
angelegt. Betrifft Bestellzeitstempel, Berichte und zeitgesteuerte Automatisierungen.
Vor Livegang prüfen.

**Shop-Adresse ist die der Agentur.** Bei Dev-Stores häufig — sie erscheint aber auf
Rechnungen und Versandpapieren. Vor der Übergabe auf den Kunden ändern.

**Versandkosten nicht besteuert.** `taxShipping: false` ist in Deutschland in der Regel
falsch: Versandkosten teilen steuerlich das Schicksal der Hauptleistung.

**Kein aktiver Versandtarif.** Ohne mindestens einen Tarif kann niemand bestellen — der
Checkout bricht ab. Fällt oft erst beim Testkauf auf.

**Richtlinien-Seiten liefern 404.** `/policies/refund-policy` und
`/policies/shipping-policy` existieren nur, wenn Text hinterlegt ist. Ein Theme, das auf
`shop.shipping_policy` prüft, blendet den Versandkosten-Hinweis dann stillschweigend aus —
und die Pflichtangabe fehlt, ohne dass es jemand sieht.

**Metafeld ohne `PUBLIC_READ`.** Per API gefüllt, im Theme unsichtbar. Immer den
Storefront-Zugriff mitsetzen.

**Metafelder erst nach der Migration angelegt.** Dann fehlen sie bei allen importierten
Produkten und müssen nachgezogen werden. Deshalb: Grundeinrichtung vor Produktmigration.

**Kein Kanal veröffentlicht automatisch.** Steht `autoPublish` überall auf `false`, sind
neu angelegte Produkte unsichtbar, bis sie explizit publiziert werden.
