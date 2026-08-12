# Powerland Concurrentie-Dashboard — Platform-overzicht & Aanbevelingen

> **Doel:** één pagina die toont wat het platform NU heeft/bezit/kan (alle meerwaardes),
> plus concrete aanbevelingen voor uitbreiding — onderbouwd door de competitive-intelligence
> skills én online CI-praktijk (Klue "competitive enablement", Wikipedia CI-cyclus).
> Geen aannames: alle "NU"-feiten komen uit de repo-audit van 2026-08-12.

---

## A. WAT HET PLATFORM NU HEEFT (feitelijk, geaudit 2026-08-12)

### 1. Data & bronnen
| Onderdeel | Stand | Meerwaarde |
|-----------|-------|-----------|
| 8 concurrenten (4 direct / 2 partial / 2 indirect) | ✅ in `data.json` | Volledig beeld van de markt, niet enkel "de usual suspects" |
| Per concurrent 15 velden (diensten, sectoren, positionering, doelgroep, kanalen, sterktes, zwaktes, overlap-score, bronnen) | ✅ | Gestructureerd → dashboard kan erop filteren/sorteren |
| **Positionering nu ingevuld voor alle 8** (eigen site-tekst, geen gok) | ✅ sinds vandaag | Was 8x leeg → nu zie je in 1 oogopslag wie wát doet |
| `raw/<id>.md` bron-dossiers (8 stuks) | ✅ | Bewijs per concurrent, citeerbaar |
| 24 wekelijkse snapshots op schijf | ✅ | Historiek: wat veranderde wanneer |
| `sources`-array per concurrent | ✅ | Herleidbaarheid |

### 2. UI / Presentatie (`index.html`)
| Feature | Stand | Meerwaarde |
|---------|-------|-----------|
| FEIT/BRON-badges (groen/geel gelabeld) | ✅ | Onderscheid feit vs interpretatie — jij eiste dit |
| Per-kaart bron-link naar `raw/<id>.md` | ✅ | Klik → zie de bron |
| 5 strategische tabs: Concurrenten / Whitespace / Contentpijlers / Zwaktes / Voor Powerland | ✅ | De "keten": WIE → WAAR open → WAT zeggen → WAAROM zwak → DE ACTIE |
| Roadmap-strip bovenaan (koppel de tabs aan elkaar) | ✅ | Leest als één argument, niet losse widgets |
| Per-tab "waarom"-uitleg (kort + uitklapbaar) | ✅ | Busy reader ziet meteen waarom dit er staat |
| Powerland-huisstijl (witte header, blauw logo, 4 sectoren als filter-knoppen) | ✅ | Herkenbaar, rustig, geen overbodige chrome |

### 3. Automatisering (robuste variant)
| Onderdeel | Stand | Meerwaarde |
|-----------|-------|-----------|
| Windows Taakplanner-taak "Powerland Capture" | ✅ **maandag** 06:00 (verzet vandaag van zondag→maandag) | Draait zónder Hermes-gateway; jij werkt maandag, dan is het vers rapport klaar |
| `powerland_capture.py` (headless Playwright) | ✅ | Leest 8 sites/week, meldt veranderingen |
| `field_refresh.py` (voorstel-generator) | ✅ nieuw | Stelt positionering-update voor uit eigen site-tekst, wacht op jouw go |
| `refresh.py --one/--run-all` | ✅ | Veilige diff + rapport per verversing |
| `data.json` wordt NOOIT blind overschreven | ✅ | Respecteert "nooit raden" |

### 4. Publicatie
| Onderdeel | Stand | Meerwaarde |
|-----------|-------|-----------|
| Live op GitHub Pages (`camil96.github.io/powerland-competitors`) | ✅ | Iedereen kan het zien, geen server nodig |
| Lokaal op `127.0.0.1:8137` | ✅ | Snel testen |

---

## B. WAT HET PLATFORM NU KAN (workflow)
1. **Maandagochtend:** Taakplanner leest 8 sites → snapshot + verschil-rapport.
2. **Jij ziet:** welke concurrent veranderde (zonder dat je 8 sites bezoekt).
3. **Bij verandering:** `field_refresh.py` maakt een voorstel → jij keurt → `refresh.py` past `data.json` aan.
4. **Dashboard toont:** FEIT/BRON-gelabelde analyse met bron-links.
5. **Jij pusht** (expliciet) → live update.

---

## C. AANBEVELINGEN VOOR UITBREIDING (skills + online)

### C1. Evidence-laag per feit (volgende stap, stap 2 van je "alles in volgorde")
- **Uit skills:** `analysis-and-credibility-layer.md` eist `evidence: {claim, source_url, retrieved, quote, type}`.
- **Uit online (Klue):** "credibility = people will ask for your sources". URL alleen is waardeloos als de concurrent zijn site edit.
- **Concreet:** per positivering/dienst een bron-link met **URL + datum + letterlijk citaat + snapshot-ref**. Klik op een feit → zie exact wat er op die datum op hun site stond.
- **Meerwaarde:** onweerlegbaar bewijs; je kan ermee naar een klant/collega zonder "geloof me maar".

### C2. Battlecard-tab (verkoop-ondersteuning)
- **Uit online (Klue "competitive enablement"):** het draait niet om "wie is de concurrent" maar "wat zegt de salesman als de klant naar de concurrent vraagt".
- **Concreet:** 6e tab "Battlecard per concurrent" — hun zwakte vs jouw sterkte in 1 zin.
- **Meerwaarde:** het dashboard wordt een verkoop-wapen, niet enkel een observatie.

### C3. Sociale / nieuws-monitoring (tweede wekelijkse taak)
- **Uit skills:** `recurring-automation.md` → `0 9 * * 1` via last30days-skill, diff tegen `state/social_seen.json`, schrijf enkel NIEUW.
- **Uit online (Wikipedia CI-cyclus):** websites veranderen weinig, sociale kanalen wél.
- **Concreet:** taak die per concurrent nieuwe LinkedIn-posts/nieuws bijhoudt; stil als er niks is.
- **Meerwaarde:** je ziet hun campagnes/move voordat ze in hun website landed.

### C4. "Rust" bij groeiende data (progressive disclosure)
- **Uit skills:** `frontend-design` + jouw voorkeur voor kalmte. Optie A (uitklap per kaart) vs B (overzicht + detail-on-click). B schaalt beter.
- **Concreet:** sketch A vs B als mockup, jij kiest vóór bouw.
- **Meerwaarde:** dashboard blijft leesbaar als de data groeit (Vandotec erbij = 16 concurrenten).

### C5. Vandotec-dashboard (2e bedrijf)
- **Uit skills:** `competitive-intelligence` is gebouwd voor 2 bedrijven (Powerland + Vandotec).
- **Concreet:** zelfde engine, `brands.vandotec` in data.json, eigen concurrentenlijst.
- **Meerwaarde:** 1 tool voor je 2 bedrijven.

### C6. Self-grill vóór publicatie (grill-me skill)
- **Uit skills:** `grill-me` (mattpocock, 800K installs) — laat de agent zijn eigen claims aanvallen vóór commit.
- **Concreet:** voor elke analyse-wijziging draait de agent een grill-ronde ("is dit vak écht open?").
- **Meerwaarde:** minder tunnelvisie, jij ziet nuance i.p.v. stelligheid.

### C7. Alert/notify bij échte verandering
- **Uit skills:** `recurring-automation.md` waarschuwt: cron deliver is LOCAL-only (geen bericht). Een notification vereist een verbonden kanaal (Telegram/Discord) — jij hebt die uitgesloten.
- **Concreet:** hou het pull-only (jij kijkt maandag), OF optioneel later een Telegram-bot.
- **Meerwaarde:** geen gemiste signalen, maar geen systeem-verandering zonder je ok.

---

## D. PRIORITEITSVOORSTEL (mijn aanbeveling, jij beslist)
1. **C1 Evidence-laag** — hoogste meerwaarde, bouwt voort op je "onderbouwing"-eis, relatief klein.
2. **C4 Rust/UI** — voor je werkbaar blijft bij groei.
3. **C2 Battlecard** — maakt het een verkoop-tool.
4. **C3 Sociale monitoring** — pas als C1–C2 staan.
5. **C5 Vandotec** — wanneer je er klaar voor bent.
6. **C6/C7** — continu, geen aparte sprint.

---

## E. OPEN PUNTEN / CAVEATS (eerlijk)
- Taakplanner vuurt enkel als PC aanstaat ma 06:00 (wel `StartWhenAvailable`, maar Windows moet uit slaap).
- `field_refresh.py` doet enkel `positionering`; diensten/sectoren zijn al gevuld bij originele scrape, nog niet "weekelijks ververst".
- Live URL cached ~30s na push; raw GitHub is altijd bron van waarheid.
- Geen push gebeurd vandaag → verbeteringen (positionering) staan lokaal, niet live.
