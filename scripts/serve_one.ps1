# serve_one.ps1 — kill alle 8137 listeners, start exact één frisse server.py
$procs = Get-NetTCPConnection -LocalPort 8137 -State Listen -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty OwningProcess | Sort-Object -Unique
if ($procs) {
    $procs | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
}
Start-Sleep -Seconds 2
$still = Get-NetTCPConnection -LocalPort 8137 -State Listen -ErrorAction SilentlyContinue
if ($still) {
    Write-Error "Kon 8137 niet vrijmaken: $($still.OwningProcess -join ',')"
    exit 1
}
Start-Process -FilePath "python" -ArgumentList "server.py" `
    -WorkingDirectory "C:/Users/camil.sahnoune/competitive-intel/publish" -WindowStyle Hidden
Start-Sleep -Seconds 2
$ok = Get-NetTCPConnection -LocalPort 8137 -State Listen -ErrorAction SilentlyContinue
if (-not $ok) {
    Write-Error "Server startte niet"
    exit 1
}
Write-Host "OK: exact een server op 8137"
