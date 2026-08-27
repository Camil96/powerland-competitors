# run_monitor.ps1 — Unattended Powerland monitor-pipe (Windows Taakplanner)
#
# Wat dit doet (architectuur-correct, 2026-08-25):
#   - powerland_capture.py : maakt site-snapshots (detecteert wijzigingen, raakt data.json NIET aan)
#   - content_scan.py      : verse publieke site+RSS -> content_raw/<id>/<ts>.json (voedt "Hun contentstrategie"-tab)
#   - Schrijft een monitor-log met wat er gebeurde.
#
# Wat dit NIET doet:
#   - Raakt data.json NOOIT aan. Geen automatische feitelijke update zonder mens.
#     (refresh.py verwacht een agent die de site leest; in een unattended run is die er niet.)
#
# Vereist: Hermes-venv (Playwright zit daarin). Scripts herstarten zichzelf onder die venv
# via self-reexec, maar we roepen ze direct onder de venv aan voor zekerheid.

$PUBLISH = "C:\Users\camil.sahnoune\competitive-intel\publish"

# Schakelaar: $true = Firecrawl keyless adapter (geen key/account, 1k credits/maand)
#             $false = eigen content_scan.py (Playwright, onderhoud jij)
# Default false zoals afgesproken — Firecrawl is klaar als optie, niet de default.
$USE_FIRECRAWL = $false
$VENV_PY = "C:\Users\camil.sahnoune\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"
$DATE = Get-Date -Format "yyyyMMdd-HHmm"
$LOG = Join-Path $PUBLISH "monitor-log-$DATE.txt"

function Log($msg) {
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  $msg"
    Add-Content -Path $LOG -Value $line
    Write-Host $line
}

# pre-check
if (-not (Test-Path $VENV_PY)) { Log "FOUT: venv-python niet gevonden: $VENV_PY"; exit 1 }
if (-not (Test-Path (Join-Path $PUBLISH "data.json"))) { Log "FOUT: data.json ontbreekt in $PUBLISH"; exit 1 }

Log "=== Powerland monitor-pipe start ==="
Log "werkmap: $PUBLISH"

# 1) Site-snapshots (detecteert wijzigingen)
Log ">> powerland_capture.py ..."
try {
    & $VENV_PY (Join-Path $PUBLISH "powerland_capture.py") 2>&1 | ForEach-Object { Log "   capture: $_" }
    Log "<< powerland_capture.py klaar (exit $LASTEXITCODE)"
} catch {
    Log "FOUT in powerland_capture.py: $_"
}

# 2) Verse content-scans (publieke site + RSS, geen login)
if ($USE_FIRECRAWL) {
    Log ">> firecrawl_adapter.py (keyless) ..."
    try {
        & $VENV_PY (Join-Path $PUBLISH "scripts\firecrawl_adapter.py") 2>&1 | ForEach-Object { Log "   firecrawl: $_" }
        Log "<< firecrawl_adapter.py klaar (exit $LASTEXITCODE)"
    } catch {
        Log "FOUT in firecrawl_adapter.py: $_"
    }
} else {
    Log ">> content_scan.py ..."
    try {
        & $VENV_PY (Join-Path $PUBLISH "scripts\content_scan.py") 2>&1 | ForEach-Object { Log "   content: $_" }
        Log "<< content_scan.py klaar (exit $LASTEXITCODE)"
    } catch {
        Log "FOUT in content_scan.py: $_"
    }
}

# data.json integriteit-check (mag niet veranderd zijn)
$before = (Get-Item (Join-Path $PUBLISH "data.json")).LastWriteTime
Log "data.json last-write: $before  (moet gelijk blijven aan voor de run)"

Log "=== Powerland monitor-pipe einde ==="
Log "Bekijk snapshots/ en content_raw/ voor verse data. Curatie van data.json gebeurt met de hand (refresh.py --one)."
