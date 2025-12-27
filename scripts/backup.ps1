# =============================================================================
# Database Backup Script for Alechemy (Windows PowerShell)
# Usage: .\scripts\backup.ps1
# =============================================================================

param(
    [string]$BackupDir = ".\backups",
    [string]$DbContainer = "alechemy_db",
    [string]$DbName = "alechemy_db",
    [string]$DbUser = "alechemy_user",
    [int]$RetentionDays = 30
)

$ErrorActionPreference = "Stop"

# Create backup directory if not exists
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
}

# Generate timestamp
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFile = Join-Path $BackupDir "alechemy_backup_$Timestamp.sql"

Write-Host "🔄 Starting database backup..." -ForegroundColor Cyan
Write-Host "   Database: $DbName"
Write-Host "   Container: $DbContainer"
Write-Host "   Output: $BackupFile"

# Create backup
docker exec $DbContainer pg_dump -U $DbUser $DbName > $BackupFile

# Check if backup was successful
if (Test-Path $BackupFile) {
    $BackupSize = (Get-Item $BackupFile).Length / 1MB
    Write-Host "✅ Backup completed successfully!" -ForegroundColor Green
    Write-Host ("   Size: {0:N2} MB" -f $BackupSize)
} else {
    Write-Host "❌ Backup failed!" -ForegroundColor Red
    exit 1
}

# Remove old backups
Write-Host "🧹 Cleaning old backups (older than $RetentionDays days)..." -ForegroundColor Yellow
$CutoffDate = (Get-Date).AddDays(-$RetentionDays)
Get-ChildItem -Path $BackupDir -Filter "alechemy_backup_*.sql" | 
    Where-Object { $_.LastWriteTime -lt $CutoffDate } | 
    Remove-Item -Force

# List remaining backups
Write-Host ""
Write-Host "📁 Current backups:" -ForegroundColor Cyan
Get-ChildItem -Path $BackupDir -Filter "alechemy_backup_*.sql" | 
    Sort-Object LastWriteTime -Descending |
    Format-Table Name, @{N='Size (MB)';E={[math]::Round($_.Length/1MB, 2)}}, LastWriteTime

Write-Host ""
Write-Host "✨ Done!" -ForegroundColor Green
