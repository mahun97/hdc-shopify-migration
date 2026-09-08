#!/usr/bin/env python3
"""Phase 3 - erhebt das Zielschema des Shops und schreibt Shop-Steckbrief.md.
Aufruf: python3 1_steckbrief.py [--env pfad]"""
import json, os, sys, collections, datetime, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify import zugang, gql as _gql, titel, fehler

envp = sys.argv[sys.argv.index('--env')+1] if '--env' in sys.argv else None
env = zugang(envp)
def gql(q, v=None, still=False): return _gql(env, q, v, still)

def alle(feld, inner, key='nodes'):
    out, cur = [], None
    while True:
        d = gql('query($c:String){ %s(first:100, after:$c){ nodes { %s } pageInfo { hasNextPage endCursor } } }'
                % (feld, inner), {'c': cur})[feld]
        out += d['nodes']
        if not d['pageInfo']['hasNextPage']: return out
        cur = d['pageInfo']['endCursor']

Z = []
def s(t=''): Z.append(t)

shop = gql('{ shop { name myshopifyDomain currencyCode plan { displayName partnerDevelopment } } }')['shop']
s(f"# Shop-Steckbrief: {shop['name']}")
s()
s(f"Erhoben am {datetime.date.today().strftime('%d.%m.%Y')} · `{shop['myshopifyDomain']}` · "
  f"Plan {shop['plan']['displayName']}{' (Development)' if shop['plan']['partnerDevelopment'] else ''} · "
  f"Währung {shop['currencyCode']}")
s()
s("> Dieses Dokument beschreibt, **wie dieser Shop tickt** — nicht was drin ist. Es ist die")
s("> verbindliche Grundlage für jeden Produktimport. Vor dem Import lesen, nach Theme-Änderungen neu erheben.")
s()

# ---------- 1 Kollektionen ----------
s("## 1 · Kollektionen und ihre Aufnahmeregeln")
s()
s("Automatische Kollektionen nehmen Produkte **nur** auf, wenn die Bedingung exakt zutrifft.")
s("Schreibweise beachten — `beutel und rollen` ist nicht `beutel & rollen`.")
s()
s("| Kollektion | Handle | Typ | Bedingung | Sortierung | Produkte |")
s("|---|---|---|---|---|---|")
for c in alle('collections', 'title handle sortOrder productsCount{count} ruleSet{ appliedDisjunctively rules{ column relation condition } } templateSuffix'):
    if c['ruleSet']:
        vk = ' ODER ' if c['ruleSet']['appliedDisjunctively'] else ' UND '
        bed = vk.join(f"{r['column']} {r['relation']} `{r['condition']}`" for r in c['ruleSet']['rules'])
        typ = 'automatisch'
    else:
        bed, typ = '—', 'manuell'
    s(f"| {c['title']} | `{c['handle']}` | {typ} | {bed} | {c['sortOrder']} | {c['productsCount']['count']} |")
s()

# ---------- 2 Navigation ----------
s("## 2 · Navigation — welche Tags das Menü voraussetzt")
s()
menus = gql('{ menus(first:20){ nodes { handle title items { title url items { title url items { title url } } } } } }', still=True)
if not menus:
    s("*Nicht erhebbar — Scope `read_online_store_navigation` fehlt.*")
else:
    s("Untermenüs arbeiten oft mit **Tag-Filter-URLs** (`/collections/<koll>/<tag>+<tag>`).")
    s("Fehlt der Tag am Produkt, ist der Menüpunkt tot. Achtung: Ein Filter **ohne Treffer**")
    s("zeigt in Shopify nicht etwa nichts, sondern die **komplette Kollektion**.")
    s()
    s("| Menüpfad | Ziel | vorausgesetzte Tags |")
    s("|---|---|---|")
    def lauf(items, pfad=''):
        for it in items:
            p = (pfad + ' › ' if pfad else '') + it['title']
            u = re.sub(r'^https?://[^/]+', '', it['url'] or '')
            u = re.sub(r'^/[a-z]{2}(/|$)', '/', u)
            teil = u.split('/')
            tags = teil[3].split('+') if u.startswith('/collections/') and len(teil) > 3 else []
            warn = '  ⚠ **ohne Ziel**' if u.endswith('#') else ''
            if tags or warn:
                s(f"| {p} | `{u}` | {', '.join('`'+t+'`' for t in tags) or '—'}{warn} |")
            lauf(it.get('items') or [], p)
    for m in menus['menus']['nodes']:
        if m['handle'] in ('main-menu','footer'): lauf(m['items'])
s()

# ---------- 3 Tag-Vokabular ----------
prods = alle('products', 'title status tags vendor productType')
tagz = collections.Counter(t for p in prods for t in p['tags'])
s("## 3 · Tag-Vokabular (verbindlich)")
s()
s("Nur diese Werte sind im Shop in Gebrauch. **Die Importvorlage muss daraus ein Dropdown machen** —")
s("freie Texteingabe erzeugt genau die Schreibweisen-Fehler, die Kollektionen und Menüs aushebeln.")
s()
s('```')
for t, n in sorted(tagz.items(), key=lambda x: (-x[1], x[0])):
    s(f"{n:4d}×  {t}")
s('```')
s()

# ---------- 4 Metafelder ----------
s("## 4 · Metafelder")
s()
md = gql('{ metafieldDefinitions(first:50, ownerType:PRODUCT){ nodes { name namespace key type{ name } access{ storefront } } } }', still=True)
if md and md['metafieldDefinitions']['nodes']:
    s("| Feld | Typ | Storefront | Zweck |")
    s("|---|---|---|---|")
    for d in md['metafieldDefinitions']['nodes']:
        acc = d['access']['storefront']
        warn = '' if acc == 'PUBLIC_READ' else ' ⚠ im Theme unsichtbar'
        s(f"| `{d['namespace']}.{d['key']}` | {d['type']['name']} | {acc}{warn} | {d['name']} |")
    s()
    s("**Falle:** Ein Metafeld ohne `PUBLIC_READ` ist per API gefüllt, aber im Theme leer.")
else:
    s("*Keine Produkt-Metafeld-Definitionen vorhanden.*")
s()

# ---------- 5 Theme ----------
s("## 5 · Theme")
s()
th = gql('{ themes(first:10, roles:MAIN){ nodes { id name role } } }', still=True)
if th:
    for t in th['themes']['nodes']:
        s(f"- **{t['name']}** · Rolle {t['role']} · ID `{t['id'].split('/')[-1]}`")
    s()
    s("Vor dem Import im Produkt-Template prüfen (`templates/product.json`):")
    s()
    s("- **Tab-Sections** (`product-info-tabs`): welche Tabs existieren, worauf zeigt ihr Inhalt.")
    s("  Ein Tab mit leerem Metafeld wird **nicht angezeigt** — er sieht aus, als gäbe es ihn nicht.")
    s("- **Deaktivierte Blöcke** (`\"disabled\": true`): oft sind Beschreibung, Tabs und")
    s("  Pflichtangaben schon angelegt, aber abgeschaltet.")
    s("- **Pflichtangaben** im Preisblock: MwSt, Versandkosten, Lieferzeit.")
s()

# ---------- 6 Pflichtfelder ----------
s("## 6 · Was die Importliste enthalten muss")
s()
s("| Feld | Pflicht | Warum |")
s("|---|---|---|")
for feld, pf, warum in [
  ('Artikelnummer (SKU)','ja','muss **shopweit eindeutig** sein, sonst bricht die Bestandsführung'),
  ('Produkttitel','ja','gruppiert die Varianten — identischer Titel = ein Produkt'),
  ('Option 1 (z. B. Format)','ja','**jede Variante braucht einen unterscheidenden Wert**, sonst lehnt Shopify ab'),
  ('Option 2 (z. B. Menge)','wenn vorhanden','nur nötig, wenn sich Varianten sonst nicht unterscheiden'),
  ('Verkaufspreis','ja','—'),
  ('Gewicht','ja','ohne Gewicht rechnet der gewichtsbasierte Versand falsch'),
  ('Tags','ja','steuert Kollektionen **und** Navigation — nur Werte aus Abschnitt 3'),
  ('Bilddatei','ja','Produkte ohne Bild erscheinen als graue Kachel'),
  ('Beschreibung','ja','—'),
  ('Hersteller (GPSR)','ja','EU-Pflichtangabe seit 12/2024, bei Fremdmarken deren Anschrift'),
]:
    s(f"| {feld} | {pf} | {warum} |")
s()

# ---------- 7 Fallen ----------
s("## 7 · Bekannte Fallen in diesem Shop")
s()
s("- Tag-Filter ohne Treffer zeigt die **ganze** Kollektion, nicht eine leere Seite.")
s("- Menüeinträge vom Typ `PRODUCT` hängen an der Produkt-ID, nicht am Handle —")
s("  ein Handle-Tausch repariert so einen Link **nicht**.")
s("- `menuUpdate` verlangt die **komplette** Item-Struktur; fehlende Einträge werden gelöscht.")
s("- Liquid kennt **kein** `then` in `case/when`.")
s("- Automatische Kollektionen rechnet Shopify **asynchron** nach — nach dem Taggen einige Minuten warten.")
s("- Produktbilder sind **nicht** pro Sprache umschaltbar; nur der Alt-Text ist übersetzbar.")
s()

offen = [p['title'] for p in prods if p['status']=='ACTIVE']
s("---")
s(f"*Erhoben aus {len(prods)} Produkten ({len(offen)} aktiv) und {len(tagz)} Tags.*")

ziel = 'Shop-Steckbrief.md'
open(ziel, 'w').write('\n'.join(Z) + '\n')
titel(f'{ziel} geschrieben')
print(f'  {len(Z)} Zeilen · {len(tagz)} Tags · {len(prods)} Produkte')
print('\n  Wichtigster Abschnitt: 3 (Tag-Vokabular) — davon hängen Kollektionen und Menü ab.\n')
