# ROADMAP — Concurrentie-Intelligentie Dashboard (Powerland + Vandotec)

Werkwijze: GSD-stijl in-gesprek — elke fase eindigt op een verificatie-gate.
De user geeft pas "ja / pushen" als hij het resultaat ZELF heeft gezien op de
lokale server (127.0.0.1:8137). Nooit auto-push.

Status legenda: [x] af (lokaal) · [ ] open · [-] uitgesteld

## Fase 0 — Veiligstellen (DONE)
- [x] pages.py (Powerland-huisstijl) lokaal gecommit
- [x] .planning/ in .gitignore (lek-preventie: repo-root = Pages-root)
- [x] 10 commits lokaal, 0 open working-copy wijzigingen
- Let op: 9 commits staan nog NIET op GitHub (awaiting "pushen")

## Fase 1 — Powerland live zetten + verifiëren
Doel: het bestaande Powerland-dashboard écht draaiend tonen + bewijzen dat het werkt.
- [ ] 1.1 Server herstarten op 8137 (oude listeners doden eerst)
- [ ] 1.2 Browser-check: dashboard laadt, 8 kaarten, filters, battlecards-tab
- [ ] 1.3 Live HTTP-check: /, /data.json, /concurrent/<id>, /evidence/<id>/<datum>
- [ ] 1.4 User beoordeelt op lokale server
- [ ] 1.5 (bij "pushen") commit + push origin main → live URL verifiëren

Mijlpaal M1: Powerland-dashboard live + geverifieerd (lokaal én na push op Pages).

## Fase 2 — Vandotec-dashboard (uitgesteld t/m user-keuze 2026-08-11)
Voorwaarde: Vandotec-concurrentenlijst van de user (NOOIT geraden — vast regel).
- [ ] 2.1 User levert Vandotec-concurrenten (naam + domein)
- [ ] 2.2 Dezelfde engine: data.json parent_brand="vandotec" + eigen raw/<brand>/
- [ ] 2.3 Scrape + log (2 manieren) + categoriseer overlap
- [ ] 2.4 Dashboard toont Vandotec-sectie / 2e bedrijf-switch
- [ ] 2.5 Verifiëren + (bij "pushen") live

Mijlpaal M2: Vandotec-dashboard live.

## Fase 3 — Terugkerende monitoring (robust)
- [ ] 3.1 Headless Playwright capture-script (geen agent-cron — die hangt)
- [ ] 3.2 Windows Taakplanner-taak (wekelijks, geen Gateway) i.p.v. fragiele cron
- [ ] 3.3 Field-refresh proposal (geen data.json overschrijven = geen raden)
- [ ] 3.4 Verify: 1 capture-run 8/8, 0 failures

Mijlpaal M3: dashboard blijft "levend" zonder handwerk.

## Open vragen / beslissingen
- Vandotec: wacht op user-input (geen domeinen verzinnen).
- Live-zetten Powerland: pas bij expliciete "ja / pushen".

## Niet doen
- Geen auto-push naar GitHub.
- Geen concurrent-domeinen raden.
- Geen .planning/ naar Pages (al geblokkeerd via .gitignore).
