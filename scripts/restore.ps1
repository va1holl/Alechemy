# =============================================================================
# Database Restore Script for Alechemy (Windows PowerShell)
# Usage: .\scripts\restore.ps1 -BackupFile <path_to_backup>
# =============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$BackupFile,
    
    [string]$DbContainer = "alechemy_db",
    [string]$DbName = "alechemy_db",
    [string]$DbUser = "alechemy_user"
)

$ErrorActionPreference = "Stop"

# Check if backup file exists
if (-not (Test-Path $BackupFile)) {
    Write-Host "❌ Backup file not found: $BackupFile" -ForegroundColor Red
    Write-Host ""
    Write-Host "Available backups:" -ForegroundColor Yellow
    Get-ChildItem -Path ".\backups" -Filter "alechemy_backup_*.sql" 2>$null |
        Format-Table Name, LastWriteTime
    exit 1
}

Write-Host "⚠️  WARNING: This will REPLACE all data in the database!" -ForegroundColor Red
Write-Host "   Database: $DbName"
Write-Host "   Backup: $BackupFile"
Write-Host ""

$Confirm = Read-Host "Are you sure you want to continue? (yes/no)"
if ($Confirm -ne "yes") {
    Write-Host "Cancelled."
    exit 0
}

Write-Host ""
Write-Host "🔄 Stopping web container..." -ForegroundColor Cyan
docker stop alechemy_web 2>$null

Write-Host "🔄 Restoring database..." -ForegroundColor Cyan

# Drop existing connections and recreate database
$DropConnections = @"
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = '$DbName'
AND pid <> pg_backend_pid();
"@

docker exec $DbContainer psql -U $DbUser -d postgres -c $DropConnections 2>$null
docker exec $DbContainer psql -U $DbUser -d postgres -c "DROP DATABASE IF EXISTS $DbName;"
docker exec $DbContainer psql -U $DbUser -d postgres -c "CREATE DATABASE $DbName OWNER $DbUser;"

# Restore from backup
Get-Content $BackupFile | docker exec -i $DbContainer psql -U $DbUser $DbName

Write-Host "🔄 Starting web container..." -ForegroundColor Cyan
docker start alechemy_web

Write-Host ""
Write-Host "✅ Database restored successfully!" -ForegroundColor Green
Write-Host "   You may need to run migrations if the backup is from an older version."
