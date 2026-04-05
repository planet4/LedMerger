
# crop_canvas.ps1
# Crops a 4224x256 DaVinci export to 4224x64 (center crop)
# Place this script in the same folder as your file and run it.
 
$Input = Get-ChildItem -Filter "*.mp4" | Select-Object -First 1
 
if (-not $Input) {
    Write-Host "No mp4 file found in this folder." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit
}
 
$Output = [System.IO.Path]::GetFileNameWithoutExtension($Input.Name) + "_64px.mp4"
 
Write-Host "Cropping $($Input.Name) -> $Output" -ForegroundColor Cyan
 
& ffmpeg -i "$($Input.FullName)" -vf "crop=4224:64:0:96" -c:v libx264 -crf 16 -pix_fmt yuv420p "$Output" -y -loglevel error
 
if ((Test-Path $Output) -and ((Get-Item $Output).Length -gt 0)) {
    Write-Host "SUCCESS: $Output" -ForegroundColor Green
} else {
    Write-Host "FAILED." -ForegroundColor Red
}
 
Read-Host "Done! Press Enter"