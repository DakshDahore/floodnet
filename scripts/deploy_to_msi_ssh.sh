#!/usr/bin/env bash
set -e
echo "=================================================================="
echo " PROJECT FLOODLOCK // NATIVE OPENSSH DEPLOYMENT SENTINEL"
echo " Target Host: yuvamps1@192.168.1.109:22 (MSI1 Windows Server)"
echo " Remote Root: C:\\Users\\YuvaMPS1\\Documents\\server\\floodlock"
echo "=================================================================="

MSI_USER="${MSI_USER:-yuvamps1}"
MSI_HOST="${MSI_HOST:-192.168.1.109}"
MSI_PORT="${MSI_PORT:-22}"
REMOTE_DIR="C:/Users/YuvaMPS1/Documents/server/floodlock"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "[*] Verifying network connection to ${MSI_HOST}:${MSI_PORT}..."
if ! ssh -p "$MSI_PORT" -o ConnectTimeout=5 -o StrictHostKeyChecking=accept-new "${MSI_USER}@${MSI_HOST}" "echo [✓] OpenSSH Handshake Verified" 2>/dev/null; then
    echo "[!] ERROR: Unable to reach ${MSI_USER}@${MSI_HOST}:${MSI_PORT} via OpenSSH."
    echo "    Please verify on Windows PowerShell (Admin):"
    echo "      1. Start-Service sshd"
    echo "      2. Set-Service -Name sshd -StartupType 'Automatic'"
    echo "      3. New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH SSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22"
    exit 1
fi

echo "[*] Creating remote directory structure on MSI1..."
ssh -p "$MSI_PORT" "${MSI_USER}@${MSI_HOST}" "powershell -Command \"New-Item -ItemType Directory -Force -Path '${REMOTE_DIR}\\data', '${REMOTE_DIR}\\floodlock_trainer', '${REMOTE_DIR}\\floodlock_backend_local'\""

echo "[*] Synchronizing datasets, models, and backend code via scp..."
scp -P "$MSI_PORT" -r data/* "${MSI_USER}@${MSI_HOST}:${REMOTE_DIR}/data/"
scp -P "$MSI_PORT" -r floodlock_trainer/* "${MSI_USER}@${MSI_HOST}:${REMOTE_DIR}/floodlock_trainer/"
scp -P "$MSI_PORT" -r floodlock_backend_local/* "${MSI_USER}@${MSI_HOST}:${REMOTE_DIR}/floodlock_backend_local/" 2>/dev/null || true

echo "=================================================================="
echo " [✓] DEPLOYMENT SYNCHRONIZED SUCCESSFULLY VIA NATIVE OPENSSH"
echo "=================================================================="
