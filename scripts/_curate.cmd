@echo off
set VENV=C:\Users\camil.sahnoune\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe
set PUB=C:\Users\camil.sahnoune\competitive-intel\publish
set ELECTRA={"services":["Laadnetwerk-operator (774 stations beschikbaar, 64 in aanbouw)","Electra-laadpas","Electra+ abonnement","App (routeplanner, Autocharge)","Voor professionals (fleet / host een station)"]}
set IONITY={"services":["Europees snellaadnetwerk (887 locaties, 24 landen, 74 in aanbouw)","Abonnementen IONITY Power 365 / Motion 365","IONITY App","IONITY Direct","Partner program / Fleets"]}
"%VENV%" "%PUB%\refresh.py" --one electra --facts "%ELECTRA%"
"%VENV%" "%PUB%\refresh.py" --one ionity --facts "%IONITY%"
"%VENV%" "%PUB%\refresh.py" --run-all
