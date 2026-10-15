#!/bin/bash

cd "$(dirname "$0")"

# Arrêter une ancienne instance SENTOX si elle existe
pkill -f "python web/app.py" 2>/dev/null || true

# Attendre un court instant
sleep 1

# Lancer SENTOX en arrière-plan
nohup env PYTHONPATH=. python web/app.py > sentox.log 2>&1 &

PID=$!

echo "========================================"
echo " SENTOX DEMARRE"
echo " PID : $PID"
echo " PORT : 5000"
echo " LOG : sentox.log"
echo "========================================"
