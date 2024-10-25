# Get the conda environments in JSON format and convert to PowerShell object
$envJson = conda env list --json | ConvertFrom-Json

# Extract environment names from paths
$envNames = $envJson.envs | ForEach-Object { Split-Path $_ -Leaf }

# Environments to preserve
$preserve = @('base', 'yolov2')

# Filter environments to remove
$toRemove = $envNames | Where-Object { $_ -notin $preserve }

# Display information
Write-Host "Found environments:" -ForegroundColor Cyan
$envNames | ForEach-Object { Write-Host "  - $_" }

Write-Host "`nPreserving:" -ForegroundColor Green
$preserve | ForEach-Object { Write-Host "  - $_" }

Write-Host "`nWill remove:" -ForegroundColor Yellow
$toRemove | ForEach-Object { Write-Host "  - $_" }

# Confirm before proceeding
$confirmation = Read-Host "`nDo you want to proceed with removal? (y/n)"
if ($confirmation -eq 'y') {
    foreach ($env in $toRemove) {
        Write-Host "`nRemoving environment: $env" -ForegroundColor Yellow
        try {
            conda env remove --name $env
            Write-Host "Successfully removed $env" -ForegroundColor Green
        }
        catch {
            Write-Host "Error removing environment '$env' - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    Write-Host "`nCleanup completed!" -ForegroundColor Green
}
else {
    Write-Host "`nOperation cancelled by user." -ForegroundColor Red
}