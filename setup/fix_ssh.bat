@echo off
:: FloodLock Windows SSH Auto-Fixer
:: Must be run as Administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [!] ERROR: Please right-click this file and select "Run as administrator"
    pause
    exit /b 1
)

echo [*] Setting password for yuvamps1 to 1416...
net user yuvamps1 1416

echo [*] Writing pure UTF-8 SSH public key...
if not exist "%ProgramData%\ssh" mkdir "%ProgramData%\ssh"
if not exist "%USERPROFILE%\.ssh" mkdir "%USERPROFILE%\.ssh"

set KEY=ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIDHSpo8WtPUnxI37xfpZsuNLemXsKA3c7NEPaTbFPs+ daksh@Daksh

powershell -NoProfile -Command "[System.IO.File]::WriteAllText('%ProgramData%\ssh\administrators_authorized_keys', '%KEY%' + [Environment]::NewLine, (New-Object System.Text.UTF8Encoding($false)))"
powershell -NoProfile -Command "[System.IO.File]::WriteAllText('%USERPROFILE%\.ssh\authorized_keys', '%KEY%' + [Environment]::NewLine, (New-Object System.Text.UTF8Encoding($false)))"

echo [*] Setting strict ACL permissions...
icacls "%ProgramData%\ssh\administrators_authorized_keys" /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F" >nul
icacls "%USERPROFILE%\.ssh\authorized_keys" /inheritance:r /grant "yuvamps1:F" /grant "SYSTEM:F" >nul

echo [*] Restarting OpenSSH Server...
net stop sshd >nul 2>&1
net start sshd >nul 2>&1

echo [✓] SUCCESS! Windows SSH is now completely unlocked for Arch Linux.
echo You can close this window now.
pause
