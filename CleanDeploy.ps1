# CleanDeploy.ps1
param (
    [string]$ProjectRoot = (Get-Location),
    [string]$OutputZip = "deploy.zip"
)

Write-Host "Cleaning project at: $ProjectRoot"

# Xóa thư mục .git nếu tồn tại
$gitFolder = Join-Path $ProjectRoot ".git"
if (Test-Path $gitFolder) {
    Write-Host "Removing directory: $gitFolder"
    Remove-Item $gitFolder -Recurse -Force
}

# Xóa virtual environment nếu tồn tại
$venvFolder = Join-Path $ProjectRoot "myproject-venv"
if (Test-Path $venvFolder) {
    Write-Host "Removing virtual environment: $venvFolder"
    Remove-Item $venvFolder -Recurse -Force
}

# Kiểm tra file/folder nhạy cảm
$SensitivePatterns = @(
    "myproject-venv",
    "*.pyc",
    "__pycache__",
    ".env",
    ".DS_Store",
    "*.config.json"
)

$SensitiveItems = @()
foreach ($pattern in $SensitivePatterns) {
    $SensitiveItems += Get-ChildItem -Path $ProjectRoot -Recurse -Include $pattern -Force -ErrorAction SilentlyContinue
}

if ($SensitiveItems.Count -gt 0) {
    Write-Warning "Still found some sensitive items:"
    $SensitiveItems | ForEach-Object { Write-Host " - $($_.FullName)" }

    # Xóa các file/folder nhạy cảm
    foreach ($item in $SensitiveItems) {
        if (Test-Path $item.FullName) {
            try {
                Remove-Item $item.FullName -Force -Recurse -ErrorAction Stop
                Write-Host "Deleted sensitive item: $($item.FullName)" -ForegroundColor Yellow
            } catch {
                Write-Warning "Failed to delete: $($item.FullName)"
            }
        }
    }
}

# Tạo requirements.txt
Write-Host "Generating requirements.txt ..."
try {
    & python -m pip freeze > (Join-Path $ProjectRoot "requirements.txt")
    Write-Host "requirements.txt updated."
} catch {
    Write-Warning "Failed to generate requirements.txt. Check Python installation."
}

# Tạo deploy.zip
Write-Host "Creating $OutputZip ..."
if (Test-Path $OutputZip) {
    Remove-Item $OutputZip -Force
}
Compress-Archive -Path "$ProjectRoot\*" -DestinationPath "$ProjectRoot\$OutputZip" -Force
Write-Host "Deploy package $OutputZip is ready." -ForegroundColor Green
