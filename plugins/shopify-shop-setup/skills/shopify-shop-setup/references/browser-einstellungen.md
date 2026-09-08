# Referenz: Shop-Einstellungen über den Browser

Was die Admin-API nicht anbietet, lässt sich über Claude in Chrome ausfüllen —
**Allgemein, Checkout, Kundenkonten, Benachrichtigungen**. Der Shopify-Admin hat dabei
drei Eigenheiten, die man kennen muss.

## 1 · Der Tab muss im Vordergrund sein

Chrome drosselt Hintergrund-Tabs, der Admin rendert dann nur Bruchstücke. Prüfen mit
`document.visibilityState` — steht dort `hidden`, die Person bitten, den Tab anzuklicken
und das Fenster aktiv zu lassen.

## 2 · Die Felder liegen im Shadow DOM

Der Admin ist auf Web Components umgestellt. Eine einzelne Einstellungsseite hat leicht
**über 500 Shadow-Hosts**. Folge:

- `document.querySelectorAll('input')` findet fast nichts und liefert **falsche Negative** —
  „Feld nicht vorhanden", obwohl es da ist.
- **`find` funktioniert** und durchdringt das Shadow DOM. Damit arbeiten.
- Eigenes JavaScript muss rekursiv durch `shadowRoot` laufen:

```js
function alleTiefen(sel){
  const out=[]; const lauf=r=>{ r.querySelectorAll('*').forEach(e=>{
    if(e.matches&&e.matches(sel)) out.push(e);
    if(e.shadowRoot) lauf(e.shadowRoot); }); };
  lauf(document); return out;
}
```

## 3 · Getippt werden muss wirklich

Werte per `element.value = '…'` zu setzen löst Reacts Änderungserkennung **nicht** aus.
Der Speichern-Knopf bliebe grau, das Formular sähe gefüllt aus — und niemand merkt es.
Also: Feld anklicken, dann `type` verwenden.

Kontrolle vor dem Speichern: Ist der Speichern-Knopf aktiv geworden?

```js
const btn = alleTiefen('button').find(b=>/speichern/i.test(b.innerText||''));
btn && !(btn.disabled || btn.getAttribute('aria-disabled')==='true')
```

Ist er noch grau, hat die Eingabe nicht gegriffen.

## Ablauf für ein Einstellungsfeld

1. Zur Seite navigieren, warten bis geladen
2. Mit `find` die Zeile suchen und anklicken — viele Werte öffnen erst einen Dialog
3. Mit `find` das Eingabefeld holen, anklicken, `type`
4. Prüfen, ob Speichern aktiv wurde
5. **Der Person zeigen, was gespeichert werden soll, und erst nach Freigabe klicken**
6. Danach neu laden und den gespeicherten Wert gegenlesen

## Was nie automatisiert wird

Zahlungsanbieter-Onboarding (Bankdaten, Ausweis), Domainkauf, Planwahl. Dort führst du
die Person hin und lässt sie selbst klicken.
