# test_serve_one.py — assert exact 1 listener op 8137 na serve_one.ps1
import subprocess, sys

PS = r"C:/Users/camil.sahnoune/competitive-intel/publish/scripts/serve_one.ps1"

r = subprocess.run(
    ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", PS],
    capture_output=True, text=True,
)
if r.returncode != 0:
    print("serve_one.ps1 faalde:")
    print(r.stdout)
    print(r.stderr)
    sys.exit(1)

# tel listeners — robuust tegen lege output (0 listeners)
out = subprocess.run(
    ["powershell.exe", "-Command",
     "$c=@(Get-NetTCPConnection -LocalPort 8137 -State Listen -ErrorAction SilentlyContinue); $c.Count"],
    capture_output=True, text=True,
).stdout.strip()
try:
    n = int(out)
except ValueError:
    print(f"Kon listener-count niet parsen: '{out}'")
    sys.exit(1)

assert n == 1, f"verwacht exact 1 listener, kreeg: {n}"
print(f"OK: {n} listener op 8137")
