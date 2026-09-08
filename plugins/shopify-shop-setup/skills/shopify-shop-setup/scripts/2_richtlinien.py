#!/usr/bin/env python3
"""Spielt eine gelieferte Richtlinie in den Shop ein. Schreibt KEINE Texte selbst.
Aufruf:
  python3 2_richtlinien.py --pruefen
  python3 2_richtlinien.py --datei agb.html --typ TERMS_OF_SERVICE
Typen: TERMS_OF_SERVICE, PRIVACY_POLICY, REFUND_POLICY, SHIPPING_POLICY,
       LEGAL_NOTICE, CONTACT_INFORMATION, SUBSCRIPTION_POLICY"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify import zugang, gql, pruefe_fehler, titel, fehler, gate

TYPEN = {'TERMS_OF_SERVICE':'AGB','PRIVACY_POLICY':'Datenschutzerklärung',
         'REFUND_POLICY':'Widerrufs- / Rückgabebelehrung','SHIPPING_POLICY':'Versandinformationen',
         'LEGAL_NOTICE':'Impressum','CONTACT_INFORMATION':'Kontaktinformationen',
         'SUBSCRIPTION_POLICY':'Abo-Bedingungen'}
envp = sys.argv[sys.argv.index('--env')+1] if '--env' in sys.argv else None
env = zugang(envp)

d = gql(env, '{ shop { shopPolicies { type title url body } } }', still=True)
if d is None: fehler('Richtlinien nicht lesbar — Berechtigung read_legal_policies fehlt.')
vorhanden = {p['type']: p for p in d['shop']['shopPolicies']}

if '--pruefen' in sys.argv or '--datei' not in sys.argv:
    titel('Richtlinien im Shop')
    for typ, name in TYPEN.items():
        p = vorhanden.get(typ)
        text = re.sub('<[^>]+>', '', (p or {}).get('body') or '').strip()
        if not text: print(f'  FEHLT    {name}')
        else:        print(f'  {len(text):5d} Z. {name}   {p.get("url") or ""}')
    print('\n  Texte kommen vom Kunden oder einem Rechtsdienstleister — nicht selbst formulieren.\n')
    sys.exit(0)

datei = sys.argv[sys.argv.index('--datei')+1]
typ   = sys.argv[sys.argv.index('--typ')+1].upper()
if typ not in TYPEN: fehler(f'Unbekannter Typ "{typ}". Erlaubt: {", ".join(TYPEN)}')
if not os.path.exists(datei): fehler(f'{datei} nicht gefunden')
inhalt = open(datei, encoding='utf-8').read().strip()
if not inhalt: fehler(f'{datei} ist leer')

nur_text = re.sub('<[^>]+>', '', inhalt).strip()
alt = re.sub('<[^>]+>', '', (vorhanden.get(typ) or {}).get('body') or '').strip()
titel(f'{TYPEN[typ]} einspielen')
print(f'  Quelle:   {datei}  ({len(nur_text)} Zeichen Text)')
print(f'  Im Shop:  {"leer" if not alt else str(len(alt)) + " Zeichen — wird ERSETZT"}')
print(f'\n  Beginn:   {nur_text[:150].replace(chr(10), " ")}…')
gate(f'{TYPEN[typ]} im Shop {env["SHOP"]} setzen' + (' und den vorhandenen Text ersetzen.' if alt else '.'))

M = '''mutation($p:ShopPolicyInput!){ shopPolicyUpdate(shopPolicy:$p){
  shopPolicy { type url } userErrors { field message } } }'''
r = gql(env, M, {'p': {'type': typ, 'body': inhalt}})['shopPolicyUpdate']
pruefe_fehler(r, 'shopPolicyUpdate')
print(f'\n  Gesetzt. Erreichbar unter: {r["shopPolicy"]["url"]}')
print('  Bitte die Seite aufrufen und die Formatierung prüfen.\n')
