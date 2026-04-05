# slice_canvas.ps1
# Slices a 4224x64 canvas into individual display files.
# Place this script in the same folder as your file and run it.

$Input = Get-ChildItem -Filter "*.mp4" | Where-Object { $_.Name -notmatch "shortside|longside|media" } | Select-Object -First 1

if (-not $Input) {
    Write-Host "No mp4 file found in this folder." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit
}

$Base = [System.IO.Path]::GetFileNameWithoutExtension($Input.Name)

Write-Host "Slicing $($Input.Name)..." -ForegroundColor Cyan

$Slices = @(
    @{ Name = "${Base}_1344_shortside.mp4";      Crop = "crop=1344:64:0:0"    },
    @{ Name = "${Base}_576_longside_left.mp4";   Crop = "crop=576:64:1344:0"  },
    @{ Name = "${Base}_1728_longside_center.mp4"; Crop = "crop=1728:64:1920:0" },
    @{ Name = "${Base}_576_longside_right.mp4";  Crop = "crop=576:64:3648:0"  }
)

foreach ($Slice in $Slices) {
    Write-Host "  -> $($Slice.Name)" -ForegroundColor Cyan
    & ffmpeg -i "$($Input.FullName)" -vf $Slice.Crop -c:v libx264 -crf 16 -pix_fmt yuv420p $Slice.Name -y -loglevel error

    if ((Test-Path $Slice.Name) -and ((Get-Item $Slice.Name).Length -gt 0)) {
        Write-Host "     SUCCESS" -ForegroundColor Green
    } else {
        Write-Host "     FAILED" -ForegroundColor Red
    }
}

Read-Host "Done! Press Enter"
