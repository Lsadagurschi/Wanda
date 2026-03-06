#!/bin/sh
# Script de inicialização para Railway/Render
# Garante que $PORT é expandido corretamente em tempo de execução
exec gunicorn app:app --workers 2 --timeout 120 --bind "0.0.0.0:${PORT:-5000}"
