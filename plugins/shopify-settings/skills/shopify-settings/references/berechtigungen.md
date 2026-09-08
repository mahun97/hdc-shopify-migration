# Referenz: Berechtigungen für beide Shopify-Skills

*Für Claude: im Chat als kopierbaren Block ausgeben.*

Diese Liste deckt **Grundeinrichtung und Produktmigration** ab. Einmal vollständig setzen
erspart das mehrfache Neuinstallieren der App.

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

## Wofür welche Berechtigung

| Berechtigung | wird gebraucht für |
|---|---|
| `products`, `files`, `inventory` | Produkte, Bilder, Varianten |
| `publications` | Veröffentlichen im Onlineshop |
| `themes`, `theme_code` | Pflichtangaben, Tabs, Galerie-Anpassungen |
| `translations` | zweisprachige Shops |
| `online_store_navigation` | Menüs und Untermenüs |
| `content` | Seiten und Weiterleitungen |
| `legal_policies` | AGB, Widerruf, Datenschutz, Versandrichtlinie |
| `shipping` | Versandzonen und Tarife |
| `locales`, `markets` | Sprachen und Märkte |
| `locations` | Lagerstandorte |

## Merksatz

**Berechtigung nachtragen reicht nicht — die App muss danach neu installiert werden.**
Deshalb die Liste immer vollständig setzen, auch wenn zunächst nur ein Teil gebraucht wird.
