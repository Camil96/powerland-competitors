# Copy-conventies — taalbeleid dashboard

Vastgelegd 2026-08-21, volgens gebruikersbeslissing: bronnen worden overgenomen
zoals ze zijn (taalfouten inbegrepen), verder is alles correct Nederlands.

## Regel 1 — Door ons geschreven tekst = altijd correct Nederlands
Alles wat wij genereren of schrijven is Nederlands, foutloos:
- UI-labels, knoppen, headers, placeholders (`index.html`, `pages.py`)
- Analyse-secties in `data.json` (whitespace, pillars, roadmap, explain, recommendation)
- Battlecards (`their_weak`, `our_play`, `note`)

Geen enkele ongevraagde switch naar Engels in door-ons-gegenereerde tekst.

## Regel 2 — Concurrent-eigen bron-citaat = bronzeerlijk, onteerd
De `positioning` van een concurrent is hun letterlijke site-tekst. Die:
- wordt **onteerd** weergegeven (inclusief eventuele taalfouten of Engels),
- wordt **niet** vertaald,
- wordt **niet** verwijderd,
- krijgt **geen** "vertaald"-label.
Voorbeeld: Reeload en Ionity staan volledig in het Engels (hun site) — dat blijft
zo staan. Ceratec "process & automation" blijft ook zo.

## Regel 3 — Leenwoorden / afkortingen
- Zakelijke afkortingen die in NL zakentaal gangbaar zijn, mogen: KMO, B2B, EMS,
  VCA, BESS.
- Puur Engelse leenwoorden in *zichtbare* UI-tekst vermijden. Technische velden
  die niet zichtbaar zijn (bv. `based_on`) mogen EN bevatten — die toont de UI
  niet.
- Bezittelijk voornaamwoord bij bedrijfsnaam: "Powerlands" (met -s), niet
  "Powerland haar/zijn".

## Regel 4 — Toekomstige generaties volgen dit
- Vandotec-dashboard: zelfde beleid (NL-code, onteerde bron-quotes).
- `refresh.py` / capture-scripts: mogen bron-tekst overschrijven met de
  concurrent-zijn letterlijke site-tekst, nooit met onze eigen EN-vertaling.
- Monitoring/wekelijkse capture: rapporteer veranderingen in bron-taal niet als
  "fout" — het is hun tekst.

## Controle bij elke wijziging
1. Lees elke zichtbare string die wij schrijven.
2. Bron-quotes (concurrent `positioning`) expliciet uitsluiten van de NL-check.
3. Geen EN-lek in zichtbare UI zonder expliciete gebruikersbeslissing.
