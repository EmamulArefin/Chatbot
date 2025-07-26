# PowerShell script to install Bengali language support for Tesseract
# Run this as Administrator

$tempPath = "$env:TEMP\ben.traineddata"
$tesseractPath = "C:\Program Files\Tesseract-OCR\tessdata\ben.traineddata"

Write-Host "Downloading Bengali language data for Tesseract OCR..."
if (-not (Test-Path $tempPath)) {
    Invoke-WebRequest -Uri "https://github.com/tesseract-ocr/tessdata/raw/main/ben.traineddata" -OutFile $tempPath
} else {
    Write-Host "Bengali language data already downloaded."
}

Write-Host "Copying to Tesseract directory..."
try {
    Copy-Item $tempPath $tesseractPath -Force
    Write-Host "Bengali language support installed successfully!"
    Write-Host "You can now restart your Streamlit application."
    
    # Clean up temp file
    Remove-Item $tempPath -Force
} catch {
    Write-Host "Error: Cannot copy to Tesseract directory. Administrator privileges required." -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run this script as Administrator:" -ForegroundColor Yellow
    Write-Host "1. Right-click on PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host "2. Navigate to this directory: cd '$PWD'" -ForegroundColor Yellow
    Write-Host "3. Run: .\install_bengali_lang.ps1" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Or manually copy the file:" -ForegroundColor Yellow
    Write-Host "From: $tempPath" -ForegroundColor Cyan
    Write-Host "To: $tesseractPath" -ForegroundColor Cyan
}
