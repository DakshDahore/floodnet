@echo off
title FloodLock Cloudflare Tunnel Exposer
echo ==================================================================
echo  PROJECT FLOODLOCK // CLOUDFLARE SECURE TUNNEL (MSI1 BACKEND)
echo ==================================================================
echo [*] Exposing local port 8000 via Cloudflare Tunnel...
cloudflared tunnel --url http://localhost:8000
pause
